# Working together on the final report

Use this repository for the shared LaTeX report and experiment evidence. Every
contributors can use pull requests and merge their own changes. Peer review is
optional. The Canvas deadline is
**30 October 2026, 23:59 Singapore time**.

## Current branches and review

[PR #1](https://github.com/horiiiiii032929/cs5424-team14/pull/1), containing the
A/B evidence and first shared LaTeX draft, merged into `main` on 29 October.
Create new feature branches from `origin/main` and target `main` in your PR.
The report cleanup is on `codex/maintainable-latex-report`; its PR also contains
the agreed A selection and the earlier Overleaf handoff changes.

`main` does not require approval or resolved review conversations to merge.
Contributors with write access can merge their own pull requests. CODEOWNERS
supplies suggested reviewers when a review is helpful.

## Shared Overleaf report

Use the [shared Overleaf project](https://www.overleaf.com/project/6ae2d836f7dbb8dab0442621) for final joint
report edits. Hikaru supplied this project on 29 October. The repository retains
code, evidence and reviewed source snapshots; see [the handoff](docs/overleaf-handoff.md).
Check the live project against the repo source before importing any ZIP, and
export the final reviewed Overleaf source back to a feature branch for review.
The project contents and collaborator access were not verified by this cleanup.

## What to edit

The editable source is `submission/report/`. `main.tex` loads the section files:

| File under `submission/report/sections/` | Work | People to coordinate with |
|---|---|---|
| `00_cover.tex` | Names and AI declaration | Everyone |
| `01_contributions.tex` | Each person's contribution | Everyone |
| `02_baseline_a.tex` | Task 1 / A baseline | Hikaru and Kelvin |
| `03_optimized_a.tex` and `workload-a/*.tex` | Task 2 / A introduction and individual experiments | Hikaru and Kelvin |
| `04_baseline_b.tex` | Task 3 / B baseline | Desmond and Xincheng |
| `05_optimized_b.tex` | Task 4 / B optimizations | Desmond and Xincheng |
| `06_conclusion.tex` | Lessons and limitations | Both pairs |
| `07_references.tex` | Sources actually consulted | Everyone |

Edit the `.tex` section files directly. The older Markdown draft is a reference,
not a second source to update in parallel. Do not run `prepare_report.py` over
teammates' edits: it is an import/conversion helper that overwrites the report.
Keep changes scoped to your section where possible to reduce merge conflicts.

The latest PDF page count is recorded in `submission/validation.json`. Keep text at least 10 pt;
shorten repeated material if adding content would exceed the limit. Sections
2-5 must retain experiment IDs matching the result archive, methods, relevant
tables/figures, and evidence for their claims.

## Example for Kelvin

```sh
git fetch origin
git switch -c codex/kelvin-a-report origin/main
# Edit submission/report/sections/02_baseline_a.tex and/or 03_optimized_a.tex.
bash scripts/build_report.sh
git add submission/report/sections/
git commit -m "Review A report conclusions and write-path findings"
git push -u origin codex/kelvin-a-report
gh pr create --base main
```

Without the GitHub CLI, use GitHub's **Compare & pull request**, choose the base
branch above. Desmond can use the same workflow with a separate B branch.
Request a teammate under **Reviewers** when feedback would be useful. Authors
can merge their own pull requests without waiting for approval.

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
