#!/usr/bin/env python3
"""在后台标签页里做互动：点赞、关注。不激活窗口、不抢焦点。

候选来自 X 的实时搜索流（`#交朋友` 等圈子标签），一页约 10–20 条，
比主页时间线稳——隐藏标签页不会触发 X 的分页，但首屏服务端就渲染好了。

三个子命令：
  scan    打开搜索流，把首屏卡片写进 data/growth/pool.jsonl
  like    对池子里最新的帖子点赞（每日上限 50，间隔 20–60 秒）
  follow  关注帖子的作者（每日上限 20，间隔 45–120 秒）

台账 data/growth/ledger.jsonl 记录每一次动作；data/growth/PAUSE 存在即停。

用法：
  python3 scripts/engage.py scan  --window-id 123 --tab 1 --queries "#交朋友" "蓝朋友"
  python3 scripts/engage.py like  --window-id 123 --tab 1 --limit 10
  python3 scripts/engage.py follow --window-id 123 --tab 1 --limit 5 --apply
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
import urllib.parse

BASE = pathlib.Path("data/growth")
POOL = BASE / "pool.jsonl"
LEDGER = BASE / "ledger.jsonl"
PAUSE = BASE / "PAUSE"

LIKE_CAP = 50
FOLLOW_CAP = 20
REPLY_CAP = 10
LIKE_DELAY = (20, 60)
FOLLOW_DELAY = (45, 120)

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

SCAN_JS = r"""(() => {
  const out = [];
  for (const a of document.querySelectorAll('article')) {
    const link = a.querySelector('a[href*="/status/"]');
    if (!link) continue;
    const m = link.getAttribute('href').match(/^\/([^/]+)\/status\/(\d+)/);
    if (!m) continue;
    const like = a.querySelector('[data-testid="like"],[data-testid="unlike"]');
    const timeEl = a.querySelector('time');
    out.push({
      handle: m[1], id: m[2],
      text: a.innerText.split('\n').slice(3).join('\n').slice(0, 300),
      liked: like ? like.getAttribute('data-testid') === 'unlike' : null,
      at: timeEl ? timeEl.getAttribute('datetime') : null
    });
  }
  return JSON.stringify(out);
})()"""

LIKE_JS = r"""(() => {
  const id = "__ID__";
  const card = [...document.querySelectorAll('article')].find(a => a.querySelector('a[href*="/status/' + id + '"]'));
  if (!card) return 'card-not-found';
  const b = card.querySelector('[data-testid="like"]');
  if (!b) return 'already-liked-or-no-button';
  b.click();
  return 'clicked';
})()"""

LIKE_STATE_JS = r"""(() => {
  const id = "__ID__";
  const card = [...document.querySelectorAll('article')].find(a => a.querySelector('a[href*="/status/' + id + '"]'));
  if (!card) return 'card-not-found';
  const b = card.querySelector('[data-testid="like"],[data-testid="unlike"]');
  return b ? b.getAttribute('data-testid') : 'none';
})()"""

FOLLOW_PROBE_JS = r"""(() => {
  const scope = document.querySelector('[data-testid="primaryColumn"]') || document;
  const btns = [...scope.querySelectorAll('[data-testid$="-follow"],[data-testid$="-unfollow"]')]
    .filter(b => b.offsetParent !== null && !/订阅|Subscribe/i.test(b.innerText.trim()));
  const b = btns[0] || null;
  return JSON.stringify({present: !!b, testid: b ? b.getAttribute('data-testid') : null,
                         label: b ? b.innerText.trim() : null});
})()"""

FOLLOW_CLICK_JS = r"""(() => {
  const scope = document.querySelector('[data-testid="primaryColumn"]') || document;
  const labels = ['关注', '回关', 'Follow', 'Follow back'];
  const btns = [...scope.querySelectorAll('[data-testid$="-follow"]')]
    .filter(b => b.offsetParent !== null && labels.includes(b.innerText.trim()));
  if (!btns.length) return 'no-follow-button';
  btns[0].click();
  return 'clicked';
})()"""


def ex(window_id: str, tab: int, js: str, timeout: float = 25.0) -> str:
    proc = subprocess.run(["osascript", "-e", RUN_JS, window_id, str(tab), js],
                          capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return proc.stdout.strip()


def nav(window_id: str, tab: int, url: str, wait: float = 6.0) -> None:
    """用 location.href 导航，不用 AppleScript 的 set URL —— 后者会把窗口提到前台。"""
    ex(window_id, tab, f"location.href={json.dumps(url)}; 'nav'")
    time.sleep(wait)


def today(action: str) -> int:
    if not LEDGER.exists():
        return 0
    day = datetime.datetime.now().astimezone().strftime("%Y-%m-%d")
    n = 0
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("action") == action and row.get("ok") and row.get("ts", "").startswith(day):
            n += 1
    return n


def log(action: str, row: dict) -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                            "action": action, **row}, ensure_ascii=False) + "\n")


def seen(action: str) -> set[str]:
    if not LEDGER.exists():
        return set()
    out = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("action") == action and row.get("ok"):
            out.add(row.get("target", ""))
    return out


def load_pool() -> list[dict]:
    if not POOL.exists():
        return []
    rows = {}
    for line in POOL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[row["id"]] = row
    return list(rows.values())


def cmd_scan(args) -> int:
    BASE.mkdir(parents=True, exist_ok=True)
    total = 0
    new = 0
    existing = {r["id"] for r in load_pool()}
    with POOL.open("a", encoding="utf-8") as f:
        for q in args.queries:
            url = "https://x.com/search?q=" + urllib.parse.quote(q) + "&src=typed_query&f=live"
            nav(args.window_id, args.tab, url, wait=args.wait)
            raw = ex(args.window_id, args.tab, SCAN_JS)
            try:
                cards = json.loads(raw)
            except json.JSONDecodeError:
                print(f"[{q}] 解析失败：{raw[:120]}")
                continue
            for c in cards:
                total += 1
                if c["id"] in existing:
                    continue
                c["query"] = q
                c["scanned_at"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
                existing.add(c["id"])
                new += 1
            print(f"[{q}] 首屏 {len(cards)} 条，新增 {new}")
    print(f"合计看到 {total} 条，新增入池 {new} 条 → {POOL}")
    return 0


def cmd_like(args) -> int:
    budget = min(args.limit, LIKE_CAP - today("like"))
    if budget <= 0:
        print(f"今日点赞已达上限 {LIKE_CAP}")
        return 0
    done = seen("like")
    pool = [p for p in load_pool() if p["id"] not in done and not p.get("liked")]
    if not pool:
        print("池子里没有可点赞的新帖，先跑 scan")
        return 0
    print(f"可点 {len(pool)} 条，本次额度 {budget}")
    ok = 0
    consecutive = 0
    for card in pool[:budget]:
        if PAUSE.exists():
            print("暂停开关存在，停止")
            break
        nav(args.window_id, args.tab, f"https://x.com/{card['handle']}/status/{card['id']}", wait=args.wait)
        state = ex(args.window_id, args.tab, LIKE_STATE_JS.replace("__ID__", card["id"]))
        if state == "unlike":
            print(f"SKIP @{card['handle']} 已经赞过")
            log("like", {"target": card["id"], "handle": card["handle"], "ok": False, "reason": "already-liked"})
            continue
        clicked = ex(args.window_id, args.tab, LIKE_JS.replace("__ID__", card["id"]))
        time.sleep(2)
        after = ex(args.window_id, args.tab, LIKE_STATE_JS.replace("__ID__", card["id"]))
        success = clicked == "clicked" and after == "unlike"
        log("like", {"target": card["id"], "handle": card["handle"], "ok": success,
                     "reason": "" if success else f"{clicked}/{after}"})
        print(f"{'OK ' if success else 'FAIL'} @{card['handle']} {card['id']} ({clicked}/{after})")
        if success:
            ok += 1
            consecutive = 0
        else:
            consecutive += 1
            if consecutive >= 3:
                print("连续 3 次失败，停止")
                break
        time.sleep(random.uniform(*LIKE_DELAY))
    print(f"完成：点赞 {ok} 条")
    return 0


def cmd_follow(args) -> int:
    budget = min(args.limit, FOLLOW_CAP - today("follow"))
    if budget <= 0:
        print(f"今日关注已达上限 {FOLLOW_CAP}")
        return 0
    done = seen("follow")
    pool = [p for p in load_pool() if p["handle"] not in done]
    handles = []
    for p in pool:
        if p["handle"].lower() not in [h.lower() for h in handles]:
            handles.append(p["handle"])
    if not handles:
        print("池子里没有新作者，先跑 scan")
        return 0
    targets = handles[:budget]
    print(f"候选作者 {len(handles)} 个，本次额度 {budget}：{', '.join(targets)}")
    if not args.apply:
        print("dry-run：未执行关注，确认后加 --apply")
        return 0
    ok = 0
    consecutive = 0
    for handle in targets:
        if PAUSE.exists():
            print("暂停开关存在，停止")
            break
        nav(args.window_id, args.tab, f"https://x.com/{handle}", wait=args.wait)
        probe = json.loads(ex(args.window_id, args.tab, FOLLOW_PROBE_JS))
        if not probe.get("present"):
            print(f"SKIP @{handle} 没有关注按钮")
            continue
        if "unfollow" in (probe.get("testid") or ""):
            print(f"SKIP @{handle} 已关注")
            log("follow", {"target": handle, "ok": False, "reason": "already-following"})
            continue
        clicked = ex(args.window_id, args.tab, FOLLOW_CLICK_JS)
        time.sleep(3)
        after = json.loads(ex(args.window_id, args.tab, FOLLOW_PROBE_JS))
        success = clicked == "clicked" and "unfollow" in (after.get("testid") or "")
        log("follow", {"target": handle, "ok": success,
                       "reason": "" if success else f"{clicked}/{after.get('testid')}"})
        print(f"{'OK ' if success else 'FAIL'} @{handle} ({clicked}/{after.get('testid')})")
        if success:
            ok += 1
            consecutive = 0
        else:
            consecutive += 1
            if consecutive >= 3:
                print("连续 3 次失败，停止（检查是否被限流）")
                break
        time.sleep(random.uniform(*FOLLOW_DELAY))
    print(f"完成：关注 {ok} 个")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="后台标签页互动：scan / like / follow")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("scan", "like", "follow"):
        p = sub.add_parser(name)
        p.add_argument("--window-id", required=True)
        p.add_argument("--tab", type=int, default=1)
        p.add_argument("--wait", type=float, default=6.0, help="每次导航后等几秒")
        if name == "scan":
            p.add_argument("--queries", nargs="+", default=["#交朋友"])
        else:
            p.add_argument("--limit", type=int, default=10)
        if name == "follow":
            p.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if PAUSE.exists():
        print(f"暂停开关存在：{PAUSE}")
        return 3
    return {"scan": cmd_scan, "like": cmd_like, "follow": cmd_follow}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
