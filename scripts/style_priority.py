#!/usr/bin/env python3
"""把对标账号的评分整理成「起草优先参考」清单。

用法：
    python3 scripts/style_priority.py data/eval/target-ratings.json [--min 4]

输入是评分页导出的 [{id, score}]，输出 data/eval/target-priority.json：
只保留分数 > --min（默认 4，即 Principal 的「大于 4 分」）的帖子，
按分数排序给出正文、长度/带图/问句画像，供起草时优先模仿。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data/target/posts-merged/posts.jsonl"
OUT = ROOT / "data/eval/target-priority.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("ratings", nargs="?", help="评分页导出的 target-ratings.json")
    ap.add_argument("--min", type=int, default=4, help="只保留分数大于该值的帖子（默认 4）")
    args = ap.parse_args()
    if not args.ratings:
        raise SystemExit(__doc__)
    scores = {r["id"]: r["score"] for r in json.loads(pathlib.Path(args.ratings).read_text(encoding="utf-8"))}
    total_scored = len(scores)
    scores = {pid: s for pid, s in scores.items() if s > args.min}
    posts = {r["id"]: r for r in (json.loads(l) for l in SRC.read_text(encoding="utf-8").splitlines() if l.strip())}

    ranked = []
    for pid, score in scores.items():
        p = posts.get(pid)
        if not p:
            continue
        text = p["text"]
        ranked.append({
            "id": pid, "score": score, "text": text, "chars": len(text),
            "lines": len([l for l in text.splitlines() if l.strip()]),
            "question": "？" in text or "?" in text,
            "media": bool(p.get("media")),
            "views": p.get("views"), "likes": p.get("likes"),
        })
    ranked.sort(key=lambda r: (-r["score"], -(r["views"] or 0)))
    top = [r for r in ranked if r["score"] >= 8] or ranked[:20]

    chars = [r["chars"] for r in top] or [0]
    profile = {
        "top_n": len(top),
        "chars_median": int(statistics.median(chars)),
        "chars_p90": sorted(chars)[max(0, int(len(chars) * 0.9) - 1)],
        "lines_median": int(statistics.median([r["lines"] for r in top] or [0])),
        "question_share": round(sum(r["question"] for r in top) / len(top), 2) if top else 0,
        "media_share": round(sum(r["media"] for r in top) / len(top), 2) if top else 0,
    }
    out = {"scored": total_scored, "kept": len(ranked), "min_exclusive": args.min,
           "profile": profile, "ranking": ranked}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} scored={total_scored} kept(>{args.min})={len(ranked)} top_profile={profile}")


if __name__ == "__main__":
    main()
