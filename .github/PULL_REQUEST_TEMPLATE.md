## What changed

State the report sections or experiment IDs changed and the resulting conclusion.

## Evidence and checks

- [ ] Claims link to the relevant experiment/job and retain abort/failure caveats.
- [ ] Report source compiles (`bash scripts/build_report.sh` for report changes).
- [ ] Rendered PDF checked: at most 20 pages including cover, font at least 10 pt.
- [ ] Contributions and AI declarations reflect actual work/tools used.
- [ ] No credentials, private interaction records or generated upload ZIPs added.

## Review

- [ ] Requested a teammate other than the author as reviewer.
- [ ] Review conversations resolved before merging.

Review the source diff and the compiled report. Do not merge before another
person explicitly approves. Use `codex/workload-a-followup` as the base until
PR #1 merges; afterward use `main`.
