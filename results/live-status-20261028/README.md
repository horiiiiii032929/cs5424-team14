# Live project audit — 28 October 2026

Checked around 21:06–21:12 Singapore time, against SSH, fetched Git refs,
PR #1 and the live shared report. No jobs were submitted or cancelled; no
remote source, database, shared document or GitHub content was changed.

## SSH and repository

- SSH succeeds as `cs14` on `xlogin2`; PostgreSQL client/pgbench report 18.6.
  Saved job logs record Citus 14.1.0. The existing installation and all three
  isolated Hikaru deployments are present. Benchmarks start temporary servers
  under Slurm; this check does not certify a continuously running database.
- Queue empty at the saved check. See [accounting](cluster-status.txt).
- PR #1 remains OPEN, draft, mergeable, with no recorded review decision or
  checks. Main remains `82058e6`; the working branch remains `a9e03bf`.
- Fetch discovered `origin/kelvin/expt_a10-14` at `e1bc3b4`. Desmond's branch
  remains `5fa3815`. The initial local working tree was clean.
- Recomputed hashes for 391 matched-A archive files, 275 a115 archive files,
  and 975 original B archive files: no mismatches (1,641 files total).

## Today's B evidence

The full `supplementary-results/` tree and current b0/b6 source and relevant
Slurm output were copied from `/home/stuproj/cs14/citus_project` into `raw/`.
All 263 files match independent remote SHA-256 checks, with exact file coverage
in [the manifest](import-manifest.json). These hashes verify readback bytes,
not the source used at job execution; no runtime source-hash manifest was found.
The ignored `cluster-readback.tar.gz` is the original transfer archive.

Matched b0/b6 jobs use xcnf0 coordinator/xcnf1–4 workers, scale 1, data/pgbench
seed 42, SERIALIZABLE, B weights 10/10/5/5/10/10/30/10/10, 60-second warmups,
600-second measurements, full logging, and resets after warmup and between
client counts. This supplementary matrix covers 1/4/8/16 clients only.

| Design / job | Clients | TPS | Warmup / measurement exit | Failed records | Retry attempts |
|---|---:|---:|---|---:|---:|
| b0 / 1029473 | 1 | 5.190 | 0 / 0 | 0 | 0 |
| b0 / 1029473 | 4 | 5.477 | 0 / 2 | 31 | 168 |
| b0 / 1029473 | 8 | 5.615 | 0 / 0 | 129 | 569 |
| b0 / 1029473 | 16 | 5.597 | 2 / 0 | 382 | 1,210 |
| b6 / 1030000 | 1 | 108.250 | 0 / 0 | 0 | 0 |
| b6 / 1030000 | 4 | 394.380 | 0 / 0 | 0 | 7 |
| b6 / 1030000 | 8 | 540.890 | 0 / 2 | 0 | 30 |
| b6 / 1030000 | 16 | 554.982 | 0 / 0 | 0 | 52 |
| b6 correctness / 1031186 | 4 | 391.953 | 0 / 0 | 0 | 4 |

For all nine measured cases, independently counted raw success/failure records
and retry attempts, matched summary counts and exits to phase logs, and checked
successful scripts / configured duration against TPS. Details are in
[case-review.json](case-review.json). Aborted observations remain in this table
for diagnosis and are not eligible clean comparisons. Only c1 supplies a
zero-failure matched pair: 108.250 / 5.190 = **20.86×**. b0 c8 completes both
phases but retains 129 final failures; it is not a zero-failure comparison.
All five matched b6 T6 equivalence records compare 1,000 merchants in each
direction with zero differences, including the record after aborted c8.

Correctness job 1031186 is a separate 300-second, four-client measurement.
Its three checkpoints (before T7, after T7 and after c4) each report zero for
negative inventory, order-total mismatch, duplicate inventory ID and duplicate
order-item ID. The controlled forward/reverse T7 test reports conservation
PASS. This is useful additional evidence, not retroactive validation of the
matched performance jobs or proof of all transaction semantics.
Predecessor 1031165 failed before measurement: its validator reported failure
despite four zero-violation rows. The original failed script was not captured
at runtime, so the precise harness cause is not established here. Keep that
failed attempt distinct from the successful successor.

## Shared report readback and remaining risks

The [readable snapshot](shared-report-readback.txt) includes both planning and
Report tabs of the [shared document](https://docs.google.com/document/d/1OnjeyIoiXQpPWMFnOJerrP6eLZtnRzWuPm8XigARjgs/edit).
It contains Kelvin's substantial write-path section and today's matched B
comparison. Earlier local statements that Kelvin's section is still awaited
are therefore stale. Full member names are present on the cover.

Before submission:

1. Confirm final A/B choices and contributions. a112 remains the supported A
   recommendation (matched 16.8–28.2× fresh a0; repeat c64 warmup caveat).
   a115 has no clean full matrix. The write-path section says a10 is "kept",
   whereas the provisional A selection is a112, which retains explicit
   transaction blocks: explain whether "kept" means a separately reported
   result or part of the submitted final design. A combined design has not
   been established by these results.
2. Fill the blank four-person contribution table; replace cover/section
   instructions with actual content and explicitly list Codex/Claude Code as
   used. The A overview has stale "pending Kelvin" and 23 October cutoff text.
3. Fix A write share: the listed weights sum to **75%, not 70%**. Qualify "all
   four completed jobs exited 0" as Slurm status: a10 c32 pgbench exited 2
   (the section later acknowledges it). Clarify the claim that every write
   experiment adds exactly one change to a102: a11 also contains a14's
   VACUUM/CHECKPOINT control, as described later in the report.
4. Update B's "stock, order and global-ID checks are still missing" sentence
   with the scope and separate-run limitation of job 1031186. Preserve all
   matched and historical abort/failure caveats.
5. Turn the reference-topic list into proper citations. Export the **Report
   tab only** and verify the CURRENT PDF is at most 20 pages with fonts at
   least 10 pt. Earlier 16-page checks predate the expanded write section;
   current pagination and fonts were not verified in this audit.
6. Assemble the experiment archive from reviewed sources and outputs: the
   current submission tree contains only a0/b0 Slurm output folders, while
   most A outputs, Kelvin variants and B b1–b6 live in separate evidence trees.
   Include today's supplementary evidence with documented paths. Do not
   blindly zip the existing submission tree and assume completeness.
7. Prepare `14_files.zip`, `14_report.pdf`, and `14_ai_tool.zip` with descriptive
   `14_X.pdf` interaction records. None of these final artifacts was found in
   this repository or the checked cluster project tree. Canvas submission and
   Q&A registration were not checked.

Deadline recorded in the supplied course requirements: **30 October 2026,
23:59 Singapore time**, approximately 51 hours after this check. Packaging
target: 29 October; target upload: 30 October at 20:00. The main remaining risk
is submission assembly and reconciliation, not SSH availability. Preserve
supported results and avoid expanding the experiment scope at this stage.
