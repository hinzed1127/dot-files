"""End-to-end tests for the CLI scripts against the real Hevy API.

Only read-only calls and dry runs: nothing here creates data on the account.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import hevy


def run(script, *args):
    return subprocess.run([sys.executable, str(HERE / script), *args], capture_output=True, text=True)


class CliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            hevy.load_key()
        except SystemExit:
            raise unittest.SkipTest("no HEVY_API_KEY configured")

    def test_summary_has_all_sections(self):
        r = run("summary.py", "--weeks", "8")
        self.assertEqual(r.returncode, 0, r.stderr)
        for heading in ("Body weight", "Recent workouts", "Exercise progress",
                        "Strength vs bodyweight", "Weekly sets by muscle"):
            self.assertIn(heading, r.stdout)

    def test_find_exercise_prints_id_and_title(self):
        r = run("find_exercise.py", "bench", "press", "barbell")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertRegex(r.stdout, r"[0-9A-F]{8}\s+Bench Press \(Barbell\)")

    def test_add_exercise_dry_run_creates_nothing(self):
        r = run("add_exercise.py", "--title", "Zzz Test Exercise", "--type", "weight_reps",
                "--equipment", "barbell", "--muscle", "chest")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("DRY RUN", r.stdout)

    def test_add_exercise_refuses_existing_title(self):
        r = run("add_exercise.py", "--title", "Bench Press (Barbell)", "--type", "weight_reps",
                "--equipment", "barbell", "--muscle", "chest")
        self.assertEqual(r.returncode, 2)
        self.assertIn("already exists", r.stdout + r.stderr)

    def test_add_exercise_rejects_bad_muscle_with_choices(self):
        r = run("add_exercise.py", "--title", "Zzz", "--type", "weight_reps",
                "--equipment", "barbell", "--muscle", "quads")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("quadriceps", r.stdout + r.stderr)

    def _spec(self, title):
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump({"title": "Test Routine", "exercises": [
            {"title": title, "rest": 120, "sets": [{"lbs": 155, "reps": 5}] * 3}]}, f)
        f.close()
        return f.name

    def test_build_routine_dry_run_shows_lbs(self):
        r = run("build_routine.py", self._spec("Bench Press (Barbell)"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("DRY RUN", r.stdout)
        self.assertIn("155", r.stdout)
        self.assertIn("rest=120s", r.stdout)

    def test_build_routine_dry_run_without_rest_says_none(self):
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump({"title": "T", "exercises": [
            {"title": "Bench Press (Barbell)", "sets": [{"lbs": 155, "reps": 5}]}]}, f)
        f.close()
        r = run("build_routine.py", f.name)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("rest=none", r.stdout)

    def test_build_routine_unknown_exercise_fails_with_close_matches(self):
        r = run("build_routine.py", self._spec("Bench Press"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("close matches", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
