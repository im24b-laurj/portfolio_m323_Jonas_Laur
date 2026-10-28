# D1A – Messung vorher/nachher und Wahl der Datenstruktur

**Feature im Projekt:** Bestleistungen (`personal_bests` in `workouts.py`, Messung in `benchmark.py`)

**Commit:** `17a9159` «Bestleistungen mit dict statt verschachtelter Schleife»

## Kontext und Ziel

`personal_bests` sucht pro Übung das höchste Gewicht. Die erste Version hat zuerst eine Liste aller Übungen gebaut und danach für jede Übung nochmals alle Einträge durchlaufen. Mir ist beim Lesen aufgefallen, dass der Aufwand damit von zwei Dingen abhängt: der Anzahl Einträge und der Anzahl Übungen. Ich wollte messen, ob sich das lohnt zu ändern, statt es nur zu vermuten.

## Die zwei Varianten

Vorher (Liste, verschachtelte Schleife):

```python
def personal_bests_list(workouts):
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
```

Nachher (Dictionary, ein Durchlauf):

```python
def personal_bests(workouts):
    bests = {}
    for w in workouts:
        if w.exercise not in bests or w.weight > bests[w.exercise]:
            bests[w.exercise] = w.weight
    return sorted(bests.items(), key=best_sort_key)
```

## Analyse

Bei n Einträgen und m Übungen macht die alte Version zuerst n Suchen in der Übungsliste (`not in` auf einer Liste geht jedes Element durch, also bis zu m Vergleiche) und danach m × n Vergleiche in der zweiten Schleife. Das ist ungefähr O(n · m). Die neue Version geht einmal durch die Einträge. Nachschlagen und Schreiben im Dictionary geht über einen Hash und dauert unabhängig von der Grösse etwa gleich lang. Das ergibt O(n), dazu kommt das Sortieren der m Resultate mit O(m log m). Weil m viel kleiner als n ist, fällt das kaum ins Gewicht.

## Messung

`benchmark.py` erzeugt zufällige Einträge mit festem Seed, prüft zuerst, dass beide Varianten dieselben Bestwerte liefern (`assert`), und misst dann mit `timeit` den Durchschnitt aus 20 Läufen. Gemessen auf meinem Laptop mit Python 3.12:

| Einträge | Übungen | Liste | Dictionary | Faktor |
|---|---|---|---|---|
| 46 (echte Datenmenge) | 5 | 0.02 ms | 0.01 ms | 2.3× |
| 5000 | 20 | 5.44 ms | 0.71 ms | 7.7× |
| 5000 | 200 | 52.09 ms | 0.96 ms | 54.5× |

Die Messung bestätigt die Analyse. Bei gleicher Anzahl Einträge wird die alte Version mit zehnmal mehr Übungen ungefähr zehnmal langsamer (5.44 → 52.09 ms). Die neue bleibt fast gleich (0.71 → 0.96 ms, der kleine Anstieg kommt vom Sortieren).

## Bewertung und Begründung der Datenstruktur

Ehrlich gesagt ist der Unterschied bei meinen echten Daten bedeutungslos. 0.02 ms merkt kein Mensch. Nur wegen der Geschwindigkeit hätte sich der Umbau nicht gelohnt. Ich habe das Dictionary trotzdem gewählt, aus drei Gründen:

1. Die Datenstruktur passt zur Frage. «Für jede Übung ein Wert» ist genau das, was ein Dictionary abbildet: Schlüssel → Wert. Mit zwei Listen musste ich die Zuordnung selbst herstellen.
2. Der Code ist kürzer (6 statt 12 Zeilen) und hat nur noch eine Schleife.
3. Wenn ich das Log ein Jahr lang führe und neue Übungen dazukommen, wächst m. Die alte Version würde dann spürbar langsamer, die neue nicht.

Als Alternative habe ich überlegt, die Einträge zuerst nach Übung zu sortieren und dann mit `itertools.groupby` zu gruppieren. Das wäre O(n log n) wegen der Sortierung, also schlechter als das Dictionary und nicht einfacher zu lesen. Eine Datenbank mit `SELECT exercise, MAX(weight) ... GROUP BY exercise` wäre bei sehr vielen Daten die beste Lösung, für eine JSON-Datei mit ein paar hundert Einträgen aber übertrieben.

## Test

- Im Benchmark prüft `assert sorted(personal_bests_list(data)) == sorted(personal_bests(data))` für alle drei Datenmengen, dass beide Varianten dieselben Bestwerte liefern.
- `test_personal_bests_sorted_by_weight` und `test_personal_bests_bodyweight` in `tests/test_workouts.py`. Der zweite Test sichert einen Fall ab, den die naheliegende Kurzform falsch machen würde: Mit `w.weight > bests.get(w.exercise, 0)` käme eine Übung mit 0 kg nie ins Dictionary.

## Reflexion

Ich habe gelernt, zuerst zu messen und dann zu urteilen. Ohne die Tabelle hätte ich behauptet, die neue Version sei «viel schneller», was bei meinen Daten nicht stimmt. Die Messung mit mehreren Datengrössen zeigt dafür, wie die Varianten sich verhalten, wenn die Daten wachsen. Beim nächsten Mal würde ich auch den Speicherverbrauch anschauen und den Benchmark mehrmals laufen lassen, weil die Werte je nach Auslastung des Laptops leicht schwanken.
