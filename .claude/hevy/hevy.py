"""Shared Hevy API client and helpers used by every hevy-* skill.

Why: one place for auth, pagination, retries, kg/lb conversion and request-body
building, so the skills' scripts stay small and agree with each other.

Key lookup: HEVY_API_KEY env var, else HEVY_API_KEY=... in ~/.claude/hevy/.env.
Hevy stores kg; this account displays lbs, so scripts talk lbs and convert here.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = "https://api.hevyapp.com/v1"
KG_PER_LB = 0.45359237

EXERCISE_TYPES = ["weight_reps", "reps_only", "bodyweight_reps", "bodyweight_assisted_reps",
                  "duration", "weight_duration", "distance_duration", "short_distance_weight"]
EQUIPMENT = ["none", "barbell", "dumbbell", "kettlebell", "machine", "plate",
             "resistance_band", "suspension", "other"]
MUSCLE_GROUPS = ["abdominals", "shoulders", "biceps", "triceps", "forearms", "quadriceps",
                 "hamstrings", "calves", "glutes", "abductors", "adductors", "lats",
                 "upper_back", "traps", "lower_back", "chest", "cardio", "neck", "full_body",
                 "other"]

# Epley is unreliable for long sets, so estimates stop here.
MAX_REPS_FOR_1RM = 12


# --- units and strength math -------------------------------------------------

def lb_to_kg(lb):
    return lb * KG_PER_LB


def kg_to_lb(kg):
    return None if kg is None else round(kg / KG_PER_LB, 1)


def estimate_1rm(weight, reps):
    """Epley estimate in the same unit as weight; None when it can't be trusted."""
    if not weight or not reps or reps > MAX_REPS_FOR_1RM:
        return None
    return weight if reps == 1 else weight * (1 + reps / 30)


def working_sets(sets):
    return [s for s in sets
            if s.get("type") != "warmup" and s.get("weight_kg") is not None and s.get("reps") is not None]


def best_set(sets):
    """Working set with the highest estimated 1RM, or None."""
    scored = [(estimate_1rm(s["weight_kg"], s["reps"]), s) for s in working_sets(sets)]
    scored = [(e, s) for e, s in scored if e is not None]
    return max(scored, key=lambda p: p[0])[1] if scored else None


# --- workouts ---------------------------------------------------------------

def workout_date(workout):
    return datetime.fromisoformat(workout["start_time"]).date()


def workouts_within_weeks(workouts, weeks, today=None):
    cutoff = (today or date.today()) - timedelta(weeks=weeks)
    return [w for w in workouts if workout_date(w) >= cutoff]


# --- exercise templates -----------------------------------------------------

def find_templates(templates, query):
    """Templates whose title contains every word of query; exact title first."""
    words = query.lower().split()
    hits = [t for t in templates if all(w in t["title"].lower() for w in words)]
    return sorted(hits, key=lambda t: (t["title"].lower() != query.lower().strip(), len(t["title"])))


def _check_choice(field, value, allowed):
    if value not in allowed:
        raise ValueError(f"{field} '{value}' is not valid; choose from: {', '.join(allowed)}")


def build_custom_exercise_body(title, exercise_type, equipment_category, muscle_group, other_muscles=()):
    _check_choice("exercise_type", exercise_type, EXERCISE_TYPES)
    _check_choice("equipment_category", equipment_category, EQUIPMENT)
    _check_choice("muscle_group", muscle_group, MUSCLE_GROUPS)
    for m in other_muscles:
        _check_choice("other_muscles", m, MUSCLE_GROUPS)
    return {"exercise": {"title": title, "exercise_type": exercise_type,
                         "equipment_category": equipment_category, "muscle_group": muscle_group,
                         "other_muscles": list(other_muscles)}}


# --- routines ---------------------------------------------------------------

def _template_id(entry, templates):
    if "template_id" in entry:
        return entry["template_id"]
    title = entry["title"].strip()
    exact = [t for t in templates if t["title"].strip() == title]
    if exact:
        return exact[0]["id"]
    close = [t["title"] for t in find_templates(templates, title)[:5]]
    hint = f"; close matches: {', '.join(close)}" if close else ""
    raise ValueError(f"no exercise titled '{title}'{hint}")


def _routine_set(s):
    rr = s.get("rep_range")
    return {"type": s.get("type", "normal"),
            "weight_kg": lb_to_kg(s["lbs"]) if s.get("lbs") is not None else None,
            "reps": s.get("reps"),
            "distance_meters": s.get("distance_meters"),
            "duration_seconds": s.get("duration_seconds"),
            "custom_metric": None,
            "rep_range": {"start": rr[0], "end": rr[1]} if rr else None}


def build_routine_body(spec, templates):
    """Turn a lbs-based routine spec (see hevy-routine-builder) into a POST /routines body."""
    return {"routine": {
        "title": spec["title"], "folder_id": spec.get("folder_id"), "notes": spec.get("notes", ""),
        "exercises": [
            {"exercise_template_id": _template_id(e, templates),
             "superset_id": e.get("superset"), "rest_seconds": e.get("rest"),
             "notes": e.get("notes"), "sets": [_routine_set(s) for s in e["sets"]]}
            for e in spec["exercises"]]}}


# --- HTTP -------------------------------------------------------------------

def load_key():
    key = os.environ.get("HEVY_API_KEY")
    if key:
        return key.strip()
    env = HERE / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("HEVY_API_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit(f"HEVY_API_KEY not found: set the env var or add it to {env}")


def request(method, path, key, body=None, **params):
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE}{path}" + (f"?{qs}" if qs else "")
    data = None if body is None else json.dumps(body).encode()
    headers = {"api-key": key}
    if data is not None:
        headers["Content-Type"] = "application/json"
    for attempt in range(5):
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            # 4xx means our request is wrong; retrying won't help (429 aside).
            if 400 <= e.code < 500 and e.code != 429:
                sys.exit(f"{method} {path} failed: HTTP {e.code} {detail}")
            err = f"HTTP {e.code} {detail}"
        except Exception as e:
            err = str(e)
        print(f"  retry {attempt + 1} for {method} {path}: {err}", file=sys.stderr)
        time.sleep(2 ** attempt)
    sys.exit(f"giving up on {method} {path}")


def get(path, key, **params):
    return request("GET", path, key, **params)


def post(path, key, body):
    return request("POST", path, key, body=body)


def fetch_all(path, list_key, key, page_size, max_pages=None):
    """Every item from a paginated list endpoint (newest first for workouts)."""
    items, page = [], 1
    while True:
        data = get(path, key, page=page, pageSize=page_size)
        items += data[list_key]
        if page >= data["page_count"] or (max_pages and page >= max_pages):
            return items
        page += 1
