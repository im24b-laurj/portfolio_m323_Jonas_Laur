import json
import tempfile
import unittest
from pathlib import Path

from app import app

TEST_DATA = [
    {"date": "2026-10-01", "exercise": "Bankdrücken", "sets": 3, "reps": 8, "weight": 60},
    {"date": "2026-10-01", "exercise": "Kniebeugen", "sets": 3, "reps": 5, "weight": 80},
    {"date": "2026-10-03", "exercise": "Bankdrücken", "sets": 3, "reps": 8, "weight": 62.5},
    {"date": "2026-09-28", "exercise": "Kreuzheben", "sets": 1, "reps": 5, "weight": 100},
]


class AppTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        data_file = Path(self.tmp.name) / "workouts.json"
        data_file.write_text(json.dumps(TEST_DATA), encoding="utf-8")
        app.config["DATA_FILE"] = data_file
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def get_text(self, url):
        return self.client.get(url).get_data(as_text=True)

    def test_total_volume_all(self):
        self.assertIn("4640 kg", self.get_text("/"))

    def test_total_volume_filtered(self):
        self.assertIn("2940 kg", self.get_text("/?exercise=Bankdrücken"))

    def test_filter_unknown_exercise(self):
        self.assertIn("Gesamtvolumen: <strong>0 kg", self.get_text("/?exercise=Rudern"))

    def test_sort_by_weight(self):
        text = self.get_text("/?sort=weight")
        self.assertLess(text.index("Kreuzheben</td>"), text.index("Kniebeugen</td>"))

    def test_stats_october(self):
        text = self.get_text("/stats?month=2026-10")
        self.assertIn("Trainingstage im Monat: <strong>2", text)
        self.assertIn("4140 kg", text)

    def test_stats_defaults_to_latest_month(self):
        self.assertIn("4140 kg", self.get_text("/stats"))

    def test_stats_invalid_month(self):
        self.assertEqual(self.client.get("/stats?month=abc").status_code, 400)

    def test_bests(self):
        text = self.get_text("/bests")
        self.assertIn("<td>Bankdrücken</td><td>62.5 kg</td>", text)
        self.assertIn("<td>Kreuzheben</td><td>100.0 kg</td>", text)

    def test_add_without_csrf_token(self):
        response = self.client.post("/add", data={"date": "2026-10-05", "exercise": "Rudern",
                                                  "sets": 3, "reps": 10, "weight": 40})
        self.assertEqual(response.status_code, 400)

    def test_add_workout(self):
        with self.client.session_transaction() as session:
            session["csrf_token"] = "test"
        self.client.post("/add", data={"csrf_token": "test", "date": "2026-10-05",
                                       "exercise": "Rudern", "sets": 3, "reps": 10, "weight": 40})
        self.assertIn("5840 kg", self.get_text("/"))


if __name__ == "__main__":
    unittest.main()
