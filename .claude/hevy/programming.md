# Strength-first programming principles

Shared by hevy-workout-planner and hevy-progress-checkin. These are general rules of thumb for a lifter prioritizing strength over size. Treat them as defaults; Dan's goals.md, injuries and what he says today override them.

## Session shape

- 1-2 main lifts first (squat, bench, deadlift or trap bar, overhead press, row variants): 3-5 working sets of 3-6 reps, leaving 1-3 reps in reserve (RPE 7-9). Heavy sets early, while fresh.
- 3-5 accessories after: 6-12 reps, 2-4 sets, chosen to support the main lifts or cover muscle groups that are under-trained. Hypertrophy-range work is fine here and is a side effect, not the aim.
- About 5-7 exercises total. Include ramp-up warmup sets for the first main lift.
- If Dan uses a PT/prehab block (a custom "PT Exercises" template appears in his history), put it first.

## Choosing weights (anchor to real data, never guess)

- Take the exercise's recent best working set from `summary.py` and its e1RM.
- Rough load for a rep target as a share of e1RM: 3 reps about 90%, 5 reps about 85%, 8 reps about 77%, 10 reps about 73%.
- If he already did the lift recently at a given weight and hit every target rep, add the smallest practical jump (about 5 lb upper body, 5-10 lb lower body, one dumbbell step). If he missed reps, repeat the weight. If an exercise has no history, start conservative and say so.
- Round to weights that exist on the equipment (5 lb plate jumps for barbells, dumbbell steps in 5 lb).

## Frequency and recovery

- Use "days since last trained" from `summary.py`. Avoid heavy work for the same primary muscle within about 48 hours. Lower-body heavy days need more spacing than upper.
- For "full body" requests, pick one lower-body, one horizontal push, one pull, and one vertical push or hip hinge pattern, rotating which is the main lift versus accessory from session to session.
- Weekly sets per muscle in `summary.py` are a sanity check: a rough range for steady progress is about 6-12 hard sets per muscle group per week for strength-focused training. Flag big gaps.

## Stagnation

- Same e1RM for 3+ sessions: change something (rep range, variation, a lighter week of about 10% lower load, or more weekly volume) instead of repeating it. Explain which and why.
- Judge trends cautiously. Dan only recently started logging in detail, sessions vary in rep ranges and the trend label compares single sessions, so confirm with the actual sets before calling anything a problem.

## Injuries

- Substitute or avoid movements that load the affected area; reduce load rather than push through pain.
- When the injury or its severity is unclear, ask. If something sounds like it needs a clinician, say so plainly. You are not a physical therapist.

## Strength standards

- `summary.py` compares best e1RM to bodyweight against approximate standards (novice, intermediate, advanced, elite). They are rough, mostly useful for spotting which lifts lag the others. Taller lifters usually have longer ranges of motion, so do not read the labels as precise.
