import os
import re
import secrets
from datetime import date
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, session, url_for

from workouts import (Workout, add_workout, exercise_names, filter_by_exercise,
                      load_workouts, month_stats, personal_bests, save_workouts,
                      sort_workouts, total_volume)

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

    result = sort_workouts(filter_by_exercise(workouts, exercise), sort)

    return render_template(
        "index.html",
        workouts=result,
        exercises=exercise_names(workouts),
        selected=exercise,
        sort=sort,
        total_volume=total_volume(result),
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
    save_workouts(app.config["DATA_FILE"], add_workout(workouts, workout))
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
        latest = max((w.date for w in workouts), default=date.today())
        year, month_number = latest.year, latest.month

    result = month_stats(workouts, year, month_number)
    return render_template(
        "stats.html",
        month=f"{year}-{month_number:02d}",
        total_volume=result.total_volume,
        training_days=result.training_days,
    )


@app.route("/bests")
def bests():
    workouts = load_workouts(app.config["DATA_FILE"])
    return render_template("bests.html", bests=personal_bests(workouts))


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
