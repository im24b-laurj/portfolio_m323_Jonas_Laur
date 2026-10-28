# D1B – Refactoring-Techniken und Performance-Massnahmen

**Feature im Projekt:** ganzes Projekt, siehe Commit-Historie

## Drei Refactoring-Techniken

**1. Extract Function** (Commit `cd5f4c6`): Die Formel `w.sets * w.reps * w.weight` stand dreimal in `app.py`. Ich habe sie in die Funktion `volume` ausgelagert. Zweck: Eine Änderung an der Formel muss nur noch an einer Stelle gemacht werden.

```python
def volume(workout):
    return workout.sets * workout.reps * workout.weight
```

**2. Replace Loop with Pipeline** (Commit `2a99ba9`): Die Schleifen zum Filtern und Summieren in der Route `index` habe ich durch `filter` und `reduce` ersetzt. Zweck: Die Route zeigt nur noch, *was* passiert, und die einzelnen Schritte sind testbar.

```python
result = sort_workouts(filter_by_exercise(workouts, exercise), sort)
```

**3. Replace Conditional with Lookup** (Commit `2a99ba9`): Die `if/elif/else`-Kette für die Sortierung wurde zum Dictionary `SORT_KEYS`. Zweck: Neue Sortierungen ohne neuen Zweig, und unbekannte Werte fallen automatisch auf das Datum zurück.

## Zwei Performance-Massnahmen

**1. Dictionary statt verschachtelter Schleife** (Commit `17a9159`): `personal_bests` ging früher für jede Übung einmal durch alle Einträge. Jetzt reicht ein Durchlauf mit einem Dictionary. Zweck: Laufzeit wächst nur noch mit der Anzahl Einträge, nicht mit Einträgen × Übungen. Messung siehe D1A.

**2. Set statt Liste für eindeutige Werte**: In `exercise_names` und bei den Trainingstagen in `month_stats` hiess es früher `if x not in liste: liste.append(x)`. Jetzt nehme ich `set(...)`. Zweck: Die Prüfung «schon vorhanden?» ist bei einem Set ungefähr gleich schnell, egal wie viele Elemente drin sind. Bei einer Liste wird jedes Mal von vorne gesucht.

## Test

Nach jedem Commit habe ich `python -m unittest` laufen lassen. Die zehn Route-Tests aus dem ersten Commit liefen bei allen Refactorings ohne Änderung durch.

## Reflexion

Bei meinen knapp 50 Einträgen merkt man die Performance-Massnahmen nicht. Ich habe sie trotzdem gemacht, weil der neue Code auch kürzer ist.
