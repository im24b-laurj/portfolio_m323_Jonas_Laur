# B1A – Imperative Route deklarativ umgesetzt

**Feature im Projekt:** Startseite mit Filter und Sortierung (Route `/` in `app.py`)

## Kontext und Ziel

Auf der Startseite kann ich die Einträge nach Übung filtern und nach Datum, Gewicht oder Volumen sortieren. Darunter steht das Gesamtvolumen. Input sind die Query-Parameter `exercise` und `sort`, Output die Tabelle und die Summe.

## Konzept

Imperativer Code beschreibt Schritt für Schritt, wie ein Ergebnis entsteht: Liste anlegen, Schleife, Bedingung, anhängen. Deklarativer Code beschreibt, was das Ergebnis ist: «die Einträge dieser Übung, sortiert nach diesem Schlüssel». Wie das intern abläuft, übernehmen `filter`, `sorted` und `reduce`.

## Vorher: imperativ (Commit `cd5f4c6`)

```python
@app.route("/")
def index():
    workouts = load_workouts(app.config["DATA_FILE"])
    exercise = request.args.get("exercise", "")
    sort = request.args.get("sort", "date")

    result = []
    for w in workouts:
        if exercise == "" or w.exercise == exercise:
            result.append(w)

    if sort == "weight":
        result.sort(key=lambda w: w.weight, reverse=True)
    elif sort == "volume":
        result.sort(key=volume, reverse=True)
    else:
        result.sort(key=lambda w: w.date, reverse=True)

    total = 0
    for w in result:
        total += volume(w)
    ...
```

## Nachher: deklarativ (Commit `2a99ba9`)

```python
# workouts.py
SORT_KEYS = {
    "date": lambda w: w.date,
    "weight": lambda w: w.weight,
    "volume": volume,
}

def filter_by_exercise(workouts, exercise):
    if not exercise:
        return tuple(workouts)
    return tuple(filter(lambda w: w.exercise == exercise, workouts))

def sort_workouts(workouts, sort):
    key = SORT_KEYS.get(sort, SORT_KEYS["date"])
    return tuple(sorted(workouts, key=key, reverse=True))

# app.py
result = sort_workouts(filter_by_exercise(workouts, exercise), sort)
...
total_volume=total_volume(result),
```

## Vergleich

Lesbarkeit der Route: Vorher waren es rund 15 Zeilen Logik, nachher eine Zeile. Die Route liest sich jetzt fast wie die Anforderung: filtern, sortieren, summieren. Wer wissen will, *wie* gefiltert wird, schaut in die Funktion.

Erweiterbarkeit: Für eine neue Sortierung musste ich vorher einen weiteren `elif`-Zweig in die Route schreiben. Jetzt ist es ein Eintrag im Dictionary `SORT_KEYS`. Ein ungültiger Wert wie `?sort=xyz` fällt mit `.get(..., SORT_KEYS["date"])` automatisch auf Datum zurück, das war vorher der `else`-Zweig.

Testbarkeit: Die imperative Version konnte ich nur über den Flask-Testclient prüfen und im HTML nach Text suchen. Die deklarativen Funktionen teste ich direkt mit Tupeln (`tests/test_workouts.py`). Das ist schneller und die Fehlermeldungen sind genauer.

Nachteile: Der Code ist jetzt auf zwei Dateien verteilt. Für jemanden, der das Projekt zum ersten Mal sieht, ist die imperative Version vielleicht schneller zu verstehen, weil alles an einem Ort steht. Ausserdem erzeugt jeder Schritt ein neues Tupel, die alte Version hat die Liste an Ort und Stelle sortiert. Bei meinen knapp 50 Einträgen ist das nicht messbar. Lambdas in `SORT_KEYS` sind nur einzeilig sinnvoll, komplexere Schlüssel würde ich als benannte Funktion schreiben, so wie `volume`.

Entscheid: Ich habe die deklarative Variante behalten. Der grösste Vorteil für mich ist die Testbarkeit. Ausserdem brauche ich `total_volume` und `filter_by_exercise` auch an anderen Stellen, in der imperativen Version hätte ich die Schleifen kopieren müssen.

## Test

Gleiches Verhalten vor und nach dem Umbau, geprüft mit denselben Route-Tests:

- `/?exercise=Bankdrücken` → «2940 kg»
- `/?exercise=Rudern` (keine Einträge) → «0 kg»
- `/?sort=weight` → Kreuzheben (100 kg) steht vor Kniebeugen (80 kg)

Zusätzlich neu: `sort_workouts(WORKOUTS, "drop table")` → erster Eintrag ist der neueste (`test_unknown_sort_falls_back_to_date`).

## Reflexion

Schwierig war zu entscheiden, wo die Grenze liegt. Ich hätte auch das Laden der Query-Parameter in eine Funktion packen können, habe es aber gelassen, weil das zu Flask gehört und nicht zur Logik. Beim nächsten Projekt würde ich die Logik von Anfang an in eigene Funktionen schreiben statt in die Route. Dann muss ich nicht umbauen.
