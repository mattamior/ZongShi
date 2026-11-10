#!/usr/bin/env python3
"""Capture a full public status timeline for one X profile via the documented FxTwitter endpoint.

Saves every raw page, keeps a resumable cursor, and splits the authored statuses into
replies (have `replying_to`) and originals (no reply metadata). Nothing is published or
authenticated: this client sends no cookies, tokens, or API keys.

Defaults target the original benchmark account; pass --handle/--account-id
(plus --since for a bounded window) to capture another account.

Usage:
    python3 scripts/collect_target.py --output-dir data/target/<ts>
    python3 scripts/collect_target.py --output-dir data/target/<ts> --resume
    python3 scripts/collect_target.py --handle btcmos --account-id 1865722200185307136 \
        --output-dir data/target/btcmos --since 2026-10-20
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HANDLE = "FKFKFKFKFKTB"
ACCOUNT_ID = "2105258399885844480"
BASE_URL = "https://api.fxtwitter.com/2/profile"
PAGE_SIZE = 100
MAX_PAGES = 400
USER_AGENT = "zongshi-x-style-research/1.0 (public profile timeline capture)"
RETRYABLE_STATUS = {404, 425, 429, 500, 502, 503, 504}
MAX_RETRIES = 6


def as_object(value: object, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def as_list(value: object, label: str) -> list:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a JSON array")
    return value


def log(message: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}Z] {message}", flush=True)


def fetch_json(url: str) -> tuple:
    """Return (raw_body, parsed). Retries only on transient/rate-limit responses."""
    request = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": USER_AGENT}
    )
    last_error = "unknown"
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = response.read()
            return body, as_object(json.loads(body), "API response")
        except urllib.error.HTTPError as error:
            last_error = f"HTTP {error.code}"
            if error.code not in RETRYABLE_STATUS or attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"API returned HTTP {error.code} for {url}") from error
            retry_after = error.headers.get("Retry-After", "")
            try:
                delay = max(1.0, min(120.0, float(retry_after)))
            except ValueError:
                delay = min(60.0, float(2 ** attempt) * 1.5 * random.uniform(0.8, 1.2))
            log(f"{last_error}; retry {attempt + 1}/{MAX_RETRIES} in {delay:.1f}s")
            time.sleep(delay)
        except urllib.error.URLError as error:
            last_error = f"network error: {error.reason}"
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"Network request failed for {url}: {error.reason}") from error
            delay = min(60.0, float(2 ** attempt) * 1.5)
            log(f"{last_error}; retry {attempt + 1}/{MAX_RETRIES} in {delay:.1f}s")
            time.sleep(delay)
        except json.JSONDecodeError as error:
            last_error = "invalid JSON"
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"API returned invalid JSON for {url}") from error
            time.sleep(min(60.0, float(2 ** attempt)))
    raise RuntimeError(f"request failed after {MAX_RETRIES} attempts: {last_error}")


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_progress(path: Path) -> dict:
    if not path.exists():
        return {}
    return as_object(json.loads(path.read_text(encoding="utf-8")), "progress")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--handle", default=HANDLE, help="expected screen name of the profile")
    parser.add_argument("--account-id", default=ACCOUNT_ID, help="numeric user id; defaults to the original account")
    parser.add_argument("--profile-ref", default=None,
                        help="profile ref for the API; defaults to id:<account-id>")
    parser.add_argument("--since", default=None,
                        help="UTC date/datetime lower bound; stop paging once older and drop earlier rows")
    parser.add_argument("--resume", action="store_true", help="continue from source/progress.json")
    parser.add_argument("--sleep", type=float, default=1.2, help="seconds between page requests")
    parser.add_argument("--with-replies", type=int, default=1, choices=(0, 1),
                        help="1: replies+posts (parents inflate rows); 0: posts+reposts, no parents")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES, help="safety cap on page requests")
    args = parser.parse_args()

    output_dir: Path = args.output_dir
    handle: str = args.handle
    expected_id: str = str(args.account_id)
    profile_ref: str = args.profile_ref or f"id:{expected_id}"
    since_ts = None
    if args.since:
        parsed = datetime.fromisoformat(args.since)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        since_ts = int(parsed.timestamp())
    pages_dir = output_dir / "source" / "pages"
    progress_path = output_dir / "source" / "progress.json"

    if output_dir.exists() and any(output_dir.iterdir()) and not args.resume:
        raise SystemExit(f"Refusing to overwrite existing capture: {output_dir} (use --resume)")
    pages_dir.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(timezone.utc).isoformat()
    progress = load_progress(progress_path) if args.resume else {}
    cursor = progress.get("cursor") or None
    page_count = int(progress.get("page_count") or 0)
    all_results = []
    for page_path in sorted(pages_dir.glob("page-*.json")):
        try:
            payload = as_object(json.loads(page_path.read_text(encoding="utf-8")), page_path.name)
        except (json.JSONDecodeError, ValueError):
            continue
        all_results.extend(item for item in as_list(payload.get("results"), page_path.name) if isinstance(item, dict))
    if args.resume and all_results:
        log(f"resume: {page_count} pages, {len(all_results)} rows already on disk")

    _, profile_response = fetch_json(f"{BASE_URL}/{profile_ref}")
    profile = as_object(profile_response.get("user"), "profile.user")
    returned_handle = profile.get("screen_name")
    account_id = profile.get("id")
    if not isinstance(returned_handle, str) or returned_handle.casefold() != handle.casefold():
        raise ValueError(f"Profile endpoint resolved unexpected account: {returned_handle!r}")
    if str(account_id) != expected_id:
        raise ValueError(f"Profile endpoint resolved unexpected account id: {account_id!r}")
    reported_statuses = profile.get("statuses")

    seen_cursors = set()
    if isinstance(progress.get("seen_cursors"), list):
        seen_cursors = set(str(item) for item in progress["seen_cursors"])
    termination_reason = progress.get("termination_reason") or "not_finished"
    pagination_complete = bool(progress.get("api_cursor_exhausted"))
    page_errors = 0

    while termination_reason == "not_finished":
        if page_count >= args.max_pages:
            termination_reason = "page_limit_reached"
            break
        query = {"count": PAGE_SIZE, "with_replies": str(args.with_replies)}
        if cursor is not None:
            query["cursor"] = cursor
        url = f"{BASE_URL}/{profile_ref}/statuses?{urllib.parse.urlencode(query)}"
        try:
            body, response = fetch_json(url)
        except RuntimeError as error:
            page_errors += 1
            log(f"page {page_count + 1} failed: {error}")
            if page_errors >= 3:
                termination_reason = "repeated_request_failure"
                break
            time.sleep(30)
            continue

        code = response.get("code")
        if code != 200:
            raise RuntimeError(f"Unexpected API response code {code!r} on page {page_count + 1}")

        page_results = [item for item in as_list(response.get("results"), "response.results") if isinstance(item, dict)]
        page_count += 1
        (pages_dir / f"page-{page_count:04d}.json").write_bytes(body)
        all_results.extend(page_results)
        log(f"page {page_count}: {len(page_results)} rows (total {len(all_results)})")

        cursor_object = response.get("cursor")
        next_cursor = None
        if isinstance(cursor_object, dict):
            next_cursor = cursor_object.get("bottom")

        if not page_results:
            if next_cursor:
                termination_reason = "empty_page_with_continuation_cursor"
            else:
                pagination_complete = True
                termination_reason = "cursor_exhausted_after_empty_page"
            break
        page_ts = [int(item["created_timestamp"]) for item in page_results if item.get("created_timestamp")]
        if since_ts is not None and page_ts and min(page_ts) < since_ts:
            termination_reason = "since_reached"
            break
        if next_cursor is None or next_cursor == "":
            pagination_complete = True
            termination_reason = "cursor_exhausted_after_short_page" if len(page_results) < PAGE_SIZE else "full_page_without_cursor"
            break
        if not isinstance(next_cursor, str):
            raise ValueError("Pagination cursor.bottom must be a string")
        if next_cursor in seen_cursors:
            raise RuntimeError("Pagination cursor repeated; refusing to mark crawl complete")
        seen_cursors.add(next_cursor)
        cursor = next_cursor

        write_json(
            progress_path,
            {
                "page_count": page_count,
                "cursor": cursor,
                "seen_cursors": sorted(seen_cursors),
                "termination_reason": termination_reason,
                "api_cursor_exhausted": pagination_complete,
                "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            },
        )
        time.sleep(args.sleep + random.uniform(0.0, 0.4))

    write_json(
        progress_path,
        {
            "page_count": page_count,
            "cursor": cursor,
            "seen_cursors": sorted(seen_cursors),
            "termination_reason": termination_reason,
            "api_cursor_exhausted": pagination_complete,
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    )

    timeline = {}
    duplicates = 0
    for status in all_results:
        status_id = status.get("id")
        if not isinstance(status_id, str) or not status_id:
            continue
        if status_id in timeline:
            duplicates += 1
        else:
            timeline[status_id] = status

    authored = []
    reposted = []
    for status in timeline.values():
        author = status.get("author")
        if not isinstance(author, dict):
            continue
        if status.get("reposted_by") is not None:
            if str((status["reposted_by"] or {}).get("id")) == expected_id:
                reposted.append(status)
            continue
        if str(author.get("id")) != expected_id:
            continue
        authored.append(status)
    reposts = len(reposted)
    authored.sort(key=lambda item: int(item.get("created_timestamp") or 0))

    captured_authored = len(authored)
    if since_ts is not None:
        in_window = lambda item: int(item.get("created_timestamp") or 0) >= since_ts
        authored = [item for item in authored if in_window(item)]
        reposted = [item for item in reposted if in_window(item)]
    replies = [item for item in authored if item.get("replying_to")]
    originals = [item for item in authored if not item.get("replying_to")]

    def dump_jsonl(path: Path, rows: list) -> None:
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    dump_jsonl(output_dir / "authored.jsonl", authored)
    dump_jsonl(output_dir / "replies.jsonl", replies)
    dump_jsonl(output_dir / "originals.jsonl", originals)
    dump_jsonl(output_dir / "reposts.jsonl", reposted)

    timestamps = [int(item["created_timestamp"]) for item in authored if item.get("created_timestamp")]
    collection = {
        "account": {
            "handle": returned_handle,
            "id": account_id,
            "display_name": profile.get("name"),
            "profile_url": f"https://x.com/{returned_handle}",
            "reported_status_count_at_capture": reported_statuses,
            "followers": profile.get("followers"),
            "following": profile.get("following"),
            "joined": profile.get("joined"),
        },
        "source": {
            "provider": "FxTwitter public API",
            "endpoint": f"{BASE_URL}/{profile_ref}/statuses",
            "parameters": {"count": PAGE_SIZE, "with_replies": str(args.with_replies), "profile_ref": profile_ref},
            "row_semantics": "with_replies=1 embeds the replied-to parent post as an extra row, so each reply consumes two rows; with_replies=0 returns posts plus reposts and no parents.",
            "client_authentication": "none; no cookies, tokens, or API keys are sent",
            "raw_pages": "source/pages/page-*.json",
            "progress": "source/progress.json",
        },
        "collection": {
            "started_at_utc": started_at,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "page_count": page_count,
            "timeline_rows": len(all_results),
            "unique_timeline_statuses": len(timeline),
            "duplicate_rows": duplicates,
            "authored_statuses": len(authored),
            "reply_count": len(replies),
            "original_count": len(originals),
            "reposts_excluded": reposts,
            "oldest_timestamp": min(timestamps) if timestamps else None,
            "newest_timestamp": max(timestamps) if timestamps else None,
            "reported_vs_observed_ratio": round(len(authored) / reported_statuses, 4) if reported_statuses else None,
            "api_cursor_exhausted": pagination_complete,
            "termination_reason": termination_reason,
            "window_since": args.since,
            "before_window_dropped": captured_authored - len(authored),
        },
        "coverage_note": (
            f"termination_reason={termination_reason!r}; api_cursor_exhausted={pagination_complete}. "
            "Third-party upstream, not the owner's official export. Deleted, withheld, protected, or "
            "upstream-omitted posts may be absent; do not describe this as a guaranteed complete archive."
        ),
    }
    write_json(output_dir / "collection.json", collection)
    log(
        f"done: {len(authored)} authored ({len(replies)} replies / {len(originals)} originals) "
        f"of {reported_statuses!r} reported; pages={page_count}; reason={termination_reason}"
    )
    if not pagination_complete:
        log("coverage is partial: cursor did not exhaust")
        sys.exit(0)


if __name__ == "__main__":
    main()
