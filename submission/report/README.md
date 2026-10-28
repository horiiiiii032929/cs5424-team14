# Team 14 shared LaTeX report

Edit the `.tex` files under `sections/`. `main.tex` loads them in the required
order. Hikaru and Kelvin own `02_baseline_a.tex` and `03_optimized_a.tex`;
Desmond and Xincheng own `04_baseline_b.tex` and `05_optimized_b.tex`. Everyone
checks the cover, contributions, conclusion and references.

The team workflow, current PR base and reviewer instructions are in
[CONTRIBUTING.md](../../CONTRIBUTING.md). Use a feature branch, request another
teammate's review, and obtain approval before merging. `report.md` is the older
conversion reference; the section `.tex` files are the shared source of truth.

From the repository root:

```sh
bash scripts/build_report.sh
```

This uses Tectonic or latexmk to build `submission/upload/14_report.pdf` and
creates `submission/14_report_overleaf.zip`. Upload that ZIP to Overleaf with
`main.tex` selected as the main document. All section/image paths are relative.

The report currently has 20 pages including the cover. The assignment allows at
most 20 pages and minimum 10-point font. Shorten repetition if adding content,
then rebuild and inspect the PDF. Contribution statements, final B design choice,
references and the team-wide AI declaration still require team confirmation.

`scripts/prepare_report.py` is a one-time import/conversion tool, not the normal
editing/build command. It now refuses to overwrite the report without an explicit
`--overwrite` flag. Running it with that flag regenerates section files and can
replace teammates' manual edits; do not use it in the normal review workflow.

A selection is confirmed: a112 final, a115 follow-up with abort caveats, a10
separate. See [the Overleaf handoff](../../docs/overleaf-handoff.md) for the
proposed shared editing location; no Overleaf project has been created yet.
