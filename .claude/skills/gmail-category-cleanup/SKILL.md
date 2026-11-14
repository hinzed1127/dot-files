---
name: gmail-category-cleanup
description: Bulk-clean Gmail's Promotions and Updates categories using a keep-list of protected senders (financial, receipts, security, medical, government, personal). Previews the exact trash set with a sender breakdown before acting, waits for explicit approval, and uses TRASH (30-day recovery) — never permanent delete. Distinct from gmail-inbox-audit, which ranks individual senders; this operates on whole categories minus a safety keep-list.
allowed-tools: Bash
---

# Gmail Category Cleanup

Sweep the **Promotions** and **Updates** categories in bulk, sparing a curated keep-list of senders that carry real value (statements, receipts, security, medical, government, shared docs, and Dan's explicit keeps).

Use this when the inbox is dominated by category mail and sender-by-sender (`gmail-inbox-cleanup`) would be too slow. Use `gmail-inbox-audit` instead when you need a ranked view of individual senders.

## Ground Rules

- **Preview before every trash.** Always show the count and sender breakdown first. Never trash without Dan's explicit "yes".
- **TRASH, not delete.** The script only ever adds the `TRASH` label. Never `messages.delete`.
- **Promotions is safe to sweep; Updates is NOT — it needs the keep-list.** Updates mixes receipts, statements, bank/security alerts, medical, government, and shared-doc mail in with junk. Never bulk-trash Updates without the keep-list applied and a reviewed preview.
- **Never trust `resultSizeEstimate`.** It caps ~201 and misreports. All scripts here paginate for real counts.
- **Grow the keep-list.** Whenever Dan says "keep X" during a run, add that fragment to `keep_senders.json` so it's protected next time — don't just pass `--keep` and forget it.

## Step 1 — Confirm access & measure the categories

```bash
gws gmail +triage
python3 ~/.claude/skills/gmail-category-cleanup/count_categories.py
```

This prints true counts for inbox total, promotions, updates, social, forums. Social/forums are usually negligible.

## Step 2 — Preview Promotions

```bash
python3 ~/.claude/skills/gmail-category-cleanup/category_cleanup.py --category promotions
```

Prints the exact query, the number of messages that would be trashed, and a full sender breakdown. **Read the breakdown.** Promotions is almost always pure marketing, but scan for:
- financial/account senders (banks, card marketing arms)
- possibly-personal senders (individual humans, contractors, service providers)

If Dan wants to spare any, either add `--keep <fragment>` for this run or add the fragment to `keep_senders.json` (preferred if it should persist).

## Step 3 — Execute Promotions (after approval)

```bash
python3 ~/.claude/skills/gmail-category-cleanup/category_cleanup.py --category promotions --execute
```

Re-run the same `--keep` flags you previewed with. Report the count trashed and the new inbox total (`count_categories.py`).

## Step 4 — Preview Updates (keep-list critical)

```bash
python3 ~/.claude/skills/gmail-category-cleanup/category_cleanup.py --category updates
```

Updates is the dangerous one. The keep-list already excludes the big financial/receipt/security/medical/government/personal senders, but **always scan the breakdown for stragglers** that slipped through:
- new receipt/order/shipping senders
- new statement/invoice senders
- security/login/account notices
- medical portals, appointment reminders
- government/legal/settlement mail
- shared Google Docs, individual people

Add any you find to `keep_senders.json` (persists) or `--keep` (this run only), then re-preview until the trash set is clean.

## Step 5 — Execute Updates (after approval)

```bash
python3 ~/.claude/skills/gmail-category-cleanup/category_cleanup.py --category updates --keep <extra1> --keep <extra2> --execute
```

Report count trashed and new inbox total.

## The keep-list

`keep_senders.json` (next to the scripts) holds sender fragments — substring matches against the `From` address — grouped by kind (financial, receipts, security, government, medical, personal, explicit_keeps). Grouping is cosmetic; every fragment across every group is excluded from trashing.

To protect a sender permanently, add its fragment to the appropriate group. To spare one just for the current run, pass `--keep <fragment>`.

## Recovery

Everything trashed stays recoverable for 30 days. To undo a sweep, search `in:trash <query>` and move messages back:
```bash
# example: pull a mistakenly-trashed sender back to the inbox
gws gmail users messages list --params '{"userId":"me","q":"in:trash from:example.com"}'
# then batchModify addLabelIds INBOX, removeLabelIds TRASH on those IDs
```

## Category reference

- **promotions** — marketing, sales, deals, most newsletters. Safe bulk target.
- **updates** — receipts, confirmations, statements, notifications. Keep-list required.
- **social** — social-network notifications. Usually tiny.
- **forums** — mailing lists, groups. Usually tiny.
