import json, pathlib, sys
sys.path.insert(0, "data/eval")
from seed_hot import ROWS as HOT
from seed_rest import ROWS as REST

NEWS = [json.loads(l) for l in open("data/news/2026-11-09.jsonl")]
def src(key):
    hits = [r for r in NEWS if key in r["title"]]
    if not hits:
        raise SystemExit(f"no source for {key}")
    return {"source_url": hits[0]["url"], "source_title": hits[0]["title"]}

rows = HOT + REST
assert len(rows) == 192, len(rows)

seen, out = set(), []
for topic, claim, skey, text in [(r[0], r[2], r[3], r[4]) for r in rows]:
    key = "".join(text.split())
    assert key not in seen, f"dup: {text[:20]}"
    seen.add(key)
    assert "@grok" in text, text[:20]
    assert len(text) <= 90, (len(text), text[:20])
    d = {"date": "2026-11-09", "topic": topic, "claim": claim, "text": text}
    if skey:
        d.update(src(skey))
    out.append(d)

hot = [d for d in out if d["topic"][0] in "TH"]
ever = [d for d in out if d["topic"][0] == "E"]
assert len(hot) == 102 and len(ever) == 90, (len(hot), len(ever))
priority = [17, 21, 20, 18, 16, 12, 11, 10, 9, 22, 19, 15, 14, 13, 8, 7, 6, 23, 5, 4, 3, 2, 1, 0]
slots = [f"{h:02d}:{m:02d}" for h in priority for m in (0, 15, 30, 45)]
assert len(slots) == 96

ordered = []
i_hot = i_ever = 0
for _ in slots:
    pair = []
    for _ in range(2):
        if i_hot < len(hot):
            pair.append(hot[i_hot]); i_hot += 1
        else:
            pair.append(ever[i_ever]); i_ever += 1
    ordered.append(pair)
out = [d for pair in ordered for d in pair]

for i, slot in enumerate(slots):
    c1, c2 = out[2 * i], out[2 * i + 1]
    acc1, acc2 = ("A", "B") if i % 2 == 0 else ("B", "A")
    c1.update(id=f"b{2*i+1:03d}", slot=slot, account=acc1, variant=1)
    c2.update(id=f"b{2*i+2:03d}", slot=slot, account=acc2, variant=2)

pathlib.Path("data/drafts/2026-11-09-batch.jsonl").write_text(
    "\n".join(json.dumps(d, ensure_ascii=False) for d in out) + "\n", encoding="utf-8")
print("rows", len(out), "slots", len(slots),
      "A cand", sum(1 for d in out if d["account"] == "A"),
      "assertion", sum(1 for d in out if d["claim"] == "assertion"))
