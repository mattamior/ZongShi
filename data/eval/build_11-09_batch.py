import json, pathlib, sys
sys.path.insert(0, "data/eval")
from seed_hot import ROWS as S1
from seed_rest import ROWS as S2
from seed_hot2 import ROWS as S3
from seed_rest2 import ROWS as S4

NEWS = [json.loads(l) for l in open("data/news/2026-11-09.jsonl")]
def src(key):
    hits = [r for r in NEWS if key in r["title"]]
    if not hits:
        raise SystemExit(f"no source for {key}")
    return {"source_url": hits[0]["url"], "source_title": hits[0]["title"]}

seen, out = set(), []
for topic, _, claim, skey, text in S1 + S2 + S3 + S4:
    key = "".join(text.split())
    assert key not in seen, f"dup: {text[:24]}"
    seen.add(key)
    assert "@grok" in text, text[:24]
    assert len(text) <= 90, (len(text), text[:24])
    d = {"date": "2026-11-09", "topic": topic, "claim": claim, "text": text}
    if skey:
        d.update(src(skey))
    out.append(d)
assert len(out) == 384, len(out)

hot = [d for d in out if d["topic"][0] in "TH"]
ever = [d for d in out if d["topic"][0] in "EF"]
assert len(hot) == 170 and len(ever) == 214, (len(hot), len(ever))

priority = [17, 21, 20, 18, 16, 12, 11, 10, 9, 22, 19, 15, 14, 13, 8, 7, 6, 23, 5, 4, 3, 2, 1, 0]
slots = [(h, m, a) for h in priority for m in (0, 15, 30, 45) for a in ("A", "B")]
assert len(slots) == 192

i_hot = i_ever = 0
ordered = []
for _ in slots:
    pair = []
    for _ in range(2):
        if i_hot < len(hot):
            pair.append(hot[i_hot]); i_hot += 1
        else:
            pair.append(ever[i_ever]); i_ever += 1
    ordered.append(pair)

flat = [d for pair in ordered for d in pair]
for i, (h, m, a) in enumerate(slots):
    c1, c2 = flat[2 * i], flat[2 * i + 1]
    for j, c in enumerate((c1, c2), start=1):
        c.update(id=f"b{2*i+j:03d}", slot=f"{h:02d}:{m:02d}", account=a, variant=j)

pathlib.Path("data/drafts/2026-11-09-batch.jsonl").write_text(
    "\n".join(json.dumps(d, ensure_ascii=False) for d in flat) + "\n", encoding="utf-8")
print("posts", len(slots), "candidates", len(flat), "hot", len(hot), "ever", len(ever))
