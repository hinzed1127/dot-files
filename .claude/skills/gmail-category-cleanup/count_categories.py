#!/usr/bin/env python3
"""
Report real inbox counts by Gmail category and total, using full pagination.

Gmail's resultSizeEstimate is unreliable (caps around 201, and misreports age
filters) — this script paginates every query to get true counts.

Usage:
    python3 count_categories.py
"""

import subprocess, json, sys


def gws_json(args):
    r = subprocess.run(args, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        cleaned = "\n".join(l for l in r.stdout.splitlines() if not l.strip().startswith("Using"))
        return json.loads(cleaned)


def count(q):
    total, token = 0, None
    while True:
        params = {"userId": "me", "q": q, "maxResults": 500}
        if token:
            params["pageToken"] = token
        d = gws_json(["gws", "gmail", "users", "messages", "list", "--params", json.dumps(params)])
        total += len(d.get("messages", []))
        token = d.get("nextPageToken")
        if not token:
            break
    return total


def main():
    queries = [
        ("inbox total", "in:inbox"),
        ("promotions", "in:inbox category:promotions"),
        ("updates", "in:inbox category:updates"),
        ("social", "in:inbox category:social"),
        ("forums", "in:inbox category:forums"),
    ]
    print(f"{'bucket':<16} count")
    print("-" * 24)
    for label, q in queries:
        print(f"{label:<16} {count(q)}")


if __name__ == "__main__":
    main()
