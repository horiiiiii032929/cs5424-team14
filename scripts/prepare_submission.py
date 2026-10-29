#!/usr/bin/env python3
"""Assemble a reviewable result ZIP, preserving conflicting source snapshots."""
from pathlib import Path
import csv, hashlib, json, re, shutil, zipfile
from organize_submission import RETIRED_EXPERIMENTS

ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/'submission/files/citus_project_team_14'
BUILD=ROOT/'submission/_build'
UPLOAD=ROOT/'submission/upload'
REMOTE=BUILD/'remote-20261028/raw'
RENAMES={'expt_xc_b1':'expt_b201','expt_xc_b2':'expt_b202','expt_b3v_control':'expt_b203','expt_b3v_cover':'expt_b204'}
PROVENANCE=[]
CONFLICTS=[]

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def copy_file(src,dest,source):
    if src.name in {'.DS_Store','AGENTS.md'} or src.name.startswith('.env'):
        return
    if dest.exists():
        if digest(src)!=digest(dest):
            CONFLICTS.append(dict(source=str(src.relative_to(ROOT)),destination=str(dest.relative_to(ROOT))))
            return
    else:
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dest)
    PROVENANCE.append(dict(destination=str(dest.relative_to(STAGE)),source=str(src.relative_to(ROOT)),sha256=digest(src),collection=source))

def merge_tree(src,dest,label):
    for p in sorted(src.rglob('*')):
        if p.is_file() and not any(part in RETIRED_EXPERIMENTS for part in p.relative_to(src).parts) and '.git' not in p.parts and '__pycache__' not in p.parts:
            copy_file(p,dest/p.relative_to(src),label)

if STAGE.exists():
    raise SystemExit('Staging directory exists. Preserve it or remove only the generated submission/files directory before rebuilding.')
if not REMOTE.exists(): raise SystemExit('Remote readback must be extracted first.')
STAGE.mkdir(parents=True)
UPLOAD.mkdir(parents=True,exist_ok=True)
merge_tree(ROOT/'citus_project_team_14',STAGE,'repository baseline and A implementations')

# Missing experiment source comes from the independent archived Kelvin/B imports.
for dirname in ['cluster-import-20261019','b-branch-review-20261022/raw']:
    source=ROOT/'results'/dirname
    for expt in sorted(source.glob('expt_*')):
        if expt.name in RETIRED_EXPERIMENTS: continue
        if not (STAGE/expt.name).exists(): merge_tree(expt,STAGE/expt.name,dirname)

# Merge job outputs and retain each import's available source separately.
archives=['cluster-import-20261019','cluster-smoke-20261019',
          'cluster-diagnostic-original-20261019','cluster-diagnostic-20261019',
          'cluster-full-20261019','cluster-diagnostic-t6-20261020',
          'cluster-full-a115-20261022','b-branch-review-20261022/raw']
for label in archives:
    base=ROOT/'results'/label
    if (base/'citus_project_team_14').exists(): base=base/'citus_project_team_14'
    for expt in sorted(base.glob('expt_*')):
        if not expt.is_dir() or expt.name in RETIRED_EXPERIMENTS: continue
        dest=STAGE/expt.name
        if not dest.exists(): merge_tree(expt,dest,label)
        if (expt/'slurm-results').exists(): merge_tree(expt/'slurm-results',dest/'slurm-results',label)
        for p in expt.glob('citus-*'):
            if p.is_file():copy_file(p,dest/p.name,label)
        snap=dest/'source_snapshots'/label.split('/')[0]
        for p in expt.iterdir():
            if p.name=='slurm-results' or p.name.startswith('citus-'): continue
            if p.is_dir():merge_tree(p,snap/p.name,label)
            elif p.is_file():copy_file(p,snap/p.name,label)

# Complete retained live team folders; never resurrect owner-retired experiments.
for expt in sorted(REMOTE.glob('expt_*')):
    if expt.name in RETIRED_EXPERIMENTS: continue
    dest=STAGE/RENAMES.get(expt.name,expt.name)
    if not dest.exists():merge_tree(expt,dest,'live remote readback 2026-10-28')
    if (expt/'slurm-results').exists():merge_tree(expt/'slurm-results',dest/'slurm-results','live remote readback 2026-10-28')
    for p in expt.glob('citus-*'):
        if p.is_file():copy_file(p,dest/p.name,'live remote readback 2026-10-28')
    for p in expt.iterdir():
        if p.name=='slurm-results' or p.name.startswith('citus-'):continue
        snap=dest/'source_snapshots/live-readback-20261028'/p.name
        if p.is_dir():merge_tree(p,snap,'live remote readback 2026-10-28')
        elif p.is_file():copy_file(p,snap,'live remote readback 2026-10-28')

