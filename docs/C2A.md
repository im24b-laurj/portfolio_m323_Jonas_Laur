# C2A – Aggregation und benutzerdefinierte Sortierung

**Feature im Projekt:** Bestleistungen (Seite `/bests`, Funktionen `personal_bests` und `best_sort_key` in `workouts.py`)

## Kontext und Ziel

Die Seite «Bestleistungen» zeigt pro Übung das höchste Gewicht, das ich je eingetragen habe. Die Tabelle soll mit der schwersten Übung beginnen. Haben zwei Übungen dasselbe Bestgewicht, kommen sie alphabetisch. Input sind alle Einträge, Output eine sortierte Liste von Paaren `(Übung, Gewicht)`.

## Konzept

Aggregation heisst, viele Datensätze zu wenigen Werten zusammenzufassen, hier pro Gruppe (Übung) ein Maximum. Bei der benutzerdefinierten Sortierung bekommt `sorted` über den Parameter `key` eine Funktion, die für jedes Element einen Vergleichswert liefert. Gibt diese Funktion ein Tupel zurück, vergleicht Python zuerst das erste Element, bei Gleichstand das zweite.

## Code-Beispiel

```python
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
```

Die Aggregation passiert im Dictionary `bests`: Pro Übung bleibt nur der grösste Wert stehen. `best_sort_key` dreht das Gewicht mit einem Minus um, damit gross vor klein kommt, und hängt den Namen als zweites Kriterium an. `reverse=True` ginge hier nicht, weil sonst auch die Namen rückwärts sortiert würden.

## Varianten im Vergleich

**Lambda statt benannter Funktion:** `sorted(bests.items(), key=lambda item: (-item[1], item[0]))` macht dasselbe. Mit `item[1]` und `item[0]` sieht man aber nicht, was Gewicht und was Name ist. Die benannte Funktion entpackt das Paar in `exercise, weight` und hat einen Docstring. Ausserdem kann ich sie einzeln testen. Darum habe ich hier keine Lambda genommen, obwohl ich sonst im Projekt viele verwende.

**Aggregation mit `reduce`:** Ich habe auch eine Variante ohne Schleife ausprobiert:

```python
def personal_bests_reduce(workouts):
    bests = reduce(
        lambda acc, w: {**acc, w.exercise: max(w.weight, acc.get(w.exercise, w.weight))},
        workouts, {})
    return sorted(bests.items(), key=best_sort_key)
```

Das ist «reiner», weil kein Dictionary verändert wird, sondern bei jedem Schritt ein neues entsteht. Dafür wird das Dictionary bei jedem Eintrag komplett kopiert, und die Zeile ist schwer zu lesen. Die Schleife verändert zwar `bests`, aber nur lokal in der Funktion. Von aussen ist `personal_bests` trotzdem eine pure function: gleicher Input, gleicher Output, keine Seiteneffekte. Ich habe die Schleife behalten.

**Mit `itertools.groupby`:** Funktioniert nur, wenn die Daten vorher nach Übung sortiert sind. Das wäre ein zusätzlicher Sortierschritt und eine typische Fehlerquelle, wenn man ihn vergisst.

## Test

- Testdaten → `[("Kreuzheben", 100), ("Kniebeugen", 80), ("Bankdrücken", 62.5)]`
- Rudern und Kniebeugen mit je 80 kg → `[("Kniebeugen", 80), ("Rudern", 80)]`, also alphabetisch bei Gleichstand
- Nur Klimmzüge mit 0 kg → `[("Klimmzüge", 0)]`. Dieser Fall war der Grund für die Bedingung `w.exercise not in bests`. Mit `w.weight > bests.get(w.exercise, 0)` wäre die Übung gar nicht in der Liste aufgetaucht.

## Reflexion

Statt mit dem negativen Gewicht hätte ich auch zweimal sortieren können, zuerst nach Name, dann nach Gewicht absteigend. Das funktioniert, weil Python stabil sortiert, ist aber schwerer nachzuvollziehen. Gelernt habe ich, dass ein Tupel als Schlüssel mehrere Sortierkriterien auf einmal abdeckt. Bei Text-Feldern, die man absteigend will, funktioniert das Minus nicht, dort müsste ich doch zweimal sortieren.
