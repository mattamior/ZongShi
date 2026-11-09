#!/usr/bin/env python3
"""给当天热点稿找新闻配图：先取原文 og:image，取不到用图片搜索兜底，仍没有就不配图。

只处理有 source_url 的稿子；日常观察类不配图。结果写 data/drafts/images.json。
    python3 site/fetch_images.py              # 原文优先 + 搜索兜底
    python3 site/fetch_images.py --no-search  # 只要原文图
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import urllib.parse
import urllib.request

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent
DATE = "2026-11-09"
UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
MIN_W = 480

PAGE_PATTERNS = [
    r'property="og:image"\s+content="([^"]+)"',
    r'name="twitter:image"\s+content="([^"]+)"',
    r'<meta[^>]+itemprop="image"[^>]+content="([^"]+)"',
    r'"image"\s*:\s*"(https?://[^"]+?\.(?:jpg|jpeg|png|webp))"',
]
SIZE_RE = re.compile(r'[?&]w=(\d+)[^"]*?[?&]h=(\d+)')


def get(url: str, limit: int = 800_000) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=15).read(limit)


def page_image(url: str) -> str | None:
    try:
        html = get(url).decode("utf-8", "ignore")
    except Exception:
        return None
    for pat in PAGE_PATTERNS:
        m = re.search(pat, html)
        if m:
            return m.group(1).replace("&amp;", "&")
    return None


def search_image(title: str) -> str | None:
    q = urllib.parse.quote(re.sub(r"[「」《》!！?？]", " ", title)[:30])
    url = f"https://image.baidu.com/search/acjson?tn=resultjson_com&word={q}&pn=0&rn=20&ie=utf-8"
    try:
        raw = get(url).decode("utf-8", "ignore").replace('\\"', '"')
    except Exception:
        return None
    for m in re.finditer(r'"(?:middleURL|thumbURL)":"(https?://[^"]+)"', raw):
        u = m.group(1).replace("\\/", "/")
        size = SIZE_RE.search(u)
        if size and (int(size.group(1)) < MIN_W or int(size.group(2)) < 260):
            continue
        return u
    return None


def save_image(src: str, path: pathlib.Path) -> bool:
    try:
        blob = get(src)
        import io
        im = Image.open(io.BytesIO(blob)).convert("RGB")
        if im.width > 1000:
            im = im.resize((1000, round(im.height * 1000 / im.width)), Image.LANCZOS)
        im.save(path, quality=82, optimize=True)
        return True
    except Exception:
        return False


def post_rows() -> list[dict]:
    rows = []
    for name in (f"{DATE}-batch.jsonl", f"{DATE}.jsonl", f"{DATE}-candidates.jsonl"):
        p = ROOT.parent / "data/drafts" / name
        if p.exists():
            rows += [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-search", action="store_true", help="只用原文图，搜索不兜底")
    args = ap.parse_args()

    news = {}
    for line in (ROOT.parent / "data/news" / f"{DATE}.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            news.setdefault(r["url"], r)

    out_dir = ROOT / "img"
    out_dir.mkdir(exist_ok=True)
    for f in out_dir.glob("*"):
        f.unlink()
    (ROOT.parent / "data/drafts/images.json").unlink(missing_ok=True)

    cache: dict[str, dict | None] = {}
    for url, item in news.items():
        src, origin, credit = page_image(url), "article", item["title"][:28]
        if not src and not args.no_search:
            src, origin, credit = search_image(item["title"]), "search", "百度图片"
        if not src:
            cache[url] = None
            continue
        name = f"n{len(cache):03d}.jpg"
        if not save_image(src, out_dir / name):
            cache[url] = None
            continue
        cache[url] = {"src": f"img/{name}", "origin": origin, "credit": credit}

    mapping = {}
    for d in post_rows():
        hit = cache.get(d.get("source_url"))
        if hit:
            mapping[d["id"]] = hit

    # 单条指定配图：人工给关键词，覆盖按来源匹配的结果
    overrides = {}
    ov_json = ROOT.parent / "data/drafts/image_overrides.json"
    if ov_json.exists():
        overrides = json.loads(ov_json.read_text(encoding="utf-8"))
    for pid, spec in overrides.items():
        src = spec.get("url") or search_image(spec["q"])
        if not src or not save_image(src, out_dir / f"o_{pid}.jpg"):
            print(f"  override failed: {pid} {spec['q']}")
            continue
        mapping[pid] = {"src": f"img/o_{pid}.jpg", "origin": "search", "credit": spec.get("credit", "百度图片")}

    (ROOT.parent / "data/drafts/images.json").write_text(
        json.dumps(mapping, ensure_ascii=False, indent=0), encoding="utf-8")
    size = sum(f.stat().st_size for f in out_dir.glob("*"))
    print(f"posts_with_image={len(mapping)} files={len(list(out_dir.glob('*')))} bytes={size}")


if __name__ == "__main__":
    main()
