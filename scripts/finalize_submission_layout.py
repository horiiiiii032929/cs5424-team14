#!/usr/bin/env python3
"""Separate local-only designs from the required Slurm experiment submission tree."""
from pathlib import Path
import csv,hashlib,json,re,shutil,zipfile

ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/'submission/files/citus_project_team_14'
inventory=json.loads((STAGE/'experiment-inventory.json').read_text())
local=[];cluster=[]
for entry in inventory:
    name=entry['experiment'];source=STAGE/name
    if not entry['jobs']:
        target=STAGE/'supporting_implementations/local_only'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        if source.exists():shutil.move(str(source),str(target))
        entry['path']=str(target.relative_to(STAGE));entry['classification']='local-only implementation; no Slurm benchmark'
        local.append(entry)
    else:
        entry['classification']='Slurm experiment (including preserved failed attempts)'
        cluster.append(entry)

# Repeated execution uses the already established support inventory.
support_file=STAGE/'supporting-implementation-inventory.json'
if support_file.exists() and not local:local=json.loads(support_file.read_text())
(STAGE/'experiment-inventory.json').write_text(json.dumps(cluster,indent=2)+'\n')
support_file.write_text(json.dumps(local,indent=2)+'\n')
provenance=json.loads((STAGE/'packaging-provenance.json').read_text())
for item in provenance:
    for entry in local:
        prefix=entry['experiment']+'/'
        if item['destination'].startswith(prefix):
            item['destination']='supporting_implementations/local_only/'+item['destination']
(STAGE/'packaging-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
readme=STAGE/'README.md';s=readme.read_text()
s=s.replace('Each expt_* directory contains run.sh, transactions/, available slurm-results/job-*/',
    'Each top-level expt_* directory contains run.sh, transactions/, slurm-results/job-*/')
note='''## Local-only supporting implementations

The eight designs a103-a110 have no recorded Slurm experiment. Their source is
preserved under supporting_implementations/local_only/, with descriptions in
supporting-implementation-inventory.json. Local test outputs are retained under
evidence/local-only/. They are not included among the top-level course-cluster
experiments and do not establish course-scale performance. No Slurm output has
been invented to fill a missing run.

'''
if '## Local-only supporting implementations' not in s:s=s.replace('## Experiments\n',note+'## Experiments\n')
for entry in local:
    s=re.sub(r'^- '+re.escape(entry['experiment'])+r':.*\n','',s,flags=re.M)
readme.write_text(s)
for entry in cluster:
    expt=STAGE/entry['experiment']
    assert re.fullmatch(r'expt_[ab]\d+',expt.name)
    assert (expt/'run.sh').is_file() and (expt/'README.md').is_file()
    assert len(list((expt/'transactions').glob('*.sql')))==9
    for job in (expt/'slurm-results').glob('job-*'):
        for suffix in ['out','err']:assert (expt/f'citus-{job.name[4:]}.{suffix}').is_file()
files=sorted(p for p in STAGE.rglob('*') if p.is_file() and p.name!='checksums.sha256')
(STAGE/'checksums.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(STAGE))+'\n' for p in files))
target=ROOT/'submission/upload/14_files.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(STAGE.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(STAGE.parent))
with zipfile.ZipFile(target) as z:assert z.testzip() is None
print('Final layout:',len(cluster),'Slurm experiment folders,',len(local),'local-only supporting implementations;',sum(len(e['jobs']) for e in cluster),'job folders; ZIP CRC passed.')
