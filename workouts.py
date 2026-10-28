import json
from dataclasses import dataclass
from datetime import date
from functools import reduce
from typing import NamedTuple


@dataclass(frozen=True)
class Workout:
    date: date
    exercise: str
    sets: int
    reps: int
    weight: float


class MonthStats(NamedTuple):
    total_volume: float
    training_days: int


def volume(workout):
    """Trainingsvolumen eines Eintrags: Sätze x Wiederholungen x Gewicht."""
    return workout.sets * workout.reps * workout.weight


SORT_KEYS = {
    "date": lambda w: w.date,
    "weight": lambda w: w.weight,
    "volume": volume,
}


def exercise_names(workouts):
    return sorted(set(map(lambda w: w.exercise, workouts)))


def filter_by_exercise(workouts, exercise):
    if not exercise:
        return tuple(workouts)
    return tuple(filter(lambda w: w.exercise == exercise, workouts))


def sort_workouts(workouts, sort):
    key = SORT_KEYS.get(sort, SORT_KEYS["date"])
    return tuple(sorted(workouts, key=key, reverse=True))


def total_volume(workouts):
    return reduce(lambda total, w: total + volume(w), workouts, 0)


def add_workout(workouts, workout):
    """Gibt ein neues Tupel zurück, das Original bleibt unverändert."""
    return (*workouts, workout)


def month_stats(workouts, year, month):
    in_month = tuple(filter(lambda w: (w.date.year, w.date.month) == (year, month), workouts))
    return MonthStats(
        total_volume=reduce(lambda total, v: total + v, map(volume, in_month), 0),
        training_days=len(set(map(lambda w: w.date, in_month))),
    )


def parse_workout(raw):
    return Workout(
        date=date.fromisoformat(raw["date"]),
        exercise=raw["exercise"],
        sets=int(raw["sets"]),
        reps=int(raw["reps"]),
        weight=float(raw["weight"]),
    )


def workout_to_dict(workout):
    return {
        "date": workout.date.isoformat(),
        "exercise": workout.exercise,
        "sets": workout.sets,
        "reps": workout.reps,
        "weight": workout.weight,
    }


def load_workouts(path):
    with open(path, encoding="utf-8") as file:
        return tuple(parse_workout(raw) for raw in json.load(file))


def save_workouts(path, workouts):
    with open(path, "w", encoding="utf-8") as file:
        json.dump([workout_to_dict(w) for w in workouts], file, indent=2, ensure_ascii=False)


def personal_bests(workouts):
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
