# Working together on the final report

Use this repository for the shared LaTeX report and experiment evidence. Every
change goes through a pull request and at least one other person's approval.
Do not merge your own work before peer review. The Canvas deadline is
**30 October 2026, 23:59 Singapore time**.

## Current branches and first review

[PR #1](https://github.com/horiiiiii032929/cs5424-team14/pull/1) contains the
current A work, evidence review and LaTeX report. Kelvin is the first requested
reviewer. It is not merged into `main` yet.

**Until PR #1 is merged**, create report branches from
`origin/codex/workload-a-followup` and target that same branch in your PR.
This lets the team contribute to the actual report rather than the older main
snapshot. After PR #1 merges, start from and target `main` instead.

Both `main` and the report integration branch require a pull request with one
approval from someone other than the author. New commits dismiss old approvals;
resolve review conversations before merging. CODEOWNERS supplies suggested
reviewers; the one-approval rule is enforced by branch protection, not just this
document.

## Overleaf handoff proposal

Kelvin proposed using Overleaf for the final joint report edits. See
[the handoff](docs/overleaf-handoff.md). Once that project is created and shared,
use it as the editable report and use repo PRs for reviewed source snapshots.
Until the handoff is complete, use the section files and PR workflow below.

## What to edit

The editable source is `submission/report/`. `main.tex` loads the section files:

| File under `submission/report/sections/` | Work | People to coordinate with |
|---|---|---|
| `00_cover.tex` | Names and AI declaration | Everyone |
| `01_contributions.tex` | Each person's contribution | Everyone |
| `02_baseline_a.tex` | Task 1 / A baseline | Hikaru and Kelvin |
| `03_optimized_a.tex` | Task 2 / A optimizations | Hikaru and Kelvin |
| `04_baseline_b.tex` | Task 3 / B baseline | Desmond and Xincheng |
| `05_optimized_b.tex` | Task 4 / B optimizations | Desmond and Xincheng |
| `06_conclusion.tex` | Lessons and limitations | Both pairs |
| `07_references.tex` | Sources actually consulted | Everyone |

Edit the `.tex` section files directly. The older Markdown draft is a reference,
not a second source to update in parallel. Do not run `prepare_report.py` over
teammates' edits: it is an import/conversion helper that overwrites the report.
Keep changes scoped to your section where possible to reduce merge conflicts.

The current PDF is 20 pages including the cover. Keep text at least 10 pt;
shorten repeated material if adding content would exceed the limit. Sections
2-5 must retain experiment IDs matching the result archive, methods, relevant
tables/figures, and evidence for their claims.

## Example for Kelvin

```sh
git fetch origin
git switch -c codex/kelvin-a-report origin/codex/workload-a-followup
# Edit submission/report/sections/02_baseline_a.tex and/or 03_optimized_a.tex.
bash scripts/build_report.sh
git add submission/report/sections/
git commit -m "Review A report conclusions and write-path findings"
git push -u origin codex/kelvin-a-report
gh pr create --base codex/workload-a-followup --reviewer horiiiiii032929
```

Without the GitHub CLI, use GitHub's **Compare & pull request**, choose the base
branch above, and select another teammate under **Reviewers**. Desmond can use
the same workflow with a separate B branch and request Hikaru or Kelvin.

Reviewers should check the diff, evidence and rendered PDF, leave comments where
needed, and explicitly **Approve** when satisfied. A comment alone is not an
approval. If you are the PR author, you cannot supply your own required approval.

## Build and preview

Install Tectonic or a standard LaTeX distribution, or upload the report source
to Overleaf. From the repository root:

```sh
bash scripts/build_report.sh
```

This compiles `submission/report/main.tex` and writes
`submission/upload/14_report.pdf`. It also creates
`submission/14_report_overleaf.zip` from the current section files and images.
For Overleaf, set `main.tex` as the main document. A generated PDF is a preview
of the source at build time; rebuild after every report edit.

The three final Canvas uploads are `14_files.zip`, `14_report.pdf`, and
`14_ai_tool.zip`. Their generated upload directory is ignored by Git. The
archive/AI record checklist is in [submission/README.md](submission/README.md),
with the assignment mapping in
[submission/assignment-requirements.md](submission/assignment-requirements.md).

## Evidence and private files

- Preserve measured aborts, warmup exits, retries and final failures. Slurm
  COMPLETED and passing integrity checks alone do not establish a clean result.
- Cite the experiment/job and distinguish matched full runs, short diagnostics,
  local pilots and separate correctness checks. Do not silently combine a10
  and a112 into a design that has not been benchmarked.
- Keep original source/results and use new experiment IDs for new changes.
  Coordinate any cluster work first: the shared port is 5446.
- Never commit passwords, `.env`, SSH keys, private AI transcripts or generated
  upload archives. Each member must preserve their actual AI interactions for
  the private AI submission and confirm their tools on the cover.

## Access

Hikaru (`horiiiiii032929`), Kelvin (`ktingit`) and Desmond (`awhdesmond`) have
repository write access. Xincheng's GitHub username is not known yet; add the
confirmed account before assigning it as a reviewer or owner. No username is
guessed from a person's name.
