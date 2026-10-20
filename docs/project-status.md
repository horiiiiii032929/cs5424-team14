# Project status — 20 October 2026

Last reconciliation: 20 October 2026, 16:55 Singapore time. Cluster SSH timed out
before login; the current queue and a115 full results could not be verified.
This is the current status reference. Dated experiment records remain evidence
of their own checkpoints.

## Code and review

The a114/a115 work was merged into `codex/workload-a-followup` at `4caf234` and
pushed. That merge was into the PR branch; it did not merge
[PR #1](https://github.com/horiiiiii032929/cs5424-team14/pull/1) into `main`.
`main` still points at the 15 October snapshot. The PR remains a draft while
full a115 results and final selection await review.

## Workload A

| Evidence | Verified finding | Decision |
|---|---|---|
| Full matched a0 977740 / a112 977773 | Same xcnf0–4 nodes, scale 1, six client counts, 60 s warmup / 600 s measurement. a112 54.2–90.8 TPS versus a0 3.2–3.6 TPS (16.8–28.2×); zero a112 measured failures; six passing validations. Baseline retains serialization failures. | a112 is provisional, pending team agreement. |
| a112 repeat 978177, seed 7 | Measured TPS within 2.5% of seed 42; six validations passed. The 64-client warmup exited 2; that case is excluded from clean comparisons. | Repetition supports a112 but does not establish a general concurrency fix. |
| a114 diagnostic 979865 | 85.333 TPS; T6 764.5 ms versus a112 diagnostic 650.6 ms. Core and exact summary validation passed. | Do not promote the striped daily summary design. |
| a115 diagnostic 979866 | a112 plus only `orders(created_at)`; 288.633 TPS, T6 115.9 ms, zero failed transactions, two retried transactions / two retry attempts, validation passed. | Leading candidate; a 60 s diagnostic is insufficient for final selection. |
| a115 full jobs 979909 / 979910 | Submitted for seeds 42 / 7 on xcnf0–4; last saved submission checkpoint says queued. No full-run results imported. | Current Slurm state and completion are unverified; inspect before resubmitting. |

Sources: [full comparison and repeat](../results/cluster-full-20261019/README.md),
[T6 diagnostics](../results/cluster-diagnostic-t6-20261020/README.md),
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

The [shared report](https://docs.google.com/document/d/1OnjeyIoiXQpPWMFnOJerrP6eLZtnRzWuPm8XigARjgs/edit)
contains the B team's b1–b6 analysis. It reports about 539 TPS at 16 clients and
483.53 TPS at 64 for b6. These are teammate-reported values: optimized B scripts,
raw results, settings and job IDs have not been archived in this checkout or
independently reviewed here. The B draft documents aborted b3 cases and residual
b4 client aborts; do not treat their partial TPS as clean comparisons.
The B pair must confirm its final design and supply the complete evidence.

The A draft now includes completed matched results, repeat caveats and a114/a115
diagnostics. Final report assembly still needs full names, confirmed individual
contributions, B evidence, final A/B choices, conclusion, references and PDF
layout checks. List both Codex and Claude Code where actually used and preserve
full interaction records for each.

## Next actions and dates

1. Restore cluster access and inspect jobs 979909/979910. Follow the
   [runbook](workload-a-cluster-runbook.md) to import finished jobs once all
   outputs are available; inspect every warmup, measurement, validation and hash.
2. Compare both a115 seeds with a0/a112; update the figure and report only after
   reviewing the full matrix. Confirm the A decision with Kelvin.
3. Archive the B experiments/results and obtain the B pair's final decision.
4. Review the draft PR, confirm contribution statements and assemble submissions.

Internal targets: final experiments **23 October**, complete report draft
**27 October**, packaging **29 October**, target upload **30 October at 20:00**.
Official deadline: **30 October 2026, 23:59 Singapore time**.
Required outputs: `14_files.zip`, `14_report.pdf` (at most 20 pages, font at least
10), and `14_ai_tool.zip` containing descriptive `14_X.pdf` interaction reports.
