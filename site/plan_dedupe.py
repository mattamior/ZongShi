#!/usr/bin/env python3
"""按正文去重：完全一样或几乎一样的帖子只留一条（优先「选定」>「备选」>「池」，再按时间）。

同主题但换了角度的帖子不算重复——那是不同写法，不是重复内容。
结果写 data/drafts/dedup.json，原稿不动。
"""
from __future__ import annotations

import difflib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
DATE = "2026-11-09"
THRESHOLD = 0.92


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
                out.append(d)
    rank = {"选定": 0, "备选": 1, "池": 2}
    out.sort(key=lambda r: (rank[r["origin"]], r.get("slot", ""), r.get("variant", 0)))
    return out


def main() -> None:
    norm = lambda t: "".join(t.split())
    kept: list[tuple[str, str]] = []  # (id, normalized text)
    dup: dict[str, str] = {}
    for r in rows():
        text = norm(r["text"])
        hit = None
        for kid, ktext in kept:
            if text == ktext:
                hit = kid
                break
            if abs(len(text) - len(ktext)) < 20 * 2:
                if difflib.SequenceMatcher(None, text, ktext).ratio() >= THRESHOLD:
                    hit = kid
                    break
        if hit:
            dup[r["id"]] = hit
        else:
            kept.append((r["id"], text))

    (ROOT.parent / "data/drafts/dedup.json").write_text(
        json.dumps(dup, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"total={len(kept) + len(dup)} kept={len(kept)} duplicates={len(dup)}")
    for d, k in list(dup.items())[:8]:
        print(f"  {d} == {k}")


if __name__ == "__main__":
    main()
