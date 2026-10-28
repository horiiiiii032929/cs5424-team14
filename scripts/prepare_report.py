#!/usr/bin/env python3
"""Convert the frozen shared report into an editable local LaTeX review draft."""
from pathlib import Path
import re
import sys
import subprocess

if '--overwrite' not in sys.argv:
    raise SystemExit('This conversion overwrites the shared report. Edit section .tex files and use build_report.sh. To intentionally regenerate, pass --overwrite (and --from-edited for report.md).')

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'submission/report'
text = (OUT / 'report.md').read_text() if '--from-edited' in sys.argv else (ROOT / 'submission/_build/report-source-20261028.md').read_text()
text = text[text.index('# 1. Team Contribution'):]
text = text.replace('Section 1 lists the team member contributions to the project: for each team member, state the tasks contributed by that student.',
    'The following contribution allocation is a draft for each member to confirm before submission.')
text = text.replace('| Hikaru | A |  |', '| Hikaru | A | Implemented a101-a115, correctness tooling, cluster evidence audits, figures and A analysis; assembled the submission draft. |')
text = text.replace('| Kelvin | A |  |', '| Kelvin | A | Ran a102 and a10/a11/a12/a14; investigated write-path tuning and drafted the write-path analysis. |')
text = text.replace('| Dessi | B |  |', '| Dessi | B | Baseline installation and B b0-b6 design/results and B analysis; confirm individual attribution with the B pair. |')
text = text.replace('| Xincheng | B |  |', '| Xincheng | B | B placement/index proposals and supplementary B experiments; confirm precise implementation, validation and writing contributions. |')
text = text.replace('Workload A is 70% writes', 'Workload A is 75% writes')
text = text.replace('a112 remains provisional pending final team selection.', 'a112 is the recommended A design, subject to final confirmation by the A pair.')
text = text.replace('pending Kelvin’s agreement', 'subject to the A pair’s final confirmation')
text = text.replace('Final selection requires Kelvin/the A pair’s agreement before the 23 October cutoff.', 'The A pair must confirm the final selection before submission.')
text = text.replace('and adds exactly one change.', 'and tests the changes described below. In particular, a11 uses a14 as its VACUUM/CHECKPOINT control.')
text = text.replace('All four completed jobs exited 0 and passed all six post-run correctness checks:', 'All four completed Slurm jobs exited 0 and passed all six post-run correctness checks; a10/c32 nevertheless has pgbench exit 2 and is excluded from clean comparisons. The invariant checks found')
text = text.replace('We keep it.', 'It remains a useful separately measured result; incorporation into a112 has not been benchmarked.')
text = text.replace('and is kept.', 'and is retained as a separately measured result. A combined a10/a112 design has not been benchmarked.')
text = text.replace('although stock, order and global-ID checks are still missing.',
    'and a separate correctness job (1031186) subsequently checked negative inventory, order-total equality and duplicate inventory/order-item IDs at three checkpoints with zero violations, and passed a controlled forward/reverse T7 conservation test. Its four-client measurement used 300 seconds and had zero failed records, four retry attempts and phase exits of zero. These separate-run checks do not retroactively validate every earlier benchmark.')
text = text.replace('## Because this rewrite', 'Because this rewrite')
text = text.replace('- [ ] ', '- ').replace('\x0b',' ').replace('[Page Break]','')
text = text.replace('**Serialization failures**','**Serial. failures**').replace('**`pgbench_exit_code`**','**Exit code**')
text = re.sub(r'Working draft updated 22 October 2026[^\n]*\n', '', text)
text = text.replace('Hikaru’s contributions include A implementations a101–a115, correctness/local benchmark tooling, course diagnostics and evidence review, exact validator repair, repository setup, figures and A drafting. Dessi’s B placement ideas are credited in a111–a115; Kelvin owns a102’s original cluster run and the write-side experiments. Confirm full names and contribution statements with the team. Declare both Codex and Claude Code where used and retain their interaction records.',
    'Dessi’s B placement ideas are credited in a111-a115; Kelvin owns the original a102 cluster run and the write-path experiments. Individual contribution statements are collected in Section 1.')
text = re.sub(r'!\[\]\([^\n]+\)', lambda m: '![A figure](images/'+ ('workload-a-baseline-indexes.png' if 'ALKuztay' in m[0] else 'workload-a-full-matched.png') + ')', text)
text = text.replace('a112 is the provisional A design', 'a112 is the recommended A design')

# Preserve the full, editable source alongside its typeset form.
(OUT / 'report.md').write_text(text.replace('.png)', '.pdf)'))

def esc(s):
    trans={'’':"'",'‘':"'",'“':'"','”':'"','–':'-','—':' -- ','−':'-', '\u000b':' ', '\u00a0':' ', '…':'...', '×':r'\ensuremath{\times}', '→':r'\ensuremath{\rightarrow}', '≥':r'\ensuremath{\geq}', '≤':r'\ensuremath{\leq}', '≈':r'\ensuremath{\approx}'}
    # Escape literal source before introducing our own LaTeX commands.
    result=''
    for c in s:
        if c in trans: result+=trans[c]
        elif c in '\\{}$&#%_': result+='\\'+c if c!='\\' else r'\textbackslash{}'
        elif c=='~': result+=r'\textasciitilde{}'
        elif c=='^': result+=r'\textasciicircum{}'
        elif ord(c)>127: result+='?' if c=='\ufffc' else c
        else: result+=c
    return result

