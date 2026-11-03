---
name: hevy-progress-checkin
description: Walk Dan through a training progress check-in using his recent Hevy history - what's improving, what's stagnating or slipping, which muscle groups are neglected - then update his goals. Use whenever Dan asks how his training is going, wants a progress review or check-in, asks about plateaus, trends, strength levels or whether he's getting stronger, or says his goals have changed, even if he doesn't say "Hevy".
---

# Hevy progress check-in

Be a coach who has read the data: specific, honest, not gushing. Numbers come from the script; you interpret them.

## 1. Pull the data

```bash
python3 ~/.claude/hevy/summary.py --weeks 12 --recent 5
```

Use a different `--weeks` if Dan names a window. Also read `~/.claude/hevy/goals.md` (goals, injuries) and `~/.claude/hevy/programming.md` (what counts as stagnation, volume ranges).

## 2. Interpret with care

The trend labels are crude: they compare the latest session with earlier ones. Dan only recently started logging in detail and varies rep ranges, so before calling something "regressing", look at the actual sets (rep range changes, deload, machine settings, an injury week). Say when data is too thin to judge rather than inventing a story. Weekly sets are averaged over the weeks since his first workout in the window (shown in the heading), so use that figure as printed.

## 3. Walk him through it

Short sections, in this order:

- **Looking good**: lifts progressing, strength levels vs bodyweight that are solid.
- **Stagnating or slipping**: with the evidence (the sets), your best read on why, and a concrete change to try.
- **Under-trained**: muscle groups with low weekly sets or long gaps, given his strength goal.
- **Strength vs bodyweight**: which lifts lag the others.
- **Consistency**: sessions per week against his target (about 3).

Keep it scannable; he has ADHD. Lead with the most important takeaway.

## 4. Clarify goals and save them

Ask one open question first: has anything shifted in his goals, injuries or schedule? Let his answer decide the follow-ups (target lifts or numbers, injuries new or recovered, strength vs size emphasis), one at a time. Don't list every topic up front. Then update `~/.claude/hevy/goals.md` (edit in place, add a dated line to its Changelog). The planner reads this file, so keep it accurate and short.

`goals.md` is private (the dotfiles repo is public): it is git-ignored and synced only through the encrypted yadm archive. After changing it, remind Dan to run `yadm encrypt` and commit the updated archive; do not commit goals.md itself or push without asking.
