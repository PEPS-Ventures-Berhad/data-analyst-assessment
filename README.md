# Data Analyst Assessment

PEPS Ventures Berhad. Practical exercise for the Data Analyst role.

## What this is

Our data team processes Malaysian property transaction data every month. Banks and valuation firms rely on the output. Most of the processing is done by scripts and AI agents. Your job, if you join us, is to decide whether what they produced is fit to be served.

This repo is a small copy of that job. Everything in it is **synthetic**. No real transaction, person or property appears in it.

## Ground rules

- **Time box: 3 hours.** Stop at 3 hours even if you are not finished. Tell us what you would do next. We read an honest partial answer better than a padded complete one.
- **Any tool is allowed**: SQL, Python, pandas, DuckDB, Excel, AI assistants. If you used an AI assistant, say where in `submission/NOTES.md`. In the interview you will walk us through your work and extend it live, so only submit what you can defend.
- **Do not change anything under `data/`.** Raw data is read only. Put your own code in `work/` and your answers in `submission/`.
- Python 3.10 or later runs everything here. No packages are needed for the pipeline itself.
- Please do not publish this repo or your answers.

## The data

| File | What it is |
|---|---|
| `data/raw/sales_delta_2026_08.csv` | The August 2026 sales delta as it arrived from the source. |
| `data/reference/districts.csv` | The districts in scope, with the postcode range of each. |
| `data/reference/prism_baseline_counts_2026_08.csv` | The official count of unique August 2026 transactions per district, from the source's own reporting system (PRISM). A property belongs to a district only if it is physically inside it. Treat this file as correct. |

Some words are in Malay, as they are in the real data. `Daerah` means district. `Teres` is a terrace house, `Pangsapuri` an apartment, `Berkembar` a semi-detached house, `Banglo` a bungalow.

## Task 1. Reconcile two counts (about 40 min)

Run the pipeline on `main`:

```
python pipeline/process_delta.py
```

It reports 2,441 rows out. PRISM says 2,973. Explain the difference.

We want every cause, the number of rows behind each cause, and proof that your causes add up to the gap exactly. Write it for a manager who does not read code.

Answer in `submission/01-reconciliation.md`.

## Task 2. Review an automated run (about 60 min)

An AI agent picked up the ticket to fix the pipeline. Its work is on the branch `agent/pr-0007-normalise-and-dedupe`. Its pull request description is `PR-0007.md` on that branch.

```
git checkout agent/pr-0007-normalise-and-dedupe
git diff main
python pipeline/process_delta.py
python -m unittest discover -s tests
```

You are the reviewer. Decide: **approve, hold, or reject.** Give your reasons, the checks you ran, and what you would ask the agent to change, if anything.

Answer in `submission/02-review.md`.

## Task 3. Design a control (about 30 min)

A client wrote in: the August mean price per square foot for Sabak Bernam looks too low against July. They are right, and the figure had already been published.

Find what happened. Then specify the check that would have caught it before publication: what it tests, where in the process it runs, what it does when it fires, and what it costs. You do not have to build it.

Answer in `submission/03-control.md`.

## Task 4. Write the escalation note (about 20 min)

It is the day before the monthly load. Based on what you found in Tasks 1 to 3, write a note of half a page to the Head of Data. Say what you found, what you are sure of, what you are not sure of, what you need, and by when.

Answer in `submission/04-escalation.md`.

## How to submit

Commit your work on a branch named `submission/<your-name>`, zip the whole folder including the `.git` directory, and email it back. We will read your commit history as well as your answers.
