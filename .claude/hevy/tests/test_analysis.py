"""Tests for analysis.py. Run: python3 -m unittest discover -s ~/.claude/hevy/tests"""
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import analysis
import hevy

KG = hevy.lb_to_kg

TEMPLATES = [
    {"id": "BP", "title": "Bench Press (Barbell)", "primary_muscle_group": "chest"},
    {"id": "SQ", "title": "Squat (Barbell)", "primary_muscle_group": "quadriceps"},
    {"id": "PT", "title": "PT Exercises", "primary_muscle_group": "other"},
]


def workout(day, *exercises):
    return {"start_time": f"{day}T17:00:00+00:00", "exercises": [
        {"exercise_template_id": tid, "title": tid, "sets": sets} for tid, sets in exercises]}


def sets(*pairs, kind="normal"):
    return [{"type": kind, "weight_kg": None if lb is None else KG(lb), "reps": reps} for lb, reps in pairs]


class ExerciseSessionsTest(unittest.TestCase):
    def test_one_entry_per_workout_with_best_set_in_lbs_oldest_first(self):
        ws = [
            workout("2026-10-20", ("BP", sets((135, 5), (145, 3)))),
            workout("2026-10-10", ("BP", sets((135, 5)))),
        ]
        got = analysis.exercise_sessions(ws)["BP"]["sessions"]
        self.assertEqual([s["date"] for s in got], [date(2026, 10, 10), date(2026, 10, 20)])
        self.assertEqual((got[1]["lb"], got[1]["reps"]), (145.0, 3))
        self.assertAlmostEqual(got[0]["e1rm_lb"], 135 * (1 + 5 / 30), places=0)

    def test_unloaded_exercises_are_skipped(self):
        ws = [workout("2026-10-10", ("PT", sets((None, 10))))]
        self.assertEqual(analysis.exercise_sessions(ws), {})

    def test_same_template_with_different_titles_is_merged_by_id(self):
        w1 = workout("2026-10-10", ("BP", sets((135, 5))))
        w2 = workout("2026-10-12", ("BP", sets((140, 5))))
        w2["exercises"][0]["title"] = "bench press (barbell) "
        self.assertEqual(len(analysis.exercise_sessions([w1, w2])["BP"]["sessions"]), 2)


class ClassifyTrendTest(unittest.TestCase):
    def sessions(self, *e1rms):
        return [{"date": date(2026, 10, i + 1), "e1rm_lb": e} for i, e in enumerate(e1rms)]

    def test_fewer_than_three_sessions_is_insufficient(self):
        self.assertEqual(analysis.classify_trend(self.sessions(150, 160)), "insufficient data")

    def test_recent_best_above_prior_best_is_progressing(self):
        self.assertEqual(analysis.classify_trend(self.sessions(150, 152, 160)), "progressing")

    def test_flat_is_stagnating(self):
        self.assertEqual(analysis.classify_trend(self.sessions(150, 160, 159)), "stagnating")

    def test_clear_drop_is_regressing(self):
        self.assertEqual(analysis.classify_trend(self.sessions(160, 162, 140)), "regressing")


class MuscleVolumeTest(unittest.TestCase):
    WS = [
        workout("2026-10-30", ("BP", sets((135, 5), (135, 5), (95, 10, ))), ("SQ", sets((185, 5)))),
        workout("2026-10-20", ("BP", sets((135, 5)))),
        workout("2026-08-01", ("BP", sets((135, 5)))),
    ]

    def test_average_weekly_working_sets_in_window(self):
        got = analysis.weekly_sets_by_muscle(self.WS, TEMPLATES, weeks=4, today=date(2026, 11, 3))
        self.assertEqual(got["chest"], 1.0)  # 4 sets in window / 4 weeks
        self.assertEqual(got["quadriceps"], 0.25)

    def test_warmup_sets_do_not_count(self):
        ws = [workout("2026-10-30", ("BP", sets((95, 10), kind="warmup") + sets((135, 5))))]
        got = analysis.weekly_sets_by_muscle(ws, TEMPLATES, weeks=1, today=date(2026, 11, 3))
        self.assertEqual(got["chest"], 1.0)

    def test_days_since_each_muscle_was_trained(self):
        got = analysis.days_since_trained(self.WS, TEMPLATES, today=date(2026, 11, 3))
        self.assertEqual(got["chest"], 4)
        self.assertEqual(got["quadriceps"], 4)


class FormatSetsTest(unittest.TestCase):
    def test_collapses_repeated_sets_and_marks_warmups(self):
        s = sets((115, 10), kind="warmup") + sets((145, 8), (145, 8), (145, 8), (150, 6))
        self.assertEqual(analysis.format_sets(s), "w115x10, 145x8 x3, 150x6")

    def test_unweighted_sets_show_reps_only(self):
        self.assertEqual(analysis.format_sets(sets((None, 10), (None, 10))), "10r x2")


if __name__ == "__main__":
    unittest.main()