# Relocate supplementary results into the corresponding expt_aN/expt_bN tree.
supplementary=REMOTE/'supplementary-results'
if supplementary.exists():
    for job in sorted(supplementary.rglob('job-*')):
        if not job.is_dir():continue
        parts=job.relative_to(supplementary).parts
        expt='expt_b0' if 'b0' in parts else 'expt_b6'
        merge_tree(job,STAGE/expt/'slurm-results'/job.name,'live supplementary '+str(job.relative_to(supplementary)))

# Include evidence reviews and reproduction helpers, without duplicating raw logs.
evidence=STAGE/'evidence'
for folder in ['cluster-import-20261019','cluster-smoke-20261019','cluster-diagnostic-original-20261019',
               'cluster-diagnostic-20261019','cluster-full-20261019','cluster-diagnostic-t6-20261020',
               'cluster-full-a115-20261022','b-branch-review-20261022','live-status-20261028']:
    for p in (ROOT/'results'/folder).iterdir():
        if p.is_file() and p.suffix in {'.md','.json','.csv','.txt'} and p.name!='shared-report-readback.txt':
            copy_file(p,evidence/folder/p.name,folder)
for folder in ['correctness-native-20261014','correctness-verified-20261014','followup-20261019',
               'correctness-deferrable-20261019','correctness-summary-20261019',
               't6-plan-check-20261019','local-pilot-20261014','deferrable-pilot-20261019','summary-pilot-20261019',
               'correctness-readonly-20261019','correctness-join-placement-20261019',
               'scalable-validator-checks-20261019','readonly-pilot-20261019',
               'join-placement-pilot-20261019','local-native-20261014']:
    merge_tree(ROOT/'results'/folder,evidence/'local-only'/folder,folder)
for p in (ROOT/'scripts').glob('*.py'):copy_file(p,STAGE/'analysis_scripts'/p.name,'repository analysis scripts')

DESCRIPTIONS={
'expt_a0':'Preserved A baseline 918524 and fresh matched baseline 977740.',
'expt_a10':'Kelvin: single-statement autocommit for T2/T5/T8/T9; c32 measured abort.',
'expt_a11':'Kelvin: fillfactor 80 with VACUUM/CHECKPOINT control.',
'expt_a12':'Kelvin: synchronous_commit off; durability trade-off, not recommended.',
'expt_a14':'Kelvin: post-load VACUUM/CHECKPOINT control.',
'expt_a101':'Merchant colocation; local and cluster abort caveats.',
'expt_a102':'Lookup indexes; preserve c16 warmup caveat in job 965657.',
'expt_a103':'One-call place-order implementation; local evidence only.',
'expt_a104':'Maintained exact daily sales summaries; local evidence only.',
'expt_a105':'work_mem 64MB; local evidence only.',
'expt_a106':'Executor pool 2; local evidence only.',
'expt_a107':'Executor pool 8; local evidence only.',
'expt_a108':'Combined merchant placement/index/function/summary; local abort caveats.',
'expt_a109':'Merchant colocation plus READ ONLY; local evidence only.',
'expt_a110':'Combined design plus READ ONLY; local evidence only.',
'expt_a111':'Product/order join colocation on lookup indexes; diagnostic and smoke results.',
'expt_a112':'Recommended A design: a111 plus READ ONLY; full seed-42 and seed-7 repeat (c64 warmup caveat).',
'expt_a113':'a112 plus READ ONLY DEFERRABLE; diagnostic only.',
'expt_a114':'a112 with striped exact daily summaries; rejected diagnostic.',
'expt_a115':'a112 with orders(created_at); diagnostic/full results have documented repeated aborts.',
'expt_b0':'B baseline, historical and supplementary matched/T6/T7 runs; failures remain visible.',
'expt_b1':'B product/inventory colocation; historical matrix.',
'expt_b2':'B order/item colocation; historical matrix.',
'expt_b3':'B T6 covering index and VACUUM; aborted concurrent cases.',
'expt_b4':'B READ ONLY, coordinator T6 timestamps and query-plan capture.',
'expt_b5':'B merchant/customer order index.',
'expt_b6':'B static historical T6 rollup, matched supplementary results and separate correctness harness.',
'expt_xc_b1':'Xincheng supplementary product-based inventory/T7 experiments; inspect actual config for mix.',
'expt_xc_b2':'Xincheng supplementary T6 time-index experiment; inspect actual config for mix.',
'expt_b3v_control':'Supplementary B T6 control; current source readback, confirm attribution with B pair.',
'expt_b3v_cover':'Supplementary B T6 covering-index control; confirm attribution with B pair.'}