def inline(s):
    pieces=[];pos=0
    pat=r'\[([^\]]+)\]\((https?://[^)]+)\)|`([^`]+)`|\*\*([^*]+)\*\*'
    for m in re.finditer(pat,s):
        pieces.append(esc(s[pos:m.start()]))
        if m[1]: pieces.append(r'\href{'+m[2].replace('%',r'\%').replace('#',r'\#')+'}{'+esc(m[1])+'}')
        elif m[3]: pieces.append(r'\texttt{'+esc(m[3]).replace(r'\_',r'\_\allowbreak{}')+'}')
        else: pieces.append(r'\textbf{'+inline(m[4])+'}')
        pos=m.end()
    pieces.append(esc(s[pos:]))
    return ''.join(pieces)

preamble=r'''\documentclass[11pt,a4paper]{article}
\usepackage[margin=20mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern,graphicx,longtable,booktabs,array,hyperref,enumitem,fancyhdr,needspace}
\hypersetup{colorlinks=true,urlcolor=blue,linkcolor=black,pdftitle={Team 14 Distributed Databases Report},pdfauthor={Team 14}}
\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt}
\setlength{\emergencystretch}{3em}
\setlist{nosep,leftmargin=1.5em}
\pagestyle{fancy}\fancyhf{}\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0pt}
\begin{document}
\begin{titlepage}
\vspace*{22mm}
{\Large CS4224 / CS5424 Distributed Databases\par}
\vspace{10mm}
{\Huge Project Report\par}
\vspace{7mm}{\LARGE Team 14\par}
\vspace{15mm}
Ang Wei Hao Desmond\par
Cai Xincheng\par
Horinouchi Hikaru\par
Kelvin Ting Hong Xiang\par
\vspace{15mm}
AI tools used: OpenAI Codex and Claude Code.\par
\vfill
Review draft prepared 28 October 2026.\par
Submission deadline: 30 October 2026, 23:59 Singapore time.\par
\end{titlepage}
'''

lines=text.splitlines(); body=[];i=0; image_count=0
while i<len(lines):
    line=lines[i].strip()
    if not line or line=='#': i+=1;continue
    if line=='# [Page Break]': body.append(r'\clearpage');i+=1;continue
    if line.startswith('!['):
        path=re.search(r'\(([^)]+)\)',line)[1].replace('.png','.pdf')
        following=i+1
        while following<len(lines) and not lines[following].strip(): following+=1
        caption=lines[following].strip() if following<len(lines) and lines[following].strip().startswith('Figure ') else ''
        body.append(r'\begin{figure}[htbp]\centering\includegraphics[width=\linewidth]{'+path+r'}')
        if caption: body.append(r'\par\smallskip\raggedright '+inline(caption))
        body.append(r'\end{figure}')
        i=following+1 if caption else i+1
        continue
    if line.startswith('|'):
        table=[]
        while i<len(lines) and lines[i].strip().startswith('|'):
            cells=lines[i].strip().strip('|').split('|')
            if not all(re.fullmatch(r'\s*:?-+:?\s*',c) for c in cells): table.append([c.strip() for c in cells])
            i+=1
        n=len(table[0]);width=(170-4*n)/n
        if len(table)<=7: body.append(r'\needspace{10\baselineskip}')
        spec=''.join(r'>{\raggedright\arraybackslash}p{'+str(round(width,2))+'mm}' for _ in range(n))
        body.append(r'{\fontsize{10.5}{12.5}\selectfont\setlength{\tabcolsep}{2mm}\renewcommand{\arraystretch}{1.15}')
        body.append(r'\begin{longtable}{'+spec+'}'+r'\toprule')
        for j,row in enumerate(table):
            body.append(' & '.join(inline(c) for c in row)+r' \\')
            if j==0:body.append(r'\midrule\endhead')
        body.append(r'\bottomrule\end{longtable}}')
        continue
    heading=re.match(r'^(#{1,3})\s+(.+)',line)
    if heading:
        level=len(heading[1]);title=heading[2]
        if level==1:title=re.sub(r'^\d+\.\s*','',title)
        body.append(r'\needspace{4\baselineskip}'+'\\'+['section','subsection','subsubsection'][level-1]+('{' if level==1 and title!='References' else '*{')+inline(title)+'}')
        i+=1;continue
    if line.startswith('- '):
        body.append(r'\begin{itemize}')
        while i<len(lines) and lines[i].strip().startswith('- '):
            body.append(r'\item '+inline(lines[i].strip()[2:]));i+=1
        body.append(r'\end{itemize}');continue
    line=re.sub(r'^\d+\.\s+','',line)
    if line.startswith('*') and line.endswith('*'):body.append(r'{\itshape '+inline(line.strip('* '))+'}'+r'\par')
    else:body.append(inline(line)+r'\par')
    i+=1

(OUT/'main.tex').write_text(preamble+'\n'.join(body)+'\n\\end{document}\n')
print('Prepared local LaTeX report with',len(text.split()),'words')
subprocess.run([sys.executable,str(ROOT/'scripts/split_report.py')],check=True)
