#!/usr/bin/env python3
"""把审稿站打包成可静态托管的 site/dist（Cloudflare Pages 直传用）。

    python3 site/build_dist.py
    npx wrangler pages deploy site/dist --project-name zongshi-review

dist 里只有页面会用到的东西：两个页面、样式、配图，外加 noindex 头。
「保存到仓库」按钮在非 localhost 域名下由页面自身隐藏（POST /save 依赖 site/serve.py）。
"""
from __future__ import annotations

import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent
DIST = ROOT / "dist"
PAGES = ("index.html", "target.html", "style.css")
HEADERS = """/*
  X-Robots-Tag: noindex, nofollow
  X-Content-Type-Options: nosniff
"""
ROBOTS = "User-agent: *\nDisallow: /\n"


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    for name in PAGES:
        shutil.copy2(ROOT / name, DIST / name)
    shutil.copytree(ROOT / "img", DIST / "img")
    (DIST / "_headers").write_text(HEADERS, encoding="utf-8")
    (DIST / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    total = sum(p.stat().st_size for p in DIST.rglob("*") if p.is_file())
    print(f"wrote {DIST.relative_to(ROOT.parent)}  files={sum(1 for p in DIST.rglob('*') if p.is_file())}  {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
