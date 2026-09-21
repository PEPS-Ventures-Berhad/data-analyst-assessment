import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
import process_delta as p  # noqa: E402


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(p.RAW, newline="", encoding="utf-8") as f:
            cls.rows = list(csv.DictReader(f))
        cls.districts = p.load_districts()
        cls.kept, cls.stats = p.process(cls.rows, cls.districts)

    def test_every_kept_row_has_a_known_district(self):
        self.assertTrue(all(r["district"] in self.districts for r in self.kept))

    def test_no_row_is_lost_to_district_spelling(self):
        self.assertEqual(self.stats["unknown_district"], 0)

    def test_both_date_formats_parse(self):
        self.assertEqual(p.parse_date("2026-08-17").isoformat(), "2026-08-17")
        self.assertEqual(p.parse_date("17/08/2026").isoformat(), "2026-08-17")
        self.assertEqual(p.parse_date("03/08/2026").isoformat(), "2026-08-03")
        self.assertEqual(self.stats["unparseable_date"], 0)

    def test_every_kept_row_is_in_the_reporting_month(self):
        self.assertTrue(all(r["transaction_date"].startswith("2026-08") for r in self.kept))

    def test_border_leakage_is_excluded(self):
        self.assertTrue(all(p.in_district(r, self.districts) for r in self.kept))

    def test_no_duplicates_remain(self):
        keys = [p.dedupe_key(r) for r in self.kept]
        self.assertEqual(len(keys), len(set(keys)))

    def test_count_is_within_tolerance_of_prism(self):
        baseline = p.load_baseline_total()
        self.assertLessEqual(abs(len(self.kept) - baseline) / baseline, p.TOLERANCE)


if __name__ == "__main__":
    unittest.main()
