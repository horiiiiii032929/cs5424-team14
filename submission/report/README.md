# Team 14 report — upload-ready LaTeX

## Upload to Overleaf

1. In Overleaf, choose **New Project → Upload Project**.
2. Upload **14_report_overleaf.zip**.
3. Select **main.tex** as the main document and **pdfLaTeX** as the compiler.
4. Click **Recompile**. Overleaf runs BibTeX automatically.
5. Download the finished PDF and name it **14_report.pdf** for Canvas.

No custom fonts, shell escape, Python, or external asset downloads are required
to compile the uploaded project. The ZIP opens directly at main.tex.

## Where to edit

| File | Edit here |
|---|---|
| metadata.tex | Names, team number, title, date and AI tools |
| report-style.tex | Shared fonts, margins, spacing, table and caption style |
| main.tex | Order of sections |
| sections/00_cover.tex | Cover layout; values come from metadata |
| sections/01_contributions.tex | Individual contributions |
| sections/02_baseline_a.tex | Section 2 — Hikaru and Kelvin |
| sections/03_optimized_a.tex | Section 3 introduction and experiment order |
| sections/workload-a/*.tex | One experiment or topic per file |
| sections/04_baseline_b.tex | Section 4 — Desmond and Xincheng; preserved |
| sections/05_optimized_b.tex | Section 5 — Desmond and Xincheng; preserved |
| sections/06_conclusion.tex | Section 6 — joint conclusions |
| sections/07_references.tex | Bibliography commands |
| references.bib | Reference details |
| images/*.pdf | Self-contained vector figures |

The A modules include a102, a101, a111, a112/a113 diagnostics, a112 full results,
a114, a115, and Kelvin's a10, a14, a11 and a12. Changes stay close to their evidence.
The older report.md in the repository is an archived conversion reference, is
not included in this ZIP, and should not be updated in parallel.

## Normal editing

Write paragraphs as ordinary LaTeX; a blank line starts a new paragraph. Use
standard section, subsection, table, figure, label and ref commands. Numbering
for the rewritten sections is automatic. Three optional helpers are available:

- \expt{a112} prints the experiment identifier.
- \code{shared_buffers} prints an identifier and permits line breaks.
- \evidence{...} adds a short provenance note.

Use \citep{pgbench} to cite an entry from references.bib.
Use Table~\ref{tab:a-matched} or Section~\ref{sec:a112-full} instead of typing
numbers. Add \label immediately after a table/figure caption. Add a new module
with an \input line in sections/03_optimized_a.tex.

Tables use tabularx: Y is a flexible left-aligned column, Z centered and R
right-aligned. r/l/c are natural-width columns. Example:

~~~tex
\begin{table}[htbp]
\caption{Results with the run and measurement conditions identified.}
\label{tab:example}
\begin{tabularx}{\linewidth}{@{}Yr@{}}
\toprule
Experiment & TPS \\
\midrule
\expt{a112} & 54.238 \\
\bottomrule
\end{tabularx}
\end{table}
~~~

Do not use resizebox or shrink fonts to fit a table. Shorten headings, wrap text,
or split the table. Body text is 11 pt and table/caption/reference text is 10.5 pt.
Workload B retains its original manual table/figure labels and formatting so
teammates' text is preserved; converting B can be a separate reviewed change.

## Build locally

From the repository root:

~~~sh
bash scripts/build_report.sh
~~~

This uses Tectonic or latexmk and writes:
- submission/upload/14_report.pdf
- submission/14_report_overleaf.zip

To create only the upload ZIP, with no local LaTeX compiler:

~~~sh
bash scripts/build_report.sh --source-only
~~~

The desktop LaTeX editor can also open this project and preview main.tex.
Never run scripts/prepare_report.py --overwrite on this maintained source:
that legacy importer can replace manual edits and the modular structure.

## Before the final submission

- Confirm all names, individual contributions, and every AI tool actually used.
- The B members should confirm their attribution and final B selection.
- Preserve phase aborts, failures, hardware differences and validation scope.
- Keep a112 as the measured final A design; a10 is separate and a115 is follow-up.
- Check the entire compiled PDF, including the cover, is at most 20 pages.
- Keep all text at least 10 pt, including figures and references.
- Review the bibliography and complete the separate team-wide AI interaction ZIP.
- The Overleaf ZIP is for editing. Canvas receives 14_report.pdf, 14_files.zip,
  and 14_ai_tool.zip in their respective assignments.

This is a reviewable draft, not evidence that team review or Canvas upload is
complete. The PDF cover uses the planned submission date; it is not a receipt.

Repository contributions follow the peer-review workflow in CONTRIBUTING.md
at the repository root. Obtain another member's approval before merging.
