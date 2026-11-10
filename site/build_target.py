#!/usr/bin/env python3
"""生成对标账号评分页：把各账号原创帖渲染成可打 0–10 分的页面。

账号清单在 data/target/accounts.json，每条给出 handle、显示名和原创帖文件。
新增账号只需往清单里加一条，再重跑本脚本。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent
MANIFEST = REPO / "data/target/accounts.json"


def normalize(row: dict, acct: dict) -> dict:
    ts = row.get("created_timestamp") or 0
    dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone()
    return {
        "id": row["id"], "text": row["text"], "chars": len(row["text"]),
        "date": dt.strftime("%Y-%m-%d"), "time": dt.strftime("%H:%M"),
        "ts": ts,
        "views": row.get("views"), "likes": row.get("likes"), "replies": row.get("replies"),
        "media": bool(row.get("media")), "url": row.get("url", ""),
        "acct": acct["key"],
    }


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    accounts = manifest["accounts"]
    out = []
    for acct in accounts:
        path = REPO / acct["posts"]
        rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        out.extend(normalize(r, acct) for r in rows)
        print(f"{acct['key']}: {len(rows)} posts")
    out.sort(key=lambda x: x["ts"])
    tpl = (ROOT / "target_template.html").read_text(encoding="utf-8")
    html = tpl.replace("__DATA__", json.dumps(out, ensure_ascii=False))
    html = html.replace("__ACCOUNTS__", json.dumps(accounts, ensure_ascii=False))
    css_ver = hashlib.sha1((ROOT / "style.css").read_bytes()).hexdigest()[:8]
    html = html.replace('href="style.css"', f'href="style.css?v={css_ver}"')
    (ROOT / "target.html").write_text(html, encoding="utf-8")
    print(f"wrote site/target.html  posts={len(out)}  bytes={len(html.encode())}")


if __name__ == "__main__":
    main()
