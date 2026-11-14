---
name: hevy-routine-builder
description: Save a planned workout into Dan's Hevy app as a routine, with sets, weights in lbs, reps, rest timers and supersets, ready to run at the gym. Use whenever Dan says to save, add, push or put a workout or plan into Hevy, asks to create or build a Hevy routine, asks to change, fix or swap something in a routine already saved in Hevy, or says "yes" to saving a plan from the hevy-workout-planner skill.
---

# Hevy routine builder

Turns a plan into a Hevy routine via `build_routine.py`, either as a new routine or by replacing an existing one. Hevy's API cannot delete, so a mistaken new routine stays until Dan deletes it in the app; to fix a routine already saved, update it instead of creating a second one. Preview, then confirm, then create or update.

## Steps

1. **Resolve exercises.** Every exercise needs a Hevy template title that matches exactly (or a `template_id`). Look titles up with `python3 ~/.claude/hevy/find_exercise.py <words>`. If an exercise doesn't exist, use the hevy-add-exercise skill first. The "PT Exercises" custom template is Dan's prehab block. When several variants match (Lat Pulldown (Cable) vs (Machine)), pick the one in his recent history and name the choice in the preview so he can switch it.
2. **Write the spec** as a JSON file (scratchpad or temp dir, not the repo). Weights are in lbs; the script converts to kg:
   ```json
   {
     "title": "Upper A - Nov 4",
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
   Set fields: `type` (warmup, normal, failure, dropset; default normal), `lbs`, `reps`, `rep_range` [lo, hi], `duration_seconds`, `distance_meters`. Exercises sharing a `superset` number are grouped. Use exercise-level `notes` for cues and injury-related swaps. Hevy does not keep routine-level notes (verified live), so don't put anything important there. Fill the details Dan didn't give instead of asking up front, and flag them in the preview so he corrects them there: title is the plan's name or "<focus> - <date>"; rest is about 180s for main lifts at 3-6 reps and 90-120s for accessories.
3. **Dry run** (default, sends nothing): `python3 ~/.claude/hevy/build_routine.py spec.json`. Unknown titles fail with close matches. Show Dan the printed routine and get his OK.
4. **Create**: re-run with `--create`. It reads the routine back from Hevy and prints what was stored (in lbs). Check it matches the plan and report any difference.

**Changing a saved routine**: find its id with `python3 ~/.claude/hevy/list_routines.py <title words>`, write a spec for the whole routine as it should end up (the update replaces the title and every exercise; it keeps the routine's folder unless the spec sets `folder_id`), dry run as above, then re-run with `--update ROUTINE_ID`. It prints the routine it is replacing and reads the result back. Only update a routine Dan asked to change.

If Dan wants a week of workouts, make one routine per session, one confirmation for the set.
