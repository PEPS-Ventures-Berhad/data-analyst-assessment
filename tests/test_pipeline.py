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
            rows = list(csv.DictReader(f))
        cls.districts = p.load_districts()
        cls.kept = p.process(rows, cls.districts)

    def test_every_kept_row_has_a_known_district(self):
        self.assertTrue(all(r["district"] in self.districts for r in self.kept))

    def test_every_kept_row_is_in_the_reporting_month(self):
        for r in self.kept:
            d = p.parse_date(r["transaction_date"])
            self.assertEqual((d.year, d.month), p.REPORTING_MONTH)


if __name__ == "__main__":
    unittest.main()
