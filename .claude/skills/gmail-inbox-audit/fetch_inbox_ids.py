#!/usr/bin/env python3
"""
Fetch all inbox message IDs from Gmail and write to /tmp/gmail_inbox_ids.json.

Always writes fresh — deletes any existing file first to prevent stale data.
Paginates through all results using gws CLI.

Output: /tmp/gmail_inbox_ids.json — list of message ID strings
"""

import subprocess, json, time, os, sys

OUTPUT = "/tmp/gmail_inbox_ids.json"

# Always start fresh — stale IDs cause inflated counts
if os.path.exists(OUTPUT):
    os.remove(OUTPUT)
if os.path.exists("/tmp/gmail_inbox_headers.json"):
    os.remove("/tmp/gmail_inbox_headers.json")

all_ids = []
page_token = None
page = 0

while True:
    params = {"userId": "me", "labelIds": ["INBOX"], "maxResults": 500}
    if page_token:
        params["pageToken"] = page_token

    result = subprocess.run(
        ["gws", "gmail", "users", "messages", "list", "--params", json.dumps(params)],
        capture_output=True, text=True, timeout=30
    )

    if result.returncode != 0:
        print(f"Error on page {page}: {result.stderr[:200]}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)
    msgs = data.get("messages", [])
    all_ids.extend(m["id"] for m in msgs)
    page_token = data.get("nextPageToken")
    page += 1

    print(f"  Page {page}: {len(msgs)} IDs (running total: {len(all_ids)})", file=sys.stderr)

    if not page_token:
        break

    time.sleep(0.3)

with open(OUTPUT, "w") as f:
    json.dump(all_ids, f)

print(f"Total inbox messages: {len(all_ids)}", file=sys.stderr)
print(f"Saved to {OUTPUT}")
