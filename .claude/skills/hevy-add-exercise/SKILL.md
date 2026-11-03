---
name: hevy-add-exercise
description: Add a custom exercise to Dan's Hevy exercise library, but only if Hevy doesn't already have it. Use whenever Dan describes an exercise to add or log in Hevy, says an exercise is missing from Hevy, asks to create a custom exercise, or names a movement (e.g. a variation, machine or PT exercise) that he wants available for workouts and routines.
---

# Add a custom Hevy exercise

Hevy's API has no delete or edit endpoint for exercises, so a wrong exercise stays until Dan removes it in the app. Check first, preview, and confirm before creating.

## Steps

1. **Check the library first.** Run `python3 ~/.claude/hevy/find_exercise.py <words>` with a few different word combinations (e.g. "zercher", then "squat zercher"). Hevy's own naming is usually `Name (Equipment)`; the exercise may exist under a slightly different name. If a match exists, tell Dan the exact title and stop.
2. **Map Dan's description to Hevy's fields.** Ask one question at a time for what's missing:
   - title: follow Hevy's `Name (Equipment)` style, e.g. "Zercher Squat (Barbell)"
   - type: weight_reps, reps_only, bodyweight_reps, bodyweight_assisted_reps, duration, weight_duration, distance_duration, short_distance_weight
   - equipment: none, barbell, dumbbell, kettlebell, machine, plate, resistance_band, suspension, other
   - primary muscle: abdominals, shoulders, biceps, triceps, forearms, quadriceps, hamstrings, calves, glutes, abductors, adductors, lats, upper_back, traps, lower_back, chest, cardio, neck, full_body, other
   - secondary muscles (optional, same list)
3. **Dry run** (the default; nothing is sent):
   ```bash
   python3 ~/.claude/hevy/add_exercise.py --title "..." --type weight_reps --equipment barbell \
     --muscle quadriceps --other glutes abdominals
   ```
   It exits 2 if the title already exists (case-insensitive) and lists similar existing exercises. Show Dan the final title and fields and ask for his OK.
4. **Create** by re-running with `--create`. Report the returned exercise id and title.

If Dan gives several exercises, do them one at a time through the same steps.
