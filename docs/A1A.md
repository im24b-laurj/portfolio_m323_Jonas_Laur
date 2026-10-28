# A1A – Dieselbe Aufgabe in OO, prozedural und funktional

**Feature im Projekt:** Gesamtvolumen der angezeigten Einträge (Startseite `/`)

## Aufgabe

Auf der Startseite steht unter der Tabelle das Gesamtvolumen aller angezeigten Einträge. Input ist eine Sammlung von `Workout`-Objekten, Output eine Zahl in kg. Ich habe diese Aufgabe in drei Paradigmen umgesetzt und danach entschieden, welche Variante im Projekt bleibt.

## Variante 1: prozedural

So stand es in der ersten Version direkt in der Route (Commit `94948f6`):

```python
total = 0
for w in result:
    total += w.sets * w.reps * w.weight
```

Eine Variable wird angelegt und in einer Schleife Schritt für Schritt verändert. Das Programm beschreibt genau, *wie* der Computer rechnen soll.

## Variante 2: objektorientiert

Diese Variante habe ich zum Vergleich geschrieben, sie ist nicht im Projekt geblieben:

```python
class WorkoutLog:
    def __init__(self, workouts):
        self._workouts = list(workouts)

    def add(self, workout):
        self._workouts.append(workout)

    def total_volume(self):
        return sum(w.sets * w.reps * w.weight for w in self._workouts)
```

Daten und Verhalten liegen zusammen in einem Objekt. Der Aufrufer schreibt `log.total_volume()` und muss nicht wissen, wie die Einträge intern gespeichert sind.

## Variante 3: funktional (aktuelle Version)

```python
def volume(workout):
    return workout.sets * workout.reps * workout.weight


def total_volume(workouts):
    return reduce(lambda total, w: total + volume(w), workouts, 0)
```

Es gibt keine veränderte Variable. `reduce` faltet die Sammlung zu einem Wert zusammen, `volume` ist eine eigene pure function.

## Vergleich und Bewertung

Lesbarkeit: Die prozedurale Schleife versteht jeder sofort, auch ohne Vorwissen. `reduce` mit Lambda ist für Anfänger schwerer zu lesen. Ehrlich gesagt wäre `sum(map(volume, workouts))` noch lesbarer als `reduce`. Ich habe `reduce` bewusst gewählt, weil ich es für dieses Modul anwenden wollte.

Wiederverwendung: In der prozeduralen Version stand die Formel `sets * reps * weight` dreimal in `app.py` (Sortierung, Summe, Statistik). Das war der Hauptgrund für den Umbau. Funktional gibt es die Formel genau einmal in `volume`. Die OO-Variante hätte das auch gelöst, aber nur innerhalb der Klasse.

Testbarkeit: `total_volume` bekommt ein Tupel und gibt eine Zahl zurück. Der Test ist eine Zeile, ohne Flask und ohne Datei. Die prozedurale Version konnte ich nur über die ganze Route testen. Die OO-Variante ist auch gut testbar, braucht aber zuerst ein Objekt.

Zustand: Die Klasse `WorkoutLog` hat eine Methode `add`, welche die interne Liste verändert. Das passt nicht zu meinem Entscheid, alle Einträge immutable zu halten (siehe A1I). In einer Flask-App wird pro Request neu geladen, ein langlebiges Objekt mit Zustand bringt dort wenig.

Entscheid: Ich habe die funktionale Variante genommen. Die Klasse wäre sinnvoll, wenn mehrere Methoden auf denselben Zustand angewiesen wären, etwa bei einer Datenbankverbindung. Für reine Berechnungen auf Daten sind kleine Funktionen in meinem Projekt einfacher. Die prozedurale Schleife ist nicht falsch, aber sie gehört nicht in die Route.

## Test

- `total_volume(WORKOUTS)` mit den vier Testeinträgen → `4640`
- `total_volume(())` → `0` (Edge Case leere Liste, `test_total_volume_empty`)
- Die Route-Tests aus `tests/test_app.py` (z. B. «2940 kg» bei Filter Bankdrücken) liefen mit der prozeduralen und mit der funktionalen Version gleich durch.

## Reflexion

Am meisten gebracht hat mir, die OO-Variante wirklich hinzuschreiben, statt nur darüber nachzudenken. Auf dem Papier sieht man sofort, dass `add` meine Immutability-Regel bricht. Ich würde nicht sagen, dass ein Paradigma immer besser ist. Für Datenauswertung wie in meinem Trainingslog passt der funktionale Stil am besten, für Dinge mit Zustand würde ich wieder Klassen verwenden.
