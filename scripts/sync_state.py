#!/usr/bin/env python3
"""审稿站状态与仓库双向同步。

    python3 scripts/sync_state.py pull    # 线上 → data/drafts/review.json、data/eval/target-ratings.json
    python3 scripts/sync_state.py push    # 仓库 → 线上（按 id 合并）
    python3 scripts/sync_state.py push --replace   # 整段覆盖线上
    python3 scripts/sync_state.py show    # 只看线上摘要

线上端点默认 https://zs.lapplax.com/api/state，可用 --url 覆盖（例如本地
`wrangler pages dev site/dist --port 8789` 时的 http://127.0.0.1:8789/api/state）。
pull 采用合并：线上有的 id 覆盖本地同 id，本地独有的保留；未知 id 丢弃。
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "data/drafts/review.json"
RATINGS = ROOT / "data/eval/target-ratings.json"
MANIFEST = ROOT / "data/target/accounts.json"
DEFAULT_URL = "https://zs.lapplax.com/api/state"
STATUS = {"used": "used", "rejected": "rejected", "duplicate": "dup", "edited": "edited"}
BACK = {"used": "used", "rejected": "rejected", "dup": "duplicate"}


def call(url: str, payload: dict | None = None, timeout: float = 20.0) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    # Cloudflare 的浏览器完整性检查会拦 Python 默认 UA，带一个正常 UA + Accept
    req = urllib.request.Request(url, data=data, method="GET" if payload is None else "POST",
                                 headers={"content-type": "application/json", "accept": "application/json",
                                          "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                                                        "Chrome/142.0.0.0 Safari/537.36"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{url} 返回 {e.code}: {e.read()[:200].decode(errors='replace')}")
    except urllib.error.URLError as e:
        raise SystemExit(f"连不上 {url}: {e.reason}")


def drafts() -> dict[str, dict]:
    out = {}
    for path in sorted((ROOT / "data/drafts").glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                out[row["id"]] = row
    return out


def target_ids() -> set[str]:
    """所有对标账号语料的帖子 id；只认清单里的账号，防止未知 id 写回仓库。"""
    if not MANIFEST.exists():
        return set()
    ids: set[str] = set()
    for acct in json.loads(MANIFEST.read_text(encoding="utf-8"))["accounts"]:
        path = ROOT / acct["posts"]
        ids.update(json.loads(l)["id"] for l in path.read_text(encoding="utf-8").splitlines() if l.strip())
    return ids


def to_server(review_rows: list[dict], rating_rows: list[dict], known: set[str], targets: set[str]) -> dict:
    review = {}
    for r in review_rows:
        if r["id"] not in known:
            continue
        entry = {}
        status = BACK.get(r.get("state"))
        if status:
            entry["status"] = status
        if r.get("text"):
            entry["text"] = r["text"]
        if r.get("image"):
            entry["image"] = r["image"]
        if entry:
            review[r["id"]] = entry
    ratings = {str(r["id"]): int(r["score"]) for r in rating_rows
               if r.get("id") in targets and isinstance(r.get("score"), int)}
    return {"review": review, "ratings": ratings}


def local_state(known: set[str], targets: set[str]) -> dict:
    review = json.loads(REVIEW.read_text(encoding="utf-8")) if REVIEW.exists() else []
    ratings = json.loads(RATINGS.read_text(encoding="utf-8")) if RATINGS.exists() else []
    return to_server(review, ratings, known, targets)


def merge_doc(base: dict, patch: dict) -> dict:
    """按 id 合并（replace=false）或整段覆盖（replace=true）后的完整文档。"""
    out = {"review": dict(base.get("review") or {}), "ratings": dict(base.get("ratings") or {})}
    for key in ("review", "ratings"):
        if key not in patch:
            continue
        if patch.get("replace"):
            out[key] = dict(patch[key] or {})
        else:
            out[key].update(patch[key] or {})
    return out


def local_doc() -> dict:
    return local_state(set(drafts()), target_ids())


def apply_doc(doc: dict) -> tuple[int, int]:
    """把服务端文档合并写回仓库文件；未知 id 丢弃。"""
    known = drafts()
    targets = target_ids()
    remote = doc.get("review") or {}
    rows = json.loads(REVIEW.read_text(encoding="utf-8")) if REVIEW.exists() else []
    by_id = {r["id"]: r for r in rows}
    added = 0
    for pid, entry in remote.items():
        if pid not in known:
            continue
        status = entry.get("status")
        state = STATUS.get(status, "edited" if entry.get("text") else None)
        if not state:
            continue
        row = by_id.get(pid) or {"id": pid, "date": known[pid].get("date", "")}
        row["state"] = state
        row["text"] = entry.get("text") or known[pid].get("text", "")
        row["image"] = entry.get("image") or None
        if pid not in by_id:
            added += 1
        by_id[pid] = row
    # 保持仓库里原有顺序，新出现的 id 追加在后面，避免每次 pull 都重排整个文件
    seen = {r["id"] for r in rows}
    out = [by_id[r["id"]] for r in rows] + [by_id[pid] for pid in sorted(set(by_id) - seen)]
    REVIEW.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    scores = {str(k): v for k, v in (doc.get("ratings") or {}).items() if k in targets and isinstance(v, int)}
    old = json.loads(RATINGS.read_text(encoding="utf-8")) if RATINGS.exists() else []
    merged = {r["id"]: int(r["score"]) for r in old if isinstance(r.get("score"), int)}
    merged.update(scores)
    RATINGS.write_text(json.dumps([{"id": k, "score": v} for k, v in sorted(merged.items())],
                                  ensure_ascii=False, indent=1), encoding="utf-8")
    return added, len(scores)


def cmd_pull(args: argparse.Namespace) -> None:
    doc = call(args.url)
    added, scores = apply_doc(doc)
    print(f"pull: 线上 review {len(doc.get('review') or {})} 条（新增 {added}）、ratings {scores} 条 → 仓库")


def cmd_push(args: argparse.Namespace) -> None:
    payload = local_doc()
    if args.replace:
        payload["replace"] = True
    res = call(args.url, payload)
    print(f"push: review {len(payload['review'])} 条、ratings {len(payload['ratings'])} 条 → 线上，"
          f"updatedAt={res.get('updatedAt')}")


def cmd_show(args: argparse.Namespace) -> None:
    doc = call(args.url)
    review = doc.get("review") or {}
    print(f"线上 review {len(review)} 条: "
          f"{dict(collections.Counter(v.get('status', 'text') for v in review.values()))}")
    ratings = doc.get("ratings") or {}
    print(f"线上 ratings {len(ratings)} 条，均分 "
          f"{(sum(ratings.values()) / len(ratings)):.2f}" if ratings else "线上 ratings 0 条")
    print(f"updatedAt={doc.get('updatedAt')}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["pull", "push", "show"])
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--replace", action="store_true", help="push 时整段覆盖线上，而不是按 id 合并")
    args = ap.parse_args()
    {"pull": cmd_pull, "push": cmd_push, "show": cmd_show}[args.action](args)


if __name__ == "__main__":
    main()
