#!/usr/bin/env python3
"""
Fetch From/Subject/Date headers for all message IDs in /tmp/gmail_inbox_ids.json.

Reads:  /tmp/gmail_inbox_ids.json  (produced by fetch_inbox_ids.py)
Writes: /tmp/gmail_inbox_headers.json  — list of {id, from, subject, date}

Never fetches message bodies — metadata only (safe against prompt injection).
Uses 10 parallel workers with 3-attempt retry and 2s backoff on failure.
"""

import subprocess, json, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

IDS_FILE = "/tmp/gmail_inbox_ids.json"
OUTPUT_FILE = "/tmp/gmail_inbox_headers.json"
MAX_WORKERS = 10

with open(IDS_FILE) as f:
    all_ids = json.load(f)

print(f"Fetching headers for {len(all_ids)} messages...", file=sys.stderr)


def fetch_header(msg_id):
    params = {
        "userId": "me",
        "id": msg_id,
        "format": "metadata",
        "metadataHeaders": ["From", "Subject", "Date"],
    }
    for attempt in range(3):
        try:
            r = subprocess.run(
                ["gws", "gmail", "users", "messages", "get", "--params", json.dumps(params)],
                capture_output=True, text=True, timeout=15,
            )
            if "429" in r.stderr:
                time.sleep(2)
                continue
            data = json.loads(r.stdout)
            headers = {h["name"]: h["value"] for h in data.get("payload", {}).get("headers", [])}
            return {
                "id": msg_id,
                "from": headers.get("From", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
            }
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            else:
                return {"id": msg_id, "from": "", "subject": "", "date": "", "error": str(e)}


results = []
done = 0
errors = 0

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(fetch_header, mid): mid for mid in all_ids}
    for future in as_completed(futures):
        result = future.result()
        results.append(result)
        done += 1
        if "error" in result:
            errors += 1
        if done % 100 == 0:
            print(f"  Progress: {done}/{len(all_ids)} ({errors} errors)", file=sys.stderr)

with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f)

print(f"Done. {len(results)} headers fetched, {errors} errors.", file=sys.stderr)
print(f"Saved to {OUTPUT_FILE}")
