#!/usr/bin/env python3
"""Print a compact training summary from Hevy (weights in lbs, read-only).

Use this first for planning a workout or doing a progress check-in. It prints:
body weight, recent workouts, per-exercise strength trend, and weekly sets by
muscle group, so you don't have to read raw API JSON.

  summary.py --weeks 8            # planner default
  summary.py --weeks 12 --recent 5  # check-in; only list the last 5 workouts in detail
"""
import argparse

import analysis
import hevy


def latest_body_weight_lb(key):
    data = hevy.get("/body_measurements", key, page=1, pageSize=10)
    for m in data["body_measurements"]:
        if m.get("weight_kg"):
            return hevy.kg_to_lb(m["weight_kg"]), m["date"]
    return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--weeks", type=int, default=8, help="window to analyze (default 8)")
    ap.add_argument("--recent", type=int, default=None,
                    help="list only this many most recent workouts in detail (default: all in window)")
    args = ap.parse_args()

    key = hevy.load_key()
    all_workouts = hevy.fetch_all("/workouts", "workouts", key, 10)
    templates = hevy.fetch_all("/exercise_templates", "exercise_templates", key, 100)
    muscle_of = {t["id"]: t["primary_muscle_group"] for t in templates}
    workouts = hevy.workouts_within_weeks(all_workouts, args.weeks)

    lb, on = latest_body_weight_lb(key)
    print("## Body weight")
    print(f"{lb} lb (logged {on})" if lb else "none logged")

    print(f"\n## Recent workouts ({len(workouts)} in the last {args.weeks} weeks, "
          f"{len(workouts) / args.weeks:.1f}/week)")
    for w in workouts[:args.recent]:
        print(f"{hevy.workout_date(w)}  {w['title'].strip()}")
        for ex in w["exercises"]:
            print(f"    {ex['title'].strip()} [{muscle_of.get(ex['exercise_template_id'], '?')}]: "
                  f"{analysis.format_sets(ex['sets'])}")

    print("\n## Exercise progress (best working set per session; e1RM = Epley, reps <= 12)")
    progress = analysis.exercise_sessions(workouts)
    for entry in sorted(progress.values(), key=lambda e: -len(e["sessions"])):
        s = entry["sessions"]
        best = max(x["e1rm_lb"] for x in s)
        print(f"{entry['title']}: {len(s)} sessions, last {s[-1]['date']} {s[-1]['lb']:g}x{s[-1]['reps']}, "
              f"best e1RM {best:.0f}, trend: {analysis.classify_trend(s)}")

    print("\n## Weekly sets by muscle (avg working sets/week; days since last trained)")
    sets = analysis.weekly_sets_by_muscle(workouts, templates, args.weeks)
    since = analysis.days_since_trained(workouts, templates)
    for muscle, n in sorted(sets.items(), key=lambda p: -p[1]):
        print(f"{muscle}: {n:.1f}/wk, last trained {since[muscle]}d ago")


if __name__ == "__main__":
    main()
