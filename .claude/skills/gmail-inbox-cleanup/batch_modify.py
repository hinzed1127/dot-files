#!/usr/bin/env python3
"""
Apply Gmail label changes to a set of messages in batches of ≤500.

Usage:
    python3 batch_modify.py --email sender@example.com --action trash
    python3 batch_modify.py --email sender@example.com --action archive
    python3 batch_modify.py --email sender@example.com --action label --label-id Label_43
    python3 batch_modify.py --email sender@example.com --action archive-label --label-id Label_43

Actions:
    trash         — add TRASH, remove INBOX
    archive       — remove INBOX and UNREAD (no label applied)
    label         — add label, keep in inbox, mark read
    archive-label — add label, remove INBOX and UNREAD

Reads message IDs from /tmp/gmail_inbox_headers.json filtered by --email.
On --keep-newest N: keeps the N most recent messages (by ID, desc) and acts on the rest.
"""

import subprocess, json, sys, time, re, argparse

HEADERS_FILE = "/tmp/gmail_inbox_headers.json"

parser = argparse.ArgumentParser()
parser.add_argument("--email", required=True, help="Sender email fragment to match (substring)")
parser.add_argument("--action", required=True, choices=["trash", "archive", "label", "archive-label"])
parser.add_argument("--label-id", help="Gmail label ID (required for label/archive-label actions)")
parser.add_argument("--keep-newest", type=int, default=0, help="Keep N most recent messages, act on the rest")
parser.add_argument("--dry-run", action="store_true", help="Print what would happen without making changes")
args = parser.parse_args()

if args.action in ("label", "archive-label") and not args.label_id:
    print("--label-id required for label/archive-label actions", file=sys.stderr)
    sys.exit(1)

with open(HEADERS_FILE) as f:
    messages = json.load(f)

def get_email(from_str):
    m = re.search(r'<([^>]+)>', from_str)
    return m.group(1).strip().lower() if m else from_str.strip().lower()

matched = [msg for msg in messages if args.email.lower() in get_email(msg.get("from", ""))]

if args.keep_newest > 0:
    matched_sorted = sorted(matched, key=lambda m: m["id"], reverse=True)
    kept = matched_sorted[:args.keep_newest]
    acted = matched_sorted[args.keep_newest:]
    print(f"Keeping {len(kept)} most recent. Acting on {len(acted)}.")
    for k in kept:
        print(f"  KEEP: {k['date'][:16]}  {k['subject'][:60]}")
else:
    acted = matched

ids = [m["id"] for m in acted]
print(f"Matched {len(ids)} messages from '{args.email}'")

if not ids:
    print("Nothing to do.")
    sys.exit(0)

# Build label modification
if args.action == "trash":
    add_labels = ["TRASH"]
    remove_labels = ["INBOX"]
elif args.action == "archive":
    add_labels = []
    remove_labels = ["INBOX", "UNREAD"]
elif args.action == "label":
    add_labels = [args.label_id]
    remove_labels = ["UNREAD"]
elif args.action == "archive-label":
    add_labels = [args.label_id]
    remove_labels = ["INBOX", "UNREAD"]

if args.dry_run:
    print(f"DRY RUN — would apply: add={add_labels} remove={remove_labels} to {len(ids)} messages")
    sys.exit(0)

BATCH_SIZE = 500
for i in range(0, len(ids), BATCH_SIZE):
    chunk = ids[i:i + BATCH_SIZE]
    body = {"ids": chunk}
    if add_labels:
        body["addLabelIds"] = add_labels
    if remove_labels:
        body["removeLabelIds"] = remove_labels

    for attempt in range(3):
        r = subprocess.run(
            ["gws", "gmail", "users", "messages", "batchModify",
             "--params", '{"userId":"me"}',
             "--json", json.dumps(body)],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            print(f"  Batch {i // BATCH_SIZE + 1}: {len(chunk)} messages updated")
            break
        elif "429" in r.stderr and attempt < 2:
            print(f"  Rate limited, retrying in 2s...", file=sys.stderr)
            time.sleep(2)
        else:
            print(f"  Batch {i // BATCH_SIZE + 1} FAILED: {r.stdout[:200]}", file=sys.stderr)
            break

print("Done.")
