"""Tests for hevy.py. Run: python3 -m unittest discover -s ~/.claude/hevy/tests

Pure-function tests use hand-built dicts shaped like the Hevy API responses.
LiveApiTest talks to the real API (read-only) and is skipped if no key is configured.
"""
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import hevy

TEMPLATES = [
    {"id": "A1", "title": "Bench Press (Barbell)", "is_custom": False},
    {"id": "A2", "title": "Incline Bench Press (Barbell)", "is_custom": False},
    {"id": "A3", "title": "Bench Press (Dumbbell)", "is_custom": False},
    {"id": "C1", "title": "PT Exercises", "is_custom": True},
]


class UnitConversionTest(unittest.TestCase):
    def test_lb_to_kg_uses_exact_factor(self):
        self.assertAlmostEqual(hevy.lb_to_kg(100), 45.359237)

    def test_kg_to_lb_rounds_to_tenth(self):
        self.assertEqual(hevy.kg_to_lb(hevy.lb_to_kg(145)), 145.0)
        self.assertEqual(hevy.kg_to_lb(None), None)


class OneRepMaxTest(unittest.TestCase):
    def test_epley_estimate(self):
        self.assertAlmostEqual(hevy.estimate_1rm(200, 5), 200 * (1 + 5 / 30))

    def test_single_rep_is_the_weight(self):
        self.assertEqual(hevy.estimate_1rm(300, 1), 300)

    def test_high_rep_sets_are_not_estimated(self):
        self.assertIsNone(hevy.estimate_1rm(100, 20))

    def test_missing_data_is_none(self):
        self.assertIsNone(hevy.estimate_1rm(None, 5))
        self.assertIsNone(hevy.estimate_1rm(100, None))
        self.assertIsNone(hevy.estimate_1rm(0, 5))


class WorkingSetsTest(unittest.TestCase):
    def test_excludes_warmups_and_sets_without_weight_and_reps(self):
        sets = [
            {"type": "warmup", "weight_kg": 40, "reps": 10},
            {"type": "normal", "weight_kg": 80, "reps": 5},
            {"type": "normal", "weight_kg": None, "reps": 5},
            {"type": "failure", "weight_kg": 80, "reps": 3},
        ]
        got = hevy.working_sets(sets)
        self.assertEqual([s["reps"] for s in got], [5, 3])

    def test_best_set_is_highest_estimated_1rm(self):
        sets = [
            {"type": "normal", "weight_kg": 100, "reps": 5},
            {"type": "normal", "weight_kg": 110, "reps": 3},
            {"type": "normal", "weight_kg": 90, "reps": 8},
        ]
        # e1RM: 116.7, 121.0, 114.0
        self.assertEqual(hevy.best_set(sets)["weight_kg"], 110)

    def test_best_set_of_nothing_is_none(self):
        self.assertIsNone(hevy.best_set([{"type": "warmup", "weight_kg": 40, "reps": 10}]))


class WorkoutWindowTest(unittest.TestCase):
    WORKOUTS = [
        {"id": "w3", "start_time": "2026-10-30T17:00:00+00:00"},
        {"id": "w2", "start_time": "2026-10-01T17:00:00+00:00"},
        {"id": "w1", "start_time": "2026-08-01T17:00:00+00:00"},
    ]

    def test_keeps_workouts_within_n_weeks_of_today(self):
        got = hevy.workouts_within_weeks(self.WORKOUTS, 8, today=date(2026, 11, 3))
        self.assertEqual([w["id"] for w in got], ["w3", "w2"])

    def test_workout_date_is_the_calendar_date(self):
        self.assertEqual(hevy.workout_date(self.WORKOUTS[0]), date(2026, 10, 30))


class FindTemplatesTest(unittest.TestCase):
    def test_all_words_must_match_case_insensitively(self):
        got = hevy.find_templates(TEMPLATES, "bench barbell")
        self.assertEqual([t["id"] for t in got], ["A1", "A2"])

    def test_exact_title_sorts_first(self):
        got = hevy.find_templates(TEMPLATES, "bench press (barbell)")
        self.assertEqual(got[0]["id"], "A1")

    def test_no_match_is_empty(self):
        self.assertEqual(hevy.find_templates(TEMPLATES, "deadlift"), [])


class CustomExerciseBodyTest(unittest.TestCase):
    def test_builds_api_body(self):
        body = hevy.build_custom_exercise_body(
            "Zercher Squat", "weight_reps", "barbell", "quadriceps", ["glutes", "abdominals"])
        self.assertEqual(body, {"exercise": {
            "title": "Zercher Squat", "exercise_type": "weight_reps",
            "equipment_category": "barbell", "muscle_group": "quadriceps",
            "other_muscles": ["glutes", "abdominals"]}})

    def test_rejects_unknown_muscle_group(self):
        with self.assertRaisesRegex(ValueError, "muscle_group.*quads"):
            hevy.build_custom_exercise_body("X", "weight_reps", "barbell", "quads")

    def test_rejects_unknown_equipment(self):
        with self.assertRaisesRegex(ValueError, "equipment_category.*cable"):
            hevy.build_custom_exercise_body("X", "weight_reps", "cable", "chest")

    def test_rejects_unknown_type(self):
        with self.assertRaisesRegex(ValueError, "exercise_type.*weights"):
            hevy.build_custom_exercise_body("X", "weights", "barbell", "chest")


