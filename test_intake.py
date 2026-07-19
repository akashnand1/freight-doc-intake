import unittest

from intake import normalize
from extract import extract
from triage import triage
from fixtures import MESSAGES


def run(msg_id):
    raw = next(m for m in MESSAGES if m["id"] == msg_id)
    return triage(extract(normalize(raw)))


class TestIntake(unittest.TestCase):
    def test_unknown_channel_raises(self):
        with self.assertRaises(ValueError):
            normalize({"id": "X", "channel": "fax", "body": "hello"})

    def test_voice_confidence_below_text(self):
        v = normalize({"id": "V", "channel": "voice", "body": "x"})
        t = normalize({"id": "T", "channel": "text", "body": "x"})
        self.assertLess(v["base_confidence"], t["base_confidence"])


class TestExtraction(unittest.TestCase):
    def test_two_places_give_origin_and_destination_in_order(self):
        msg = normalize({"id": "X", "channel": "text",
                         "body": "2 trucks Jebel Ali to Riyadh 22/07 cement"})
        ext = extract(msg)
        self.assertEqual(ext["origin"][0], "Jebel Ali")
        self.assertEqual(ext["destination"][0], "Riyadh")

    def test_single_place_is_low_confidence(self):
        msg = normalize({"id": "X", "channel": "text", "body": "truck to Riyadh please"})
        self.assertLess(extract(msg)["destination"][1], 0.8)

    def test_weekday_is_never_a_confident_date(self):
        msg = normalize({"id": "X", "channel": "text",
                         "body": "3 flatbed Dubai to Muscat sunday steel"})
        self.assertLess(extract(msg)["pickup_date"][1], 0.8)


class TestTriage(unittest.TestCase):
    def test_clean_order_auto_books(self):
        self.assertEqual(run("MSG-01")["decision"], "AUTO_BOOK")

    def test_vague_date_goes_to_review_and_names_the_field(self):
        d = run("MSG-02")
        self.assertEqual(d["decision"], "REVIEW")
        self.assertIn("pickup_date", d["confirm"])

    def test_non_orders_are_rejected(self):
        self.assertEqual(run("MSG-05")["decision"], "REJECT")
        self.assertEqual(run("MSG-06")["decision"], "REJECT")

    def test_never_auto_books_on_missing_critical_field(self):
        d = run("MSG-04")
        self.assertNotEqual(d["decision"], "AUTO_BOOK")


if __name__ == "__main__":
    unittest.main()
