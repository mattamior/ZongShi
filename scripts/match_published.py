#!/usr/bin/env python3
"""把已经发出去的帖子对回稿件：哪条稿子、几点发的、改了什么。

用途：Principal 在 App 里手动定时发帖，稿子在我们这里。主页上能看到已发的帖子，
把它们和稿件库做文本比对，就能反推出排期，不用手工记。

做法：读主页首屏的 article（后台标签页即可，首屏是服务端渲染的），
归一化（去掉 @grok、#标签、空白、标点）后用 difflib 找最像的稿子。

用法：
  python3 scripts/match_published.py --window-id 1455425140 --tab 1
  python3 scripts/match_published.py --window-id 1455425140 --tab 1 --threshold 0.6
"""
from __future__ import annotations

import argparse
import datetime
import difflib
import json
import pathlib
import re
import subprocess
import sys
import time

SOURCES = [
    ("今日稿", "data/drafts/2026-11-06.jsonl"),
    ("第一批", "data/eval/20261106T-samples/samples.jsonl"),
    ("第二批", "data/eval/20261106T-samples2/samples.jsonl"),
    ("第三批", "data/eval/20261106T-samples3/samples.jsonl"),
]
OUT = pathlib.Path("data/scheduled/published.jsonl")

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

READ_JS = r"""(() => {
  const out = [];
  for (const a of document.querySelectorAll('article')) {
    const l = a.querySelector('a[href*="/status/"]');
    if (!l) continue;
    const m = l.getAttribute('href').match(/^\/([^/]+)\/status\/(\d+)/);
    const t = a.querySelector('time');
    if (!m) continue;
    out.push({handle: m[1], id: m[2], at: t ? t.getAttribute('datetime') : null,
              text: a.innerText});
  }
  return JSON.stringify(out);
})()"""


def norm(s: str) -> str:
    s = s.replace("@grok", " ").replace("@Grok", " ")
    s = re.sub(r"#\S+", " ", s)
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[，。！？、：；,.!?;:~～…「」“”\"'（）()\[\]<>《》-]", "", s)
    return s


def ex(window_id: str, tab: int, js: str) -> str:
    proc = subprocess.run(["osascript", "-e", RUN_JS, window_id, str(tab), js],
                          capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return proc.stdout.strip()


def load_drafts() -> list[dict]:
    rows = []
    for label, path in SOURCES:
        p = pathlib.Path(path)
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            rows.append({"source": label, "id": r["id"], "text": r["text"], "norm": norm(r["text"])})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="把已发布帖子对回稿件")
    ap.add_argument("--window-id", required=True)
    ap.add_argument("--tab", type=int, default=1)
    ap.add_argument("--threshold", type=float, default=0.60)
    ap.add_argument("--refresh", action="store_true", help="先导航到主页再读")
    args = ap.parse_args()

    if args.refresh:
        ex(args.window_id, args.tab, "location.href='https://x.com/MattDjj'; 'nav'")
        time.sleep(7)

    raw = ex(args.window_id, args.tab, READ_JS)
    try:
        posts = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(f"读取失败：{raw[:200]}")

    drafts = load_drafts()
    known = set()
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                known.add(json.loads(line)["tweet_id"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    new_rows = []
    for post in posts:
        if post["id"] in known:
            continue
        # article 的 innerText 里混着头像区、时间、互动数，先把正文段取出来
        body = "\n".join(post["text"].split("\n")[1:])
        target = norm(body)
        best, score = None, 0.0
        for d in drafts:
            r = difflib.SequenceMatcher(None, target, d["norm"]).ratio()
            if r > score:
                best, score = d, r
        row = {
            "tweet_id": post["id"], "handle": post["handle"], "posted_at": post["at"],
            "draft_id": best["id"] if score >= args.threshold else None,
            "draft_source": best["source"] if score >= args.threshold else None,
            "similarity": round(score, 3),
            "edited": score < 0.999 and score >= args.threshold,
            "text": body.strip()[:200],
            "matched_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        new_rows.append(row)

    with OUT.open("a", encoding="utf-8") as f:
        for row in new_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    for row in new_rows:
        tag = row["draft_id"] or "未匹配"
        mark = "（有改动）" if row["edited"] else ""
        print(f"{row['posted_at']}  {row['tweet_id']}  → {tag} {row['draft_source'] or ''} "
              f"相似度 {row['similarity']}{mark}")
    print(f"\n新增 {len(new_rows)} 条；台账 {OUT}")

    # 稿件库侧：哪些还没发
    used = {json.loads(l)["draft_id"] for l in OUT.read_text(encoding="utf-8").splitlines() if l.strip()}
    unused = [d for d in drafts if d["id"] not in used and d["source"] == "今日稿"]
    print(f"今日稿未发：{', '.join(d['id'] for d in unused) or '无'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
