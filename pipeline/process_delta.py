"""Monthly sales delta processing. Reads the raw delta, normalises, guards,
de-duplicates, then writes the district summary and the run log.

Usage: python pipeline/process_delta.py
"""
import csv
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "sales_delta_2026_08.csv"
DISTRICTS = ROOT / "data" / "reference" / "districts.csv"
BASELINE = ROOT / "data" / "reference" / "prism_baseline_counts_2026_08.csv"
OUT = ROOT / "output" / "district_summary_2026_08.csv"
LOG = ROOT / "runs" / "2026-08-run-log.md"
REPORTING_MONTH = (2026, 8)
TOLERANCE = 0.05


def load_districts():
    with open(DISTRICTS, newline="", encoding="utf-8") as f:
        return {r["district"]: r for r in csv.DictReader(f)}


def load_baseline_total():
    with open(BASELINE, newline="", encoding="utf-8") as f:
        return sum(int(r["transaction_count"]) for r in csv.DictReader(f))


def normalise_district(value):
    """The source spells a district two ways: 'Petaling' and 'DAERAH PETALING'."""
    name = " ".join(value.strip().split())
    if name.upper().startswith("DAERAH "):
        name = name[7:]
    return name.title()


def parse_date(value):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


def in_district(row, districts):
    ref = districts[row["district"]]
    return int(ref["postcode_from"]) <= int(row["postcode"]) <= int(ref["postcode_to"])


def dedupe_key(row):
    """One sale is one scheme, one date, one price."""
    return (row["scheme_name"], row["transaction_date"], row["price_rm"])


def process(rows, districts):
    stats = Counter()
    kept, seen = [], set()
    for row in rows:
        row = dict(row)
        row["district"] = normalise_district(row["district"])
        if row["district"] not in districts:
            stats["unknown_district"] += 1
            continue
        when = parse_date(row["transaction_date"])
        if when is None:
            stats["unparseable_date"] += 1
            continue
        row["transaction_date"] = when.isoformat()
        if (when.year, when.month) != REPORTING_MONTH:
            stats["outside_reporting_month"] += 1
            continue
        if not in_district(row, districts):
            stats["postcode_outside_district"] += 1
            continue
        key = dedupe_key(row)
        if key in seen:
            stats["duplicates_removed"] += 1
            continue
        seen.add(key)
        kept.append(row)
    return kept, stats


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
    kept, stats = process(rows, load_districts())
    summary = summarise(kept)
    baseline = load_baseline_total()
    variance = (len(kept) - baseline) / baseline
    verdict = "PASS" if abs(variance) <= TOLERANCE else "FAIL"
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)
    LOG.parent.mkdir(exist_ok=True)
    lines = [
        "# Run log, August 2026 sales delta", "",
        f"- Rows in: {len(rows)}",
        f"- Unknown district: {stats['unknown_district']}",
        f"- Unparseable date: {stats['unparseable_date']}",
        f"- Outside reporting month: {stats['outside_reporting_month']}",
        f"- Postcode outside district (border leakage guard): {stats['postcode_outside_district']}",
        f"- Duplicates removed: {stats['duplicates_removed']}",
        f"- Rows out: {len(kept)}", "",
        f"PRISM baseline {baseline}. Variance {variance:+.1%}, tolerance +/-{TOLERANCE:.0%}: **{verdict}**", "",
        "| District | Count | Median psf | Mean psf |", "|---|---|---|---|",
    ]
    lines += [f"| {s['district']} | {s['transaction_count']} | {s['median_psf']} | {s['mean_psf']} |" for s in summary]
    LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"rows in {len(rows)}, rows out {len(kept)}, variance {variance:+.1%} {verdict}")


if __name__ == "__main__":
    main()
