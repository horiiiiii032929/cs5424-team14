# Team 14 project update — 15 October 2026

Applied to the existing Drive planning documents on 15 October 2026 using
`hori0329@gmail.com`: Project Hub, Our Optimization Ideas and Plan, Workload A
plan, Workload B plan, Project Schedule, Report Checklist and AI Usage Log.
The saved Drive content was checked after editing. Teammates' original ideas and
image references were retained. This file is the general update summary; each
Drive document also contains relevant details and corrections to stale fields.

## Code and results

Our [team GitHub repository](https://github.com/horiiiiii032929/cs5424-team14) is
now public. Everyone can view or clone the code and results without an invitation.
Teammates can fork it and submit pull requests. Direct push access requires a
collaborator invitation using their GitHub username.

[Implementation and result report](https://github.com/horiiiiii032929/cs5424-team14/blob/main/results/README.md)

Hikaru's five Workload A optimization ideas are implemented as eight experiments:

| Experiment | Idea |
|---|---|
| expt_a101 | Store each merchant's related data together |
| expt_a102 | Add indexes for repeated lookups |
| expt_a103 | Place an order through one database function call |
| expt_a104 | Maintain exact daily sales totals |
| expt_a105 | Test more memory per query |
| expt_a106 | Test a smaller Citus executor connection pool |
| expt_a107 | Test a larger Citus executor connection pool |
| expt_a108 | Combine data placement, indexes, order function and sales totals |

The experiment numbers are provisional until we check for conflicts with other
team experiments. Dessi's existing A/B baseline snapshots are preserved as
expt_a0 and expt_b0. This update does not claim that Workload B optimization is
complete.

## What has been tested

- All 138 checks in the native distributed correctness suite passed.
- The local benchmark attempted 18 cases: 16 completed with passing integrity
  checks; two aborted with serialization/distributed commit errors.
- Merchant colocation and the combined design looked promising at one client,
  but both aborted at four clients. They need investigation before selection.
- These were short local Docker measurements. Small baseline samples mean we
  cannot choose the final design from these numbers alone.
- Raw logs, failures, source hashes and settings are in the repository. Failed
  measurements are excluded from the performance comparison.

## Next steps

1. Review everyone's ideas together and merge duplicates. Keep each distinct
   experiment and its results, including changes that did not help.
2. Restore course-cluster access, check the live team experiment folders, and
   agree on experiment numbers and job order before running new jobs.
3. Reproduce and investigate the two concurrent failures while keeping the
   required isolation and workload unchanged.
4. Review smoke-run results, then run the original scale-1 benchmark settings
   at 1, 4, 8, 16, 32 and 64 clients. Repeat promising designs and compare them
   using throughput, latency and failure/retry counts.
5. Select the best supported design for each workload and explain both the
   successful and unsuccessful experiments in the report.

The last SSH attempts on 14 October timed out before authentication. No new
course-cluster jobs have been submitted by this implementation work.

## Submission reminder

Deadline: **30 October 2026, 23:59 Singapore time**. The later availability
cutoff on 1 November is not the stated due date.

- Result archive: `14_files.zip`, containing `citus_project_team_14/`.
- Project report: `14_report.pdf`, at most 20 pages and font size at least 10.
- AI usage reports: descriptive `14_X.pdf` files inside `14_ai_tool.zip`.

The report must include team contributions, baseline and optimized designs for
both workloads, experiment IDs matching the submitted folders, evidence for
claims, a conclusion and references. Declare AI use on the cover page and
describe its use in the additional AI reports. The repository includes an AI
assistance record to support that declaration.
