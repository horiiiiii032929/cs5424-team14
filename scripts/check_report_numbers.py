#!/usr/bin/env python3
"""Check report table cells and job references against the staged submission CSVs.

Run from any directory after preparing submission/files/. This checks explicit
tables, not arbitrary prose, design semantics, or team-wide AI completeness.
"""
from pathlib import Path
import csv,json,re
R=Path(__file__).resolve().parents[1];S=R/'submission/files/citus_project_team_14';T=R/'submission/report'
checks=[];fail=[]
def rows(e,j,txn=False):
 p=S/f'expt_{e}/slurm-results/job-{j}/benchmark-results'/('transaction_metrics.csv' if txn else 'summary.csv')
 return list(csv.DictReader(p.open()))
def row(e,j,c,t=None):return next(x for x in rows(e,j,t is not None) if int(x['clients'])==c and (t is None or x['transaction']==t))
def compare(label,printed,actual):
 val=str(printed).replace(',','').strip();digits=len(val.split('.')[1]) if '.' in val else 0;tol=.5*10**(-digits)+.00051
 item=dict(label=label,reported=val,source=float(actual));checks.append(item)
 if abs(float(val)-float(actual))>tol:fail.append(item)
def nums(cell):return re.findall(r'(?<![A-Za-z])\d[\d,]*(?:\.\d+)?',cell)
def table(source,label):
 text=(T/source).read_text();after=text.split('\\label{'+label+'}',1)[1];return after.split('\\end{tabularx}',1)[0]
def datalines(text):return [l for l in text.splitlines() if '&' in l and re.match(r'^\s*(?:\d+|T\d+|Overall|b[06])\s*&',l)]
# All printed A baseline, matched-throughput and a112 latency table cells.
for l in datalines(table('sections/02_baseline_a.tex','tab:a-baseline')):
 a=[x.strip() for x in l.split('&')];c=int(a[0]);r=row('a0',918524,c)
 for cell,k in zip(a[1:],['overall_tps','overall_median_latency_ms','overall_p95_latency_ms','overall_p99_latency_ms','serialization_failures']):compare(f'a0/918524/c{c}/{k}',nums(cell)[0],r[k])
for l in datalines(table('sections/workload-a/a112_full.tex','tab:a-matched')):
 a=l.split('&');c=int(a[0]);base=row('a0',977740,c);opt=row('a112',977773,c)
 expected=[base['overall_tps'],opt['overall_tps'],float(opt['overall_tps'])/float(base['overall_tps']),base['serialization_failures'],opt['serialization_failures']]
 for i,(cell,val) in enumerate(zip(a[1:],expected)):compare(f'A matched c{c} col{i}',nums(cell)[0],val)
for l in datalines(table('sections/workload-a/a112_full.tex','tab:a112-latency')):
 a=l.split('&');c=int(a[0]);r=row('a112',977773,c)
 for cell,k in zip(a[1:],['overall_median_latency_ms','overall_p95_latency_ms','overall_p99_latency_ms','retried_transactions']):compare(f'a112 latency c{c} {k}',nums(cell)[0],r[k])
for l in datalines(table('sections/workload-a/a10_autocommit.tex','tab:a10')):
 a=l.split('&');t=a[0].strip()
 for cell,c in zip(a[1:],[1,4,8,64]):
  for val,e,j in zip(nums(cell),['a102','a10'],[965657,966308]):compare(f'{e}/{t}/c{c}/p50',val,row(e,j,c,t)['p50_latency_ms'])
for l in datalines(table('sections/workload-a/a115_timestamp_index.tex','tab:a115')):
 a=l.split('&');c=int(a[0]);
 for cell,j in zip(a[1:],[979909,979910]):
  if 'TPS' in cell:compare(f'a115/{j}/c{c}',nums(cell)[0],row('a115',j,c)['overall_tps'])
# Historical B baseline and each progressive comparison.
b=(T/'sections/04_baseline_b.tex').read_text();fields=['overall_tps','overall_median_latency_ms','overall_p95_latency_ms','overall_p99_latency_ms','retried_transactions','serialization_failures','pgbench_exit_code']
for l in datalines(b):
 a=l.split('&')
 if a[0].strip().isdigit():
  c=int(a[0]);r=row('b0',918781,c)
  for cell,k in zip(a[1:],fields):compare(f'B baseline c{c} {k}',nums(cell)[0],r[k])
jobs=[918781,928267,928583,929009,931181,931635,956803];opt=(T/'sections/05_optimized_b.tex').read_text();parts=re.split(r'\\subsection\*?\{\\texttt\{expt\\_\\allowbreak\{\}b\d\}\}',opt)[1:]
for i,part in enumerate(parts,1):
 for l in datalines(part):
  a=l.split('&');t=a[0].strip()
  if '\\rightarrow' not in l:continue
  keys=['overall_tps','overall_median_latency_ms','overall_p95_latency_ms','overall_p99_latency_ms'] if t=='Overall' else ['tps','p50_latency_ms','p95_latency_ms','p99_latency_ms']
  for cell,k in zip(a[1:],keys):
   for val,n in zip(nums(cell),[i-1,i]):compare(f'b{n}/c64/{t}/{k}',val,row(f'b{n}',jobs[n],64,None if t=='Overall' else t)[k])
# B historical transaction means and shares of accumulated transaction latency.
for text,e,j in [(b,'b0',918781),(parts[1],'b2',928583)]:
 for l in datalines(text):
  if '\\%' not in l or '\\rightarrow' in l:continue
  a=l.split('&');t=a[0].strip()
  if not re.fullmatch('T[1-9]',t) or len(a)!=5:continue
  for offset,c in [(1,1),(3,64)]:
   r=row(e,j,c,t);allr=[x for x in rows(e,j,True) if int(x['clients'])==c];den=sum(float(x['avg_latency_ms'])*int(x['successful_transactions']) for x in allr)
   compare(f'{e}/{t}/c{c}/avg',nums(a[offset])[0],r['avg_latency_ms']);compare(f'{e}/{t}/c{c}/share',nums(a[offset+1])[0],100*float(r['avg_latency_ms'])*int(r['successful_transactions'])/den)
for l in datalines(opt):
 a=l.split('&');e=a[0].strip()
 if e not in ['b0','b6']:continue
 j=1029473 if e=='b0' else 1030000;r=row(e,j,1)
 for cell,k in zip(a[1:],fields[:4]):compare(f'{e}/{j}/c1/{k}',nums(cell)[0],r[k])
# Three read-only diagnostic table values.
for match in re.finditer(r'\\expt\{(a\d+)\}\s*&\s*(\d+)\s*&[^\n]*&\s*(\d+\.\d+)', table('sections/workload-a/a112_a113_read_only.tex','tab:a-read-only')):
 e,j,value=match.groups();compare(f'{e}/{j}/diagnostic TPS',value,row(e,int(j),4)['overall_tps'])
# Exact report job references and experiment identifiers must resolve in archive.
alltext='\n'.join(p.read_text() for p in T.rglob('*.tex'));ids=set(re.findall(r'\b(?:9\d{5}|10\d{5})\b',alltext));missing_jobs=[j for j in sorted(ids) if not list(S.glob(f'expt_*/slurm-results/job-{j}'))]
result={'numeric_cells_checked':len(checks),'mismatches':fail,'explicit_job_ids':sorted(ids),'missing_jobs':missing_jobs}
(R/'submission/report-numeric-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

raise SystemExit(bool(fail or missing_jobs))
