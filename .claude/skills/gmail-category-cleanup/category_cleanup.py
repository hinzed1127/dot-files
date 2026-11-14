#!/usr/bin/env python3
"""
Bulk-clean a Gmail category (promotions / updates) using a keep-list.

Two modes:
    preview   (default) — build the trash query, count real matches (full pagination),
                          and print a sender breakdown. Touches nothing.
    execute   — actually move the matched messages to TRASH (30-day recovery).
                Requires the explicit --execute flag.

The trash query is:  in:inbox category:<CAT> <keep-list exclusions> <extra excludes>

Keep-list lives in keep_senders.json next to this script. Any sender fragment in it is
excluded from trashing. Add ad-hoc keeps for a single run with --keep (repeatable).

Examples:
    # See what a promotions sweep would trash, plus who:
    python3 category_cleanup.py --category promotions

    # Same but also spare two more senders just this run:
    python3 category_cleanup.py --category updates --keep whitecrane --keep jpmorgan

    # Actually trash them (after reviewing the preview):
    python3 category_cleanup.py --category promotions --execute

Never uses messages.delete. Never uses resultSizeEstimate (it lies — always paginate).
"""

import subprocess, json, sys, re, argparse, os, time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KEEP_FILE = os.path.join(SCRIPT_DIR, "keep_senders.json")


def gws_json(args):
    """Run a gws command and parse JSON, tolerating a leading 'Using keyring...' line."""
    r = subprocess.run(args, capture_output=True, text=True)
    out = r.stdout
    try:
        return json.loads(out), r.returncode, r.stderr
    except json.JSONDecodeError:
        # Strip any non-JSON preamble lines (e.g. keyring backend notice).
        cleaned = "\n".join(l for l in out.splitlines() if not l.strip().startswith("Using"))
        return json.loads(cleaned), r.returncode, r.stderr


def load_keep_fragments():
    with open(KEEP_FILE) as f:
        data = json.load(f)
    frags = []
    for k, v in data.items():
        if k.startswith("_"):
            continue
        frags.extend(v)
    return frags


def build_query(category, keep_fragments, extra_keeps):
    frags = keep_fragments + list(extra_keeps)
    excl = " ".join(f"-from:{e}" for e in frags)
    return f"in:inbox category:{category} {excl}".strip()


def list_all_ids(query):
    """Full pagination — never trust resultSizeEstimate."""
    ids, token = [], None
    while True:
        params = {"userId": "me", "q": query, "maxResults": 500}
        if token:
            params["pageToken"] = token
        d, rc, err = gws_json(["gws", "gmail", "users", "messages", "list",
                               "--params", json.dumps(params)])
        if rc != 0:
            print(f"list failed: {err[:300]}", file=sys.stderr)
            sys.exit(1)
        ids += [m["id"] for m in d.get("messages", [])]
        token = d.get("nextPageToken")
        if not token:
            break
    return ids


def fetch_from(msg_id):
    d, rc, _ = gws_json(["gws", "gmail", "users", "messages", "get", "--params",
                         json.dumps({"userId": "me", "id": msg_id,
                                     "format": "metadata", "metadataHeaders": ["From"]})])
    if rc != 0:
        return ""
    hs = {h["name"]: h["value"] for h in d.get("payload", {}).get("headers", [])}
    return hs.get("From", "")


def sender_breakdown(ids, workers=12):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        froms = list(ex.map(fetch_from, ids))
    def addr(f):
        m = re.search(r"<([^>]+)>", f or "")
        return (m.group(1) if m else (f or "")).strip().lower()
    def name(f):
        return re.sub(r"\s*<[^>]+>", "", f or "").strip().strip('"')
    counts, disp = Counter(), {}
    for f in froms:
        a = addr(f)
        counts[a] += 1
        disp[a] = name(f)
    return counts, disp


def trash(ids):
    BATCH = 500
    for i in range(0, len(ids), BATCH):
        chunk = ids[i:i + BATCH]
        body = {"ids": chunk, "addLabelIds": ["TRASH"],
                "removeLabelIds": ["INBOX", "UNREAD"]}
        for attempt in range(3):
            r = subprocess.run(["gws", "gmail", "users", "messages", "batchModify",
                                "--params", '{"userId":"me"}', "--json", json.dumps(body)],
                               capture_output=True, text=True)
            if r.returncode == 0:
                print(f"  batch {i // BATCH + 1}: trashed {len(chunk)}")
                break
            elif "429" in r.stderr and attempt < 2:
                print("  rate limited, retrying in 2s...", file=sys.stderr)
                time.sleep(2)
            else:
                print(f"  batch {i // BATCH + 1} FAILED: {r.stdout[:200]} {r.stderr[:200]}",
                      file=sys.stderr)
                return False
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--category", required=True, choices=["promotions", "updates", "social", "forums"],
                   help="Gmail category to clean")
    p.add_argument("--keep", action="append", default=[], metavar="FRAGMENT",
                   help="Extra sender fragment to spare this run (repeatable)")
    p.add_argument("--execute", action="store_true",
                   help="Actually trash. Without this, preview only.")
    p.add_argument("--no-breakdown", action="store_true",
                   help="Skip the per-sender breakdown in preview (faster)")
    args = p.parse_args()

    keep_fragments = load_keep_fragments()
    query = build_query(args.category, keep_fragments, args.keep)
    print(f"QUERY: {query}\n")

    ids = list_all_ids(query)
    print(f"MATCHED (would trash): {len(ids)} messages"
          + (f", plus {len(args.keep)} ad-hoc keep(s) excluded" if args.keep else ""))

    if not ids:
        print("Nothing to do.")
        return

    if not args.no_breakdown:
        counts, disp = sender_breakdown(ids)
        print(f"\n{len(counts)} senders:\n")
        for a, n in counts.most_common():
            print(f"{n:>3}  {disp.get(a, '')[:30]:<32} {a}")

    if not args.execute:
        print(f"\nPREVIEW ONLY. Re-run with --execute to trash these {len(ids)} messages.")
        return

    print(f"\nTrashing {len(ids)} messages (TRASH label, 30-day recovery)...")
    ok = trash(ids)
    print("Done." if ok else "Completed with errors — see above.")


if __name__ == "__main__":
    main()
