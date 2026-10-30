#!/usr/bin/env python3
"""Reconcile submission documentation and evidence without rewriting experiment code/logs."""
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
EXTRA_EVIDENCE = (
    'correctness-readonly-20261019', 'correctness-join-placement-20261019',
    'scalable-validator-checks-20261019', 'readonly-pilot-20261019',
    'join-placement-pilot-20261019', 'local-native-20261014',
)
# These source variants have only inherited b2 results, not independent runs.
# Preserve them as supporting source rather than top-level experiments.
# b202 was also retired from active development, but its two real jobs must be
# retained under the brief's requirement to submit all experiment outputs.
RETIRED_EXPERIMENTS = frozenset(('expt_b203', 'expt_b204',
                               'expt_b3v_control', 'expt_b3v_cover'))
SOURCE_ONLY_VARIANTS = {'expt_b3v_control': 'expt_b203', 'expt_b3v_cover': 'expt_b204'}
INHERITED = {('expt_b201', 'job-918781'): 'expt_b0'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def organize(stage):
    retired = [p.name for p in stage.glob('expt_*') if p.name in RETIRED_EXPERIMENTS]
    if retired:
        raise RuntimeError(f'Rebuild from prepare_submission.py to exclude retired experiments: {retired}')
    provenance_file = stage / 'packaging-provenance.json'
    provenance = json.loads(provenance_file.read_text())
    known = {(p['source'], p['destination']) for p in provenance}

    def copy_preserved(src, dest, collection):
        if dest.exists() and digest(src) != digest(dest):
            raise RuntimeError(f'Refusing to overwrite differing evidence: {dest}')
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            shutil.copy2(src, dest)
        pair = (str(src.relative_to(ROOT)), str(dest.relative_to(stage)))
        if pair not in known:
            provenance.append(dict(source=pair[0], destination=pair[1],
                                   sha256=digest(src), collection=collection))
            known.add(pair)

    for folder in EXTRA_EVIDENCE:
        source = ROOT / 'results' / folder
        if not source.is_dir():
            raise RuntimeError(f'Missing supporting evidence: {source}')
        for src in sorted(source.rglob('*')):
            if src.is_file() and src.name != '.DS_Store':
                copy_preserved(src, stage / 'evidence/local-only' / folder / src.relative_to(source),
                               'supporting local evidence; not a Slurm benchmark')

    for original, submitted in SOURCE_ONLY_VARIANTS.items():
        source = ROOT / 'submission/_build/remote-20261028/raw' / original
        if not source.is_dir():
            raise RuntimeError(f'Missing historical source variant: {source}')
        for src in sorted(source.rglob('*')):
            if src.is_file() and src.name not in ('.DS_Store', 'AGENTS.md') and not src.name.startswith('.env'):
                copy_preserved(src, stage / 'supporting_implementations/retired' / submitted / src.relative_to(source),
                               'retired source variant; job 928583 is inherited b2 evidence')
    (stage / 'supporting_implementations/retired/README.md').write_text(
        '# Retired source variants\n\n'
        'b203 (original expt_b3v_control) and b204 (expt_b3v_cover) have no independent '
        'benchmark. Their job-928583 files are copies of expt_b2 evidence, not measurements '
        'of these variants. Source and inherited output are retained for completeness; '
        'count job 928583 only once, under expt_b2. The independently run but unselected '
        'b202 experiment remains at the archive root with its two actual jobs.\n')

    # Retain the starter installer, then apply only the already configured team's
    # notification directive. The installation commands must remain identical.
    installer = stage / 'install_citus_slurm.sh'
    configured = ROOT / 'submission/_build/remote-20261028/raw/install_citus_slurm.sh'
    old, new = installer.read_text(), configured.read_text()
    strip_mail = lambda text: re.sub(r'^#SBATCH --mail-user=.*\n', '', text, flags=re.M)
    if strip_mail(old) != strip_mail(new):
        raise RuntimeError('Configured installer differs beyond its notification address')
    if old != new:
        original = stage / 'source_snapshots/original-installer/install_citus_slurm.sh'
        copy_preserved(installer, original, 'original installer before notification configuration')
        shutil.copy2(configured, installer)
        pair = (str(configured.relative_to(ROOT)), 'install_citus_slurm.sh')
        if pair not in known:
            provenance.append(dict(source=pair[0], destination=pair[1], sha256=digest(configured),
                                   collection='configured installer; notification-only difference'))
            known.add(pair)

    inventory = json.loads((stage / 'experiment-inventory.json').read_text())
    for entry in inventory:
        name = entry['experiment']
        entry['classification'] = 'Slurm experiment; retained failed attempts are not clean results'
        if name == 'expt_b202':
            entry['classification'] = 'retired supplementary experiment; actual runs retained for completeness'
            entry['description'] = 'T6 time-index supplementary experiment, original expt_xc_b2; not selected for the final B design.'
        if name == 'expt_a112':
            entry['description'] = 'Selected A design: a111 plus READ ONLY; retain seed-7/c64 warmup caveat.'
        for job in entry['jobs']:
            canonical = INHERITED.get((name, job['job']), name)
            job['canonical_experiment'] = canonical
            job['inherited_copy'] = canonical != name
        readme = stage / name / 'README.md'
        text = readme.read_text().split('\n\n## Submission packaging note', 1)[0]
        note = '\n\n## Submission packaging note\n\n' + entry['description'] + '\n\n'
        note += 'Classification: ' + entry['classification'] + '.\n'
        for job in entry['jobs']:
            note += '- ' + job['job'] + ': '
            note += ('INHERITED from ' + job['canonical_experiment'] +
                     '; not an independent measurement of this variant.' if job['inherited_copy']
                     else 'Original result; inspect phase exits and failed records.') + '\n'
        note += '\nUse the archive-root job-source-map.json and REPRODUCE.md. '
        note += 'Readback source hashes do not certify execution-time source.\n'
        readme.write_text(text + note)
    (stage / 'experiment-inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')

    source_paths = {}
    for path in sorted(stage.rglob('*')):
        if path.is_file() and path.suffix in ('.sh', '.sql'):
            source_paths.setdefault(digest(path), []).append(str(path.relative_to(stage)))
    jobs = {}
    for entry in inventory:
        name = entry['experiment']
        for item in entry['jobs']:
            jobid = item['job']
            job = jobs.setdefault(jobid, dict(job=jobid, canonical_experiment=item['canonical_experiment'],
                                            locations=[], runtime_source_files=[],
                                            source_identity='not certified: no runtime hash manifest'))
            job['locations'].append(f'{name}/slurm-results/{jobid}')
            manifest = stage / name / 'slurm-results' / jobid / 'code-sha256.txt'
            if manifest.exists() and not job['runtime_source_files']:
                job['source_identity'] = 'runtime manifest checked against preserved packaged files'
                for line in manifest.read_text().splitlines():
                    sha, runtime_path = line.split(None, 1)
                    matches = source_paths.get(sha, [])
                    if not matches:
                        raise RuntimeError(f'Runtime source unavailable: {jobid} {runtime_path}')
                    matches = sorted(matches, key=lambda p: (not p.startswith(name + '/'), p))
                    job['runtime_source_files'].append(dict(runtime_path=runtime_path, sha256=sha,
                                                          packaged_matches=matches))
    (stage / 'job-source-map.json').write_text(json.dumps(list(jobs.values()), indent=2) + '\n')

    for source, target in [('package-readme.md', 'README.md'), ('reproduction-guide.md', 'REPRODUCE.md')]:
        (stage / target).write_text((ROOT / 'submission' / source).read_text())
    with (stage / 'README.md').open('a') as f:
        f.write('\n## Experiment directory index\n\n')
        for entry in inventory:
            f.write(f"- **{entry['experiment']}**: {entry['description']} Jobs: " +
                    ', '.join(j['job'] + (f" (inherited from {j['canonical_experiment']})" if j['inherited_copy'] else '')
                              for j in entry['jobs']) + '.\n')
    (stage / 'analysis_scripts/README.md').write_text(
        '# Archived repository utilities\n\nThese files are preserved source references, not standalone tools in this ZIP. '
        'Their path assumptions refer to the original repository. See ../REPRODUCE.md for the checkout and working directory. '
        'Cluster run.sh entry points do not depend on this directory.\n')
    # Distinguish original source identity from edited final destination identity.
    for item in provenance:
        item['source_sha256'] = item.get('source_sha256', item['sha256'])
        item['packaged_sha256'] = digest(stage / item['destination'])
        item['destination_modified'] = item['source_sha256'] != item['packaged_sha256']
        item['sha256_semantics'] = 'legacy alias of source_sha256, not final destination hash'
    provenance_file.write_text(json.dumps(provenance, indent=2) + '\n')


if __name__ == '__main__':
    raise SystemExit('Run finalize_submission_layout.py to organize and rebuild checksums/ZIP together.')
