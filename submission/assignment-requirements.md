# Check against the supplied project overview

Authority: the Canvas Project overview pasted by Hikaru on 28 October 2026.
The overview, rather than the earlier shared report's structure, governs this
check. The original attachment was read directly; no new requirement is inferred
from a team preference or a previous working draft.

## Required report structure

| Overview requirement | Local report |
|---|---|
| `14_report.pdf`, at most 20 pages, font at least 10 | Compiled PDF checked including the cover; current measurements are in `validation.json`. |
| Cover: team number, all member names, AI tools or NONE | Team 14, four names, Codex and Claude Code; each member must confirm names/tools. |
| Section 1: individual contributions | Draft allocation is present; each member must confirm it. |
| Section 2: Task 1, baseline A | Explicit `expt_a0` subsection, baseline TPS and p50/p95/p99 table, fresh matched-control distinction. |
| Section 3: Task 2, optimized A | Explicit a102/a101/a111/a113/a112/a114/a115 and write-path experiment subsections, measured progression/controls, full a112 percentile table and two figures. |
| Section 4: Task 3, baseline B | `expt_b0` subsection with TPS/latency/failure tables. |
| Section 5: Task 4, optimized B | b1-b6 subsections; matched b0/b6 and separate correctness evidence retain scope and failure caveats. |
| Section 6: conclusion and lessons/difficulties | Combined-design benefit, negative summary result, timing/validation distinction and concurrency limitations. |
| References consulted | Existing source links retained; authors must verify completeness and relevance. |
| Sections 2-5 organized by experiment, with matching identifiers | Course experiment IDs match submitted directories; supplementary expt_xc_b1 is identified by submitted alias `expt_b201`. |
| Claims supported by experimental evidence | Matched combined gains are distinguished from component effects; aborted runs are not clean rankings. Different xcnc/xcnf hardware is now explicit in the T7-only comparison. |

## Required result-folder structure

The ZIP has a single `citus_project_team_14/` root, `install_citus_slurm.sh`,
and a README describing the experiments. Every one of the **23 top-level
experiment folders** follows `expt_[ab]N` and has `run.sh`, nine transaction SQL
files, `slurm-results/job-N/`, and matching `citus-N.out` and `citus-N.err` files.
There are 48 job-directory paths representing 45 distinct Slurm IDs; some
historical control folders retain the same original job ID and are not counted
as independent runs.

The organization follow-up explicitly labels b203/b204 as unbenchmarked source
variants containing inherited b2/job-928583 evidence, and b201/job-918781 as an
inherited b0 baseline. The 23 folders do not represent 23 independently measured
designs. `job-source-map.json` records canonical job ownership and runtime source
matches where available. Additional local correctness/pilot evidence has been
included; see [the organization follow-up](organization-2026-10-29.md).

Eight local-only designs (a103-a110) have no Slurm run. Their code is retained
under `supporting_implementations/local_only/`, separately from the course
experiment folders. Their local outputs remain under `evidence/local-only/`.
This avoids implying that local pilots meet the cluster benchmarking task.
No missing job output is fabricated. The report discusses these only as
supporting implementations/validation and focuses its performance findings on
the available cluster experiments.

The source-folder aliases b201-b204 are documented in the archive README and
provenance map. Baselines a0/b0 are preserved. Failed and cancelled attempts
are retained with their actual exit/failure evidence.

## AI documentation and submission

The overview explicitly requires preserving AI interactions and additional PDFs
describing each tool, with prompts/outputs or interaction records. The AI ZIP
contains `14_codex_interactions.pdf` and `14_claude_code_interactions.pdf` from
recovered local sessions, plus supplemental tool records. **Completeness is not
established:** earlier cloud conversations and teammates' records/tools must be
checked. A usage summary alone does not satisfy the interaction requirement.

Upload one team version of each required file to its corresponding assignment:
`14_files.zip`, `14_report.pdf`, and `14_ai_tool.zip`. No file has been uploaded.
Deadline: 30 October 2026, 23:59 Singapore time. The overview also requires all
members at a 20-minute week-13 Q&A, with no presentation; registration remains
to be checked.

## What the brief does not require

It does not prescribe Google Docs, LaTeX, a particular visual template, a
fixed number of optimization ideas per person, or discussion of every pilot.
LaTeX is suitable if the PDF meets the stated structure, length and font rules.
The A/B pairing is the team's allocation. The grading priorities are design
decisions, experimental design, interpretation and report quality.
