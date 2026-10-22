# Project status — 22 October 2026

Latest reconciliation: 22 October, after VPN reconnection (UTC+8). Both a115
jobs are fully imported and audited in
[the complete evidence archive](../results/cluster-full-a115-20261022/README.md).
The earlier timeout and partial readback remain historical checkpoints; they are
no longer access/import blockers. B source and raw output are also imported and
reviewed. Queue/accounting observations are dated snapshots, not live guarantees.

## Code and review

Work is on `codex/workload-a-followup`, the branch for
[draft PR #1](https://github.com/horiiiiii032929/cs5424-team14/pull/1), not `main`.
`main` remains the 15 October snapshot. B evidence was imported from
`desmond/expt_b0-6` at `5fa38157a7c1cb9abf1097e731f934a97a3db7c4` into
`results/b-branch-review-20261022/raw/`, preserving the original branch layout
and bytes. It does not overwrite submission baselines or select a final B design.

## Workload A

| Evidence | Verified finding | Decision |
|---|---|---|
| Full matched a0 977740 / a112 977773 | Same xcnf0–4 nodes, scale 1, six client counts, 60 s warmup / 600 s measurement. a112 54.2–90.8 TPS versus a0 3.2–3.6 TPS (16.8–28.2×); zero a112 measured failures; six passing validations. Baseline retains serialization failures. | a112 is provisional, pending team agreement. |
| a112 repeat 978177, seed 7 | Measured TPS within 2.5% of seed 42; six validations passed. The 64-client warmup exited 2; that case is excluded from clean comparisons. | Repetition supports a112 but does not establish a general concurrency fix. |
| a114 diagnostic 979865 | 85.333 TPS; T6 764.5 ms versus a112 diagnostic 650.6 ms. Core and exact summary validation passed. | Do not promote the striped daily summary design. |
| a115 diagnostic 979866 | a112 plus only `orders(created_at)`; 288.633 TPS, T6 115.9 ms, zero failed transactions, two retried transactions / two retry attempts, validation passed. | Promising diagnostic; full-run aborts prevent blanket promotion. |
| a115 full jobs 979909 / 979910 | Complete import: 275 files, 13 matching runtime source hashes per job, all 24 phase commands/exits and 12 passing validations reviewed. Seven cases complete both phases; six also have zero failed records. Seed-42 c32/c64 and seed-7 c8/c16/c64 measurements abort; both c64 warmups abort. Seed-42 c4 has one serialization failure despite exit 0. | Faster eligible observations support the index, but neither seed is a clean full matrix. a112 stays provisional; confirm final choice with Kelvin. |


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
confirmed individual contributions, agreed A/B choices, complete references and
PDF layout checks. Keep Codex and Claude Code declarations where actually used
and preserve full interaction records. The current a0/a112 figure remains valid;
no flagged a115 or B throughput is silently promoted into its clean comparison.

## Next actions and dates

1. Confirm A with Kelvin using the completed a115 audit. At one client both
   a115 seeds pass at 109.9–115.5 TPS, about 2.1× same-seed a112; higher-count
   evidence is incomplete. Retain all failure/retry and a112 repeat caveats.
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
