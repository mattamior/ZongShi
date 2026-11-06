# History depth: why 2026-09-30 → 10-20 is missing

- Time: `2026-11-06T11:00–11:20+08:00`.
- Principal objection: the account was mature from day one, so every post since creation matters. The earlier "accept 293 posts" position is withdrawn.

## Routes tried, and where each stops

| Route | Command | Depth reached | Ending |
|---|---|---|---|
| Posts (`with_replies=0`) | `collect_target.py --with-replies 0` | **2026-10-20** | 21 pages / 352 rows, then 0 rows + cursor |
| Replies (`with_replies=1`) | `collect_target.py` | **2026-10-27** | 164 pages / 6,539 rows, then 0 rows + cursor |
| Media | `/media?count=100` | **2026-10-22** | 56 rows in one page, then 0 rows |
| Cross-route cursor | posts cursor + `with_replies=1`; reply cursor + `with_replies=0` | — | 0 rows both directions |
| Deeper probe past posts floor | 8 further pages from the last cursor | — | all 0 rows |
| Twitter syndication timeline | `syndication.twitter.com/srv/timeline-profile/...` | — | HTTP 429 (rate limited, twice, 20 s apart) |
| Nitter mirrors | `xcancel.com` 451, `nitter.poast.org` TLS failure, `twstalker.com` 403 | — | blocked from this network |
| Web search index | `site:x.com/FKFKFKFKFKTB` | — | no indexed posts (one third-party mirror URL, content unavailable) |

All three API routes converge on late October, at different depths and with different page budgets (352 vs 6,539 rows). That rules out a per-route row cap and points to a **retention window in the mirror layer**: the provider keeps roughly the last few hundred to few thousand statuses and then answers with an empty page plus a cursor.

The profile itself reports **6,633 statuses** (up from 6,611 a day earlier), so the earlier content exists; it is simply not served.

## Consequence

- Rough size of the hole: at the observed 15–20 posts/day, 2026-09-30 → 10-20 is about **200–250 posts**, on top of the 293 already captured.
- The only authoritative source is the account owner's official X archive. `tweets.js` / `tweets-part*.js` contains every surviving post with `in_reply_to_status_id_str`, so replies, reposts and mention-led posts can be filtered exactly.

## Prepared for the import

- `scripts/import_official_export.py` — strips the `window.YTD.tweets.partN =` prefix, parses `Wed Oct 01 09:15:00 +0000 2026` timestamps, drops replies / reposts / mention-led posts, emits the project schema. Verified on a constructed archive with one valid post and three exclusions (replies 1, retweets 1, mention_led 1) — the single surviving post then analyzed correctly through `analyze_posts.py`.
- `scripts/merge_posts.py` — unions JSONL corpora by status ID, preferring the record that carries `views` (mirror rows have reach numbers, archive rows do not). Verified: 293 + 1 → 294 unique.

## Nothing is blocked that does not depend on the export

P2 (generation + distribution self-check) can proceed against the 293 posts now, and be re-run after the archive lands. `STYLE.md` marks the missing window as an open limitation rather than assuming early posts were less mature.

## Limits

- Retention-window explanation is inferred from route behavior, not documented by the provider.
- The 200–250 estimate assumes a stable posting rate before 2026-10-20; the account's first days could be much denser or sparser.
- The syndication endpoint 429'd; it may work later, but it only ever returns ~20 recent items, so it cannot close the gap.
