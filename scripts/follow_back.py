#!/usr/bin/env python3
"""回关：把最近关注我、而我还没关注的人，按日限额回关。

只在一件事上动用 Chrome：在指定窗口的指定标签页里执行 JavaScript。
不激活窗口、不切换标签、不导航、不新建标签——窗口可以一直待在后台。

流程：
  1. /1.1/account/verify_credentials.json  取自己的 user_id
  2. /1.1/followers/list.json              取最近 N 个关注我的人
  3. /1.1/friends/ids.json                 取我已关注的全部 id
  4. 差集 → 候选（关注我但我不关注）
  5. 逐个 POST /1.1/friendships/create.json，间隔随机 45–120 秒
  6. 台账写入 data/growth/follow-back.jsonl

默认 dry-run，只出候选不动手。--apply 才真的关注。

用法：
  python3 scripts/follow_back.py --list-windows
  python3 scripts/follow_back.py --window-id 123456 --tab 1 --dry-run
  python3 scripts/follow_back.py --window-id 123456 --tab 1 --apply --limit 20

前提：Chrome 菜单「显示 → 开发者 → 允许 Apple 事件中的 JavaScript」。
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import random
import subprocess
import sys
import time

BEARER = ("AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA")

DAILY_LIMIT = 20          # 每天最多回关多少个
DELAY_RANGE = (45, 120)   # 两次关注之间的秒数，人类节奏
MAX_CONSECUTIVE_ERRORS = 2
LEDGER = pathlib.Path("data/growth/follow-back.jsonl")
PAUSE_FLAG = pathlib.Path("data/growth/PAUSE")

RUN_JS = """on run argv
set target to item 1 of argv
set t to (item 2 of argv) as integer
set js to item 3 of argv
tell application "Google Chrome"
  repeat with w in windows
    if ((id of w) as text) is target then
      return execute (tab t of w) javascript js
    end if
  end repeat
  return "__ZS_NO_WINDOW__"
end tell
end run"""

LIST_WINDOWS = """tell application "Google Chrome"
  set out to ""
  repeat with w in windows
    set out to out & (id of w) & "\\t" & (index of w) & "\\t" & (title of w) & linefeed
  end repeat
  return out
end tell"""

# 取自己 + 最近关注者 + 已关注列表，一次装进 window.__zs_plan
PLAN_JS = r"""(async () => {
  const csrf = (document.cookie.match(/(?:^|; )ct0=([^;]+)/) || [])[1];
  if (!csrf) { window.__zs_plan = JSON.stringify({error: 'no ct0 cookie'}); return; }
  const H = {'authorization': 'Bearer __BEARER__', 'x-csrf-token': csrf,
             'x-twitter-active-user': 'yes', 'x-twitter-auth-type': 'OAuth2Session'};
  const get = async (u) => {
    const r = await fetch(u, {credentials: 'include', headers: H});
    const t = await r.text();
    if (!r.ok) throw new Error(u.replace(/[?].*/, '') + ' HTTP ' + r.status + ' ' + t.slice(0, 120));
    return JSON.parse(t);
  };
  try {
    const me = await get('/i/api/1.1/account/verify_credentials.json?skip_status=true&include_email=false');
    const uid = me.id_str;
    const fol = await get('/i/api/1.1/followers/list.json?user_id=' + uid + '&count=__COUNT__&skip_status=true&include_user_entities=false');
    const users = (fol.users || []).map(u => ({id: u.id_str, name: u.screen_name, followers: u.followers_count, verified: !!u.verified}));
    let friends = [], cursor = '-1';
    for (let page = 0; page < __PAGES__; page++) {
      const f = await get('/i/api/1.1/friends/ids.json?user_id=' + uid + '&count=5000&cursor=' + cursor);
      friends = friends.concat(f.ids || []);
      if (!f.next_cursor_str || f.next_cursor_str === '0' || f.next_cursor_str === cursor) break;
      cursor = f.next_cursor_str;
    }
    window.__zs_plan = JSON.stringify({me: uid, me_name: me.screen_name, users: users, friends: friends});
  } catch (e) {
    window.__zs_plan = JSON.stringify({error: String(e)});
  }
})()"""

FOLLOW_JS = r"""(() => {
  window.__zs_follow = 'pending';
  (async () => {
    const csrf = (document.cookie.match(/(?:^|; )ct0=([^;]+)/) || [])[1];
    const r = await fetch('/i/api/1.1/friendships/create.json', {
      method: 'POST', credentials: 'include',
      headers: {'authorization': 'Bearer __BEARER__', 'x-csrf-token': csrf,
                'content-type': 'application/x-www-form-urlencoded',
                'x-twitter-active-user': 'yes', 'x-twitter-auth-type': 'OAuth2Session'},
      body: 'user_id=__UID__&include_blocking=false'
    });
    const t = await r.text();
    window.__zs_follow = JSON.stringify({status: r.status, body: t.slice(0, 200)});
  })().catch(e => { window.__zs_follow = JSON.stringify({status: 0, body: String(e)}); });
})()"""


def exec_js(window_id: str, tab: int, js: str, timeout: float = 20.0) -> str:
    proc = subprocess.run(
        ["osascript", "-e", RUN_JS, window_id, str(tab), js],
        capture_output=True, text=True, timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"osascript failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def poll(window_id: str, tab: int, slot: str, timeout: float = 60.0) -> dict:
    """异步 JS 无法直接返回值，只能等它把结果写进 window.<slot>。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        raw = exec_js(window_id, tab, f"String(window.{slot} === undefined ? 'pending' : window.{slot})")
        if raw and raw != "pending":
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"error": f"bad payload: {raw[:200]}"}
        time.sleep(2)
    return {"error": "timeout"}


