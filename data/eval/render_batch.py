import json, pathlib, collections
rows = [json.loads(l) for l in open("data/drafts/2026-11-09-batch.jsonl")]
by_hour = collections.OrderedDict()
for r in rows:
    by_hour.setdefault(r["slot"][:2], []).append(r)
out = ["# 2026-11-09 稿件池（192 条候选，96 个发布位）", "",
       "节奏假设：24 小时 × 每小时 4 条 = 96 条/天，两个号各 2 条/小时；每 15 分钟一个位，每个位给 2 条候选，二选一。",
       "全部挂 `@grok`；`guard/check_text.py` 192 条 0 拦截；热榜取自 `data/news/2026-11-09.jsonl`（13:08 抓取）。**未发布**。",
       "「不要怕红线」我按「可以骂、可以刺、可以站队」执行，但没编事实、没点私人姓名做指控、没放链接。", ""]
for hh, rs in by_hour.items():
    out += [f"## {hh} 时", ""]
    for r in rs:
        out += [f"### {r['slot']} 号{r['account']}·{r['id']}·{len(r['text'])}字", "",
                "```", r["text"], "```", ""]
srcs = collections.OrderedDict()
for r in rows:
    if r.get("source_title"):
        srcs.setdefault(r["source_title"], []).append(r["id"])
out += ["## 来源", ""]
for t, ids in srcs.items():
    out.append(f"- {t} — {', '.join(ids)}")
out += ["", "## 限制", "",
        "- 192 条是候选池，不是终稿；未经你逐条筛。",
        "- 102 条带来源的只在标题层面核实；其余 90 条是日常观察，不涉及可核事实。",
        "- 热榜与榜位会变，发布前重抓一次。", ""]
pathlib.Path("data/drafts/2026-11-09-batch.md").write_text("\n".join(out), encoding="utf-8")
print("hours", len(by_hour), "rows", len(rows), "sources", len(srcs))
