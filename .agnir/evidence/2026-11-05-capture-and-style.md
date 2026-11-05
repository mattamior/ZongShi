# Full capture and style baseline

- Time: `2026-11-05T18:52–18:59+08:00` (Asia/Shanghai).
- Command: `python3 scripts/collect_target.py --output-dir data/target/20261105T1052Z` (new script in this repo; adapted from the reference project's collector, plus reply/original split, resumable cursor, and strict profile-id check).
- Source: `GET https://api.fxtwitter.com/2/profile/id:2105258399885844480/statuses?count=100&with_replies=1`, `cursor.bottom` pagination, 1.2 s between pages. No cookies, tokens, or API keys were sent.

## Result

- 164 pages, 6,539 timeline rows, 6,217 unique statuses, 322 duplicate rows.
- 3,223 authored statuses: **3,034 replies**, **163 originals**, 26 posts that start with an `@mention` but carry no reply metadata (excluded from original-shape statistics, since they behave like replies whose parent context was dropped).
- Window: `2026-10-27T14:51:38Z` → `2026-11-05T10:16:56Z`; 0 reposts were present in the timeline.
- Per-day authored counts: 10-27 1, 10-28 64, 10-29 493, 10-30 418, 10-31 462, 11-01 421, 11-02 450, 11-03 456, 11-04 267, 11-05 191 (partial day).

## Coverage boundary

- Profile reports 6,611 statuses; this capture observed 3,223 (48.8%).
- Page 164 returned **0 rows while still supplying a continuation cursor** (`termination_reason=empty_page_with_continuation_cursor`).
- A separate bounded probe followed that cursor for **8 further pages: all returned 0 rows**, cursor kept advancing. Same anomaly the reference project recorded for a different account.
- Conclusion: the public timeline has a depth ceiling around 3,200 statuses; the missing ~3,388 posts predate 2026-10-27. This is **not** evidence of deletion, and it is **not** the account's full history. Recovering it would need the owner's official export.

## Style baseline

- `python3 scripts/analyze_style.py data/target/20261105T1052Z` → `data/target/20261105T1052Z/style-stats.json`, then written up in `STYLE.md` and `style/target-style.json`.
- Headline numbers: replies 99.93% open with a mention, body median 4 code points / p90 10, 98.0% end without punctuation, 15.4% carry an emoji (😱 286 = top), 9.0% are emoji-only, 9.1% use a repeated-emoji run. Originals: 163, median 41 code points, 5 lines, 77.9% multi-line, 44.8% contain a question mark, 18.4% tag `@grok`.
- Cadence: 15.24 posts/hour, gap median 29 s, 64.3% of gaps under 60 s, 816 bursts (max 55), 11 gaps over 2 hours.

## Divergence from `PLAN.md` §1

`PLAN.md` §1 keeps the 18-hour exploratory sample (204 statuses) that the plan was written from. The full capture agrees on every headline shape but shifts several numbers: reply share 91.2% → 94.1%, reply emoji share 14.5% → 15.4%, emoji leader 😱 (286 of 869 emoji occurrences in replies, 32.9%; the 18-hour sample put it at 57%, which was small-sample skew), original median 41 code points (unchanged). `STYLE.md` is authoritative; §1 is retained as the plan-stage snapshot and is labeled as such.

## Limits

- 10-day window only; earlier style drift cannot be assessed.
- Topic shares come from a keyword heuristic and will double-count; treat them as directional.
- The `lang` field is unusable as a language split (`ja` 1,078 of 3,223, largely Chinese).