def list_windows() -> None:
    proc = subprocess.run(["osascript", "-e", LIST_WINDOWS], capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"osascript failed: {proc.stderr.strip()}")
    print("id\tindex\ttitle")
    print(proc.stdout.rstrip())


def today_count() -> int:
    if not LEDGER.exists():
        return 0
    day = datetime.datetime.now().astimezone().strftime("%Y-%m-%d")
    n = 0
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("ts", "").startswith(day) and row.get("ok"):
            n += 1
    return n


def append_ledger(row: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="按日限额回关关注我的人（默认只出候选）")
    ap.add_argument("--list-windows", action="store_true", help="列出 Chrome 窗口 id（不激活）")
    ap.add_argument("--window-id", help="目标 Chrome 窗口 id")
    ap.add_argument("--tab", type=int, default=1, help="标签页序号，默认 1")
    ap.add_argument("--count", type=int, default=200, help="拉取最近多少个关注者")
    ap.add_argument("--pages", type=int, default=2, help="已关注列表翻页数（每页 5000）")
    ap.add_argument("--limit", type=int, default=DAILY_LIMIT, help="本次最多回关几个")
    ap.add_argument("--apply", action="store_true", help="真的执行关注；不加则只出候选")
    args = ap.parse_args()

    if args.list_windows:
        list_windows()
        return 0
    if not args.window_id:
        sys.exit("需要 --window-id（或用 --list-windows 查）")

    if PAUSE_FLAG.exists():
        sys.exit(f"暂停开关存在：{PAUSE_FLAG}，先删除它再跑")

    already = today_count()
    budget = max(0, min(args.limit, DAILY_LIMIT) - already)
    print(f"今日已回关 {already}，上限 {DAILY_LIMIT}，本次可用 {budget}")

    exec_js(args.window_id, args.tab, "window.__zs_plan = 'pending'")
    plan_js = (PLAN_JS.replace("__COUNT__", str(args.count)).replace("__PAGES__", str(args.pages))
           .replace("__BEARER__", BEARER))
    exec_js(args.window_id, args.tab, plan_js)
    plan = poll(args.window_id, args.tab, "__zs_plan")
    if plan.get("error"):
        print(f"取数失败：{plan['error']}")
        return 2

    friends = set(plan["friends"])
    me = plan["me"]
    pending = [u for u in plan["users"] if u["id"] != me and u["id"] not in friends]
    print(f"当前账号：@{plan.get('me_name')} (id {me})")
    print(f"最近 {len(plan['users'])} 个关注者；已关注 {len(friends)} 人；待回关 {len(pending)} 人")
    for u in pending[:budget]:
        print(f"  {u['name']}\tid={u['id']}\t粉丝={u['followers']}")

    if not args.apply:
        print("\ndry-run：未执行任何关注。确认候选后加 --apply。")
        return 0
    if not pending:
        return 0

    ok = 0
    consecutive = 0
    for u in pending[:budget]:
        if PAUSE_FLAG.exists():
            print("检测到暂停开关，停止。")
            break
        follow_js = FOLLOW_JS.replace("__UID__", u["id"]).replace("__BEARER__", BEARER)
        exec_js(args.window_id, args.tab, follow_js)
        res = poll(args.window_id, args.tab, "__zs_follow", timeout=40)
        status = res.get("status", 0)
        success = status == 200
        append_ledger({
            "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "user_id": u["id"], "screen_name": u["name"], "status": status,
            "ok": success, "body": "" if success else str(res.get("body", ""))[:200],
        })
        print(f"{'OK ' if success else 'FAIL'} @{u['name']} → {status}")
        if success:
            ok += 1
            consecutive = 0
        else:
            consecutive += 1
            if consecutive >= MAX_CONSECUTIVE_ERRORS:
                print(f"连续 {consecutive} 次失败，停止（可能是账号被限，去查 403/429）。")
                break
        if u is not pending[:budget][-1]:
            time.sleep(random.uniform(*DELAY_RANGE))
    print(f"\n完成：回关 {ok} 个")
    return 0


if __name__ == "__main__":
    sys.exit(main())
