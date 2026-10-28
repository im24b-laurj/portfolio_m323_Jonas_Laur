"""Vergleicht die alte Listen-Version von personal_bests mit der dict-Version."""
import random
import timeit
from datetime import date

from workouts import Workout, personal_bests


def personal_bests_list(workouts):
    # alte Version aus dem ersten Commit
    exercises = []
    for w in workouts:
        if w.exercise not in exercises:
            exercises.append(w.exercise)
    bests = []
    for exercise in exercises:
        best = 0
        for w in workouts:
            if w.exercise == exercise and w.weight > best:
                best = w.weight
        bests.append((exercise, best))
    return bests


def generate(count, exercise_count):
    random.seed(1)
    return tuple(
        Workout(date(2026, 1, 1), f"Übung {random.randrange(exercise_count)}", 3, 8,
                random.randrange(20, 200))
        for _ in range(count)
    )


if __name__ == "__main__":
    for count, exercise_count in [(46, 5), (5_000, 20), (5_000, 200)]:
        data = generate(count, exercise_count)
        assert sorted(personal_bests_list(data)) == sorted(personal_bests(data))
        old = timeit.timeit(lambda: personal_bests_list(data), number=20) / 20
        new = timeit.timeit(lambda: personal_bests(data), number=20) / 20
        print(f"{count:>5} Einträge, {exercise_count:>3} Übungen: "
              f"Liste {old * 1000:7.2f} ms | dict {new * 1000:5.2f} ms | {old / new:5.1f}x")
