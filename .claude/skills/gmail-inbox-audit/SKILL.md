---
name: gmail-inbox-audit
description: Audit Gmail inbox by sender — counts messages, groups by sender/domain, classifies senders, and produces a ranked cleanup candidate list. Run this before gmail-inbox-cleanup. Headers only, no message bodies.
allowed-tools: Bash
---

# Gmail Inbox Audit

Read-only analysis of Gmail inbox. No mutations. Always runs fresh — stale temp files are cleared automatically.

## Ground Rules

- **Headers only.** Never fetch message bodies. `format=metadata` with `metadataHeaders=["From","Subject","Date"]` only.
- **No mutations in this phase.** Do not move, trash, label, or modify anything.
- **Always fresh data.** The scripts delete stale temp files before writing new ones.
- Pause after the audit report and wait for Dan's approval before proceeding to cleanup.

## Step 1 — Confirm Access

```bash
gws gmail +triage
```

Verify authentication works and show current inbox state.

## Step 2 — Fetch All Inbox Message IDs

```bash
python3 ~/.claude/skills/gmail-inbox-audit/fetch_inbox_ids.py
```

Paginates through all INBOX messages in batches of 500. Writes `/tmp/gmail_inbox_ids.json`.

> **Note:** `resultSizeEstimate` from the Gmail API is unreliable. Always paginate to get the real count.

## Step 3 — Fetch Headers (parallel)

```bash
python3 ~/.claude/skills/gmail-inbox-audit/fetch_inbox_headers.py
```

Reads `/tmp/gmail_inbox_ids.json`, fetches From/Subject/Date for each message using 10 parallel workers. Writes `/tmp/gmail_inbox_headers.json`. Takes ~2 minutes for ~1,300 messages.

## Step 4 — Analyze Senders

```bash
python3 ~/.claude/skills/gmail-inbox-audit/analyze_senders.py
```

Prints top 30 senders and top 15 domains. Saves aggregates to `/tmp/gmail_sender_counts.json` for use by the cleanup phase.

## Step 5 — Classify and Rank

For each of the top 30 senders, classify as one of:
- **Transactional** — receipts, shipping, confirmations
- **Newsletter / marketing** — editorial newsletters, promotional emails
- **Notification** — automated alerts, system mail, app notifications
- **Personal / human-sent** — real people writing to Dan
- **Potential spam** — unknown sender, suspicious patterns

Then produce a **ranked cleanup candidate list** ordered by `count × spam/newsletter likelihood score` (high=3, medium=2, low=1). Include the `gws` query string for each sender.

**Do NOT act on anything. Present the report and stop.**

## Output Format

```
GMAIL INBOX AUDIT — hinzed1127@gmail.com
Total inbox messages: N

TOP 30 SENDERS
# | Count | % | Category | Sender | Query
...

CLEANUP CANDIDATE LIST (ranked)
Rank | Score | Count | Category | Sender | Query
...
```

Flag any senders that look like real correspondence (personal emails, booking confirmations, receipts from active subscriptions) — these should not appear on the cleanup list.
