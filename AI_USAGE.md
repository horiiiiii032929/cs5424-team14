# AI assistance record

Tools recorded: OpenAI Codex and Claude Code. Team 14; work attributed to Hikaru
for team review. Entries below are dated checkpoints, not current job status.

- 10 October 2026: developed five Workload A proposals from the supplied
  assignment, baseline SQL and result files; added them to the team Google Doc.
- 14 October 2026: implemented experiment generation, SQL variants, transaction
  correctness tests, Docker pilot infrastructure, Slurm submission helper,
  repository documentation and result analysis at Hikaru's request.
  Ran 138 passing native distributed correctness checks and an 18-case local
  pilot (16 completed, two aborted), preserved raw evidence, and created the
  team GitHub repository, initially private and subsequently made public at
  Hikaru’s request. No new course-cluster experiments were run.
- 15 October 2026: updated seven existing Google Drive planning documents using
  hori0329@gmail.com, corrected stale coordination fields and submission names,
  added implementation/results evidence and potential overlaps for team review,
  and verified the saved content while preserving teammates' original ideas.
- 19 October 2026: incorporated Kelvin's teammate-reported a102/job 965657 and
  write-side findings; implemented attributed A adaptations and access-mode
  experiments a109–a112; ran 122 additional passing correctness checks and six
  four-client local stress cases, all of which aborted. Preserved failed cases
  without performance rankings. Pinned xcnf submission hardware, added four-client
  smoke coverage and focused experiment selection, and checked scheduling with
  stubs. Drafted A report sections and a cluster runbook. SSH remained unavailable;
  no new course-cluster jobs were submitted during that initial local phase.
  Added the A draft to sections 2–3 of the shared Google Doc's Report tab and
  appended a dated implementation update to its ideas tab. Readback confirmed
  the A text, unchanged B report text, and all 15 existing tables. Published
  code, evidence and the runbook for review in draft GitHub pull request #1.
  Later, after access was restored, retrieved and reviewed Kelvin's 30 cases,
  found a102's previously unreported 16-client warmup abort, preserved four new
  smoke jobs, and started course-scale diagnostics. Diagnosed an expensive
  post-run global-ID validator; exact replacement checks passed on the full
  dataset in 25.753 seconds and in seven deliberate-corruption regression tests.
  Cancelled only the affected own jobs and resubmitted diagnostics with the
  replacement. a113 passed 29 correctness checks but its local warmup still
  aborted. Added a reproducible baseline/index figure with the warmup caveat.
  Reviewed completed scale-1 diagnostics 977617–977619: all phases and exact
  validators passed, with observed configured-duration TPS 89.917/92.383/90.550.
  Submitted the original full matrix for a0 control 977740 and a112 candidate
  977773 on matched xcnf0–4 nodes; replaced only pending candidate 977741 to
  correct its node request and verified the full settings. Full results remain
  pending at that checkpoint (both later completed). Inserted and checked the
  report figure in the shared Google Doc,
  preserving the B text and all 15 existing tables.
- 19 October 2026 (evening, Claude Code): monitored and imported full jobs
  977740/977773 with a new reviewing importer, found the fresh a0 control is
  faster than preserved job 918524 (revising the a102 gain claim), recorded
  a112's matched 17–28× result and figure, and submitted seed-7 repeat 978177.

- 19–20 October 2026 (Claude Code, per recorded commits and supplied work log):
  imported a112 repeat 978177 and diagnosed its flagged 64-client warmup;
  implemented and merged a114/a115 into the PR branch, recorded passing a114
  correctness checks and completed cluster diagnostics, rejected a114's summary
  design, and submitted a115 full jobs 979909/979910 for seeds 42/7. Their full
  results had not been imported at the 20 October checkpoint.
- 20 October 2026 (Codex): checked Git/PR and repository/Drive documentation;
  reconciled current status, corrected the a115 diagnostic retry count to two,
  updated the A analysis and team planning documents, and refreshed the draft PR.
  Cluster access timed out, so no live a115 completion or final-selection claim
  was made. Retain the readback/validation records with this interaction.

- 22 October 2026 (Codex): read live Slurm accounting, a115 summary rows and
  benchmark/validation excerpts; established completion with measured aborts.
  Subsequent full archive imports failed with SSH timeout and VPN disconnected;
  preserved a clearly labelled transcription rather than claiming a raw import.
  Imported all 975 B branch files at 5fa38157a7c1cb9abf1097e731f934a97a3db7c4,
  verified Git blob identity, all 42 transaction-log record counts, phase exits,
  hardware/protocol differences and seven matching b6 T6 checks. Corrected B
  warmup/measurement caveats and qualified the 64-client gain claims in repo
  and shared documentation. a112 stays provisional; final team choices remain open.

- 22 October 2026 (Codex, after VPN reconnection): completed both a115 imports,
  preserving 275 files and the actual SQL source. Verified all 26 runtime hashes,
  24 phase command lines/exits, 12 raw transaction/retry/per-script count audits
  and 12 passing core validations. Classified 7 phase-eligible cases, 6 with zero
  failed records; preserved both c64 warmup aborts and all five measured aborts.
  Tightened the importer's missing-warmup policy and included SQL/transaction
  source in future imports; negative checks reject missing warmup/validation.
  Updated repo/shared documentation and the draft PR, removed the resolved
  access/import blocker, and retained a112 as provisional pending team choice.
  No benchmark SQL was changed or new jobs submitted during this review.

Keep the conversation export with prompts and outputs for the required
`14_ai_tool.zip` reports. This short record is an index, not a replacement for
the complete required interaction records. Team members must review and understand
the implementations and remain responsible for submitted code, findings and claims.
