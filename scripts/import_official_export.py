#!/usr/bin/env python3
"""Import an official X archive into the project's post schema.

The public timeline mirror only exposes the most recent few weeks; the account owner's
archive (`tweets.js` / `tweets-part*.js`) is the only authoritative source for earlier
posts. This reads those files and writes JSONL that `analyze_posts.py` can consume.

Usage:
    python3 scripts/import_official_export.py --archive-dir ~/Downloads/x-archive/data \
        --output data/target/official-export/posts.jsonl

Accept both layouts: `<archive>/data/tweets.js` and `<archive>/tweets.js`.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re

ARCHIVE_PREFIX = re.compile(r"^\s*window\.YTD\.[A-Za-z0-9_.]*\s*=\s*")


def load_archive_js(path: pathlib.Path) -> list:
    """Strip the `window.YTD.tweets.partN =` prefix and parse the JSON array."""
    text = path.read_text(encoding="utf-8")
    stripped = ARCHIVE_PREFIX.sub("", text, count=1).strip()
    if stripped.endswith(";"):
        stripped = stripped[:-1]
    payload = json.loads(stripped)
    if not isinstance(payload, list):
        raise ValueError(f"{path} does not contain a JSON array")
    return payload


def parse_created_at(value: str) -> int:
    """X archives use `Wed Oct 01 12:34:56 +0000 2026`."""
    return int(datetime.datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y").timestamp())


def is_retweet(text: str) -> bool:
    return text.startswith("RT @")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-dir", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--handle", default="FKFKFKFKFKTB")
    parser.add_argument("--account-id", default="2105258399885844480")
    args = parser.parse_args()

    candidates = sorted(args.archive_dir.glob("tweets*.js"))
    if not candidates and (args.archive_dir / "data").is_dir():
        candidates = sorted((args.archive_dir / "data").glob("tweets*.js"))
    if not candidates:
        raise SystemExit(f"No tweets*.js found under {args.archive_dir}")

    posts = []
    replies = retweets = mention_led = 0
    for path in candidates:
        for entry in load_archive_js(path):
            tweet = entry.get("tweet") if isinstance(entry, dict) else None
            if not isinstance(tweet, dict):
                continue
            text = tweet.get("full_text") or tweet.get("text") or ""
            status_id = tweet.get("id_str") or tweet.get("id")
            if not status_id:
                continue
            if is_retweet(text):
                retweets += 1
                continue
            reply_to = tweet.get("in_reply_to_status_id_str") or tweet.get("in_reply_to_status_id")
            if reply_to:
                replies += 1
                continue
            if text.startswith("@"):
                mention_led += 1
                continue
            posts.append(
                {
                    "id": str(status_id),
                    "text": text,
                    "created_timestamp": parse_created_at(tweet["created_at"]),
                    "lang": tweet.get("lang"),
                    "replying_to": None,
                    "likes": tweet.get("favorite_count"),
                    "replies": None,
                    "views": None,
                    "source": "official_export",
                    "media": [item.get("media_url_https") for item in (tweet.get("extended_entities") or {}).get("media", [])],
                }
            )

    posts.sort(key=lambda row: row["created_timestamp"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        for row in posts:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    stamps = [row["created_timestamp"] for row in posts]
    print(
        json.dumps(
            {
                "files": [str(path) for path in candidates],
                "posts": len(posts),
                "excluded": {"replies": replies, "retweets": retweets, "mention_led": mention_led},
                "window_utc": {
                    "first": datetime.datetime.fromtimestamp(min(stamps), datetime.timezone.utc).isoformat() if stamps else None,
                    "last": datetime.datetime.fromtimestamp(max(stamps), datetime.timezone.utc).isoformat() if stamps else None,
                },
                "output": str(args.output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
