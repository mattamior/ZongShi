#!/usr/bin/env python3
"""生成对标账号评分页：把 298 条原创帖渲染成可打 0–10 分的页面。"""
from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT.parent / "data/target/posts-merged/posts.jsonl"


def main() -> None:
    rows = [json.loads(l) for l in SRC.read_text(encoding="utf-8").splitlines() if l.strip()]
    out = []
    for r in rows:
        ts = r.get("created_timestamp") or 0
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone()
        out.append({
            "id": r["id"], "text": r["text"], "chars": len(r["text"]),
            "date": dt.strftime("%Y-%m-%d"), "time": dt.strftime("%H:%M"),
            "ts": ts,
            "views": r.get("views"), "likes": r.get("likes"), "replies": r.get("replies"),
            "media": bool(r.get("media")), "url": r.get("url", ""),
        })
    out.sort(key=lambda x: x["ts"])
    tpl = (ROOT / "target_template.html").read_text(encoding="utf-8")
    html = tpl.replace("__DATA__", json.dumps(out, ensure_ascii=False))
    (ROOT / "target.html").write_text(html, encoding="utf-8")
    print(f"wrote site/target.html  posts={len(out)}  bytes={len(html.encode())}")


if __name__ == "__main__":
    main()
