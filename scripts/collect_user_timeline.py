#!/usr/bin/env python3
"""Collect a full authored-post timeline through X's own GraphQL API, from a logged-in Chrome tab.

Why this exists: the public mirror and X's web profile UI both stop serving older posts
after a while, and scrolling a non-visible Chrome tab never triggers pagination at all
(Chrome throttles hidden tabs, so the sentinel never fires). This script skips the UI:
it runs `fetch` inside the already-signed-in tab, walks the `UserTweets` cursor itself,
and respects X's rate limiting instead of hammering it.

It never activates a window, never changes the active tab, and never navigates: the only
thing it does to Chrome is execute JavaScript in the tab you point it at.

Prerequisites (one-time, per Chrome profile):
    Chrome menu: 显示 -> 开发者 -> 允许 Apple 事件中的 JavaScript

Usage:
    python3 scripts/collect_user_timeline.py --window-id 1455424761 --tab 1 \
        --output-dir data/target/timeline-api
    python3 scripts/collect_user_timeline.py --window-id 1455424761 --tab 1 \
        --output-dir data/target/timeline-api --resume
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import subprocess
import sys
import tempfile
import time

HANDLE = "FKFKFKFKFKTB"
USER_ID = "2105258399885844480"
BEARER = (
    "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
)

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

DISCOVER = r"""(async () => {
  try {
    const src = [...document.querySelectorAll('script[src]')].map(s => s.src).find(u => /main\.[0-9a-f]+\.js$/.test(u));
    if (!src) { window.__zs_discover = JSON.stringify({error: 'no main bundle'}); return; }
    const text = await (await fetch(src)).text();
    const i = text.indexOf('operationName:"UserTweets"');
    if (i < 0) { window.__zs_discover = JSON.stringify({error: 'UserTweets not in bundle'}); return; }
    const before = text.slice(Math.max(0, i - 400), i);
    const idMatch = before.match(/queryId:"([A-Za-z0-9_-]+)"/);
    const from = text.lastIndexOf('featureSwitches:[', i);
    let start = text.indexOf('[', from), depth = 0, end = -1;
    for (let j = start; j < text.length; j++) {
      if (text[j] === '[') depth++;
      else if (text[j] === ']') { depth--; if (depth === 0) { end = j; break; } }
    }
    const names = JSON.parse(text.slice(start, end + 1));
    window.__zs_discover = JSON.stringify({queryId: idMatch ? idMatch[1] : null, features: names});
  } catch (e) {
    window.__zs_discover = JSON.stringify({error: String(e)});
  }
})()"""

FETCH_PAGE = r"""(() => {
  window.__zs = 'pending';
  const cursor = __CURSOR__;
  const variables = {"userId": "__USER_ID__", "count": 40, "includePromotedContent": true,
    "withQuickPromoteEligibilityTweetFields": true, "withVoice": true, "withV2Timeline": true};
  if (cursor) variables.cursor = cursor;
  const features = {};
  for (const n of __FEATURES__) features[n] = true;
  const cookie = document.cookie.match(/ct0=([^;]+)/);
  const url = 'https://x.com/i/api/graphql/__QUERY_ID__/UserTweets?variables=' +
    encodeURIComponent(JSON.stringify(variables)) + '&features=' + encodeURIComponent(JSON.stringify(features));
  fetch(url, {credentials: 'include', headers: {
    'authorization': 'Bearer __BEARER__',
    'x-csrf-token': cookie ? cookie[1] : '',
    'x-twitter-active-user': 'yes',
    'x-twitter-auth-type': 'OAuth2Session',
    'content-type': 'application/json'
  }}).then(async r => {
    const text = await r.text();
    if (!text.trim().startsWith('{')) {
      window.__zs = JSON.stringify({status: r.status, rows: [], next: null, err: text.slice(0, 120)});
      return;
    }
    const payload = JSON.parse(text);
    const timeline = ((((payload.data || {}).user || {}).result || {}).timeline || {}).timeline;
    const instructions = timeline && timeline.instructions;
    if (!instructions) {
      window.__zs = JSON.stringify({status: r.status, rows: [], next: null, err: text.slice(0, 200)});
      return;
    }
    const rows = [];
    let next = null;
    for (const instr of instructions) {
      if (instr.type !== 'TimelineAddEntries') continue;
      for (const entry of instr.entries) {
        if (entry.entryId && entry.entryId.indexOf('cursor-bottom') === 0) next = entry.content && entry.content.value;
        const result = entry.content && entry.content.itemContent &&
          entry.content.itemContent.tweet_results && entry.content.itemContent.tweet_results.result;
        if (!result) continue;
        const tweet = result.tweet || result;
        const legacy = tweet.legacy || {};
        const note = tweet.note_tweet && tweet.note_tweet.note_tweet_results &&
          tweet.note_tweet.note_tweet_results.result && tweet.note_tweet.note_tweet_results.result.text;
        const media = ((legacy.extended_entities || {}).media) || [];
        rows.push({
          id: tweet.rest_id,
          created: legacy.created_at,
          text: note || legacy.full_text || '',
          likes: legacy.favorite_count,
          reposts: legacy.retweet_count,
          replies: legacy.reply_count,
          views: tweet.views && tweet.views.count,
          media: media.length,
          reply_to: legacy.in_reply_to_status_id_str || null
        });
      }
    }
    window.__zs = JSON.stringify({status: r.status, rows: rows, next: next, err: null});
  }).catch(e => { window.__zs = JSON.stringify({status: 0, rows: [], next: null, err: String(e)}); });
  return 'started';
})()"""


def log(message: str) -> None:
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {message}", flush=True)


class Tab:
    def __init__(self, window_id: str, tab: int) -> None:
        self.window_id = window_id
        self.tab = tab

    def js(self, expression: str, timeout: int = 90) -> str:
        with tempfile.NamedTemporaryFile("w", suffix=".applescript", delete=False, encoding="utf-8") as handle:
            handle.write(RUN_JS)
            path = handle.name
        try:
            result = subprocess.run(
                ["osascript", path, self.window_id, str(self.tab), expression],
                capture_output=True, text=True, timeout=timeout,
            )
        finally:
            pathlib.Path(path).unlink(missing_ok=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip()[:300] or "osascript failed")
        out = result.stdout.strip()
        if out == "__ZS_NO_WINDOW__":
            raise RuntimeError(f"找不到窗口 id={self.window_id}")
        return out

    def js_async(self, expression: str, slot: str, tries: int = 25, interval: float = 2.0) -> str:
        """Start an async page-side job, then poll the slot it writes into."""
        self.js(f"window.{slot} = 'pending'; {expression}")
        for _ in range(tries):
            time.sleep(interval)
            value = self.js(f"window.{slot}")
            if value and value != "pending":
                return value
        raise RuntimeError(f"{slot} 未在预期时间内返回")


def discover(tab: Tab) -> tuple[str, list[str]]:
    raw = tab.js_async(DISCOVER, "__zs_discover")
    data = json.loads(raw)
    if data.get("error") or not data.get("queryId"):
        raise RuntimeError(f"无法从 bundle 里发现 UserTweets 参数: {data.get('error')}")
    return data["queryId"], data["features"]


def parse_twitter_time(value: str) -> tuple[str, int]:
    stamp = datetime.datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y")
    return value, int(stamp.timestamp())


def to_row(item: dict) -> dict:
    created_at, created_ts = parse_twitter_time(item["created"])
    media = {"count": item["media"]} if item.get("media") else {}
    return {
        "type": "status",
        "url": f"https://x.com/{HANDLE}/status/{item['id']}",
        "id": item["id"],
        "text": item["text"],
        "raw_text": {"text": item["text"]},
        "author": {"screen_name": HANDLE, "url": f"https://x.com/{HANDLE}", "id": USER_ID},
        "replies": item.get("replies"),
        "reposts": item.get("reposts"),
        "likes": item.get("likes"),
        "created_at": created_at,
        "created_timestamp": created_ts,
        "views": item.get("views"),
        "media": media,
        "provider": "x-graphql-usertweets",
    }


def load_state(path: pathlib.Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"cursor": None, "pages": 0, "query_id": None, "features": None, "done": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window-id", required=True)
    parser.add_argument("--tab", type=int, default=1)
    parser.add_argument("--output-dir", type=pathlib.Path, default=pathlib.Path("data/target/timeline-api"))
    parser.add_argument("--delay", type=float, default=8.0, help="每页之后的等待秒数")
    parser.add_argument("--max-pages", type=int, default=200)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--stop-before", default="2026-09-30", help="抓到这一天之前就停")
    args = parser.parse_args()

    if sys.platform != "darwin":
        raise SystemExit("只能在 macOS 上驱动 Google Chrome")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    corpus = args.output_dir / "posts.jsonl"
    state_path = args.output_dir / "state.json"
    state = load_state(state_path) if args.resume else {"cursor": None, "pages": 0, "query_id": None, "features": None, "done": False}

    tab = Tab(args.window_id, args.tab)
    log(f"窗口 {args.window_id} 标签 {args.tab}；页面 {tab.js('location.href')[:70]}")

    if not state.get("query_id"):
        log("从页面 bundle 里发现 UserTweets 参数…")
        state["query_id"], state["features"] = discover(tab)
        log(f"queryId={state['query_id']} features={len(state['features'])}")
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    features = json.dumps(state["features"])
    seen = set()
    if corpus.exists():
        for line in corpus.read_text(encoding="utf-8").splitlines():
            if line.strip():
                seen.add(json.loads(line)["id"])

    stop_before = datetime.date.fromisoformat(args.stop_before)
    cursor = state.get("cursor")
    pages = state.get("pages", 0)
    rate_limit_streak = 0

    with corpus.open("a", encoding="utf-8", newline="\n") as stream:
        while pages < args.max_pages:
            expression = (FETCH_PAGE
                          .replace("__CURSOR__", json.dumps(cursor))
                          .replace("__USER_ID__", USER_ID)
                          .replace("__FEATURES__", features)
                          .replace("__QUERY_ID__", state["query_id"])
                          .replace("__BEARER__", BEARER))
            raw = tab.js_async(expression, "__zs")
            page = json.loads(raw)
            pages += 1

            error = page.get("err") or ""
            if "Rate limit" in error or page.get("status") == 429:
                rate_limit_streak += 1
                wait = min(600, 60 * rate_limit_streak)
                log(f"限流（第 {rate_limit_streak} 次），等 {wait}s 后用同一游标重试")
                state.update({"cursor": cursor, "pages": pages})
                state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                time.sleep(wait)
                continue
            if error:
                log(f"第 {pages} 页出错：{error[:120]}")
                if page.get("status") in (401, 403):
                    log("会话失效，停止")
                    break
                time.sleep(15)
                continue

            rate_limit_streak = 0
            new_rows = [to_row(item) for item in page["rows"] if item.get("created") and item["id"] not in seen]
            for row in new_rows:
                seen.add(row["id"])
                stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            stream.flush()

            oldest = min((row["created_timestamp"] for row in new_rows), default=None)
            oldest_text = (datetime.datetime.fromtimestamp(oldest, datetime.timezone.utc).isoformat()
                           if oldest else "-")
            log(f"第 {pages} 页：{len(page['rows'])} 条，新增 {len(new_rows)}，累计 {len(seen)}，最早 {oldest_text}")

            cursor = page.get("next")
            state.update({"cursor": cursor, "pages": pages, "query_id": state["query_id"],
                          "features": state["features"], "done": not cursor})
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            if not cursor:
                log("游标耗尽，结束")
                break
            if oldest_text != "-" and datetime.datetime.fromtimestamp(oldest, datetime.timezone.utc).date() < stop_before:
                log(f"已经越过 {args.stop_before}，结束")
                break
            if not page["rows"]:
                log("空页；等待 30s 后重试同一游标")
                time.sleep(30)
                continue
            time.sleep(args.delay)

    log(f"完成：{len(seen)} 条，{pages} 页 → {corpus}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
