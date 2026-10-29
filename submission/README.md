# Team 14 submission handoff

Official deadline: **30 October 2026, 23:59 Singapore time**.
Proposed review draft cutoff: **29 October at 18:00**; upload target:
**30 October at 20:00**. These internal times are proposals, not teammate promises.

## Upload files

The generated `upload/` directory contains exactly the three required names:

- `14_files.zip`: one top-level `citus_project_team_14/`, including 20
  experiment folders, 44 job folders representing 43 jobs, eight separate local-only implementations,
  source snapshots, audit evidence and SHA-256 checksums.
  Local-only evidence is explicitly separate. Original source and failed runs
  are preserved; included files do not imply a performance result is clean.
- `14_report.pdf`: the complete local LaTeX review draft. Read it before upload;
  the cover uses the planned submission date and is not an upload receipt.
- `14_ai_tool.zip`: recovered local Codex/Claude dialogue PDFs and supplemental
  JSONL tool records. This is a snapshot requiring a completeness check.

`report/main.tex` loads the editable files under `report/sections/`, with A
experiments split under `report/sections/workload-a/`. Names and formatting live
in `metadata.tex` and `report-style.tex`; citations use `references.bib`. Follow
[the peer-review workflow](../CONTRIBUTING.md) and edit the appropriate A/B
section. `14_report_overleaf.zip` contains the same source and images for
Overleaf; it is not one of the three Canvas uploads. Use the
[shared Overleaf project](https://www.overleaf.com/project/6ae2d836f7dbb8dab0442621) for final edits, comparing its
live contents before importing any local ZIP.
Build storage and private AI records are ignored by Git.

The [assignment requirements check](assignment-requirements.md) maps the supplied
Canvas overview to the report and archive. Sections 2-5 now use experiment
subsections, and A baseline/final-design tables show p50, p95 and p99 as well as TPS.

## Confirmed A scope

Hikaru and Kelvin own A. a112 is the confirmed final A design, with the seed-7
c64 warmup caveat retained. a115 remains a faster but repeatedly aborting
follow-up. a10 is separate: an a10+a112 combination has not been benchmarked.
Kelvin's write-path section is incorporated. The compiled 29 October review
draft is **19 pages**; rebuild and check again after final team edits.

The [29 October teammate handoff](../docs/team-handoff-2026-10-29.md) contains a
copyable message and the remaining owners/actions.

## Remaining team review

- [x] A selection confirmed: a112 final, a115 follow-up, a10 separate.
- [ ] Kelvin and Hikaru confirm their individual contribution statements.
- [ ] Dessi and Xincheng confirm B selection and ownership, supplementary
  evidence and correctness wording. B c1 has a matched 20.86x observation;
  higher counts retain failures/aborts. Job 1031186 is separate validation.
- [ ] Everyone confirms their full name, contribution and tools actually used.
- [ ] Complete/review the bibliography against the sources actually consulted.
- [ ] Add any missing earlier cloud/ChatGPT and teammates' AI interaction PDFs.
  The recovered session inventory is in `ai/session-index.json`; it is not a
  claim of all historical or team-wide interactions. Refresh after final edits.
- [ ] Remove review wording and confirm the final PDF is at most 20 pages,
  with minimum 10-point text, all figures readable, and no placeholders.
- [ ] Check the result ZIP inventory against experiments cited in the final
  report; b202–b204 are excluded following Xincheng's removal.
- [ ] Upload each of the three files to its corresponding Canvas assignment,
  verify receipts/downloads, and confirm week-13 Q&A registration.

## Supplementary folder mapping

To satisfy the required `expt_bN` directory format without changing source bytes:

| Original remote folder | Submitted folder |
|---|---|
| `expt_xc_b1` | `expt_b201` |
| `expt_xc_b2`, `expt_b3v_control`, `expt_b3v_cover` | Excluded: owner-retired b202–b204 |

The original names remain in the provenance map and historical logs. These
aliases concern packaging only and do not establish a new experiment or owner.
Xincheng removed b202–b204 as unused in commit `1a5a2f3`; the packaging
rules exclude both their submitted names and original cluster aliases.
b201's copied 918781 belongs to b0. The package identifies these in each
README, the experiment inventory and `job-source-map.json`.
Supplementary b0/b6 results have been moved from `supplementary-results/` into
their respective experiment's `slurm-results/job-N/` in the ZIP; provenance
retains their original paths. The archive README describes every experiment.

## Rebuilding

`scripts/prepare_submission.py` assembles the result ZIP from preserved local
archives and the ignored full remote readback. It refuses to overwrite an
existing staging tree. Preserve manual edits before rebuilding. It checks
collisions, required run/transaction structure, ZIP CRCs and the single root.
Then run `scripts/finalize_submission_layout.py` to move local-only designs into
supporting implementations, check every recorded job's Slurm output/error pair,
apply `scripts/organize_submission.py` and regenerate the final archive/checksums.
This second step is required. It includes the additional correctness/pilot suites,
configured installer, explicit inherited-job labels, job-to-source map and the
documentation templates `package-readme.md` and `reproduction-guide.md`.
`checksums.sha256` records every staged file except the checksum file itself.
The provenance file distinguishes original `source_sha256` from final
`packaged_sha256`; its legacy `sha256` field is an original-source hash.

The prior result and AI ZIPs are retained privately under
`_build/before-organization-20261029/`. The original review remains in
[the audit](non-report-audit-2026-10-29.md); the changes and current outstanding
items were recorded in [the organization follow-up](organization-2026-10-29.md).
The current package is described by [the 30 October reconciliation](reconciliation-2026-10-30.md).

`scripts/prepare_ai_archive.py` uses the bundled Python runtime with ReportLab.
It exports only project sessions, excluding hidden reasoning, system/developer
metadata and automated approval-review sessions; known credentials are redacted.
Canvas upload remains a separate step. Generated upload files and private AI
records exist locally; a GitHub clone does not include them.
