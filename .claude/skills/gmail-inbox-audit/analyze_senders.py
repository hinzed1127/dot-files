#!/usr/bin/env python3
"""
Aggregate inbox messages by sender and domain, print top-N report.

Reads:  /tmp/gmail_inbox_headers.json  (produced by fetch_inbox_headers.py)
Writes: /tmp/gmail_sender_counts.json  — sender/domain aggregates for cleanup phase

Usage: python3 analyze_senders.py [--top N]   (default: 30 senders, 15 domains)
"""

import json, re, sys
from collections import defaultdict

HEADERS_FILE = "/tmp/gmail_inbox_headers.json"
OUTPUT_FILE = "/tmp/gmail_sender_counts.json"
TOP_SENDERS = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 30
TOP_DOMAINS = 15


def parse_sender(from_str):
    from_str = from_str.strip()
    m = re.search(r'<([^>]+)>', from_str)
    if m:
        email = m.group(1).strip().lower()
        display = from_str[:from_str.index('<')].strip().strip('"')
    else:
        email = from_str.lower().strip()
        display = email
    domain = email.split('@')[-1] if '@' in email else email
    return display, email, domain


with open(HEADERS_FILE) as f:
    messages = json.load(f)

sender_counts = defaultdict(int)
sender_emails = {}
domain_counts = defaultdict(int)

for msg in messages:
    frm = msg.get("from", "")
    if not frm:
        continue
    display, email, domain = parse_sender(frm)
    sender_counts[email] += 1
    if email not in sender_emails:
        sender_emails[email] = display
    domain_counts[domain] += 1

total = len(messages)
top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)

print(f"Total inbox messages: {total}\n")
print(f"TOP {TOP_SENDERS} SENDERS:")
print(f"{'#':<3} {'Count':>5} {'%':>5}  {'Sender'}")
print("-" * 85)
for i, (email, count) in enumerate(top_senders[:TOP_SENDERS], 1):
    display = sender_emails.get(email, "")
    label = f"{display} <{email}>" if display and display != email else email
    pct = count / total * 100
    print(f"{i:<3} {count:>5} {pct:>4.1f}%  {label[:65]}")
    print(f"      query: from:{email}")

print(f"\nTOP {TOP_DOMAINS} DOMAINS:")
for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:TOP_DOMAINS]:
    print(f"  {count:>5}  {domain}")

# Save aggregates for use by cleanup phase
with open(OUTPUT_FILE, "w") as f:
    json.dump({
        "total": total,
        "sender_counts": dict(sender_counts),
        "sender_names": sender_emails,
        "domain_counts": dict(domain_counts),
    }, f)

print(f"\nAggregates saved to {OUTPUT_FILE}")
