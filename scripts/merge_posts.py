#!/usr/bin/env python3
"""Union post JSONL files by status ID and write a single sorted corpus.

Used to fold an official archive (`import_official_export.py`) into the
mirror-derived corpus without duplicating posts that both sources contain.

Usage:
    python3 scripts/merge_posts.py --output data/target/posts-merged/posts.jsonl \
        data/target/20261105T-posts/posts.jsonl data/target/official-export/posts.jsonl
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=pathlib.Path, nargs="+")
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()

    merged: dict[str, dict] = {}
    per_source = {}
    for path in args.inputs:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        per_source[str(path)] = len(rows)
        for row in rows:
            rid = str(row["id"])
            previous = merged.get(rid)
            # Prefer the record that carries reach numbers; mirror rows have views, archives do not.
            if previous is None or (previous.get("views") is None and row.get("views") is not None):
                merged[rid] = row

    rows = sorted(merged.values(), key=lambda row: int(row["created_timestamp"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    print(
        json.dumps(
            {
                "inputs": per_source,
                "unique_posts": len(rows),
                "output": str(args.output),
                "window_utc": {
                    "first": datetime.datetime.fromtimestamp(int(rows[0]["created_timestamp"]), datetime.timezone.utc).isoformat() if rows else None,
                    "last": datetime.datetime.fromtimestamp(int(rows[-1]["created_timestamp"]), datetime.timezone.utc).isoformat() if rows else None,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
