# Trainingslog (M323 Portfolio)

Kleine Flask-Applikation, mit der ich mein Krafttraining erfasse und auswerte. Sie ist das Praxisprojekt für die LB02 im Modul 323 (Funktional programmieren).

Funktionen:

- Einträge anzeigen, nach Übung filtern und nach Datum, Gewicht oder Volumen sortieren
- neuen Eintrag über ein Formular speichern
- Monatsstatistik mit Trainingstagen und Gesamtvolumen
- Bestleistungen pro Übung und Fortschritt über das geschätzte 1RM

Die Daten liegen in `data/workouts.json`. Die Logik steht in `workouts.py`, die Routen in `app.py`.

## Starten

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask --app app run
```

Danach läuft die App auf http://127.0.0.1:5000.

## Tests und Messung

```bash
python -m unittest
python benchmark.py
```

## Portfolio

Die Lernnachweise zu den 15 Kompetenzfeldern liegen im Ordner `docs/`, eine Datei pro Feld (z. B. `docs/C2I.md`).
