# Google Drive Project Workspace

Account: hori0329@gmail.com

20 October reconciliation: seven existing Google Docs were updated in place and
read back: shared ideas/report, hub, A/B plans, schedule, checklist and AI log.
The Report tab now includes completed matched a0/a112 results, the seed-7/c64
warmup caveat, revised a102 interpretation, a114/a115 diagnostics (a115: two
retries), the matched full-run figure, and a completed draft section-6 conclusion.
The B sections' text, all 15 existing report tables and original figure were
preserved; the matched full figure was added at the same 420 pt text width.
The updated report pages and figures were checked in a PDF export (15 Report
pages, within a 23-page export of both tabs). [Sync verification](docs/google-drive-sync-2026-10-20.json)
records readback and preservation checks. The exported
file includes both planning and Report tabs; it is not the final submission PDF.

22 October: seven existing Docs were updated in place and read back, including
both tabs of the report/ideas document. The Report tab's 15 tables, the planning
tab's table, all numeric table text and both figures were preserved. A concurrent
T7-only paragraph edit was retained after a revision conflict; no stale replacement
was forced. The 23-page combined-tab PDF export was reviewed on the updated A,
B and conclusion pages; the Report tab remains 15 pages and is still a draft.
[Readback verification](docs/google-drive-sync-2026-10-22.json) records
revisions and preservation checks. This is still a working report, not the final PDF.

22 October reconciliation: B b0–b6 is imported from branch commit
`5fa38157a7c1cb9abf1097e731f934a97a3db7c4`, preserving 975 original files.
The 42-case review finds 22 phase-complete cases (20 with zero failed records).
b6/c16's 539.437 TPS is supported; c8's warmup and c32/c64's warmups/measurements
aborted. Seven b6 T6 checks match; general integrity and runtime hash evidence
are absent. Hardware varies across the series, so the old c64 gain claim is qualified.

Current A decision after VPN reconnection: a112 remains provisional. Both a115
full jobs are completely imported and reviewed: 275 files, 26 runtime source-hash
comparisons, 24 phase commands/exits, 12 raw transaction/retry audits and 12 passing
validations. Seven cases complete both phases; six also have zero failed records.
Seed-42 c32/c64 and seed-7 c8/c16/c64 measurements abort; both c64 warmups abort.
Eligible cases support the index, but neither seed is a clean full matrix.
The partial transcription and earlier timeout remain historical checkpoints;
import/access is no longer blocked. Final A/B choices remain with the team.
See [complete evidence](results/cluster-full-a115-20261022/README.md) and
[current status](docs/project-status.md).

The follow-up shared-Docs sync replaces the earlier blocked status and retains
the existing B tables/figures. All six affected Docs were read back; the B plan
was inspected and already current. The new combined-tab QA export has 24 pages,
with a 16-page Report tab; updated A/figure/conclusion/reference pages were
visually checked. Its verification record is
[the completed a115 sync](docs/google-drive-sync-2026-10-22-a115.json).

Code and evidence are on [draft PR #1](https://github.com/horiiiiii032929/cs5424-team14/pull/1).
The a114/a115 merge was into the PR branch, not into `main`. The requirement
and assignment-guide documents remain source references; their instructions
were preserved.

[Public team code repository](https://github.com/horiiiiii032929/cs5424-team14)
Created 14 October 2026 and made public at Hikaru’s request. Anyone can view and
clone it; GitHub usernames are needed only for direct push access.

Updated 15 October 2026 through `hori0329@gmail.com`: the hub, shared ideas,
A/B plans, schedule, report checklist and AI usage log now link to the public
repository and verified local results, with remaining course-cluster work stated.

[Project folder](https://drive.google.com/drive/folders/11cOQSSKCsp04XmKZAnHBSxZh5WTIQnLX)

- [Our Optimization Ideas and Plan](https://docs.google.com/document/d/1OnjeyIoiXQpPWMFnOJerrP6eLZtnRzWuPm8XigARjgs/edit?usp=drivesdk)

- [00 Project Hub and Team Coordination](https://docs.google.com/document/d/1mwklFOrKt5klL-ABP1ruN_GzPzAvs2QFaPcxU9WRhLM/edit?usp=drivesdk)
- [01 Project Requirements and Setup](https://docs.google.com/document/d/14J-AltuKLDreB72Vgw5bJcf_4PznZPFpHTWNVpwZT8Q/edit?usp=drivesdk)
- [Workload A Baseline and Optimization Plan](https://docs.google.com/document/d/11rntSmDQeXzabqSEbF7Zq3HV9bdf-FTmhkreIkM7np8/edit?usp=drivesdk)
- [Workload B Baseline and Optimization Plan](https://docs.google.com/document/d/13qBUKMlBFoJ1JsjHlk6GgaYH10_7ws7ynHULVmO_hTE/edit?usp=drivesdk)
- [Assignment Guide Result Files](https://docs.google.com/document/d/1LrSEabHBqmX5lph2xaG48biX4o6iH4bJPNPo0R0yehI/edit?usp=drivesdk)
- [Assignment Guide Project Report](https://docs.google.com/document/d/1MxhCfwi5nvdCHxBiwIqID2HtYCLLz7USZAo0b3ooxAU/edit?usp=drivesdk)
- [Assignment Guide AI Tool Usage Files](https://docs.google.com/document/d/1F5xs0Ce0frMqi6CgrIN6xAoT8RU7Ixq3utgVvkvJlug/edit?usp=drivesdk)
- [Report Outline and Submission Checklist](https://docs.google.com/document/d/1WdnfyzB_NLy3ffrWmHwfPshP3-q8yC5RHVyDt3s0-PQ/edit?usp=drivesdk)
- [AI Usage Log and Interaction Record](https://docs.google.com/document/d/1S6mdH7q-R0P9YHb9kzVXe9A1gBvjkV7BJDAmH1-YeE0/edit?usp=drivesdk)

- [Project Schedule and Working Responsibilities](https://docs.google.com/document/d/1PinMwUZBli6S0Aou2Tn3Np7UQ2eWCg23pNjGmZwBCZQ/edit?usp=drivesdk)

Team members: Xincheng, Dessi, Kelvin, Hikaru.

Working split for team review: Hikaru + Kelvin for Task 2 / workload A; Dessi + Xincheng for Task 4 / workload B. Each pair also owns its baseline. Kelvin is the proposed report assembly coordinator, and Hikaru the proposed packaging/upload coordinator.

Internal targets: baselines by 10 October; individual experiments by 18 October; final experiments by 23 October; report draft by 27 October; packaging by 29 October; upload on 30 October at 20:00 Singapore time, before the official 23:59 deadline.

Team number is 14; project account is cs14. Roles remain a proposed team split.
Baseline A/B snapshots are in the repository. See `results/README.md` for new
validation and measurements; local Docker runs are separate from course-cluster results.
