---
name: hevy-workout-planner
description: Plan Dan's next gym workout (or a week of workouts) from his last 8 weeks of Hevy history, strength-first. Use whenever Dan asks what to lift, wants a workout or training plan, says "plan my next workout", "what should I do today/this week", names muscle groups to focus on, asks for a full-body session, or mentions an injury that affects training, even if he never says "Hevy" or "planner". Pulls real data from the Hevy API so weights come from his actual numbers.
---

# Hevy workout planner

Plan from real logged data, not generic templates. The numbers come from scripts; your job is the judgment: what to train, how heavy, and what to avoid.

## 1. Gather context (one question at a time, only for what's missing)

- Read `~/.claude/hevy/goals.md` (baseline stats, goal, current injuries and limitations).
- If you can search the journal or past sessions, check them for recent injuries or training comments Dan made.
- Confirm what Dan's message already told you; ask only for the gaps, one question at a time:
  1. **Focus**: which muscle groups, or full body? Always ask if he didn't say.
  2. **Injuries today**: ask if goals.md lists something unconfirmed or old, or if he didn't mention any.
  3. **Scope**: assume just the next workout. Plan a week only if he asks (then ask how many sessions).

## 2. Pull the data

```bash
python3 ~/.claude/hevy/summary.py --weeks 8
```

Prints (in lbs): body weight, recent workouts with every set, per-exercise trend, strength vs bodyweight, weekly sets per muscle and days since each was last trained. It reads the API key from `~/.claude/hevy/.env`; if that is missing, tell Dan to run `yadm decrypt`. To look up an exercise's exact title or id: `python3 ~/.claude/hevy/find_exercise.py bench press`.

## 3. Plan

Read `~/.claude/hevy/programming.md` and apply it. In short:

- Strength first: main lift(s) at 3-6 reps, accessories after.
- Anchor every weight to what he actually lifted recently. Say what that was.
- Respect recovery (days since last trained) and the focus he asked for.
- Work around injuries; say what you swapped and why.
- Use exercise titles that exist in Hevy. If you want something that doesn't exist, check with `find_exercise.py`, and offer the hevy-add-exercise skill instead of inventing a title.

## 4. Present

Show the plan as a table per workout: exercise, sets x reps, weight (lb), rest, one-line reason. Keep reasoning short, and call out judgment calls (progression jumps, injury swaps, anything you extrapolated). End by offering to save it to Hevy with the hevy-routine-builder skill. Don't create anything in Hevy without his yes.
