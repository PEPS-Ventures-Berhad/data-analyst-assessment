"""Monthly sales delta processing. Reads the raw delta, keeps in-scope rows,
writes the district summary and the run log.

Usage: python pipeline/process_delta.py
"""
import csv
import statistics
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "sales_delta_2026_08.csv"
DISTRICTS = ROOT / "data" / "reference" / "districts.csv"
OUT = ROOT / "output" / "district_summary_2026_08.csv"
LOG = ROOT / "runs" / "2026-08-run-log.md"
REPORTING_MONTH = (2026, 8)


def load_districts():
    with open(DISTRICTS, newline="", encoding="utf-8") as f:
        return {r["district"]: r for r in csv.DictReader(f)}


def parse_date(value):
    try:
        return date.fromisoformat(value)
    except ValueError:
        pass
    try:
        return datetime.strptime(value, "%m/%d/%Y").date()
    except ValueError:
        return None


def process(rows, districts):
    kept = []
    for row in rows:
        if row["district"] not in districts:
            continue
        when = parse_date(row["transaction_date"])
        if when is None or (when.year, when.month) != REPORTING_MONTH:
            continue
        kept.append(row)
    return kept


def summarise(kept):
    psf = defaultdict(list)
    for row in kept:
        psf[row["district"]].append(float(row["price_rm"]) / float(row["built_up_sqft"]))
    return [
        {"district": d, "transaction_count": len(v),
         "median_psf": round(statistics.median(v), 2), "mean_psf": round(statistics.mean(v), 2)}
        for d, v in sorted(psf.items())
    ]


def main():
    with open(RAW, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    kept = process(rows, load_districts())
    summary = summarise(kept)
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)
    LOG.parent.mkdir(exist_ok=True)
    lines = ["# Run log, August 2026 sales delta", "",
             f"- Rows in: {len(rows)}", f"- Rows out: {len(kept)}", "",
             "| District | Count |", "|---|---|"]
    lines += [f"| {s['district']} | {s['transaction_count']} |" for s in summary]
    LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"rows in {len(rows)}, rows out {len(kept)}")


if __name__ == "__main__":
    main()
