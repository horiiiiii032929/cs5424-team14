#!/usr/bin/env python3
"""Review the immutable B branch import; never run benchmark scripts.

Usage: python3 scripts/review_b_branch.py results/b-branch-review-20261022
Raw files are extracted with git archive from the recorded source commit.
Phase completion is separate from correctness and failed-transaction counts.
"""
import csv
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


def value(text, key):
    match = re.search(rf'^\s*{key}\s*=\s*"?([^"\n]+)', text, re.M)
    return match.group(1).strip() if match else None


def rc(text):
    match = re.search(r'^pgbench_exit_code=(\d+)$', text, re.M)
    return int(match.group(1)) if match else None


def main():
    out = Path(sys.argv[1])
    raw = out / 'raw'
    # Use the immutable commit, not a potentially advanced branch, for provenance.
    commit = '5fa38157a7c1cb9abf1097e731f934a97a3db7c4'
    tree = subprocess.check_output(['git', 'ls-tree', '-r', commit], text=True)
    originals = {line.split('\t', 1)[1]: line.split()[2]
                 for line in tree.splitlines() if line.split('\t', 1)[1].startswith('expt_b')}
    hashes, mismatches = {}, []
    for p in sorted(raw.rglob('*')):
        if not p.is_file():
            continue
        data = p.read_bytes()
        rel = p.relative_to(raw).as_posix()
        hashes[rel] = hashlib.sha256(data).hexdigest()
        blob = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
        if originals.get(rel) != blob:
            mismatches.append(rel)
    assert not mismatches, mismatches
    assert set(hashes) == set(originals), 'missing or unexpected source files'
    rows, protocols, checks = [], [], []
    keys = ['scale', 'DURATION', 'WARMUP_DURATION', 'CLIENT_COUNTS', 'THREADS',
            'PG_ISOLATION_LEVEL', 'LOG_SAMPLE_RATE', 'DATA_SEED', 'PGBENCH_SEED',
            'PGBENCH_MAX_TRIES', 'RESET_BETWEEN_CLIENT_COUNTS', 'RESET_AFTER_WARMUP',
            'RESTART_SERVERS_BETWEEN_CLIENT_COUNTS'] + [f'T{i}_WEIGHT' for i in range(1, 10)]
    for expt in sorted(raw.glob('expt_b*')):
        for job in sorted((expt / 'slurm-results').glob('job-*')):
            b = job / 'benchmark-results'
            if not (b / 'summary.csv').exists():
                continue
            config = (b / 'config.txt').read_text()
            protocol = {key: value(config, key) for key in keys}
            protocol.update(experiment=expt.name, job_id=job.name.removeprefix('job-'),
                            topology=(job / 'topology.txt').read_text(),
                            server_versions=(job / 'server_versions.log').read_text())
            protocols.append(protocol)
            for s in csv.DictReader((b / 'summary.csv').open()):
                c = s['clients']
                warm = (b / f'warmup-c{c}.txt').read_text()
                measured = (b / f'result-c{c}.txt').read_text()
                w, m = rc(warm), rc(measured)
                assert m == int(s['pgbench_exit_code']), (expt.name, c)
                log = b / 'logs' / f'transactions-c{c}.log'
                record_count = sum(1 for _ in log.open())
                assert record_count == int(s['successful_transactions']) + int(s['failed_log_records'])
                phase_ok = w == 0 and m == 0
                rows.append(dict(experiment=expt.name, job_id=protocol['job_id'], clients=int(c),
                                 warmup_exit_code=w, measured_exit_code=m,
                                 warmup_client_aborts=len(re.findall(r'client \d+ script \d+ aborted', warm)),
                                 measured_client_aborts=len(re.findall(r'client \d+ script \d+ aborted', measured)),
                                 successful_scripts=int(s['successful_transactions']),
                                 raw_configured_duration_tps=round(int(s['successful_transactions']) / int(protocol['DURATION']), 3),
                                 failed_log_records=int(s['failed_log_records']),
                                 serialization_failures=int(s['serialization_failures']),
                                 retried_transactions=int(s['retried_transactions']),
                                 total_retries=int(s['total_retries']),
                                 transaction_log_records=record_count,
                                 phases_complete=phase_ok,
                                 clean_comparison_candidate=phase_ok and int(s['failed_log_records']) == 0,
                                 core_validation='not_recorded',
                                 runtime_source_hashes='not_recorded'))
            for p in sorted(job.glob('query-plans*.log')):
                text = p.read_text()
                if expt.name == 'expt_b6':
                    match = re.search(r'^\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*$', text, re.M)
                    values = list(map(int, match.groups())) if match else None
                    checks.append(dict(path=str(p.relative_to(out)), values=values,
                                       passed=values == [1000, 1000, 0, 0]))
    assert len(rows) == 42
    assert len(checks) == 7 and all(c['passed'] for c in checks)
    (out / 'case-review.json').write_text(json.dumps(rows, indent=2) + '\n')
    with (out / 'case-review.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    manifest = dict(source_branch='desmond/expt_b0-6', source_commit=commit,
                    reviewed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    files=hashes, git_blob_matches=len(hashes), mismatches=mismatches,
                    protocols=protocols, b6_t6_checks=checks,
                    limitation='Git blob identity verifies imported bytes, not the source used at runtime; no runtime source hash manifest or general post-run integrity suite is recorded.')
    (out / 'import-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for expt in sorted({r['experiment'] for r in rows}):
        subset = [r for r in rows if r['experiment'] == expt]
        print(expt, 'both phases complete:', [r['clients'] for r in subset if r['phases_complete']],
              'zero-failure candidates:', [r['clients'] for r in subset if r['clean_comparison_candidate']])
    print(f'{len(hashes)} files match Git blobs; 42 log counts checked; seven b6 T6 comparisons passed.')


if __name__ == '__main__':
    main()
