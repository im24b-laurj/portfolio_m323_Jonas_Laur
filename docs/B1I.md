# B1I – Design-Blatt für die Fortschrittsanzeige

**Feature im Projekt:** Fortschritt pro Übung auf der Seite «Bestleistungen» (`/bests`)

Dieses Blatt habe ich geschrieben, bevor ich das Feature umgesetzt habe (Commit `fdfb75e`). Unten steht, was ich danach anders gemacht habe.

## Ausgangslage

Die Seite «Bestleistungen» zeigte nur das höchste Gewicht pro Übung. Das sagt wenig darüber aus, ob ich stärker geworden bin, weil ich das Gewicht und die Wiederholungen ändere. 60 kg × 8 ist anstrengender als 62.5 kg × 3. Ich wollte deshalb pro Übung vergleichen, wie stark ich im ersten und im letzten Training war.

## Deklarative Anforderungen

Ich habe die Anforderungen als «was» formuliert und nicht als «wie»:

1. Für jede Übung mit mindestens zwei Einträgen gibt es genau eine Zeile.
2. Eine Zeile enthält das geschätzte Maximalgewicht (1RM) des ältesten und des neuesten Eintrags sowie die Veränderung in Prozent.
3. Das 1RM ist Gewicht × (1 + Wiederholungen / 30) (Epley-Formel), bei einer Wiederholung das Gewicht selbst.
4. Liegt das Start-1RM bei 0 (Übung mit Körpergewicht), wird keine Prozentzahl angezeigt.
5. Die Zeilen sind alphabetisch nach Übung sortiert.
6. Die gespeicherten Daten werden nicht verändert.

## Datenfluss

```
JSON-Datei
  → load_workouts            tuple[Workout, ...]
  → group_by_exercise        dict[str, tuple[Workout, ...]]
  → pro Gruppe progress_for  Progress | None
      → first_and_last       (ältester, neuester Eintrag)
      → estimate_1rm         je eine Zahl
      → progress_percent     float | None
  → None wegfiltern, sortieren
  → list[Progress] → Template bests.html
```

## Geplante Operatoren

| Operator | Input → Output | Aufgabe |
|---|---|---|
| `estimate_1rm` | `float, int → float` | Formel aus Anforderung 3 |
| `group_by_exercise` | `tuple → dict` | Einträge nach Übung bündeln |
| `first_and_last` | `tuple → (Workout, Workout)` | nach Datum sortieren, Rand nehmen |
| `progress_percent` | `float, float → float \| None` | Anforderung 4 |
| `progress_for` | `str, tuple → Progress \| None` | eine Zeile bauen, Anforderung 1 |
| `exercise_progress` | `tuple → list` | alles zusammensetzen, Anforderung 5 |

Als Rückgabetyp plante ich ein `NamedTuple` namens `Progress`, damit das Resultat unveränderlich ist (Anforderung 6) und das Template mit `p.exercise` statt `p[0]` arbeiten kann.

## Umsetzung

Die Umsetzung entspricht dem Plan. Eine Sortierung nach der Prozentzahl hätte nahegelegen, geht aber nicht sauber, weil `None` (Anforderung 4) nicht mit Zahlen vergleichbar ist. `sorted` würde dann einen `TypeError` werfen. Darum ist in Anforderung 5 die alphabetische Sortierung festgelegt.

```python
def exercise_progress(workouts: tuple[Workout, ...]) -> list[Progress]:
    groups = group_by_exercise(workouts)
    results = (progress_for(name, entries) for name, entries in groups.items())
    return sorted((p for p in results if p is not None), key=lambda p: p.exercise)
```

## Test

- Bankdrücken 60 kg × 8 (1.10.) und 62.5 kg × 8 (3.10.) → `Progress("Bankdrücken", 76.0, 79.2, 4.2)`
- Nur ein Eintrag Kniebeugen und einer Kreuzheben → leere Liste (Anforderung 1)
- Klimmzüge mit 0 kg → `percent` ist `None` (Anforderung 4)

## Reflexion

Weil die Signaturen schon feststanden, konnte ich die Tests vor dem Code schreiben. Dass `None` beim Sortieren Probleme macht, zeigt sich erst, wenn man die Edge Cases zusammen mit den anderen Anforderungen durchspielt. Beim nächsten Design-Blatt würde ich für jede Anforderung gleich einen Beispiel-Input notieren.
