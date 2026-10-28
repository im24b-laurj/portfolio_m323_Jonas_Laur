# A1I – Mutation und immutable Variante

**Feature im Projekt:** Neuen Eintrag hinzufügen (Route `/add` in `app.py`, Funktion `add_workout` in `workouts.py`)

## Kontext und Ziel

Über das Formular auf der Startseite erfasse ich ein neues Training. Die Route lädt alle bisherigen Einträge, hängt den neuen an und speichert die Liste wieder. Input ist das Formular, Output die aktualisierte JSON-Datei.

## Konzept

Mutation heisst, dass ein bestehendes Objekt verändert wird. Alle Stellen, die eine Referenz auf dieses Objekt halten, sehen danach den neuen Zustand, auch wenn sie das nicht erwarten. Bei immutable Daten wird nie etwas verändert. Wer etwas «ändern» will, erzeugt ein neues Objekt, das alte bleibt so, wie es war. In Python sind Listen und Dictionaries veränderbar, Tupel, Strings und `frozen` Dataclasses nicht.

## Umsetzung: vorher und nachher

In der ersten Version (Commit `94948f6`) habe ich die geladene Liste direkt verändert:

```python
workouts = load_workouts(app.config["DATA_FILE"])
workouts.append(workout)
save_workouts(app.config["DATA_FILE"], workouts)
```

Im Commit `2a99ba9` habe ich das umgestellt. `load_workouts` gibt jetzt ein Tupel zurück, und das Hinzufügen erzeugt ein neues Tupel:

```python
def add_workout(workouts, workout):
    """Gibt ein neues Tupel zurück, das Original bleibt unverändert."""
    return (*workouts, workout)

# in der Route
workouts = load_workouts(app.config["DATA_FILE"])
save_workouts(app.config["DATA_FILE"], add_workout(workouts, workout))
```

Auch ein einzelner Eintrag ist unveränderlich, weil `Workout` als `@dataclass(frozen=True)` definiert ist. `w.weight = 100` löst eine `FrozenInstanceError` aus.

## Einordnung

In der Route selbst hat die Mutation noch keinen Fehler verursacht, weil die Liste nur lokal lebt. Das Problem wäre aufgetaucht, sobald ich die Daten zwischenspeichere, zum Beispiel in einer globalen Variable als Cache. Dann hätte `append` den Cache für alle Requests verändert. Mit dem Tupel kann das nicht passieren, weil `append` gar nicht existiert.

## Test

- `add_workout(WORKOUTS, DEADLIFT)` → neues Tupel mit 5 Einträgen, `WORKOUTS` hat danach immer noch 4 (`test_add_workout_keeps_original`)
- Formular mit gültigem Token und Rudern 3 × 10 × 40 kg → Gesamtvolumen auf der Startseite steigt von 4640 kg auf 5840 kg (`test_add_workout`)

## Reflexion

Für mich war ungewohnt, dass `(*workouts, workout)` jedes Mal ein komplett neues Tupel baut. Bei ein paar hundert Einträgen spielt das keine Rolle, bei sehr grossen Datenmengen wäre das langsamer als `append`. Da müsste man abwägen oder eine Datenbank nehmen. Gelernt habe ich, dass immutable Daten vor allem Fehler verhindern, die man sonst lange suchen würde. Beim nächsten Projekt würde ich von Anfang an mit Tupeln und `frozen` Dataclasses starten, statt es nachträglich umzubauen.
