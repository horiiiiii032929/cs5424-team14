#!/usr/bin/env python3
"""Retrieve finished Slurm benchmark jobs and build a per-client review table.

Usage:
  python3 scripts/import_cluster_jobs.py REMOTE_DEPLOYMENT OUT_DIR expt_a0:977740 [...]

Each job's experiment source, Slurm output and slurm-results/job-N are streamed
from the cluster as one tar archive, extracted under OUT_DIR, hashed into
import-manifest.json and summarized in case-review.csv/json. A case is eligible
only when both warmup and measured pgbench exits are zero and its validation
record passed (the original a0 script has none: 'not_in_script'); Slurm
COMPLETED alone is not sufficient.
"""
import argparse
import csv
import datetime
import hashlib
import io
import json
import re
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ['experiment', 'job_id', 'pgbench_seed', 'node_list', 'clients', 'warmup_exit_code',
          'measured_exit_code', 'validation', 'successful_scripts', 'failed_log_records',
          'configured_duration_tps', 'pgbench_elapsed_tps', 'avg_latency_ms', 'p50_latency_ms',
          'p95_latency_ms', 'p99_latency_ms', 'retried_transactions', 'serialization_failures',
          'eligible']


def remote(command):
    return subprocess.run(['bash', str(ROOT / 'scripts/cluster-command.sh'), command],
                          check=True, capture_output=True).stdout


def exit_code(path):
    if not path.exists():
        return None
    match = re.search(r'^pgbench_exit_code=(\d+)$', path.read_text(errors='replace'), re.M)
    return int(match.group(1)) if match else None


def elapsed_tps(path):
    if not path.exists():
        return None
    match = re.search(r'^tps = ([0-9.]+)', path.read_text(errors='replace'), re.M)
    return float(match.group(1)) if match else None


def config_value(config, key):
    match = re.search(rf'^\s*{key}\s*[=:]\s*(\S+)', config, re.M)
    return match.group(1) if match else None


def validation_records(path):
    """verify.sql appends one block per measured client count, in run order."""
    if not path.exists():
        return []
    text = path.read_text(errors='replace')
    return ['passed' if 'passed' in block else 'failed'
            for block in re.split(r'^BEGIN$', text, flags=re.M)[1:]]


def review(out_dir, expt, job):
    job_dir = out_dir / 'citus_project_team_14' / expt / 'slurm-results' / f'job-{job}'
    bench = job_dir / 'benchmark-results'
    config = (bench / 'config.txt').read_text(errors='replace') if (bench / 'config.txt').exists() else ''
    summary = {}
    if (bench / 'summary.csv').exists():
        with (bench / 'summary.csv').open() as f:
            summary = {int(r['clients']): r for r in csv.DictReader(f)}
    duration = float(config_value(config, 'DURATION') or 600)
    validations = validation_records(job_dir / 'validation.log')
    # The unmodified starter baseline has no post-run verify.sql step.
    validates = 'verify.sql' in (out_dir / 'citus_project_team_14' / expt / 'run.sh').read_text(errors='replace')
    topology = (job_dir / 'topology.txt').read_text(errors='replace') if (job_dir / 'topology.txt').exists() else ''
    nodes = sorted(set(re.findall(r'\bxcn[a-z]\d+\b', topology)))
    rows = []
    for index, clients in enumerate(sorted(summary)):
        s = summary[clients]
        warm = exit_code(bench / f'warmup-c{clients}.txt')
        measured = exit_code(bench / f'result-c{clients}.txt')
        valid = validations[index] if index < len(validations) else ('missing' if validates else 'not_in_script')
        rows.append(dict(
            experiment=expt, job_id=job, pgbench_seed=config_value(config, 'PGBENCH_SEED'),
            node_list=','.join(nodes), clients=clients, warmup_exit_code=warm,
            measured_exit_code=measured, validation=valid,
            successful_scripts=int(s['successful_transactions']),
            failed_log_records=int(s['failed_log_records']),
            configured_duration_tps=round(int(s['successful_transactions']) / duration, 3),
            pgbench_elapsed_tps=elapsed_tps(bench / f'result-c{clients}.txt'),
            avg_latency_ms=float(s['overall_avg_latency_ms']),
            p50_latency_ms=float(s['overall_median_latency_ms']),
            p95_latency_ms=float(s['overall_p95_latency_ms']),
            p99_latency_ms=float(s['overall_p99_latency_ms']),
            retried_transactions=int(s['retried_transactions']),
            serialization_failures=int(s['serialization_failures']),
            eligible=warm in (0, None) and measured == 0 and valid in ('passed', 'not_in_script')))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('deployment')
    parser.add_argument('out_dir', type=Path)
    parser.add_argument('jobs', nargs='+', help='expt_aN:JOBID')
    args = parser.parse_args()
    if not re.fullmatch(r'/home/stuproj/cs14/[A-Za-z0-9_.-]+', args.deployment):
        parser.error('unexpected deployment path')
    pairs = []
    for item in args.jobs:
        match = re.fullmatch(r'(expt_a\d+):(\d+)', item)
        if not match:
            parser.error(f'bad job spec: {item}')
        pairs.append((match.group(1), int(match.group(2))))
    members = []
    for expt, job in pairs:
        base = f'citus_project_team_14/{expt}'
        members += [f'{base}/run.sh', f'{base}/experiment.json', f'{base}/README.md',
                    f'{base}/citus-{job}.out', f'{base}/citus-{job}.err', f'{base}/slurm-results/job-{job}']
    archive = remote(f"cd {args.deployment} && tar --ignore-failed-read -czf - {' '.join(members)} 2>/dev/null")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as tar:
        tar.extractall(args.out_dir, filter='data')
    files = {str(p.relative_to(args.out_dir)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted((args.out_dir / 'citus_project_team_14').rglob('*')) if p.is_file()}
    manifest = dict(remote_directory=args.deployment,
                    retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    archive_sha256=hashlib.sha256(archive).hexdigest(),
                    jobs=[job for _, job in pairs], files=files)
    (args.out_dir / 'import-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    rows = [row for expt, job in pairs for row in review(args.out_dir, expt, job)]
    with (args.out_dir / 'case-review.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    (args.out_dir / 'case-review.json').write_text(json.dumps(rows, indent=2) + '\n')
    for row in rows:
        flag = '' if row['eligible'] else '  <-- NOT ELIGIBLE'
        print(f"{row['experiment']} job {row['job_id']} c{row['clients']}: "
              f"{row['configured_duration_tps']} TPS, warmup={row['warmup_exit_code']} "
              f"measured={row['measured_exit_code']} validation={row['validation']} "
              f"serial_fail={row['serialization_failures']}{flag}")


if __name__ == '__main__':
    main()
