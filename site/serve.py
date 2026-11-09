#!/usr/bin/env python3
"""审稿站的本地服务：静态文件 + 把页面上导出的 JSON 直接写进仓库。

    python3 site/serve.py 8777
    POST /save?name=target-ratings.json  → data/eval/<name>
    POST /save?name=review.json&dir=drafts → data/drafts/<name>
"""
from __future__ import annotations

import json
import pathlib
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent
ALLOWED = {"target-ratings.json": REPO / "data/eval", "review.json": REPO / "data/drafts"}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def do_POST(self) -> None:
        u = urlparse(self.path)
        if u.path != "/save":
            self.send_error(404, "not found")
            return
        name = parse_qs(u.query).get("name", [""])[0]
        target_dir = ALLOWED.get(name)
        if not target_dir:
            self.send_error(400, "name not allowed")
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            self.send_error(400, "invalid json")
            return
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / name
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        body = json.dumps({"saved": str(path.relative_to(REPO)), "rows": len(data)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        print(f"saved {path.relative_to(REPO)} ({len(data)} rows)")

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
    print(f"serving {ROOT} on http://127.0.0.1:{port}  (POST /save 可用)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
