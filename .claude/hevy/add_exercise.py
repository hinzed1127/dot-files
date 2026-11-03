#!/usr/bin/env python3
"""Create a custom exercise template in Hevy, unless one with that title exists.

Use this when an exercise is missing from Hevy's library (check first with
find_exercise.py). Default is a dry run that prints the request body; add
--create to send it. Exits 2 if the title already exists.

Allowed values: types, equipment and muscle groups are listed in hevy.py
(EXERCISE_TYPES, EQUIPMENT, MUSCLE_GROUPS); bad values are rejected with the list.

  add_exercise.py --title "Zercher Squat" --type weight_reps --equipment barbell \\
      --muscle quadriceps --other glutes abdominals --create
"""
import argparse
import json
import sys

import hevy


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--title", required=True)
    ap.add_argument("--type", required=True, help="e.g. weight_reps, reps_only, bodyweight_reps, duration")
    ap.add_argument("--equipment", required=True, help="e.g. barbell, dumbbell, machine, none")
    ap.add_argument("--muscle", required=True, help="primary muscle group, e.g. quadriceps")
    ap.add_argument("--other", nargs="*", default=[], help="secondary muscle groups")
    ap.add_argument("--create", action="store_true", help="send to Hevy (default is a dry run)")
    args = ap.parse_args()

    try:
        body = hevy.build_custom_exercise_body(args.title, args.type, args.equipment, args.muscle, args.other)
    except ValueError as e:
        sys.exit(f"error: {e}")

    key = hevy.load_key()
    templates = hevy.fetch_all("/exercise_templates", "exercise_templates", key, 100)
    same = [t for t in templates if t["title"].strip().lower() == args.title.strip().lower()]
    if same:
        print(f"already exists: {same[0]['id']}  {same[0]['title']} "
              f"({'custom' if same[0]['is_custom'] else 'library'})")
        sys.exit(2)
    similar = hevy.find_templates(templates, args.title)[:5]
    if similar:
        print("similar existing exercises (make sure none of these is what you want):")
        for t in similar:
            print(f"  {t['id']}  {t['title']}")

    if not args.create:
        print("DRY RUN, would send:")
        print(json.dumps(body, indent=1))
        return
    print(f"created exercise id: {hevy.post('/exercise_templates', key, body)}")


if __name__ == "__main__":
    main()
