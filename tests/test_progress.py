import unittest
from datetime import date

from workouts import (Progress, Workout, estimate_1rm, exercise_progress, first_and_last,
                      group_by_exercise, progress_percent)
from tests.test_workouts import BENCH_1, BENCH_2, DEADLIFT, SQUAT, WORKOUTS


class ProgressTest(unittest.TestCase):
    def test_estimate_1rm(self):
        self.assertAlmostEqual(estimate_1rm(60, 8), 76.0)

    def test_estimate_1rm_single_rep(self):
        self.assertEqual(estimate_1rm(100, 1), 100)

    def test_group_by_exercise(self):
        groups = group_by_exercise(WORKOUTS)
        self.assertEqual(groups["Bankdrücken"], (BENCH_1, BENCH_2))
        self.assertEqual(len(groups), 3)

    def test_first_and_last_unsorted_input(self):
        self.assertEqual(first_and_last((BENCH_2, BENCH_1)), (BENCH_1, BENCH_2))

    def test_progress_percent(self):
        self.assertEqual(progress_percent(100, 110), 10.0)

    def test_progress_percent_start_zero(self):
        self.assertIsNone(progress_percent(0, 10))

    def test_exercise_progress(self):
        self.assertEqual(exercise_progress(WORKOUTS),
                         [Progress("Bankdrücken", 76.0, 79.2, 4.2)])

    def test_single_entry_is_skipped(self):
        self.assertEqual(exercise_progress((SQUAT, DEADLIFT)), [])

    def test_empty_input(self):
        self.assertEqual(exercise_progress(()), [])

    def test_bodyweight_exercise(self):
        pullups = (Workout(date(2026, 10, 1), "Klimmzüge", 3, 8, 0),
                   Workout(date(2026, 10, 8), "Klimmzüge", 3, 10, 0))
        self.assertEqual(exercise_progress(pullups), [Progress("Klimmzüge", 0, 0, None)])


if __name__ == "__main__":
    unittest.main()
