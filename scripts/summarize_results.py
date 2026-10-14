#!/usr/bin/env python3
"""Summarize only locally comparable measurements; never mix with Slurm."""
import argparse
import csv
import json
from pathlib import Path

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('directory',type=Path)
    args=parser.parse_args()
    rows=[]
    for path in sorted(args.directory.glob('expt_*/c*/metrics.json')):
        row=json.loads(path.read_text())
        verified=path.with_name('verification.json')
        row['verified']=verified.exists() and all(json.loads(verified.read_text()).values())
        row['status']='passed' if row['verified'] else 'incomplete'
        if path.with_name('failure.json').exists():
            row['status']='FAILED'
            row['pgbench_tps']=None
        row['transaction_types_seen']=sum(x['count']>0 for x in row['transactions'].values())
        row['sample_warning']='small sample' if row['count']<100 else ''
        if row['transaction_types_seen']<9:
            row['sample_warning']+='; incomplete transaction-type coverage'
        rows.append(row)
    for path in sorted(args.directory.glob('expt_*/c*/failure.json')):
        if path.with_name('metrics.json').exists(): continue
        failure=json.loads(path.read_text())
        rows.append(dict(experiment=failure['experiment'],clients=failure['clients'],status='FAILED',
          count=0,transaction_types_seen=0,sample_warning='Warmup failed; no measured result',
          pgbench_tps=None,successful_tps_by_duration=None,avg_ms=None,p95_ms=None,p99_ms=None,
          failed_logs=None,exit_code=None,verified=False))
    rows.sort(key=lambda r:(r['experiment'],r['clients']))
    baseline={r['clients']:r['pgbench_tps'] for r in rows if r['experiment']=='expt_a0'}
    fields=['experiment','clients','count','transaction_types_seen','sample_warning','pgbench_tps','successful_tps_by_duration','relative_to_baseline',
            'avg_ms','p95_ms','p99_ms','failed_logs','exit_code','verified','status']
    with (args.directory/'comparison.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader()
        for r in rows:
            b=baseline.get(r['clients'])
            r['relative_to_baseline']=r['pgbench_tps']/b if b and r['pgbench_tps'] is not None else None
            w.writerow(r)
    content='''# Local Docker pilot results

These are short, scale-0.01 implementation measurements on one Mac's Docker VM,
with one coordinator and four workers. They are **not course-cluster benchmarks**.
Check environment.json, each experiment's settings, source hashes and raw logs.
TPS below uses pgbench's elapsed-time denominator; comparison.csv also preserves
the starter-style count / configured-duration metric. Expected business rollbacks
count as completed scripts. One short run cannot establish statistical confidence.
**Small baseline samples and missing transaction types make speedup ratios
exploratory only. Failed runs have no valid throughput and must not be ranked.**

| Experiment | Clients | Completed scripts | Types seen / 9 | TPS | vs baseline | p95 ms | Status |
|---|---:|---:|---:|---:|---:|---:|---|
'''
    for r in rows:
        def fmt(v): return f'{v:.2f}' if v is not None else 'NA'
        ratio=fmt(r['relative_to_baseline'])+'x' if r['relative_to_baseline'] is not None else 'NA'
        count=str(r['count']) if r['status']!='FAILED' else 'NA'
        content+=f"| {r['experiment']} | {r['clients']} | {count} | {r['transaction_types_seen']} | {fmt(r['pgbench_tps'])} | {ratio} | {fmt(r['p95_ms'])} | {r['status']} |\n"
    content+='''
The next decision requires scale-1 Slurm repeats at 1, 4, 8, 16, 32 and 64 clients
under identical settings. Retain slower variants as experimental evidence. Do not
select a final design solely from this pilot.
'''
    (args.directory/'SUMMARY.md').write_text(content)
    print(content)

if __name__=='__main__': main()
