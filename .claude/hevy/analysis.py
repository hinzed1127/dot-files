"""Strength and volume analysis over Hevy workouts (all weights in lbs).

Why: the planner and check-in skills need the same numbers, and they should come
from deterministic code, not from Claude eyeballing raw JSON.
"""
from collections import defaultdict
from datetime import date

import hevy

PROGRESS_THRESHOLD = 0.02   # latest e1RM this far above the prior best counts as progress
REGRESS_THRESHOLD = -0.05   # this far below counts as regression
MIN_SESSIONS_FOR_TREND = 3


def exercise_sessions(workouts):
    """{template_id: {"title", "sessions": [{date, lb, reps, e1rm_lb}]}}, sessions oldest first.

    One entry per workout: the working set with the highest estimated 1RM.
    Keyed by template id because titles drift ("PT Exercises" vs "PT exercises").
    Exercises with no loaded sets (PT, planks) are left out.
    """
    out = {}
    for w in workouts:
        for ex in w["exercises"]:
            top = hevy.best_set(ex["sets"])
            if top is None:
                continue
            entry = out.setdefault(ex["exercise_template_id"], {"title": ex["title"].strip(), "sessions": []})
            entry["sessions"].append({
                "date": hevy.workout_date(w),
                "lb": hevy.kg_to_lb(top["weight_kg"]),
                "reps": top["reps"],
                "e1rm_lb": hevy.estimate_1rm(hevy.kg_to_lb(top["weight_kg"]), top["reps"]),
            })
    for entry in out.values():
        entry["sessions"].sort(key=lambda s: s["date"])
    return out


# Approximate male bodyweight multiples at which each level is reached, in the style of
# commonly cited strength-standard tables. Rough guides, not science: edit freely.
LEVELS = ["novice", "intermediate", "advanced", "elite"]
STRENGTH_STANDARDS = {
    "squat": {"titles": ["Squat (Barbell)"], "thresholds": [0.75, 1.25, 1.75, 2.25]},
    "bench press": {"titles": ["Bench Press (Barbell)"], "thresholds": [0.5, 1.0, 1.5, 2.0]},
    "deadlift": {"titles": ["Deadlift (Barbell)", "Deadlift (Trap bar)"], "thresholds": [1.0, 1.5, 2.0, 2.5]},
    "overhead press": {"titles": ["Overhead Press (Barbell)"], "thresholds": [0.35, 0.65, 0.9, 1.2]},
    "barbell row": {"titles": ["Bent Over Row (Barbell)"], "thresholds": [0.5, 0.9, 1.2, 1.5]},
}


def strength_levels(progress, bodyweight_lb):
    """Best e1RM per main lift as a multiple of bodyweight, with an approximate level.

    `progress` is the output of exercise_sessions. Lifts never performed are omitted.
    """
    out = []
    for lift, std in STRENGTH_STANDARDS.items():
        best = [s["e1rm_lb"] for e in progress.values() if e["title"] in std["titles"] for s in e["sessions"]]
        if not best:
            continue
        e1rm = max(best)
        ratio = round(e1rm / bodyweight_lb, 2)
        reached = [lvl for lvl, t in zip(LEVELS, std["thresholds"]) if ratio >= t]
        out.append({"lift": lift, "e1rm_lb": e1rm, "ratio": ratio,
                    "level": reached[-1] if reached else "untrained"})
    return out


def classify_trend(sessions):
    """Latest session's e1RM against the best of all earlier sessions."""
    if len(sessions) < MIN_SESSIONS_FOR_TREND:
        return "insufficient data"
    prior_best = max(s["e1rm_lb"] for s in sessions[:-1])
    change = (sessions[-1]["e1rm_lb"] - prior_best) / prior_best
    if change > PROGRESS_THRESHOLD:
        return "progressing"
    if change < REGRESS_THRESHOLD:
        return "regressing"
    return "stagnating"


def format_sets(sets):
    """Compact one-line form: 'w115x10, 145x8 x3' (w = warmup, 10r = 10 reps unweighted)."""
    tokens = []
    for s in sets:
        if s.get("reps") is None:
            body = f"{s['duration_seconds']}s" if s.get("duration_seconds") else "?"
        elif s.get("weight_kg") is None:
            body = f"{s['reps']}r"
        else:
            body = f"{hevy.kg_to_lb(s['weight_kg']):g}x{s['reps']}"
        tokens.append(("w" if s.get("type") == "warmup" else "") + body)
    parts = []
    for tok in tokens:
        if parts and parts[-1][0] == tok:
            parts[-1][1] += 1
        else:
            parts.append([tok, 1])
    return ", ".join(t if n == 1 else f"{t} x{n}" for t, n in parts)


def _primary_muscles(templates):
    return {t["id"]: t["primary_muscle_group"] for t in templates}


def weekly_sets_by_muscle(workouts, templates, weeks, today=None):
    """Average working sets per week by primary muscle group over the last `weeks` weeks."""
    muscle_of = _primary_muscles(templates)
    totals = defaultdict(int)
    for w in hevy.workouts_within_weeks(workouts, weeks, today):
        for ex in w["exercises"]:
            totals[muscle_of.get(ex["exercise_template_id"], "other")] += len(hevy.working_sets(ex["sets"]))
    return {m: n / weeks for m, n in totals.items() if n}


def days_since_trained(workouts, templates, today=None):
    """Days since each primary muscle group last had a working set."""
    today = today or date.today()
    muscle_of = _primary_muscles(templates)
    last = {}
    for w in workouts:
        d = hevy.workout_date(w)
        for ex in w["exercises"]:
            if hevy.working_sets(ex["sets"]):
                m = muscle_of.get(ex["exercise_template_id"], "other")
                last[m] = max(last.get(m, d), d)
    return {m: (today - d).days for m, d in last.items()}
