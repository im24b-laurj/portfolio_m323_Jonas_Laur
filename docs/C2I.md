# C2I – Lambda und verkettetes Map/Filter/Reduce

**Feature im Projekt:** Monatsstatistik (Seite `/stats`, Funktion `month_stats` in `workouts.py`)

## Kontext und Ziel

Auf der Statistikseite wähle ich einen Monat aus und sehe, an wie vielen Tagen ich trainiert habe und wie gross das Gesamtvolumen war. Ohne Auswahl wird der Monat des neuesten Eintrags genommen. Input sind alle Einträge plus Jahr und Monat, Output ein `MonthStats(total_volume, training_days)`.

## Konzept

Ein Lambda ist eine Funktion ohne Namen, die nur aus einem Ausdruck besteht. Es lohnt sich dort, wo eine kleine Funktion genau einmal gebraucht wird, zum Beispiel als Bedingung für `filter`. Verkettet man `filter`, `map` und `reduce`, fliesst das Ergebnis der einen Funktion direkt in die nächste, ohne Zwischenliste und ohne Schleifenvariable.

## Code-Beispiel

```python
def month_stats(workouts, year, month):
    in_month = tuple(filter(lambda w: (w.date.year, w.date.month) == (year, month), workouts))
    return MonthStats(
        total_volume=reduce(lambda total, v: total + v, map(volume, in_month), 0),
        training_days=len(set(map(lambda w: w.date, in_month))),
    )
```

Die Kette für das Volumen lautet: `filter` (nur Einträge im Monat) → `map(volume, ...)` (jeder Eintrag wird zu einer Zahl) → `reduce` (Zahlen addieren). Für die Trainingstage wird `map` mit einem Lambda verwendet, das nur das Datum herausholt. Das `set` entfernt doppelte Tage, weil ich pro Training meist zwei Übungen eintrage.

Hier kommen drei Lambdas vor. Beim Filter hätte ich eine benannte Funktion schreiben können, aber die Bedingung braucht `year` und `month` aus dem Funktionsaufruf. Ein Lambda an dieser Stelle hat direkten Zugriff darauf und bleibt einzeilig. Für das Volumen nehme ich die benannte Funktion `volume`, weil es sie schon gibt und sie auch beim Sortieren verwendet wird.

## Umsetzung

In der ersten Version (Commit `94948f6`) stand das in der Route als Schleife mit zwei Variablen `total` und `days`, die bei jedem Durchlauf verändert wurden. Für das Zählen der Tage stand dort `if w.date not in days: days.append(w.date)`, also eine Suche in einer Liste. Mit `set` ist das kürzer und schneller. `in_month` habe ich als Tupel gespeichert, weil ich es zweimal brauche. Ein `filter`-Objekt kann man nur einmal durchlaufen, beim zweiten `map` wäre es leer gewesen.

## Test

- `month_stats(WORKOUTS, 2026, 10)` → `(4140, 2)`: drei Einträge im Oktober an zwei verschiedenen Tagen
- `month_stats(WORKOUTS, 2025, 1)` → `(0, 0)`: Monat ohne Einträge
- `/stats?month=abc` → Status 400, weil die Eingabe nicht in Jahr und Monat zerlegt werden kann

## Reflexion

Die Falle mit dem einmal durchlaufbaren `filter`-Objekt ist tückisch, weil kein Fehler kommt. Ohne `tuple()` wäre das Volumen richtig, die Trainingstage aber 0, weil der Iterator beim zweiten `map` schon verbraucht ist. Ich wandle Ergebnisse, die ich mehrfach brauche, deshalb sofort mit `tuple()` um. Bei längeren Ketten würde ich Zwischenschritte benennen, damit die Zeile nicht zu lang wird. Eine Kette mit drei Funktionen ist für mich die Grenze, bei der ich sie noch auf einen Blick verstehe.
