#!/usr/bin/env python3
"""Audit the imported a115 jobs without executing benchmarks.

Usage: python3 scripts/review_a115_results.py results/cluster-full-a115-20261022
Fails on missing/mismatched evidence; phase eligibility and zero failures differ.
"""
import csv
import datetime
import hashlib
import json
import re
import shlex
import sys
from collections import Counter
from pathlib import Path

from import_cluster_jobs import review

ROOT = Path(__file__).resolve().parent.parent
COUNTS = [1, 4, 8, 16, 32, 64]
WEIGHTS = [36, 20, 10, 10, 10, 5, 5, 2, 2]


def value(text, key):
    m = re.search(rf'^\s*{key}\s*=\s*"?([^"\n]+)', text, re.M)
    assert m, f'Missing config {key}'
    return m.group(1).strip()


def main():
    out = Path(sys.argv[1])
    source = out / 'citus_project_team_14/expt_a115'
    a112 = ROOT / 'citus_project_team_14/expt_a112'
    for rel in [str(p.relative_to(source)) for p in (source / 'transactions').glob('*.sql')] + [
            'sql/indexes.sql', 'sql/verify.sql']:
        assert (source / rel).read_bytes() == (a112 / rel).read_bytes(), rel
    expected_run = (a112 / 'run.sh').read_text().replace(
        'psqlx -f "$SCRIPT_DIR/sql/indexes.sql"\n',
        'psqlx -f "$SCRIPT_DIR/sql/indexes.sql"\npsqlx -f "$SCRIPT_DIR/sql/report_time_index.sql"\n')
    assert (source / 'run.sh').read_text() == expected_run
    manifest = json.loads((out / 'import-manifest.json').read_text())
    for rel, digest in manifest['files'].items():
        assert hashlib.sha256((out / rel).read_bytes()).hexdigest() == digest, rel
    records, jobs = [], []
    for job_id, seed in [(979909, 42), (979910, 7)]:
        job = source / f'slurm-results/job-{job_id}'
        b = job / 'benchmark-results'
        readback = out.parent / 'a115-readback-20261022' / f'summary-{job_id}.csv'
        assert (b / 'summary.csv').read_bytes() == readback.read_bytes()
        config = (b / 'config.txt').read_text()
        expected = dict(scale='1', DURATION='600', WARMUP_DURATION='60',
                        CLIENT_COUNTS='1 4 8 16 32 64', PG_ISOLATION_LEVEL='serializable',
                        LOG_SAMPLE_RATE='1.0', DATA_SEED='42', PGBENCH_SEED=str(seed),
                        PGBENCH_MAX_TRIES='3', RESET_BETWEEN_CLIENT_COUNTS='1',
                        RESET_AFTER_WARMUP='0', RESTART_SERVERS_BETWEEN_CLIENT_COUNTS='1')
        expected.update({f'T{i}_WEIGHT': str(w) for i, w in enumerate(WEIGHTS, 1)})
        for k, v in expected.items():
            assert value(config, k) == v, (job_id, k)
        assert (job / 'topology.txt').read_text().splitlines() == [
            'coordinator=xcnf0', 'worker_1=xcnf1', 'worker_2=xcnf2',
            'worker_3=xcnf3', 'worker_4=xcnf4']
        versions = (job / 'server_versions.log').read_text()
        assert 'PostgreSQL 18.6' in versions and 'Citus 14.1.0' in versions
        hashes = []
        for line in (job / 'code-sha256.txt').read_text().splitlines():
            digest, remote = line.split(None, 1)
            rel = remote.split('/expt_a115/', 1)[1]
            for p in [source / rel, ROOT / 'citus_project_team_14/expt_a115' / rel]:
                assert hashlib.sha256(p.read_bytes()).hexdigest() == digest, str(p)
            hashes.append(rel)
        assert len(hashes) == 13
        validation = (job / 'validation.log').read_text()
        blocks = re.findall(r'^BEGIN\n(.*?)^COMMIT$', validation, re.M | re.S)
        assert len(blocks) == 6 and all('core invariants passed' in s for s in blocks)
        assert 'ERROR' not in validation and 'ROLLBACK' not in validation
        log = (job / 'benchmark.log').read_text()
        resets = re.findall(r'Database reset complete: before client-count c(\d+)', log)
        assert list(map(int, resets)) == COUNTS
        rows = review(out, 'expt_a115', job_id)
        assert [r['clients'] for r in rows] == COUNTS
        summary = {int(r['clients']): r for r in csv.DictReader((b / 'summary.csv').open())}
        tx_rows = list(csv.DictReader((b / 'transaction_metrics.csv').open()))
        for r in rows:
            c = r['clients']
            phase_details = {}
            for phase, prefix, duration in [('warmup', 'warmup', 60), ('measured', 'result', 600)]:
                text = (b / f'{prefix}-c{c}.txt').read_text()
                args = shlex.split(text.splitlines()[0].removeprefix('# Command: '))
                assert int(args[args.index('-c') + 1]) == c
                assert int(args[args.index('-T') + 1]) == duration
                assert f'--random-seed={seed}' in args and '--max-tries=3' in args
                assert args[args.index('-M') + 1] == 'simple'
                assert [int(a.rsplit('@', 1)[1]) for a in args if '.sql@' in a] == WEIGHTS
                if phase == 'measured':
                    assert '--sampling-rate=1.0' in args
                errors = re.findall(r'^pgbench: error: client (\d+) script (\d+) aborted.*$', text, re.M)
                phase_details[phase] = dict(configured_clients=c, duration=duration,
                                           aborted_clients=[int(x[0]) for x in errors],
                                           aborted_transactions=[f'T{int(x[1])+1}' for x in errors])
                assert r[f'{phase}_exit_code'] is not None
                if r[f'{phase}_exit_code'] == 0:
                    assert not errors
            tally, by_script, client_ids = Counter(), Counter(), set()
            retries = retried = 0
            for line in (b / f'logs/transactions-c{c}.log').open():
                f = line.split()
                client_ids.add(int(f[0]))
                ok = f[2].isdigit()
                tally['success' if ok else f[2]] += 1
                if ok:
                    by_script[f'T{int(f[3])+1}'] += 1
                retries += int(f[6])
                retried += int(f[6]) > 0
            s = summary[c]
            assert tally['success'] == r['successful_scripts']
            assert sum(v for k, v in tally.items() if k != 'success') == r['failed_log_records']
            assert tally['serialization'] == int(s['serialization_failures'])
            assert retries == int(s['total_retries']) and retried == int(s['retried_transactions'])
            for t in [x for x in tx_rows if int(x['clients']) == c]:
                assert by_script[t['transaction']] == int(t['successful_transactions'])
            assert r['measured_exit_code'] == int(s['pgbench_exit_code'])
            assert client_ids == set(range(c)), (job_id, c, sorted(client_ids))
            r.update(phase_details=phase_details, raw_log_counts=dict(tally),
                     measured_clients_with_log_records=sorted(client_ids),
                     total_retries=retries, runtime_hashes_verified=True,
                     zero_failed_records=r['failed_log_records'] == 0,
                     clean_comparison_candidate=r['eligible'] and r['failed_log_records'] == 0)
            records.append(r)
        # Record actual log excerpts, without asserting every error has a traced root cause.
        excerpts = []
        for p in sorted(job.glob('xcnf*-postgresql.log')):
            lines = p.read_text(errors='replace').splitlines()
            hit = next((i for i, line in enumerate(lines) if 'pivot, during commit attempt' in line), None)
            if hit is not None:
                excerpts.append(dict(file=p.name, line=hit + 1, text=lines[max(0, hit-1):hit+4]))
        jobs.append(dict(job_id=job_id, seed=seed, protocol=expected,
                         earlier_summary_transcription_verified=True,
                         runtime_hashes=hashes, validations_passed=len(blocks),
                         reset_client_counts=list(map(int, resets)), commit_conflict_examples=excerpts))
    assert len(records) == 12
    audit = dict(reviewed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 imported_files_verified=len(manifest['files']), jobs=jobs, cases=records,
                 phase_eligible_cases=sum(r['eligible'] for r in records),
                 clean_comparison_candidates=sum(r['clean_comparison_candidate'] for r in records))
    (out / 'audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    print(f"Verified {len(manifest['files'])} imported files, 26 runtime hash comparisons, "
          '24 phase commands/exits, 12 raw log/transaction-metric counts and 12 validations.')
    print('Phase-eligible:', audit['phase_eligible_cases'],
          'phase-eligible with zero failures:', audit['clean_comparison_candidates'])


if __name__ == '__main__':
    main()
