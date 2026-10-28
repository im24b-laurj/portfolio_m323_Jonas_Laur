# C2B – Funktion als Variable, Map, Filter und Reduce einzeln

**Feature im Projekt:** Eintragsliste auf der Startseite (Filter, Sortierung, Summe)

## Konzept

In Python sind Funktionen Objekte. Man kann sie in Variablen oder Dictionaries speichern und an andere Funktionen übergeben, ohne sie aufzurufen (ohne Klammern). `map` wendet eine Funktion auf jedes Element an, `filter` behält nur die Elemente, für die eine Funktion `True` liefert, und `reduce` fasst alle Elemente mit einer Funktion zu einem Wert zusammen.

## Funktion in einer Variable

```python
SORT_KEYS = {
    "date": lambda w: w.date,
    "weight": lambda w: w.weight,
    "volume": volume,
}

def sort_workouts(workouts, sort):
    key = SORT_KEYS.get(sort, SORT_KEYS["date"])
    return tuple(sorted(workouts, key=key, reverse=True))
```

`volume` steht ohne Klammern im Dictionary, gespeichert wird also die Funktion und nicht ihr Resultat. `key` ist danach eine Variable, die eine Funktion enthält, und wird an `sorted` weitergegeben.

## Map, Filter, Reduce

```python
# map: aus jedem Eintrag den Namen der Übung holen
def exercise_names(workouts):
    return sorted(set(map(lambda w: w.exercise, workouts)))

# filter: nur Einträge der gewählten Übung
def filter_by_exercise(workouts, exercise):
    if not exercise:
        return tuple(workouts)
    return tuple(filter(lambda w: w.exercise == exercise, workouts))

# reduce: alle Volumen zu einer Summe
def total_volume(workouts):
    return reduce(lambda total, w: total + volume(w), workouts, 0)
```

`exercise_names` füllt das Dropdown, `filter_by_exercise` und `total_volume` liefern die Tabelle und die Summe darunter.

## Test

- `exercise_names(WORKOUTS)` → `["Bankdrücken", "Kniebeugen", "Kreuzheben"]`
- `filter_by_exercise(WORKOUTS, "Bankdrücken")` → zwei Einträge
- `total_volume(())` → `0` (dank Startwert 0 bei `reduce`)

## Reflexion

Ohne den Startwert `0` wirft `reduce` bei einer leeren Liste einen `TypeError`. Das passiert bei mir jedes Mal, wenn ein Filter keine Treffer hat, deshalb gibt es dafür einen eigenen Test.
