# D1I – Vorher/Nachher aus der Commit-Historie

**Feature im Projekt:** Volumenberechnung auf Startseite und Statistikseite (`app.py`)

**Commits:** `94948f6` (vorher) → `cd5f4c6` (nachher), «Refactoring: Volumenberechnung und Übungsliste in Funktionen ausgelagert»

## Kontext und Ziel

In der ersten Version war die Berechnung des Trainingsvolumens an drei Stellen direkt in die Routen geschrieben: beim Sortieren nach Volumen, bei der Summe auf der Startseite und bei der Monatsstatistik. Dazu kam eine Schleife, die die Liste der Übungen für das Dropdown aufbaute. Das Ziel des Refactorings war, diese Logik an einer Stelle zu haben, ohne dass sich für den Benutzer etwas ändert.

## Vorher und nachher

Auszug aus `git show cd5f4c6 -- app.py`:

```diff
     elif sort == "volume":
-        result.sort(key=lambda w: w.sets * w.reps * w.weight, reverse=True)
+        result.sort(key=volume, reverse=True)
     else:
         result.sort(key=lambda w: w.date, reverse=True)

     total = 0
     for w in result:
-        total += w.sets * w.reps * w.weight
-
-    exercises = []
-    for w in workouts:
-        if w.exercise not in exercises:
-            exercises.append(w.exercise)
-    exercises.sort()
+        total += volume(w)

     return render_template(
         "index.html",
         workouts=result,
-        exercises=exercises,
+        exercises=exercise_names(workouts),
 ...
         if w.date.year == year and w.date.month == month_number:
-            total += w.sets * w.reps * w.weight
+            total += volume(w)
```

Neu in `workouts.py`:

```python
def volume(workout):
    """Trainingsvolumen eines Eintrags: Sätze x Wiederholungen x Gewicht."""
    return workout.sets * workout.reps * workout.weight


def exercise_names(workouts):
    return sorted({w.exercise for w in workouts})
```

## Einordnung

Die Technik heisst Extract Function. Ich habe bewusst nur diesen einen Schritt gemacht und die Schleifen selbst noch stehen lassen. Die Umstellung auf `filter` und `reduce` kam erst im nächsten Commit (`2a99ba9`). So war bei einem fehlschlagenden Test klar, welche Änderung schuld ist. `volume` wird an der Sortierung ohne Klammern übergeben, das funktioniert, weil `sort(key=...)` eine Funktion mit einem Parameter erwartet und `volume` genau so aussieht.

## Gleiches Verhalten per Test belegt

Die Tests in `tests/test_app.py` sind im ersten Commit entstanden und prüfen die fertigen HTML-Seiten über den Flask-Testclient. Sie kennen die interne Struktur nicht, deshalb eignen sie sich gut, um gleiches Verhalten zu belegen. Ich habe sie vor und nach dem Refactoring ohne Änderung laufen lassen:

```
$ git checkout 94948f6 && python -m unittest
Ran 10 tests in 0.124s
OK

$ git checkout cd5f4c6 && python -m unittest
Ran 10 tests in 0.111s
OK
```

Die relevanten Testfälle:

- Alle Einträge → «4640 kg» (Summe mit `volume`)
- Filter Bankdrücken → «2940 kg»
- `/stats?month=2026-10` → «4140 kg» und 2 Trainingstage (dritte Stelle mit `volume`)
- `/?sort=weight` → Kreuzheben vor Kniebeugen

## Reflexion

Schwierig war die Frage, ob `exercise_names` dasselbe Resultat liefert wie die alte Schleife. Die alte Version hat am Schluss mit `exercises.sort()` sortiert, die neue mit `sorted(...)` auf einem Set. Beide geben eine alphabetisch sortierte Liste ohne Duplikate zurück, aber erst der Test hat mir das bestätigt. Ich habe gelernt, dass Tests auf Ebene der Route für Refactorings wertvoll sind, gerade weil sie nichts über die Funktionen wissen. Beim nächsten Mal würde ich für jede Route am Anfang mindestens einen solchen Test schreiben.
