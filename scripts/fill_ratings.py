#!/usr/bin/env python3
"""把未评分的对标帖按展示量补分：>10000 → 5，1000–10000 → 4，≤1000 → 1。

用法：
    python3 scripts/fill_ratings.py data/eval/target-ratings.json

输入是评分页导出的 [{id, score}]，已评的保留原分，只补缺的；输出 data/eval/target-ratings-filled.json。
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data/target/posts-merged/posts.jsonl"
OUT = ROOT / "data/eval/target-ratings-filled.json"


def views_of(p: dict) -> int:
    try:
        return int(p.get("views") or 0)
    except (TypeError, ValueError):
        return 0


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    scored = {r["id"]: r["score"] for r in json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))}
    posts = [json.loads(l) for l in SRC.read_text(encoding="utf-8").splitlines() if l.strip()]

    filled = 0
    for p in posts:
        if p["id"] in scored:
            continue
        v = views_of(p)
        scored[p["id"]] = 5 if v > 10000 else (4 if v > 1000 else 1)
        filled += 1

    out = [{"id": pid, "score": s} for pid, s in scored.items()]
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    dist: dict[int, int] = {}
    for s in scored.values():
        dist[s] = dist.get(s, 0) + 1
    print(f"filled={filled} total={len(out)} dist={dict(sorted(dist.items()))} -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
