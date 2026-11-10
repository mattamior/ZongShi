#!/usr/bin/env python3
"""把审稿站打包成可静态托管的 site/dist（Cloudflare Pages 直传用）。

    python3 site/build_dist.py
    npx wrangler pages deploy site/dist --project-name zongshi-review

dist 里只有页面会用到的东西：两个页面、样式、配图，外加 noindex 头。
「保存到仓库」按钮在非 localhost 域名下由页面自身隐藏（POST /save 依赖 site/serve.py）。
"""
from __future__ import annotations

import json
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
STATE_FILES = {"index.html": ROOT.parent / "data/drafts/review.json",
               "target.html": ROOT.parent / "data/eval/target-ratings.json"}
STATE_MAP = {"used": "used", "rejected": "rejected", "dup": "duplicate"}


def draft_texts() -> dict[str, str]:
    texts: dict[str, str] = {}
    for path in (ROOT.parent / "data/drafts").glob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                texts[row["id"]] = row.get("text", "")
    return texts


def seed_for(page: str, texts: dict[str, str]) -> dict:
    """仓库里保存的状态 → 页面启动时注入的 localStorage 初始值。"""
    path = STATE_FILES[page]
    if not path.exists():
        return {}
    rows = json.loads(path.read_text(encoding="utf-8"))
    if page == "target.html":
        return {r["id"]: r["score"] for r in rows if isinstance(r.get("score"), int)}
    seed = {}
    for r in rows:
        entry = {}
        status = STATE_MAP.get(r.get("state"))
        if status:
            entry["status"] = status
        # 与当前稿件正文不同才注入，避免把未改动的正文塞进「已改」渲染路径
        if r.get("text") and r["text"] != texts.get(r["id"]):
            entry["text"] = r["text"]
        if entry:
            seed[r["id"]] = entry
    return seed


def inject_state(html: str, seed: dict) -> str:
    payload = json.dumps(seed, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    tag = f'<script>window.__ZS_SEED__ = {payload};</script>\n<script>'
    if "<script>" not in html:
        raise SystemExit("页面里找不到 <script> 注入点")
    return html.replace("<script>", tag, 1)


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    texts = draft_texts()
    for name in PAGES:
        if name in STATE_FILES:
            html = (ROOT / name).read_text(encoding="utf-8")
            html = inject_state(html, seed_for(name, texts))
            (DIST / name).write_text(html, encoding="utf-8")
        else:
            shutil.copy2(ROOT / name, DIST / name)
    shutil.copytree(ROOT / "img", DIST / "img")
    (DIST / "_headers").write_text(HEADERS, encoding="utf-8")
    (DIST / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    total = sum(p.stat().st_size for p in DIST.rglob("*") if p.is_file())
    print(f"seed review={len(seed_for('index.html', texts))} "
          f"ratings={len(seed_for('target.html', texts))}")
    print(f"wrote {DIST.relative_to(ROOT.parent)}  files={sum(1 for p in DIST.rglob('*') if p.is_file())}  {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
