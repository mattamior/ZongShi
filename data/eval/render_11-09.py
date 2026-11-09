import json, pathlib
sel = [json.loads(l) for l in open("data/drafts/2026-11-09.jsonl")]
cand = [json.loads(l) for l in open("data/drafts/2026-11-09-candidates.jsonl")]
out = ["# 2026-11-09 稿件", "",
       "已选 5 条是 Principal 12:14 从 24 条里挑出来的，正文未改；下面 12 条是按这 5 条的手法新写的备选。",
       "全部挂 `@grok`，`guard/check_text.py` 0 拦截；热榜来自 `data/news/2026-11-09.jsonl`（11:25 抓取）。**未发布、未排期**。", ""]
def block(title, rows):
    out.append(f"## {title}")
    out.append("")
    for r in rows:
        out.append(f"### {r['id']} {r['slot']}·{r['template']}·{len(r['text'])}字")
        out.append("")
        out.append("```")
        out.append(r["text"])
        out.append("```")
        out.append("")
block(f"已选（{len(sel)} 条）", sel)
block(f"备选（{len(cand)} 条）", cand)
out += ["## 来源", ""]
for r in sel + cand:
    if r.get("source_url"):
        out.append(f"- {r['id']}：{r['source_title']}")
out += ["", "## 限制", "",
        "- 热榜条目只到标题级核实，未打开原文。",
        "- s12 的 20 公斤、t02 的一千万罚款均为标题口径。",
        "- 全部人工撰写，未发布，无曝光与互动数据。", ""]
pathlib.Path("data/drafts/2026-11-09.md").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out[:14]))
