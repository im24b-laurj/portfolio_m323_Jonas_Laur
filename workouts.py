import json
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Workout:
    date: date
    exercise: str
    sets: int
    reps: int
    weight: float


def volume(workout):
    """Trainingsvolumen eines Eintrags: Sätze x Wiederholungen x Gewicht."""
    return workout.sets * workout.reps * workout.weight


def exercise_names(workouts):
    return sorted({w.exercise for w in workouts})


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
        return [parse_workout(raw) for raw in json.load(file)]


def save_workouts(path, workouts):
    with open(path, "w", encoding="utf-8") as file:
        json.dump([workout_to_dict(w) for w in workouts], file, indent=2)


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
