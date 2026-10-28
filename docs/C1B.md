# C1B – Algorithmus mit Beispieldurchlauf

**Feature im Projekt:** Fortschritt pro Übung (Seite `/bests`, Funktion `exercise_progress` in `workouts.py`)

## Kontext und Ziel

Der Algorithmus berechnet für jede Übung, wie viel stärker ich seit dem ersten Training geworden bin. Weil ich Gewicht und Wiederholungen variiere, vergleiche ich nicht das Gewicht, sondern das geschätzte Maximalgewicht für eine Wiederholung (1RM).

## Ablauf in Worten

1. Alle Einträge nach Übung gruppieren.
2. Übungen mit nur einem Eintrag überspringen, dort gibt es keinen Vergleich.
3. In jeder Gruppe den ältesten und den neuesten Eintrag suchen.
4. Für beide das 1RM schätzen: Gewicht × (1 + Wiederholungen / 30).
5. Die Veränderung in Prozent berechnen: (neu − alt) / alt × 100, auf eine Kommastelle gerundet.
6. Die Resultate alphabetisch sortieren.

## Code-Beispiel

```python
def estimate_1rm(weight: float, reps: int) -> float:
    if reps == 1:
        return weight
    return weight * (1 + reps / 30)


def exercise_progress(workouts: tuple[Workout, ...]) -> list[Progress]:
    groups = group_by_exercise(workouts)
    results = (progress_for(name, entries) for name, entries in groups.items())
    return sorted((p for p in results if p is not None), key=lambda p: p.exercise)
```

## Beispieldurchlauf

Input (vier Einträge aus den Tests):

| Datum | Übung | Sätze × Wdh. | Gewicht |
|---|---|---|---|
| 01.10.2026 | Bankdrücken | 3 × 8 | 60 kg |
| 01.10.2026 | Kniebeugen | 3 × 5 | 80 kg |
| 03.10.2026 | Bankdrücken | 3 × 8 | 62.5 kg |
| 28.09.2026 | Kreuzheben | 1 × 5 | 100 kg |

Schritt 1 ergibt drei Gruppen. Schritt 2 wirft Kniebeugen und Kreuzheben raus, weil sie nur einen Eintrag haben. Bei Bankdrücken ist der älteste Eintrag vom 1.10., der neueste vom 3.10. Schritt 4: 60 × (1 + 8/30) = 76.0 kg und 62.5 × (1 + 8/30) = 79.17 kg. Schritt 5: (79.17 − 76) / 76 × 100 = 4.2 %.

Output: `[Progress("Bankdrücken", 76.0, 79.2, 4.2)]`

Das ist genau der Wert, den `test_exercise_progress` erwartet.

## Reflexion

Beim Durchrechnen von Hand liegt es nahe, mit dem gerundeten Wert 79.2 weiterzurechnen. Das ergibt 4.21 %, hier zufällig auch 4.2. Im Code runde ich erst am Schluss, damit sich Rundungsfehler nicht summieren.
