#!/usr/bin/env python3
"""把当天稿池渲染成一个可直接双击打开的审稿页（数据内嵌，不依赖 fetch）。"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
DATE = "2026-11-09"

TAGS = {
    "T1": "社会", "T2": "商业", "T3": "产业", "T4": "民生", "T5": "体育", "T6": "消费",
    "T7": "电竞", "T8": "军事", "T9": "城市", "T10": "人物", "T11": "消费", "T12": "医疗",
    "T13": "社会", "T14": "天气", "T15": "文保", "T16": "历史", "T17": "社会", "T18": "娱乐",
    "T19": "娱乐", "T20": "人口", "T21": "科技", "T22": "时政", "T23": "消费", "T24": "军事",
    "T25": "体育", "T26": "时政", "T27": "城市", "T28": "科技", "T29": "生活", "T30": "职场",
    "H1": "娱乐", "H2": "职场", "H3": "产业", "H4": "教育", "H5": "文化", "H6": "健康",
    "H7": "民生", "H8": "电竞", "H9": "电竞", "H10": "天气",
}
E_TAGS = ["职场", "职场", "居住", "居住", "居住", "消费", "消费", "消费", "金融", "消费",
          "消费", "消费", "医疗", "医疗", "教育", "教育", "就业", "职场", "职场", "婚恋",
          "家庭", "社交", "消费", "出行", "出行", "居住", "出行", "生活", "消费", "居住"]
F_TAGS = ["人情", "人情", "教育", "职场", "职场", "就业", "消费", "民生", "民生", "社区",
          "居住", "消费", "出行", "保险", "金融", "金融", "金融", "消费", "医疗", "医疗",
          "医疗", "消费", "出行", "出行", "出行", "消费", "教育", "出行", "消费", "消费",
          "消费", "消费", "居住", "居住", "市政", "交通", "出行", "消费", "娱乐", "娱乐",
          "消费", "居住", "消费", "通信"]


ID_TAGS = {
    "s11": "时政", "s12": "社会", "s13": "城市", "s15": "体育", "s18": "军事",
    "t01": "商业", "t02": "文保", "t03": "社会", "t06": "娱乐", "t07": "历史",
    "t12": "产业", "u01": "民生", "u02": "娱乐", "u03": "人口", "u04": "医疗",
    "u05": "科技", "u06": "消费", "u07": "时政", "v01": "社会", "v04": "科技",
}


def tag_for(topic: str, pid: str = "") -> str:
    if pid in ID_TAGS:
        return ID_TAGS[pid]
    if topic in TAGS:
        return TAGS[topic]
    if topic.startswith("E"):
        return E_TAGS[int(topic[2:]) - 1]
    if topic.startswith("F"):
        return F_TAGS[int(topic[2:]) - 1]
    return "其他"


def load(path: str, origin: str) -> list[dict]:
    p = ROOT.parent / path
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    dedup = {}
    dedup_json = ROOT.parent / "data/drafts/dedup.json"
    if dedup_json.exists():
        dedup = json.loads(dedup_json.read_text(encoding="utf-8"))
    pool = load(f"data/drafts/{DATE}-batch.jsonl", "池")
    selected = load(f"data/drafts/{DATE}.jsonl", "选定")
    candidates = load(f"data/drafts/{DATE}-candidates.jsonl", "备选")
    images = {}
    imgjson = ROOT.parent / "data/drafts/images.json"
    if imgjson.exists():
        images = json.loads(imgjson.read_text(encoding="utf-8"))


    out = []
    for origin, rows in (("选定", selected), ("备选", candidates), ("池", pool)):
        for r in rows:
            text = r["text"]
            out.append({
                "id": r["id"], "account": r.get("account", "—"), "slot": r.get("slot", "—"),
                "origin": origin, "tag": tag_for(r.get("topic", ""), r["id"]),
                "type": "热点跟评" if r.get("claim") == "assertion" else "日常观察",
                "mode": "问句" if ("？" in text or "?" in text) else "陈述句",
                "text": text,
                "source_title": r.get("source_title", ""), "source_url": r.get("source_url", ""),
                "image": (images.get(r["id"]) or {}).get("src"),
                "image_credit": (images.get(r["id"]) or {}).get("credit", ""),
                "image_origin": (images.get(r["id"]) or {}).get("origin", ""),
                "preset": "duplicate" if dedup.get(r["id"]) else None,
            })

    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    data = json.dumps(out, ensure_ascii=False)
    html = tpl.replace("__DATA__", data)
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote site/index.html  posts={len(out)}  bytes={len(html.encode())}")


if __name__ == "__main__":
    main()