class RoutineBodyTest(unittest.TestCase):
    SPEC = {
        "title": "Upper A", "notes": "Heavy day",
        "exercises": [
            {"title": "Bench Press (Barbell)", "rest": 180, "notes": "Pause on chest",
             "sets": [{"type": "warmup", "lbs": 95, "reps": 8},
                      {"lbs": 155, "reps": 5}, {"lbs": 155, "reps": 5}]},
            {"title": "PT Exercises", "superset": 0, "sets": [{"reps": 10}]},
        ],
    }

    def test_converts_lbs_to_kg_and_fills_defaults(self):
        body = hevy.build_routine_body(self.SPEC, TEMPLATES)["routine"]
        self.assertEqual(body["title"], "Upper A")
        self.assertIsNone(body["folder_id"])
        bench = body["exercises"][0]
        self.assertEqual(bench["exercise_template_id"], "A1")
        self.assertEqual(bench["rest_seconds"], 180)
        self.assertEqual(bench["sets"][0]["type"], "warmup")
        self.assertEqual(bench["sets"][1]["type"], "normal")
        self.assertAlmostEqual(bench["sets"][1]["weight_kg"], hevy.lb_to_kg(155))
        pt = body["exercises"][1]
        self.assertEqual(pt["exercise_template_id"], "C1")
        self.assertEqual(pt["superset_id"], 0)
        self.assertIsNone(pt["sets"][0]["weight_kg"])

    def test_rep_range_passes_through(self):
        spec = {"title": "T", "exercises": [
            {"title": "Bench Press (Barbell)", "sets": [{"lbs": 100, "rep_range": [8, 12]}]}]}
        s = hevy.build_routine_body(spec, TEMPLATES)["routine"]["exercises"][0]["sets"][0]
        self.assertEqual(s["rep_range"], {"start": 8, "end": 12})
        self.assertIsNone(s["reps"])

    def test_unknown_exercise_title_is_an_error_listing_close_matches(self):
        spec = {"title": "T", "exercises": [{"title": "Bench Press", "sets": [{"reps": 5}]}]}
        with self.assertRaisesRegex(ValueError, "Bench Press.*Bench Press \\(Barbell\\)"):
            hevy.build_routine_body(spec, TEMPLATES)

    def test_template_id_can_be_given_directly(self):
        spec = {"title": "T", "exercises": [{"template_id": "A3", "sets": [{"reps": 5}]}]}
        ex = hevy.build_routine_body(spec, TEMPLATES)["routine"]["exercises"][0]
        self.assertEqual(ex["exercise_template_id"], "A3")


class ParseBodyTest(unittest.TestCase):
    def test_json_object_is_parsed(self):
        self.assertEqual(hevy.parse_body('{"id": "A1"}'), {"id": "A1"})

    def test_bare_uuid_is_returned_as_text(self):
        # POST /exercise_templates answers with just the new id, not JSON. Some uuids
        # start like a JSON number ("9834033e-1b21-...") so they must not be mistaken for one.
        for body in ("9834033e-1b21-43c5-aa1d-9811de6b958a\n", "02c166fc-9784-4a34-ab48-114ff0f9877c",
                     "ff19e182-8660-4fe3-9cf7-9fe3bda9e6ee"):
            self.assertEqual(hevy.parse_body(body), body.strip())


class RetryPolicyTest(unittest.TestCase):
    def test_reads_retry_on_server_and_network_errors(self):
        self.assertTrue(hevy.is_retryable("GET", None))
        self.assertTrue(hevy.is_retryable("GET", 503))

    def test_reads_do_not_retry_client_errors_except_rate_limit(self):
        self.assertFalse(hevy.is_retryable("GET", 404))
        self.assertTrue(hevy.is_retryable("GET", 429))

    def test_writes_retry_only_when_rate_limited(self):
        # Anything else may mean the write already happened; retrying would duplicate it.
        self.assertTrue(hevy.is_retryable("POST", 429))
        self.assertFalse(hevy.is_retryable("POST", None))
        self.assertFalse(hevy.is_retryable("POST", 500))
        self.assertFalse(hevy.is_retryable("PUT", 502))


class LiveApiTest(unittest.TestCase):
    def setUp(self):
        try:
            self.key = hevy.load_key()
        except SystemExit:
            self.skipTest("no HEVY_API_KEY configured")

    def test_user_info_reports_weight_unit(self):
        info = hevy.get("/user/info", self.key)
        self.assertIn(info["data"]["weight_unit"], ("kg", "lbs"))

    def test_workouts_paginate_newest_first(self):
        items = hevy.fetch_all("/workouts", "workouts", self.key, 10, max_pages=2)
        self.assertGreater(len(items), 10)
        times = [w["start_time"] for w in items]
        self.assertEqual(times, sorted(times, reverse=True))


if __name__ == "__main__":
    unittest.main()
