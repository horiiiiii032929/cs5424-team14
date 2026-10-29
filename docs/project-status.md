# Project status — 29 October 2026

The local report cleanup is ready for team review on
`codex/maintainable-latex-report`. The current compiled PDF is **19 pages**;
body text is 11 pt and table/caption/reference text is 10.5 pt. Report source is
modular, with shared metadata/style and a bibliography. The generated Overleaf
ZIP is the import package; `submission/report/` is the maintained local source.

Hikaru supplied the [shared Overleaf project](https://www.overleaf.com/project/6ae2d836f7dbb8dab0442621) on
29 October. Use it for joint final edits and export reviewed source back to Git.
Its live contents/access were not checked or changed in this cleanup.
[PR #1](https://github.com/horiiiiii032929/cs5424-team14/pull/1) is now merged
into `main`; new teammate PRs should target `main`. [PR #4](https://github.com/horiiiiii032929/cs5424-team14/pull/4) includes the report
cleanup and earlier A confirmation/Overleaf handoff changes. PR #3 is closed
as superseded by #4; #4 requires a teammate approval before merging.

A selection is confirmed: **a112 final, a115 follow-up, a10 separate**.
Kelvin's write-path analysis is included. The B pair still needs to confirm its
final choice and individual attribution. Everyone must check names,
contributions, references and full AI records. The archives are local review
artifacts, and no Canvas upload is recorded.

Use [the 29 October teammate handoff](team-handoff-2026-10-29.md) for the
remaining actions and copyable team message. The official deadline is
**30 October 2026 at 23:59 Singapore time**. The 30 October 20:00 upload time
is a proposed internal buffer.

## Archived 28 October checkpoint

The following records the earlier checkpoint. Its live-access, queue, branch,
PR and draft-page statements are dated observations.

**A selection resolved:** Kelvin confirmed a112 as final, a115 as follow-up with
abort caveats, and a10 as separate (no a10+a112 run). His GitHub review of PR #1
is APPROVED; the PR remains open. The [Overleaf handoff](overleaf-handoff.md)
records the proposed single-report workflow. Project creation/invitations are
pending; the checked browser session requires login.

**Shared editing:** The local LaTeX source is now split into A/B section files
under `submission/report/sections/`. [CONTRIBUTING.md](../CONTRIBUTING.md)
explains feature branches, PR bases and peer approval. PR #1 is the integration
review; until it merges, teammate report PRs target `codex/workload-a-followup`.
The report conversion helper refuses to overwrite sources without an explicit
flag. Use `bash scripts/build_report.sh` for normal compilation.

**Submission preparation:** A complete local LaTeX review draft and the three
required upload filenames are now staged under `submission/`. The result ZIP
contains 23 Slurm experiment directories, eight separate local-only supporting
implementations and 48 job folders, including the full
28 October remote readback. The AI ZIP contains recovered local interactions
but still needs earlier/cloud and teammate completeness checks. Nothing has
been uploaded. See [the handoff and review checklist](../submission/README.md).

**Live recheck, approximately 21:10 Singapore time:** SSH succeeds as `cs14`
on `xlogin2`; the queue is empty. Today's matched B jobs 1029473/1030000
support 20.86× at one client (5.190 → 108.250 TPS). Higher-count aborts and
baseline failures remain explicit. Separate B correctness job 1031186 passed
four invariants at three checkpoints and controlled T7 conservation. All 263
newly copied evidence/source files match remote SHA-256 checks. These readback
hashes do not authenticate runtime source. Kelvin's write-path section is now
in the shared report; the contribution table, references, final choices and
submission packaging still need completion. Current PDF pagination is unverified.
See the [full live audit and submission gaps](../results/live-status-20261028/README.md).
The sections below retain the earlier evidence reconciliation; statements that
Kelvin's section is still awaited or B has no additional integrity evidence
refer to that earlier checkpoint.

The A pair has confirmed a112 as final, a115 as follow-up and a10 as a
separate experiment. Kelvin's write-side section is already integrated into
the LaTeX draft. The older [A Markdown draft](workload-a-report-draft.md) is
reference material; the current report source is under `submission/report/`.

The last evidence reconciliation was 22 October, after VPN reconnection (UTC+8). Both a115
jobs are fully imported and audited in
[the complete evidence archive](../results/cluster-full-a115-20261022/README.md).
The earlier timeout and partial readback remain historical checkpoints; they are
no longer access/import blockers. B source and raw output are also imported and
reviewed. Queue/accounting observations are dated snapshots, not live guarantees.

## Code and review at the 28 October checkpoint

Work is on `codex/workload-a-followup`, the branch for
[draft PR #1](https://github.com/horiiiiii032929/cs5424-team14/pull/1), not `main`.
`main` remains the 15 October snapshot. B evidence was imported from
`desmond/expt_b0-6` at `5fa38157a7c1cb9abf1097e731f934a97a3db7c4` into
`results/b-branch-review-20261022/raw/`, preserving the original branch layout
and bytes. It does not overwrite submission baselines or select a final B design.

## Workload A

| Evidence | Verified finding | Decision |
|---|---|---|
| Full matched a0 977740 / a112 977773 | Same xcnf0–4 nodes, scale 1, six client counts, 60 s warmup / 600 s measurement. a112 54.2–90.8 TPS versus a0 3.2–3.6 TPS (16.8–28.2×); zero a112 measured failures; six passing validations. Baseline retains serialization failures. | Confirmed final A design; retain the documented repeat warmup caveat. |
| a112 repeat 978177, seed 7 | Measured TPS within 2.5% of seed 42; six validations passed. The 64-client warmup exited 2; that case is excluded from clean comparisons. | Repetition supports a112 but does not establish a general concurrency fix. |
| a114 diagnostic 979865 | 85.333 TPS; T6 764.5 ms versus a112 diagnostic 650.6 ms. Core and exact summary validation passed. | Do not promote the striped daily summary design. |
| a115 diagnostic 979866 | a112 plus only `orders(created_at)`; 288.633 TPS, T6 115.9 ms, zero failed transactions, two retried transactions / two retry attempts, validation passed. | Promising diagnostic; full-run aborts prevent blanket promotion. |
| a115 full jobs 979909 / 979910 | Complete import: 275 files, 13 matching runtime source hashes per job, all 24 phase commands/exits and 12 passing validations reviewed. Seven cases complete both phases; six also have zero failed records. Seed-42 c32/c64 and seed-7 c8/c16/c64 measurements abort; both c64 warmups abort. Seed-42 c4 has one serialization failure despite exit 0. | Faster eligible observations support the index, but neither seed is a clean full matrix. Confirmed: retain a115 as follow-up and a112 as the final A design. |


Sources: [full comparison and repeat](../results/cluster-full-20261019/README.md),
[T6 diagnostics](../results/cluster-diagnostic-t6-20261020/README.md),
[full a115 audit](../results/cluster-full-a115-20261022/README.md),
[cluster ledger](../results/cluster/README.md).
TPS uses completed scripts / configured duration, including expected business
rollbacks. Aborted warmups or measurements are flagged and excluded from clean
comparisons. Passing post-run integrity checks do not erase performance aborts.

Kelvin's a102 clean cases differ by approximately −3% to +6% from fresh a0,
compared with 49–57% over the older preserved a0 at clean concurrent counts.
Those comparisons use different node allocations and do not establish a matched
index-only speedup. Preserve both controls and the a102/c16 warmup caveat.

Correctness evidence remains separate from timing: the original suite passed
138 checks, a109–a113 passed 151 follow-up checks, a114 passed 42 checks, and
seven deliberate-corruption checks verified the exact post-run validator.
Local/small-scale concurrent aborts and the wrapped commit-time serialization
conflict remain documented.

## Workload B and report

All 975 b0–b6 source/output files now match the pinned branch's Git blobs.
[Independent review](../results/b-branch-review-20261022/README.md) covers 42 cases,
transaction-log counts, source differences, protocols, topologies and saved T6
checks. Twenty-two cases complete both phases; twenty also have zero failed
transaction records. There is no eligible 64-client B comparison under the
same zero-phase-exit policy used for A.

b6 job 956803 records 114.445/327.505/539.437 TPS at its phase-complete
1/4/16 clients. Its c8 warmup exits 2; c32/c64 warmups and measurements exit 2.
The report's 483.53 TPS at c64 is a flagged incomplete-run observation, not a
clean 50% gain over b5 (which also aborted). All seven saved b6 T6 comparisons
match 1,000 merchants with zero differences. No general post-run core-integrity
suite or runtime source-hash manifest is recorded for these B runs. File import
hashes must not be described as runtime authentication.

B allocations differ across experiments, including xcnc b1, mixed xcne/xcnf b4,
and different xcnf nodes for b5/b6. Single-seed cross-allocation results cannot
isolate the entire effect of one optimization. b6's static historical reference
rollup also differs from A a114's synchronously maintained striped summaries.
The B pair must confirm attribution, final design and any necessary matched
repeat/core validation. Report tables retain raw values with explicit abort
caveats; no final selection is inferred.

The shared report contains A/B drafts. Final assembly still needs full names,
confirmed individual contributions, confirmed B choice, complete references and
PDF layout checks. Keep Codex and Claude Code declarations where actually used
and preserve full interaction records. The current a0/a112 figure remains valid;
no flagged a115 or B throughput is silently promoted into its clean comparison.

## Next actions and dates

1. Finalize the A prose using the agreed a112/a115/a10 distinction; Kelvin's
   write-side section is integrated. At one client both a115 seeds pass at
   109.9–115.5 TPS, about 2.1× same-seed a112; higher-count evidence is
   incomplete. Retain all failure/retry and a112 repeat caveats.
2. Confirm B with its owners; decide whether an essential matched repeat or
   additional core validation is needed before the experiment cutoff.
3. Review the draft PR, confirm contributions, finish references and assemble
   submissions. Copy reviewed B folders from the evidence archive into
   `citus_project_team_14/` during final packaging. No new jobs were submitted
   during this audit.

Internal targets: final experiments **23 October**, complete report draft
**27 October**, packaging **29 October**, target upload **30 October at 20:00**.
Official deadline: **30 October 2026, 23:59 Singapore time**.
Required outputs: `14_files.zip`, `14_report.pdf` (at most 20 pages, font at least
10), and `14_ai_tool.zip` containing descriptive `14_X.pdf` interaction reports.
