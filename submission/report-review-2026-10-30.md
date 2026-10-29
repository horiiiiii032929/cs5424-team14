# Report and requirements review — 30 October 2026

## Scope and current version

The supplied Canvas Project description was reread in full, with Sections 11–12
checked directly for filenames, group submission, report format and evaluation.
One team copy of each required file is sufficient; duplicate individual uploads
are explicitly discouraged. All members attend the week-13 Q&A. The precise
handoff is in `submission-checklist.md`.

The live shared Overleaf project was downloaded through the user's signed-in
Chrome tab. It contained newer member names, contributions, B-design selection,
experiment subsection numbering and A failure analysis. Those edits were retained
in the repository. Before uploading corrections, a second download confirmed
that no teammate changes had arrived since the review snapshot. Only four
specific section files were replaced; no wholesale project import was used.

The final downloaded shared source matches all 27 exported source/assets files
in `submission/report/` byte-for-byte. Both the local build and Overleaf produce
19 pages and the same extracted numeric content. Their text extraction differs
in line breaks, hyphenation and table ordering because of the TeX engines.
The upload PDF is the exact final Overleaf download. Its minimum effective font
size is 10.4608 points; rotated graph labels were checked using the rotated
font dimension rather than character advance. All pages were rendered for
layout inspection; no clipping, unreadable figures or missing references found.

## Evidence and corrections

- `scripts/check_report_numbers.py` checks 344 explicit numerical table cells
  against the packaged CSVs, including A baseline/matched/latency/autocommit/
  diagnostic tables and B baseline/progressive/matched/time-share tables.
  After correction there are no mismatches, and all 30 explicit job references
  resolve inside the result archive. This script does not substitute for prose,
  implementation or visual review.
- Corrected b2/T4's one-client time share from 0.3% to 0.2%: the CSV-derived
  share is approximately 0.24536%, which rounds to 0.2% at one decimal.
- Clarified that the T7-only 5.188 TPS observation is b0 and 334.518 TPS is b201;
  retained their different node allocations and nonstandard workload limitation.
  The contribution statement now uses submitted experiment ID b201.
- Added the seven historical B job IDs so tables can be located without guessing.
  Matched B comparisons retain explicit jobs 1029473/1030000 and xcnf0–4.
- Qualified covering-index discussion: an index-only scan is enabled, not
  guaranteed independent of visibility. Recorded plans contain the index-only
  nodes and zero heap fetches cited in the discussion.
- Stated b6's static-rollup assumption: no backdated orders or mutations of
  historical order amounts in the supplied workload. This follows its actual
  load-time rollup and T1/T5 implementations; no broader workload is claimed.
- Preserved b6 correctness job 1031186, its three invariant checkpoints, two T7
  transfers with conserved total 1,773, zero failed measurement records and four
  retry attempts. Restored the caveat that this job cannot validate prior aborts.
- Verified the new a115 observation directly: 19 client-abort messages, 17 in
  T1 and one each in T2/T9. Softened causal wording to the failure mechanism
  actually observed in these runs rather than an isolated general explanation.
- Verified all 18 plotted TPS points against successful counts / 600 seconds,
  and all six plotted transaction-time shares against CSV-derived values.
  Checked HOT-update ranges, diagnostics, selected gains and failure caveats
  against their preserved data and the previous complete raw-log audit.
- Reviewed the cited PostgreSQL documentation and Citus general design guidance.
  The tested versions remain those recorded in server/config logs. The Citus
  stable documentation resolves to version 13 and is used for general modelling
  principles, not as a claim of the tested server version.

## Result archive completeness correction

The earlier 30 October reconciliation removed b202–b204 following retirement
from active development. On rereading Sections 11 and 11.1, that exclusion was
too broad: all experimental code and output must be submitted, even though the
report may discuss only selected experiments.

b202 has two actual jobs, 993186 and 994341, so it is restored as a top-level,
non-selected supplementary experiment. b203/b204 have no independent benchmark;
their source and inherited b2/job-928583 output are preserved separately under
`supporting_implementations/retired/`. The builder now enforces this distinction.
No experiment code or measured output was altered in this review.

The final archive has **21 experiment folders, 46 top-level job paths and
45 distinct jobs**, eight local-only designs and two retired source variants.
All 5,651 file hashes, 9,847 provenance destinations and 184 runtime-source
hashes verify. All shell/SQL/raw-result bytes in the original 23-folder archive
remain represented, including retired work. Dated earlier audit counts describe
old snapshots; this review supersedes their removal decision.

## Remaining limits

Names, contributions and A/B selections follow the current shared team report.
The report can discuss only a subset of experiments under the brief. Historical
aborts, failed transactions, hardware differences and unavailable runtime hashes
remain limitations of the evidence, not formatting problems that can be erased.
No fresh cluster performance experiment was run.

Team-wide AI completeness still requires teammates' and any missing cloud
records. Canvas upload/receipts and Q&A registration have not been performed or
verified. Generated upload files and private AI records remain local, not in Git.
