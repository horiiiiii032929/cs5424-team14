# a114 correctness — 19 October 2026

Local Docker correctness suite (`scripts/check_correctness.py`), small fixture.

- **expt_a114: 42/42 checks passed.** The 29 a112 checks, plus: exact daily summary
  (stripes summed) before and after; T6 exact vs the unsummarized query for 0, 1,
  30 and 365 days before and after; a114's actual READ ONLY T6 top-20 compared with
  the original query in one statement; orders spread over more than one stripe;
  `verify_summary.sql` (striped validator used by run.sh).
- **expt_a104: 37/37 checks passed**, rerun to confirm the summary checks now
  group stripes without changing a104's result.

Command: `python3 scripts/check_correctness.py --output results/correctness-summary-20261019
--experiments expt_a114 expt_a104` (log: `run.log`). Source hashes per experiment
are in `*/code-sha256.json`.
