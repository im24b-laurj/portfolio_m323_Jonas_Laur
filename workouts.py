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


class Progress(NamedTuple):
    exercise: str
    start_1rm: float
    current_1rm: float
    percent: float | None


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


def estimate_1rm(weight: float, reps: int) -> float:
    """Geschätztes Maximalgewicht für eine Wiederholung (Epley-Formel)."""
    if reps == 1:
        return weight
    return weight * (1 + reps / 30)


def group_by_exercise(workouts: tuple[Workout, ...]) -> dict[str, tuple[Workout, ...]]:
    groups = {}
    for w in workouts:
        groups[w.exercise] = groups.get(w.exercise, ()) + (w,)
    return groups


def first_and_last(entries: tuple[Workout, ...]) -> tuple[Workout, Workout]:
    by_date = sorted(entries, key=lambda w: w.date)
    return by_date[0], by_date[-1]


def progress_percent(start: float, end: float) -> float | None:
    if start == 0:
        return None
    return round((end - start) / start * 100, 1)


def progress_for(exercise: str, entries: tuple[Workout, ...]) -> Progress | None:
    if len(entries) < 2:
        return None
    first, last = first_and_last(entries)
    start = estimate_1rm(first.weight, first.reps)
    current = estimate_1rm(last.weight, last.reps)
    return Progress(exercise, round(start, 1), round(current, 1), progress_percent(start, current))


def exercise_progress(workouts: tuple[Workout, ...]) -> list[Progress]:
    groups = group_by_exercise(workouts)
    results = (progress_for(name, entries) for name, entries in groups.items())
    return sorted((p for p in results if p is not None), key=lambda p: p.exercise)


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


def best_sort_key(item):
    """Schwerste Übung zuerst, bei Gleichstand alphabetisch."""
    exercise, weight = item
    return -weight, exercise


def personal_bests(workouts):
    bests = {}
    for w in workouts:
        if w.exercise not in bests or w.weight > bests[w.exercise]:
            bests[w.exercise] = w.weight
    return sorted(bests.items(), key=best_sort_key)
