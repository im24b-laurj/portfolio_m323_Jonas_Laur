import unittest
from datetime import date

from workouts import (Workout, add_workout, exercise_names, filter_by_exercise,
                      month_stats, personal_bests, sort_workouts, total_volume, volume)

BENCH_1 = Workout(date(2026, 10, 1), "Bankdrücken", 3, 8, 60)
SQUAT = Workout(date(2026, 10, 1), "Kniebeugen", 3, 5, 80)
BENCH_2 = Workout(date(2026, 10, 3), "Bankdrücken", 3, 8, 62.5)
DEADLIFT = Workout(date(2026, 9, 28), "Kreuzheben", 1, 5, 100)
WORKOUTS = (BENCH_1, SQUAT, BENCH_2, DEADLIFT)


class WorkoutsTest(unittest.TestCase):
    def test_volume(self):
        self.assertEqual(volume(BENCH_1), 1440)

    def test_exercise_names_sorted_and_unique(self):
        self.assertEqual(exercise_names(WORKOUTS), ["Bankdrücken", "Kniebeugen", "Kreuzheben"])

    def test_filter_by_exercise(self):
        self.assertEqual(filter_by_exercise(WORKOUTS, "Bankdrücken"), (BENCH_1, BENCH_2))

    def test_filter_empty_means_all(self):
        self.assertEqual(filter_by_exercise(WORKOUTS, ""), WORKOUTS)

    def test_sort_by_weight(self):
        self.assertEqual(sort_workouts(WORKOUTS, "weight")[0], DEADLIFT)

    def test_unknown_sort_falls_back_to_date(self):
        self.assertEqual(sort_workouts(WORKOUTS, "drop table")[0], BENCH_2)

    def test_total_volume_empty(self):
        self.assertEqual(total_volume(()), 0)

    def test_add_workout_keeps_original(self):
        new = add_workout(WORKOUTS, DEADLIFT)
        self.assertEqual(len(new), 5)
        self.assertEqual(len(WORKOUTS), 4)

    def test_month_stats(self):
        self.assertEqual(month_stats(WORKOUTS, 2026, 10), (4140, 2))

    def test_month_stats_without_entries(self):
        self.assertEqual(month_stats(WORKOUTS, 2025, 1), (0, 0))

    def test_personal_bests_sorted_by_weight(self):
        self.assertEqual(personal_bests(WORKOUTS),
                         [("Kreuzheben", 100), ("Kniebeugen", 80), ("Bankdrücken", 62.5)])

    def test_personal_bests_same_weight_alphabetical(self):
        rows = personal_bests((Workout(date(2026, 10, 1), "Rudern", 3, 10, 80), SQUAT))
        self.assertEqual(rows, [("Kniebeugen", 80), ("Rudern", 80)])

    def test_personal_bests_bodyweight(self):
        pullup = Workout(date(2026, 10, 1), "Klimmzüge", 3, 8, 0)
        self.assertEqual(personal_bests((pullup,)), [("Klimmzüge", 0)])


if __name__ == "__main__":
    unittest.main()
