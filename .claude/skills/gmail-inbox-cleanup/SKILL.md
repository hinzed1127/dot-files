---
name: gmail-inbox-cleanup
description: Clean up Gmail inbox sender-by-sender based on an audit report. Shows 5 sample subjects before acting, waits for explicit approval on each sender, and uses TRASH label (not permanent delete) for a 30-day recovery window.
allowed-tools: Bash
---

# Gmail Inbox Cleanup

Work through a cleanup candidate list one sender at a time. Always pause for Dan's explicit "yes" before acting. Never permanently delete — use TRASH label only.

## Prerequisites

- `/tmp/gmail_inbox_headers.json` must exist and be fresh (run `gmail-inbox-audit` first)
- `/tmp/gmail_sender_counts.json` must exist (produced by audit phase)

If either file is missing or stale, stop and run the audit skill first.

## Ground Rules

- **One sender at a time.** Never batch multiple senders without approval.
- **Show 5 subjects first.** Always sample before acting.
- **Explicit approval required.** Wait for Dan's "yes" (or "trash", "archive", etc.) before every action.
- **TRASH, not delete.** Use `addLabelIds: ["TRASH"]` — never `messages.delete`.
- **Batches ≤ 500.** The script handles this automatically.
- **On 429 rate limit:** back off 2s and retry once (handled by script).

## Per-Sender Workflow

### 1. Show sample subjects

```bash
python3 - << 'EOF'
import json
MATCH = "sender@example.com"  # replace with sender email
with open("/tmp/gmail_inbox_headers.json") as f:
    msgs = json.load(f)
hits = [m for m in msgs if MATCH in m.get("from", "").lower()]
print(f"Total messages: {len(hits)}")
for m in hits[:5]:
    print(f"  {m['date'][:16]}  {m['subject'][:70]}")
EOF
```

### 2. Wait for Dan's decision

Possible responses and what they mean:

| Response | Action |
|----------|--------|
| "trash" | `--action trash` |
| "archive" / "archive for now" | `--action archive` |
| "archive under [label]" | `--action archive-label --label-id <id>` |
| "label it as [label]" (keep in inbox) | `--action label --label-id <id>` |
| "keep just the most recent N" | add `--keep-newest N` |
| "skip" / "leave it" | do nothing, move to next sender |

### 3. Look up label ID if needed

```bash
gws gmail users labels list --params '{"userId":"me"}' 2>/dev/null | python3 -c "
import json, sys
labels = json.load(sys.stdin).get('labels', [])
for l in sorted(labels, key=lambda x: x['name']):
    print(l['id'], l['name'])
"
```

### 4. Execute

```bash
# Trash all messages from a sender:
python3 ~/.claude/skills/gmail-inbox-cleanup/batch_modify.py \
  --email "sender@example.com" \
  --action trash

# Archive (remove from inbox, mark read, no label):
python3 ~/.claude/skills/gmail-inbox-cleanup/batch_modify.py \
  --email "sender@example.com" \
  --action archive

# Archive and apply a label:
python3 ~/.claude/skills/gmail-inbox-cleanup/batch_modify.py \
  --email "sender@example.com" \
  --action archive-label \
  --label-id Label_43

# Apply label but keep in inbox (e.g. newsletters Dan wants to see):
python3 ~/.claude/skills/gmail-inbox-cleanup/batch_modify.py \
  --email "sender@example.com" \
  --action label \
  --label-id Label_50

# Keep only the most recent message, trash the rest:
python3 ~/.claude/skills/gmail-inbox-cleanup/batch_modify.py \
  --email "sender@example.com" \
  --action trash \
  --keep-newest 1
```

### 5. Report after each sender

After each action, report:
- How many messages were acted on
- Estimated inbox count remaining
- Next candidate on the list

## Common Label IDs (hinzed1127@gmail.com)

| Label | ID |
|-------|----|
| Newsletters/Music | Label_43 |
| Newsletters/Reading | Label_46 |
| Newsletters/Woodworking | Label_7461009701725313382 |
| Newsletters/Substacks | Label_5387637262614572009 |
| Newsletters/Programming | Label_8859155967404123026 |
| Running/Training | Label_50 |
| Receipts | Label_2 |
| Travel | Label_39 |

> These IDs are specific to Dan's account. If labels have changed, re-fetch with the label list command above.

## Stopping Criteria

Continue until:
- Dan calls a stop, OR
- Inbox unread count is under 100
