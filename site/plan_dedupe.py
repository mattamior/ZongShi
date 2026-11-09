#!/usr/bin/env python3
"""按主题去重：同一主题只保留 2 条（优先「选定/备选」，再按时间），其余写入 data/drafts/dedup.json。"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
DATE = "2026-11-09"
KEEP = 2

# 选定/备选没有 topic 字段，手工对到池里的主题码
TOPIC_OF = {
    "s11": "T26", "s12": "T13", "s13": "T27", "s15": "T25", "s18": "T24",
    "t01": "T2", "t02": "T15", "t03": "T17", "t06": "T18", "t07": "T16", "t12": "T3",
    "u01": "T4", "u02": "T19", "u03": "T20", "u04": "T12", "u05": "T21",
    "u06": "T23", "u07": "T22", "v01": "T1", "v04": "T28",
}
RANK = {"选定": 0, "备选": 1, "池": 2}


def rows() -> list[dict]:
    out = []
    for name, origin in ((f"{DATE}.jsonl", "选定"), (f"{DATE}-candidates.jsonl", "备选"),
                         (f"{DATE}-batch.jsonl", "池")):
        p = ROOT.parent / "data/drafts" / name
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                d["origin"] = origin
                d["topic"] = d.get("topic") or TOPIC_OF.get(d["id"], d["id"])
                out.append(d)
    return out


def main() -> None:
    groups: dict[str, list[dict]] = {}
    for r in rows():
        groups.setdefault(r["topic"], []).append(r)

    dup = {}
    kept = 0
    for topic, items in groups.items():
        items.sort(key=lambda r: (RANK[r["origin"]], r.get("slot", ""), r.get("variant", 0)))
        for r in items[KEEP:]:
            dup[r["id"]] = "duplicate"
        kept += min(KEEP, len(items))

    (ROOT.parent / "data/drafts/dedup.json").write_text(
        json.dumps(dup, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"topics={len(groups)} kept={kept} duplicates={len(dup)}")


if __name__ == "__main__":
    main()
