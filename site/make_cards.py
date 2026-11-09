#!/usr/bin/env python3
"""给每条稿子生成一张标题卡（1200×675 JPEG）。热榜页面不给图，原图无从取，改由本地渲染。"""
from __future__ import annotations

import json
import pathlib
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent
DATE = "2026-11-09"
W, H = 1200, 675
BG = (13, 17, 23)
FG = (230, 237, 243)
DIM = (139, 148, 158)
FONT_CANDIDATES = [
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 1),
    ("/System/Library/Fonts/PingFang.ttc", 1),
    ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 0),
    ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 0),
    ("/Library/Fonts/Arial Unicode.ttf", 0),
]


def pick_font(size: int, bold: bool = True):
    for path, idx in FONT_CANDIDATES:
        if not pathlib.Path(path).exists():
            continue
        try:
            return ImageFont.truetype(path, size, index=idx)
        except OSError:
            continue
    raise SystemExit("找不到中文字体，用 --font 指定一个 .ttf/.ttc")

TAG_COLOR = {
    "社会": (248, 81, 73), "时政": (88, 166, 255), "体育": (63, 185, 80), "电竞": (163, 113, 247),
    "科技": (57, 197, 207), "产业": (210, 153, 34), "消费": (219, 109, 40), "民生": (126, 200, 120),
    "医疗": (240, 113, 154), "娱乐": (255, 123, 184), "人口": (121, 192, 255), "城市": (255, 166, 87),
    "历史": (188, 140, 100), "文保": (188, 140, 100), "军事": (139, 148, 158), "商业": (210, 153, 34),
    "居住": (121, 192, 255), "职场": (139, 148, 158), "教育": (126, 200, 120), "金融": (210, 153, 34),
    "出行": (57, 197, 207), "生活": (126, 200, 120), "人情": (240, 113, 154), "家庭": (240, 113, 154),
    "婚恋": (240, 113, 154), "社交": (163, 113, 247), "社区": (126, 200, 120), "天气": (121, 192, 255),
    "就业": (210, 153, 34), "保险": (210, 153, 34), "市政": (139, 148, 158), "交通": (57, 197, 207),
    "通信": (57, 197, 207), "其他": (139, 148, 158),
}

EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]+")


def clean(s: str) -> str:
    s = EMOJI.sub("", s)
    return s.replace("@grok", "").strip()


def wrap(draw, text, font, maxw):
    lines, cur = [], ""
    for ch in text:
        if draw.textlength(cur + ch, font=font) <= maxw:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def card(headline: str, sub: str, tag: str, path: pathlib.Path) -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    color = TAG_COLOR.get(tag, TAG_COLOR["其他"])
    d.rectangle([0, 0, 10, H], fill=color)

    f_head = pick_font(68, True)
    f_sub = pick_font(36, False)
    f_meta = pick_font(26, False)

    head = clean(headline)[:60]
    lines = wrap(d, head, f_head, 1030)[:3]
    while len(lines) > 2 and len("".join(lines)) > 44:
        f_head = pick_font(f_head.size - 6, True)
        lines = wrap(d, head, f_head, 1030)[:3]

    s = clean(sub)[:38]
    sub_lines = [ln for ln in wrap(d, s, f_sub, 1030)[:2]] if (s and s != head) else []

    head_h = len(lines) * int(f_head.size * 1.5)
    sub_h = len(sub_lines) * int(f_sub.size * 1.6) + 24 if sub_lines else 0
    y = max(110, (H - head_h - sub_h) // 2 - 10)
    for ln in lines:
        d.text((80, y), ln, font=f_head, fill=FG)
        y += int(f_head.size * 1.5)
    for ln in sub_lines:
        d.text((82, y + 16), ln, font=f_sub, fill=DIM)
        y += int(f_sub.size * 1.6)

    # 标签 + 日期
    pill = f" {tag} "
    tw = d.textlength(pill, font=f_meta)
    d.rounded_rectangle([80, H - 92, 80 + tw + 16, H - 52], radius=20, fill=(22, 27, 34), outline=color, width=2)
    d.text((88, H - 84), pill, font=f_meta, fill=color)
    d.text((W - 80 - d.textlength(DATE, font=f_meta), H - 84), DATE, font=f_meta, fill=DIM)

    img.save(path, quality=86, optimize=True)


def main() -> None:
    out = ROOT / "img"
    out.mkdir(exist_ok=True)
    rows = []
    for name in (f"{DATE}-batch.jsonl", f"{DATE}.jsonl", f"{DATE}-candidates.jsonl"):
        p = ROOT.parent / "data/drafts" / name
        if p.exists():
            rows += [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]

    tags = {}
    meta = ROOT.parent / "data/drafts/card-tags.json"
    if meta.exists():
        tags = json.loads(meta.read_text(encoding="utf-8"))

    n = 0
    for r in rows:
        text = r["text"]
        parts = [p.strip() for p in text.split("\n") if p.strip()]
        head = next((p for p in parts if len(clean(p)) >= 6), parts[0])
        sub = ""
        for p in parts:
            if p is not head and len(clean(p)) >= 6 and clean(p) != clean(head):
                sub = p
                break
        card(head, sub, tags.get(r["id"], "其他"), out / f"{r['id']}.jpg")
        n += 1
    print(f"cards={n}")


if __name__ == "__main__":
    main()
