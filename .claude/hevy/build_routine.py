#!/usr/bin/env python3
"""Create a Hevy routine from a JSON spec written in lbs (POST only; never edits existing routines).

Use this to save a planned workout into Hevy so it shows up ready to run in the
app. Default is a dry run that prints the routine in lbs; --create sends it,
then reads it back and prints what Hevy stored.

Spec format (exercise "title" must match a Hevy template title exactly; use
find_exercise.py to look titles up, or give "template_id" instead):

  {"title": "Upper A", "folder_id": null,   # Hevy does not store routine-level notes
   "exercises": [
     {"title": "Bench Press (Barbell)", "rest": 180, "notes": "Pause on chest", "superset": null,
      "sets": [{"type": "warmup", "lbs": 95, "reps": 8},
               {"lbs": 155, "reps": 5}, {"lbs": 155, "reps": 5},
               {"lbs": 100, "rep_range": [8, 12]}]}]}

Set fields: type (warmup|normal|failure|dropset, default normal), lbs, reps,
rep_range [lo, hi], duration_seconds, distance_meters. Exercises that share a
"superset" number are grouped.
"""
import argparse
import json
import sys

import hevy


def describe(routine, title_of):
    print(f"{routine['title']}  notes={routine.get('notes')!r}")
    for i, e in enumerate(routine["exercises"], 1):
        name = e.get("title") or title_of.get(e["exercise_template_id"], e["exercise_template_id"])
        rest = e.get("rest_seconds")
        rest = "none" if rest is None else f"{rest}s"
        print(f"{i}. {name}  superset={e.get('superset_id')}  rest={rest}  notes={e.get('notes')!r}")
        for s in e["sets"]:
            w = "bodyweight/blank" if s["weight_kg"] is None else f"{hevy.kg_to_lb(s['weight_kg']):g} lb ({s['weight_kg']:.2f} kg)"
            reps = s["reps"] if s["reps"] is not None else s.get("rep_range")
            print(f"     {s['type']:7} {w} x {reps}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("spec", help="path to routine spec JSON")
    ap.add_argument("--create", action="store_true", help="send to Hevy (default is a dry run)")
    args = ap.parse_args()

    spec = json.load(open(args.spec))
    key = hevy.load_key()
    templates = hevy.fetch_all("/exercise_templates", "exercise_templates", key, 100)
    try:
        body = hevy.build_routine_body(spec, templates)
    except ValueError as e:
        sys.exit(f"error: {e}")
    title_of = {t["id"]: t["title"] for t in templates}

    if not args.create:
        print("DRY RUN, would create:")
        describe(body["routine"], title_of)
        return
    created = hevy.post("/routines", key, body)
    routine = created.get("routine", created)
    routine = routine[0] if isinstance(routine, list) else routine
    print("created; Hevy stored:")
    describe(hevy.get(f"/routines/{routine['id']}", key)["routine"], title_of)


if __name__ == "__main__":
    main()
