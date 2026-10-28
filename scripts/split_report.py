#!/usr/bin/env python3
"""Split a freshly generated monolithic report into the shared section files."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
main=ROOT/'submission/report/main.tex'
s=main.read_text()
if r'\input{sections/' in s:
    print('Report already uses section files; no changes made.')
    raise SystemExit(0)
start=s.index(r'\begin{document}')+len(r'\begin{document}')
end=s.rindex(r'\end{document}')
body=s[start:end].strip()
markers=[
('00_cover.tex',r'\begin{titlepage}'),
('01_contributions.tex',r'\needspace{4\baselineskip}\section{Team Contribution}'),
('02_baseline_a.tex',r'\needspace{4\baselineskip}\section{Task 1: Baseline design for workload A}'),
('03_optimized_a.tex',r'\needspace{4\baselineskip}\section{Task 2: Optimized design for workload A}'),
('04_baseline_b.tex',r'\needspace{4\baselineskip}\section{Task 3: Baseline design for Workload B}'),
('05_optimized_b.tex',r'\needspace{4\baselineskip}\section{Task 4: Optimized design for Workload B}'),
('06_conclusion.tex',r'\needspace{4\baselineskip}\section{Conclusion}'),
('07_references.tex',r'\needspace{4\baselineskip}\section*{References}')]
out=main.parent/'sections';out.mkdir(exist_ok=True)
for i,(name,marker) in enumerate(markers):
    a=body.index(marker);b=body.index(markers[i+1][1]) if i+1<len(markers) else len(body)
    (out/name).write_text('% Edit this section in a feature branch and request peer review.\n'+body[a:b].strip()+'\n')
main.write_text(s[:start]+'\n'+'\n'.join(r'\input{sections/'+name+'}' for name,_ in markers)+'\n'+r'\end{document}'+'\n')
print('Split report into eight shared section files.')
