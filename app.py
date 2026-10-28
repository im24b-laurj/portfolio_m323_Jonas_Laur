import os
import re
import secrets
from datetime import date
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, session, url_for

from workouts import Workout, load_workouts, personal_bests, save_workouts

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["DATA_FILE"] = Path(__file__).parent / "data" / "workouts.json"

EXERCISE_PATTERN = re.compile(r"^[A-Za-zÄÖÜäöü \-]{2,40}$")


@app.after_request
def set_security_headers(response):
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return session["csrf_token"]


app.jinja_env.globals["csrf_token"] = csrf_token


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
        result.sort(key=lambda w: w.sets * w.reps * w.weight, reverse=True)
    else:
        result.sort(key=lambda w: w.date, reverse=True)

    total = 0
    for w in result:
        total += w.sets * w.reps * w.weight

    exercises = []
    for w in workouts:
        if w.exercise not in exercises:
            exercises.append(w.exercise)
    exercises.sort()

    return render_template(
        "index.html",
        workouts=result,
        exercises=exercises,
        selected=exercise,
        sort=sort,
        total_volume=total,
        today=date.today().isoformat(),
    )


@app.route("/add", methods=["POST"])
def add():
    token = session.get("csrf_token")
    if not token or not secrets.compare_digest(request.form.get("csrf_token", ""), token):
        abort(400)
    try:
        workout = Workout(
            date=date.fromisoformat(request.form["date"]),
            exercise=request.form["exercise"].strip(),
            sets=int(request.form["sets"]),
            reps=int(request.form["reps"]),
            weight=float(request.form["weight"]),
        )
    except (KeyError, ValueError):
        abort(400)
    if not EXERCISE_PATTERN.match(workout.exercise):
        abort(400)
    if not (1 <= workout.sets <= 20 and 1 <= workout.reps <= 100 and 0 <= workout.weight <= 500):
        abort(400)

    workouts = load_workouts(app.config["DATA_FILE"])
    workouts.append(workout)
    save_workouts(app.config["DATA_FILE"], workouts)
    return redirect(url_for("index"))


@app.route("/stats")
def stats():
    workouts = load_workouts(app.config["DATA_FILE"])
    month = request.args.get("month", "")
    if month:
        try:
            year, month_number = map(int, month.split("-"))
        except ValueError:
            abort(400)
    else:
        latest = max(w.date for w in workouts)
        year, month_number = latest.year, latest.month

    total = 0
    days = []
    for w in workouts:
        if w.date.year == year and w.date.month == month_number:
            total += w.sets * w.reps * w.weight
            if w.date not in days:
                days.append(w.date)

    return render_template(
        "stats.html",
        month=f"{year}-{month_number:02d}",
        total_volume=total,
        training_days=len(days),
    )


@app.route("/bests")
def bests():
    workouts = load_workouts(app.config["DATA_FILE"])
    return render_template("bests.html", bests=personal_bests(workouts))


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
