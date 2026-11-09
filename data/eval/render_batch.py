import json, pathlib, collections
rows = [json.loads(l) for l in open("data/drafts/2026-11-09-batch.jsonl")]
groups = collections.OrderedDict()
for r in rows:
    groups.setdefault((r["slot"], r["account"]), []).append(r)
out = ["# 2026-11-09 稿池（384 条候选，192 个发布位）", "",
       "口径：每号每小时 4 条，两个号合计每小时 8 条、每天 192 条；每 15 分钟一个位、每个号各 1 条，每条给 2 个候选，二选一。",
       "全部挂 `@grok`；`guard/check_text.py` 384 条 0 拦截；热点集中在 09-12、16-22，其余时段填日常。**未发布**。", ""]
for hour in range(24):
    hh = f"{hour:02d}"
    out += [f"## {hh} 时", ""]
    for (slot, acc), rs in groups.items():
        if slot[:2] != hh:
            continue
        lens = "/".join(str(len(r["text"])) for r in rs)
        ids = "/".join(r["id"] for r in rs)
        out += [f"### {slot} 号{acc} · {ids} · {lens}字", ""]
        for r in rs:
            out += ["```", r["text"], "```", ""]
srcs = collections.OrderedDict()
for r in rows:
    if r.get("source_title"):
        srcs.setdefault(r["source_title"], []).append(r["id"])
out += ["## 来源", ""]
for t, ids in srcs.items():
    out.append(f"- {t} — {', '.join(ids)}")
out += ["", "## 限制", "",
        "- 384 条是候选池，未逐条过你的筛；同一热题会有多个角度，发布时每号同题每天别超过 2 次。",
        "- 170 条带来源的只核到标题；214 条日常观察不涉及可核事实。",
        "- 热榜会变，发布前重抓。", ""]
pathlib.Path("data/drafts/2026-11-09-batch.md").write_text("\n".join(out), encoding="utf-8")
print("slots", len(groups), "rows", len(rows))
