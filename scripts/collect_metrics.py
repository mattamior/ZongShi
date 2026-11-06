#!/usr/bin/env python3
"""回收账号效果：每条已发帖的互动 + 账号层面的粉丝/关注快照。

数据来源分两路：
  - 帖子互动走公开接口 api.fxtwitter.com（点赞/回复/转推；它不返回查看数）
  - 账号层面走 Chrome 后台标签页读主页头部（粉丝、关注、帖子数）

每次运行追加一份快照到 data/metrics/snapshots.jsonl，跨天对比就能看出哪类稿子真的带来了关注。

用法：
  python3 scripts/collect_metrics.py --window-id 1455425140 --tab 1
  python3 scripts/collect_metrics.py --window-id 1455425140 --tab 1 --compare
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys
import time
import urllib.request

PUBLISHED = pathlib.Path("data/scheduled/published.jsonl")
SNAPSHOTS = pathlib.Path("data/metrics/snapshots.jsonl")

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

PROFILE_JS = r"""(() => {
  const col = document.querySelector('[data-testid="primaryColumn"]');
  if (!col) return JSON.stringify({error: 'no profile column'});
  const txt = col.innerText;
  const grab = (re) => { const m = txt.match(re); return m ? m[1] : null; };
  return JSON.stringify({
    followers: grab(/([\d,\.]+)\s*(?:Followers|粉丝)/i),
    following: grab(/([\d,\.]+)\s*(?:Following|正在关注)/i),
    posts: grab(/([\d,\.]+)\s*(?:posts|帖子)/i),
  });
})()"""


def ex(window_id: str, tab: int, js: str) -> str:
    proc = subprocess.run(["osascript", "-e", RUN_JS, window_id, str(tab), js],
                          capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return proc.stdout.strip()


def num(s: str | None) -> int | None:
    if not s:
        return None
    s = s.replace(",", "").replace("，", "")
    m = re.match(r"([\d.]+)\s*([万KkMm]?)", s)
    if not m:
        return None
    v = float(m.group(1))
    unit = m.group(2).lower()
    v *= {"万": 10000, "k": 1000, "m": 1_000_000}.get(unit, 1)
    return int(v)


def fx_metrics(tweet_id: str) -> dict:
    url = f"https://api.fxtwitter.com/status/{tweet_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "zongshi-metrics/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
        t = data.get("tweet") or {}
        return {"likes": t.get("likes"), "replies": t.get("replies"),
                "reposts": t.get("retweets"), "views": t.get("views")}
    except Exception as error:  # 单条失败不该让整轮失败
        return {"error": str(error)[:120]}


def load_previous() -> dict:
    if not SNAPSHOTS.exists():
        return {}
    last = None
    for line in SNAPSHOTS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            last = json.loads(line)
    return last or {}


def main() -> int:
    ap = argparse.ArgumentParser(description="回收帖子与账号指标")
    ap.add_argument("--window-id", required=True)
    ap.add_argument("--tab", type=int, default=1)
    ap.add_argument("--handle", default="MattDjj")
    ap.add_argument("--compare", action="store_true", help="和上一份快照比增量")
    args = ap.parse_args()

    if not PUBLISHED.exists():
        sys.exit(f"没有台账：{PUBLISHED}，先跑 match_published.py")

    ex(args.window_id, args.tab, f"location.href='https://x.com/{args.handle}'; 'nav'")
    time.sleep(7)
    profile = json.loads(ex(args.window_id, args.tab, PROFILE_JS))
    if profile.get("error"):
        sys.exit(f"读主页失败：{profile['error']}")

    posts = []
    for line in PUBLISHED.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        m = fx_metrics(row["tweet_id"])
        posts.append({"tweet_id": row["tweet_id"], "draft_id": row.get("draft_id"),
                      "posted_at": row.get("posted_at"), **m})

    snap = {
        "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "account": {
            "followers": num(profile.get("followers")),
            "following": num(profile.get("following")),
            "posts": num(profile.get("posts")),
        },
        "posts": posts,
    }
    SNAPSHOTS.parent.mkdir(parents=True, exist_ok=True)
    with SNAPSHOTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(snap, ensure_ascii=False) + "\n")

    print(f"账号：粉丝 {snap['account']['followers']} / 关注 {snap['account']['following']} / 帖子 {snap['account']['posts']}")
    print(f"{'帖子':<22}{'稿':<6}{'赞':>4}{'回':>4}{'转':>4}")
    for p in posts:
        print(f"{p['tweet_id']:<22}{str(p.get('draft_id') or '-'):<6}"
              f"{str(p.get('likes')):>4}{str(p.get('replies')):>4}{str(p.get('reposts')):>4}")

    if args.compare:
        prev = load_previous()
        prev = {p["tweet_id"]: p for p in prev.get("posts", [])}
        prev_acc = (prev and None) or None
        print("\n与上一份快照相比：")
        for p in posts:
            q = prev.get(p["tweet_id"])
            if not q:
                print(f"  {p['tweet_id']} 新增")
                continue
            d1 = (p.get("likes") or 0) - (q.get("likes") or 0)
            d2 = (p.get("replies") or 0) - (q.get("replies") or 0)
            print(f"  {p['tweet_id']} 赞 +{d1} 回 +{d2}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
