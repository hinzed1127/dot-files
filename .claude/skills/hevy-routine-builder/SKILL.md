---
name: hevy-routine-builder
description: Save a planned workout into Dan's Hevy app as a routine, with sets, weights in lbs, reps, rest timers and supersets, ready to run at the gym. Use whenever Dan says to save, add, push or put a workout or plan into Hevy, asks to create or build a Hevy routine, or says "yes" to saving a plan from the hevy-workout-planner skill.
---

# Hevy routine builder

Turns a plan into a Hevy routine via `build_routine.py`. It only creates new routines; it never edits existing ones. Hevy's API cannot delete, so a mistaken routine stays until Dan deletes it in the app. Preview, then confirm, then create.

## Steps

1. **Resolve exercises.** Every exercise needs a Hevy template title that matches exactly (or a `template_id`). Look titles up with `python3 ~/.claude/hevy/find_exercise.py <words>`. If an exercise doesn't exist, use the hevy-add-exercise skill first. The "PT Exercises" custom template is Dan's prehab block.
2. **Write the spec** as a JSON file (scratchpad or temp dir, not the repo). Weights are in lbs; the script converts to kg:
   ```json
   {
     "title": "Upper A - Nov 4",
     "notes": "Heavy day",
     "exercises": [
       {
         "title": "Bench Press (Barbell)",
         "rest": 180,
         "notes": "Pause on chest",
         "sets": [
           { "type": "warmup", "lbs": 95, "reps": 8 },
           { "lbs": 155, "reps": 5 },
           { "lbs": 155, "reps": 5 }
         ]
       },
       { "title": "Seated Cable Row - V Grip (Cable)", "superset": 0, "rest": 0, "sets": [{ "lbs": 100, "rep_range": [8, 10] }] }
     ]
   }
   ```
   Set fields: `type` (warmup, normal, failure, dropset; default normal), `lbs`, `reps`, `rep_range` [lo, hi], `duration_seconds`, `distance_meters`. Exercises sharing a `superset` number are grouped. Use `notes` for cues and injury-related swaps.
3. **Dry run** (default, sends nothing): `python3 ~/.claude/hevy/build_routine.py spec.json`. Unknown titles fail with close matches. Show Dan the printed routine and get his OK.
4. **Create**: re-run with `--create`. It reads the routine back from Hevy and prints what was stored (in lbs). Check it matches the plan and report any difference.

If Dan wants a week of workouts, make one routine per session, one confirmation for the set.
