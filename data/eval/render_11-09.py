import json, pathlib
rows = [json.loads(l) for l in open("data/drafts/2026-11-09.jsonl")]
out = ["# 2026-11-09 稿件（24 条）", "",
       "热点优先、互动优先、每条挂 `@grok`（Principal 2026-11-09 铁律）。",
       "热榜取自 `data/news/2026-11-09.jsonl`（11:25 抓取），榜位是快照，发布前复核。",
       "`guard/check_text.py` 24 条 0 拦截；未发布、未排期。", ""]
for r in rows:
    out += [f"### {r['id']} {r['slot']}·{r['template']}·{len(r['text'])}字", "",
            "```", r["text"], "```", ""]
out += ["## 来源", ""]
for r in rows:
    if r.get("source_url"):
        out.append(f"- {r['id']}：{r['source_title']}")
out += ["", "## 限制", "",
        "- 热榜条目只到标题级核实，未打开原文。",
        "- s01 的「14 人」来自标题；「我家楼道堆纸箱」是第一人称观察。",
        "- s05/s06/s17/s21 依赖当天赛果与榜位，发布前重抓。",
        "- 全部人工撰写，未发布，无曝光与互动数据。", ""]
pathlib.Path("data/drafts/2026-11-09.md").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out[:16]))
