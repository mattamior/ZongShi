#!/usr/bin/env python3
"""把未评分的对标帖按展示量补分（1–10 分制）。

档位：
    ≥100 万 → 10    50–100 万 → 9    20–50 万 → 8    10–20 万 → 7
    5–10 万 → 6     1–5 万 → 5       1000–1 万 → 4   100–1000 → 3
    10–100 → 2      <10 → 1

用法：
    python3 scripts/fill_ratings.py [评分.json] [--account btcmos] [--out 输出.json]

输入是评分页导出的 [{id, score}]，已评的保留原分，只补缺的；不给文件就全部按规则补。
语料来自 data/target/accounts.json（默认两个账号都补），输出默认
data/eval/target-ratings-filled.json。
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data/target/accounts.json"
OUT = ROOT / "data/eval/target-ratings-filled.json"
RULE = (
    (1_000_000, 10), (500_000, 9), (200_000, 8), (100_000, 7), (50_000, 6),
    (10_000, 5), (1_000, 4), (100, 3), (10, 2), (0, 1),
)


def view_score(views: int) -> int:
    for floor, score in RULE:
        if views >= floor:
            return score
    return 1


def views_of(post: dict) -> int:
    try:
        return int(post.get("views") or 0)
    except (TypeError, ValueError):
        return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("ratings", nargs="?", help="已导出的评分 JSON；省略则全部按展示补")
    ap.add_argument("--account", default="", help="只补该账号（accounts.json 的 key），默认全部")
    ap.add_argument("--out", type=pathlib.Path, default=OUT)
    args = ap.parse_args()

    scored: dict[str, int] = {}
    if args.ratings:
        rows = json.loads(pathlib.Path(args.ratings).read_text(encoding="utf-8"))
        scored = {r["id"]: r["score"] for r in rows}

    accounts = json.loads(MANIFEST.read_text(encoding="utf-8"))["accounts"]
    if args.account:
        accounts = [a for a in accounts if a["key"] == args.account]
        if not accounts:
            raise SystemExit(f"unknown account key: {args.account}")

    filled = 0
    for acct in accounts:
        posts = [json.loads(l) for l in (ROOT / acct["posts"]).read_text(encoding="utf-8").splitlines() if l.strip()]
        for p in posts:
            if p["id"] in scored:
                continue
            scored[p["id"]] = view_score(views_of(p))
            filled += 1

    out = [{"id": pid, "score": s} for pid, s in scored.items()]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    dist: dict[int, int] = {}
    for s in scored.values():
        dist[s] = dist.get(s, 0) + 1
    print(f"filled={filled} total={len(out)} dist={dict(sorted(dist.items()))} -> {args.out}")


if __name__ == "__main__":
    main()
