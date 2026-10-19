# AI assistance record

Tool: OpenAI Codex. Team 14; work attributed to Hikaru for team review.

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

Keep the conversation export with prompts and outputs for the required
`14_ai_tool.zip` reports. This short record is an index, not a replacement for
the complete required interaction records. Team members must review and understand
the implementations and remain responsible for submitted code, findings and claims.
