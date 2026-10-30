# Team 14 submission instructions

Source: the supplied CS4224/CS5424 Canvas Project description, especially
Sections 1, 11 and 12, reread on 30 October 2026.

## Who submits

Section 11.4 states: “Each team should submit at least two files in total;
do not make multiple submissions of each file.”

Submit **one team copy of each required file**. Designate one teammate to upload
the three files below on behalf of Team 14. Every member should not upload a
duplicate set. The brief does not require a separate personal report or code
submission from each student. Check the Canvas confirmation/receipt for each
of the three assignments after uploading; no upload has been performed here.

## What and where

| Final filename | Canvas destination |
|---|---|
| `14_files.zip` | Assignments → Project Result Files |
| `14_report.pdf` | Assignments → Project Report |
| `14_ai_tool.zip` | Assignments → Project AI Tool Usage Files |

All three are needed because the team used AI. The files are in the local
`submission/upload/` directory, which is ignored by Git. The source ZIP for
Overleaf is an editing handoff, not an additional required Canvas upload.
Leaving code on the cluster or merging GitHub PRs does not submit it to Canvas.

**Deadline: Friday, 30 October 2026, 23:59 Singapore time.** The brief applies
late penalties separately to late components: 2 marks for one day, 4 for two
days; more than two days is not graded. Partial days round up.

## Required contents and checks

- The results ZIP has one `citus_project_team_14/` root, installer and README.
  Each independently run experiment has `expt_[ab]N/run.sh`, nine transaction
  SQL files, `slurm-results/job-N/` and the corresponding Slurm `.out`/`.err`.
  Include all experiment code and outputs, even results not selected for discussion.
- The report has the team number, all four names and AI tools on its cover;
  individual contributions; Tasks 1–4 in Sections 2–5; Section 6 conclusions;
  and references. Each experimental subsection identifies its submitted code.
- Maximum report length: 20 pages. Minimum font size: 10 points. The reviewed
  Overleaf PDF is 20 pages, including its cover, with minimum effective text
  size 10.4608 points. Recheck if the team makes further edits.
- AI PDFs use descriptive `14_X.pdf` names and explain how every tool was used,
  preserving prompts/outputs or interaction records. Consolidate everyone's
  actual records in the one team AI ZIP. Add any additional tools to the report
  cover if teammates used them. A usage summary alone is insufficient.
- No clean-performance claims are inferred from aborted runs. The report
  distinguishes full runs, short diagnostics, local validation and separate
  correctness jobs, and retains failure limitations.

## Evaluation attendance

Section 12 requires a **20-minute team Q&A in week 13**, with **all members
expected to attend**. There is **no student presentation**. Registration is
announced in week 12; the team's booking has not been verified here.

The project is worth 25 marks. Evaluation considers design decisions,
experimental design, analysis/interpretation and the report, not only peak TPS.

## Remaining actions

1. Complete teammates' and any missing cloud AI records; ensure the cover lists
   every tool actually used.
2. Have the designated uploader submit the three files and verify receipts.
3. Confirm the team's Q&A booking and attendance.

The latest report and code/results checks are recorded in
`multi-agent-submission-check-2026-10-30.json` and
`overleaf-match-2026-10-30.json`. The subsequent AI-only packaging update is
`ai-finalization-2026-10-30.json`: Desmond's supplied transcript and the available
later local interactions are included; unsupplied team records still require
confirmation. Earlier dated audits describe their original snapshots.
