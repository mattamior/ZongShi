# Direction correction: posts, not replies

- Time: `2026-11-06T10:40–10:50+08:00`.
- Principal correction: this project replicates what the account **publishes**, not how it answers others. The earlier capture/analysis followed the reference project's reply-archive framing and made replies (94% of the account's output) the analysis subject; that was the wrong target.

## What changed

1. New capture path: `python3 scripts/collect_target.py --output-dir data/target/20261105T-posts --with-replies 0` — the profile timeline without replies. 21 pages, 352 rows, **278 own posts** (plus 19 replies and 55 reposts, both excluded), window 2026-10-20 → 2026-11-05. It stops at an empty page with a continuation cursor, same anomaly as before.
2. Merge: union of that route's posts with the 163 strict originals from the reply route → `data/target/posts-merged/posts.jsonl`, **293 posts**, 2026-10-20 → 2026-11-05, deduplicated by status ID.
3. New analysis: `scripts/analyze_posts.py` (post-centric: structure, openers, topics, cadence, reach). Output `data/target/posts-merged/post-stats.json`.
4. Rewritten deliverables: `STYLE.md` (posts only), `style/target-style.json` (posts spec), `style/prompt.md` (post generation only; the reply prompt was removed).

## Why the posts corpus is smaller than the reply corpus

- Replies are 94% of the account's output, and the API embeds each replied-to parent as an extra row, so a reply-route page spends about half its budget on other people's posts.
- The posts route is not subject to that, but it stops earlier in wall-clock terms (2026-10-20) because it also carries reposts.
- Net: 293 posts over 17 days is the reachable maximum today. The account was created 2026-09-30, so roughly 250–300 earlier posts remain out of reach without the owner's export.

## Post-corpus headline numbers (293 posts)

- Length median 41 code points, p90 80; non-empty lines median 3; 79.9% multi-line; 76.8% use a blank line between lines.
- 47.4% contain a question mark; 16.0% tag `@grok`; 25.6% carry an emoji (😱 81 occurrences, the dominant one); 19.1% carry media.
- Views: median 2,784, p90 52,021, max 2,098,984; likes median 9.
- Cadence: 17 posts/day, gap median 2,387 s; only 0.7% of gaps are under 10 minutes; peak hours 17:00–22:00 UTC+8.
- Openers: 卧槽系 47 (views median 5,617), 不懂就问 32 (2,521), question-led 29 (2,947), 说个冷知识 13 (3,198), 我很好奇 9 (2,181), 其他 160 (2,408).

## Limits

- Views are point-in-time snapshots; older posts have had longer to accumulate.
- The 2.1M-view outlier inflates the 卧槽系 median; treat the 2.3× gap over "other" as directional, not causal.
- Topic shares are keyword heuristics and double-count.
- 9-30 → 10-20 is missing, so style drift in the account's first three weeks cannot be ruled out.
