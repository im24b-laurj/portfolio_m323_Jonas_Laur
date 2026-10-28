# C1A – Komposition zu einem Ablauf mit Testfällen

**Feature im Projekt:** Fortschritt pro Übung (`progress_for` und `exercise_progress` in `workouts.py`)

## Kontext und Ziel

Die Teilfunktionen aus C1I müssen zu einem Ablauf zusammengesetzt werden, den die Route `/bests` mit einem Aufruf nutzen kann. Input ist das Tupel aller Einträge, Output eine Liste von `Progress`-Werten für das Template.

## Komposition im Projekt

```python
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

# app.py
return render_template("bests.html", bests=personal_bests(workouts),
                       progress=exercise_progress(workouts))
```

Die Komposition hat zwei Ebenen. `progress_for` setzt die Teilfunktionen für *eine* Übung zusammen. `exercise_progress` wendet `progress_for` auf alle Gruppen an, filtert die leeren Resultate und sortiert. Jede Ebene gibt einen Wert zurück, der direkt in die nächste passt.

## Vergleich von zwei Varianten

Bevor ich mich entschieden habe, habe ich eine zweite Variante geschrieben, die alles mit `map` und `filter` verkettet:

```python
def exercise_progress(workouts):
    return sorted(
        filter(None, map(lambda item: progress_for(*item), group_by_exercise(workouts).items())),
        key=lambda p: p.exercise,
    )
```

Beide Varianten liefern dasselbe Resultat, die Tests laufen mit beiden durch. Die zweite ist kürzer, aber ich musste beim Lesen von innen nach aussen denken: zuerst gruppieren, dann `map`, dann `filter`, dann `sorted`. Das `*item` zum Entpacken des Tupels ist ausserdem nicht auf den ersten Blick klar. `filter(None, ...)` wirft alles raus, was «falsy» ist. Das funktioniert hier, weil ein `Progress` nie leer ist, wäre aber eine Falle, wenn das Resultat einmal eine Zahl wäre, die 0 sein kann.

In der gewählten Variante steht jeder Schritt auf einer eigenen Zeile und hat einen Namen (`groups`, `results`). Die Generator-Ausdrücke sind genauso lazy wie `map` und `filter`, ich verliere also keine Effizienz. `is not None` sagt genau, was ich meine. Darum habe ich mich für die Variante mit Zwischenvariablen entschieden.

Eine dritte Möglichkeit wäre eine einzige Funktion ohne Teilfunktionen gewesen. Die habe ich verworfen, weil ich dann die Edge Cases nicht mehr einzeln testen könnte (siehe C1I).

## Testfälle inklusive Edge Cases

Alle in `tests/test_progress.py`:

| Test | Input | Erwartet |
|---|---|---|
| Normalfall | 4 Testeinträge (2 × Bankdrücken, je 1 × Kniebeugen, Kreuzheben) | `[Progress("Bankdrücken", 76.0, 79.2, 4.2)]` |
| Edge Case: nur ein Eintrag pro Übung | Kniebeugen, Kreuzheben | `[]` |
| Edge Case: leere Eingabe | `()` | `[]` |
| Edge Case: Körpergewicht | 2 × Klimmzüge mit 0 kg | `[Progress("Klimmzüge", 0, 0, None)]` |

Ohne die Prüfung `start == 0` in `progress_percent` würde der letzte Fall mit einem `ZeroDivisionError` abstürzen und die ganze Seite einen Fehler 500 zeigen. Im Template wird `None` als «–» angezeigt.

Zusätzlich habe ich die Seite im Browser mit den echten Daten (46 Einträge, September und Oktober 2026) kontrolliert. Bankdrücken zeigt dort 76.0 kg → 88.7 kg, also +16.7 %, was zu meiner Steigerung von 60 auf 70 kg passt.

## Reflexion

Gelernt habe ich, dass kürzer nicht automatisch besser ist. Die verkettete Variante hat sich zuerst «funktionaler» angefühlt, war aber schlechter zu lesen. Wichtig war mir auch, dass die Route nichts vom Algorithmus wissen muss: Sie ruft eine Funktion auf und gibt das Resultat ans Template. Wenn ich die Formel ändern will, zum Beispiel auf Brzycki statt Epley, muss ich nur `estimate_1rm` anpassen und die Tests aktualisieren. Beim nächsten Mal würde ich die Edge Cases noch konsequenter vor dem Code als Tests schreiben, weil man Fälle wie die Division durch 0 sonst leicht übersieht.
