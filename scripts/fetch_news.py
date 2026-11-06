#!/usr/bin/env python3
"""Pull today's headlines with links, so «卧槽系» posts can cite a real source instead of inventing one.

Three public boards, no API keys, no login. Any single source may fail; the run only fails when
every source fails. Output is one JSONL row per headline with the link kept, because guard/banned.md
forbids assertions without a source.

Usage:
    python3 scripts/fetch_news.py --output-dir data/news
    python3 scripts/fetch_news.py --output-dir data/news --limit 30
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
TIMEOUT = 15

# 与选题配比挂钩的粗分类，只用于打标签，不参与过滤
TOPIC_HINTS = {
    "时政/社会": ["习近平", "国务院", "政策", "社保", "房价", "失业", "教育", "医疗", "警方", "法院",
                  "判决", "政府", "两会", "外交", "选举", "战争", "地震", "事故", "通报",
                  "被查", "投案", "纪委", "官员", "起诉", "派出所", "预警", "取消", "涨工资",
                  "利率", "遗产", "继承", "暴涨", "暴跌", "涨停", "跌停", "生育", "养老"],
    "AI/科技": ["AI", "人工智能", "大模型", "芯片", "机器人", "OpenAI", "GPT", "算力", "自动驾驶"],
    "币圈": ["比特币", "以太坊", "加密货币", "币", "区块链", "USDT"],
    "娱乐/八卦": ["明星", "演员", "离婚", "恋情", "演唱会", "综艺", "电影", "票房", "塌房"],
}


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read().decode("utf-8", errors="replace")


def tag_topic(title: str) -> str:
    for topic, hints in TOPIC_HINTS.items():
        if any(hint.lower() in title.lower() for hint in hints):
            return topic
    return "日常/其他"


def from_toutiao(limit: int) -> list[dict]:
    payload = json.loads(fetch("https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"))
    rows = []
    for rank, item in enumerate(payload.get("data", [])[:limit], 1):
        title = (item.get("Title") or "").strip()
        if not title:
            continue
        rows.append({"title": title, "url": item.get("Url", ""), "source": "toutiao",
                     "rank": rank, "hot": item.get("HotValue")})
    return rows


def from_zhihu(limit: int) -> list[dict]:
    payload = json.loads(fetch(f"https://api.zhihu.com/topstory/hot-lists/total?limit={limit}"))
    rows = []
    for rank, item in enumerate(payload.get("data", [])[:limit], 1):
        target = item.get("target") or {}
        title = (target.get("title") or "").strip()
        if not title:
            continue
        url = target.get("url") or ""
        match = re.search(r"/questions/(\d+)", url)
        if match:
            url = f"https://www.zhihu.com/question/{match.group(1)}"
        rows.append({"title": title, "url": url, "source": "zhihu", "rank": rank,
                     "hot": (item.get("detail_text") or "")})
    return rows


def from_baidu(limit: int) -> list[dict]:
    html = fetch("https://top.baidu.com/board?tab=realtime")
    words = re.findall(r'"word":"((?:[^"\\]|\\.){2,80})"', html)
    rows, seen = [], set()
    for rank, raw in enumerate(words, 1):
        title = json.loads(f'"{raw}"').strip()
        if not title or title in seen:
            continue
        seen.add(title)
        rows.append({"title": title,
                     "url": "https://www.baidu.com/s?wd=" + urllib.parse.quote(title),
                     "source": "baidu", "rank": rank, "hot": None})
        if len(rows) >= limit:
            break
    return rows


SOURCES = {"toutiao": from_toutiao, "zhihu": from_zhihu, "baidu": from_baidu}


def normalize(title: str) -> str:
    return re.sub(r"[\s\W_]+", "", title).lower()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=pathlib.Path, default=pathlib.Path("data/news"))
    parser.add_argument("--limit", type=int, default=25, help="每个来源取多少条")
    args = parser.parse_args()

    now = datetime.datetime.now(datetime.timezone.utc)
    collected: dict[str, dict] = {}
    failures: dict[str, str] = {}

    for name, loader in SOURCES.items():
        try:
            rows = loader(args.limit)
        except Exception as error:  # 单个源坏掉不影响整体
            failures[name] = f"{type(error).__name__}: {error}"
            continue
        for row in rows:
            row["topic"] = tag_topic(row["title"])
            row["fetched_at"] = now.isoformat(timespec="seconds")
            key = normalize(row["title"])
            if key and key not in collected:
                collected[key] = row

    if not collected:
        print(json.dumps({"error": "所有来源都失败", "failures": failures}, ensure_ascii=False), file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out = args.output_dir / f"{now.astimezone().date().isoformat()}.jsonl"
    with out.open("w", encoding="utf-8", newline="\n") as stream:
        for row in collected.values():
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")

    by_topic: dict[str, int] = {}
    for row in collected.values():
        by_topic[row["topic"]] = by_topic.get(row["topic"], 0) + 1
    print(json.dumps({"written": len(collected), "path": str(out), "by_topic": by_topic,
                      "failures": failures}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