for original,submitted in RENAMES.items():
    DESCRIPTIONS[submitted]=DESCRIPTIONS[original]+' Original folder: '+original+'.'

inventory=[]
for expt in sorted(STAGE.glob('expt_*')):
    jobs=[]
    for job in sorted((expt/'slurm-results').glob('job-*')):
        summary=job/'benchmark-results/summary.csv'
        count=len(list(csv.DictReader(summary.open()))) if summary.exists() else 0
        jobs.append(dict(job=job.name,summary_rows=count))
    inventory.append(dict(experiment=expt.name,description=DESCRIPTIONS.get(expt.name,'Supplementary experiment; confirm description with owner.'),jobs=jobs))
    if not (expt/'run.sh').exists() or not (expt/'transactions').is_dir():
        raise RuntimeError('Missing source structure: '+expt.name)
    notes='\n\n## Submission packaging note\n\n'+DESCRIPTIONS.get(expt.name,'Supplementary experiment.')+'\n'
    notes+='Available imported job folders: '+(', '.join(j['job'] for j in jobs) or 'None; do not infer a course-scale result.')+'.\n'
    notes+='Current or imported source variants are retained under source_snapshots/. Only recorded runtime hashes establish runtime source identity.\n'
    readme=expt/'README.md'
    readme.write_text((readme.read_text() if readme.exists() else '# '+expt.name+'\n')+notes)

(STAGE/'experiment-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
(STAGE/'packaging-provenance.json').write_text(json.dumps(PROVENANCE,indent=2)+'\n')
(STAGE/'packaging-conflicts.json').write_text(json.dumps(CONFLICTS,indent=2)+'\n')
if CONFLICTS:raise RuntimeError(f'{len(CONFLICTS)} output collisions need review; archive not built.')
readme='''# CS4224 / CS5424 Team 14 result files

This archive assembles the preserved baseline, A/B experiment implementations,
course-cluster job outputs and separate local validation evidence. Recommended A
design: a112, subject to the A pair confirming it. B selection requires the B pair
to confirm b6 and the report wording. Failed and cancelled attempts are preserved;
their inclusion does not certify clean performance.

Each expt_* directory contains run.sh, transactions/, available slurm-results/job-*/
and original citus-*.out/.err. source_snapshots/ preserves scripts from earlier
imports and the 28 October readback without replacing the selected top-level
source. Readback hashes are distinct from runtime code-sha256.txt evidence.
Supplementary folder names are normalized to the required expt_bN format:
expt_xc_b1 -> expt_b201. The owner-retired b202-b204 variants are excluded.
The original names and file paths remain in the
provenance map and source snapshots. Original file bytes are preserved.

The supplementary b0/b6 jobs originally stored under supplementary-results/ are
relocated into the corresponding expt_b0/expt_b6/slurm-results/job-*/ directories.
Their original paths are recorded in packaging-provenance.json. Job 1031186 is a
separate 300-second correctness measurement, not a full-matrix replacement.

evidence/ contains original audit readmes and manifests (whose paths refer to
their original archives), and local-only/ contains small-scale checks and pilots.
Local timing must not be reported as course-cluster performance. No missing
cluster run is fabricated for variants tested only locally.

Use experiment-inventory.json for the complete job map and checksums.sha256 for
archive byte verification. Preserve phase exits, failed records and retry counts
when interpreting summary.csv. Slurm COMPLETED is not a clean benchmark test.

The provided installer is preserved for completeness. It removes an existing
installation: reuse the course installation instead of casually rerunning it.

## Experiments

'''
for x in inventory:
    readme+='- '+x['experiment']+': '+x['description']+' Jobs: '+(', '.join(j['job'] for j in x['jobs']) or 'no imported cluster job')+'.\n'
(STAGE/'README.md').write_text(readme)
files=sorted(p for p in STAGE.rglob('*') if p.is_file())
(STAGE/'checksums.sha256').write_text(''.join(digest(p)+'  '+str(p.relative_to(STAGE))+'\n' for p in files))
archive=UPLOAD/'14_files.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(STAGE.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(STAGE.parent))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert all(x.startswith('citus_project_team_14/') for x in z.namelist())
print('Created',archive, 'experiments',len(inventory),'jobs',sum(len(x['jobs']) for x in inventory),'files',len(files)+1,'bytes',archive.stat().st_size)
