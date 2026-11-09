#!/usr/bin/env python3
"""把对标账号的评分整理成「起草优先参考」清单。

用法：
    python3 scripts/style_priority.py data/eval/target-ratings.json

输入是评分页导出的 [{id, score}]，输出 data/eval/target-priority.json：
按分数排序的帖子正文、长度/带图/问句画像，供起草时优先模仿高分表达。
"""
from __future__ import annotations

import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data/target/posts-merged/posts.jsonl"
OUT = ROOT / "data/eval/target-priority.json"


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    scores = {r["id"]: r["score"] for r in json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))}
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
    out = {"scored": len(scores), "profile": profile, "ranking": ranked}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} scored={len(scores)} ranked={len(ranked)} top_profile={profile}")


if __name__ == "__main__":
    main()
