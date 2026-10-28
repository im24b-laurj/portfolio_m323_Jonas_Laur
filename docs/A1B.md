# A1B – Prozedur und pure function

**Feature im Projekt:** Einträge speichern und Trainingsvolumen berechnen (`workouts.py`)

## Kontext und Ziel

Mein Trainingslog speichert Krafttrainings-Einträge in einer JSON-Datei und berechnet daraus das Volumen (Sätze × Wiederholungen × Gewicht). Für diesen Nachweis stelle ich zwei Funktionen aus demselben Modul nebeneinander: eine, die etwas tut, und eine, die nur etwas ausrechnet.

## Konzept

Eine Prozedur ist eine Folge von Anweisungen, die einen Seiteneffekt hat. Sie schreibt in eine Datei, ändert eine Variable oder gibt etwas aus. Ein Rückgabewert ist nicht ihr Zweck. Eine pure function hängt nur von ihren Parametern ab und verändert nichts ausserhalb. Mit denselben Eingaben liefert sie immer dasselbe Resultat.

## Code-Beispiel

```python
# Prozedur: schreibt in eine Datei, gibt nichts zurück
def save_workouts(path, workouts):
    with open(path, "w", encoding="utf-8") as file:
        json.dump([workout_to_dict(w) for w in workouts], file, indent=2, ensure_ascii=False)


# pure function: rechnet nur mit dem Parameter
def volume(workout):
    """Trainingsvolumen eines Eintrags: Sätze x Wiederholungen x Gewicht."""
    return workout.sets * workout.reps * workout.weight
```

`save_workouts` ist eine Prozedur, weil ihr ganzer Zweck der Seiteneffekt ist: Nach dem Aufruf liegt eine andere Datei auf der Festplatte. Ruft man sie zweimal auf, passiert etwas Zweites. `volume` liest nur Attribute des übergebenen Eintrags und gibt eine Zahl zurück. Sie weiss nichts von Dateien, Flask oder globalen Variablen.

## Test

- `volume(Workout(date(2026, 10, 1), "Bankdrücken", 3, 8, 60))` → `1440` (in `tests/test_workouts.py`, `test_volume`)
- `save_workouts` lässt sich nur indirekt testen: In `tests/test_app.py` (`test_add_workout`) wird über die Route ein Eintrag gespeichert. Danach muss das Gesamtvolumen auf der Startseite von 4640 kg auf 5840 kg steigen. Dafür brauche ich eine temporäre Datei, weil die Funktion sonst meine echten Daten überschreiben würde.

## Reflexion

Beim Testen habe ich gemerkt, wie unterschiedlich viel Aufwand die beiden Arten machen. Für `volume` reicht eine Zeile. Für die Prozedur musste ich in `setUp` ein temporäres Verzeichnis anlegen und den Pfad in der App-Konfiguration umbiegen. Ganz ohne Prozeduren geht es in einer Web-App nicht, irgendwo muss gespeichert werden. Ich versuche deshalb, die Seiteneffekte an wenigen Stellen (Laden, Speichern) zu sammeln und den Rest als pure functions zu schreiben.
