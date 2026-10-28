# B1B – Elemente des Functional Design im Projekt

**Feature im Projekt:** Datenmodell und Startseite (`workouts.py`, `app.py`)

## Konzept

Functional Design baut ein Programm aus drei Elementen auf: immutable data types (Daten, die sich nach dem Erstellen nicht mehr ändern), constructors (Funktionen, die aus Rohdaten gültige Werte erzeugen) und composable operators (kleine Funktionen, die man zu grösseren Abläufen zusammenstecken kann, weil der Output der einen zum Input der nächsten passt).

## Elemente mit Fundort

| Element | Im Projekt | Fundort |
|---|---|---|
| immutable data type | `Workout` als `@dataclass(frozen=True)` | `workouts.py:9` |
| immutable data type | `MonthStats` und `Progress` als `NamedTuple` | `workouts.py:17`, `workouts.py:22` |
| immutable data type | Sammlungen als Tupel (`load_workouts`) | `workouts.py:133` |
| constructor | `parse_workout` baut aus einem JSON-Dict einen `Workout` | `workouts.py:113` |
| composable operators | `filter_by_exercise`, `sort_workouts`, `total_volume` | `workouts.py:45`, `:51`, `:56` |
| Komposition | `sort_workouts(filter_by_exercise(workouts, exercise), sort)` | `app.py:43` |

## Code-Beispiel

```python
@dataclass(frozen=True)
class Workout:
    date: date
    exercise: str
    sets: int
    reps: int
    weight: float


def parse_workout(raw):
    return Workout(
        date=date.fromisoformat(raw["date"]),
        exercise=raw["exercise"],
        sets=int(raw["sets"]),
        reps=int(raw["reps"]),
        weight=float(raw["weight"]),
    )

# app.py, Route index
result = sort_workouts(filter_by_exercise(workouts, exercise), sort)
```

Der Konstruktor `parse_workout` wandelt Strings aus der Datei in die richtigen Typen um, damit später niemand mehr mit `"2026-10-01"` rechnen muss. Die Operatoren nehmen alle ein Tupel von `Workout` entgegen, darum lassen sie sich in der Route verschachteln.

## Test

- `filter_by_exercise(WORKOUTS, "Bankdrücken")` → Tupel mit den zwei Bankdrücken-Einträgen
- `w.weight = 100` auf einem `Workout` → `FrozenInstanceError`

## Reflexion

Bei «Konstruktor» denkt man in Python zuerst an `__init__`. Im Sinn von Functional Design ist aber auch `parse_workout` ein Konstruktor, weil es aus unsicheren Rohdaten einen gültigen, unveränderlichen Wert macht.
