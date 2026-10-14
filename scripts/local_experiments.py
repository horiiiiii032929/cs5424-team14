#!/usr/bin/env python3
"""Distributed Docker checks/pilot. Never label these course-cluster results."""
import argparse
import csv
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ['docker', 'compose', '-f', str(ROOT / 'compose.yaml')]


def run(args, text=None, check=True):
    p = subprocess.run(args, input=text, text=True, capture_output=True, cwd=ROOT)
    if check and p.returncode:
        raise RuntimeError(f"Command failed: {' '.join(args)}\n{p.stdout}\n{p.stderr}")
    return p


def sql(query, database='postgres'):
    return run(COMPOSE + ['exec', '-T', 'coordinator', 'psql', '-X', '-qAt', '-v',
                           'ON_ERROR_STOP=1', '-U', 'postgres', '-d', database], query).stdout.strip()


def extract_function(script, name):
    match = re.search(r'^' + re.escape(name) + r'\(\) \{\n.*?^\}', script, re.M | re.S)
    if not match:
        raise ValueError(f'Missing function {name}')
    return match.group(0)


def initialize_cluster():
    run(COMPOSE + ['up', '-d', '--wait'], check=True)
    for service in ['coordinator','worker1','worker2','worker3','worker4']:
        run(COMPOSE + ['exec','-T',service,'psql','-U','postgres','-c','CREATE EXTENSION IF NOT EXISTS citus;'])
    for worker in ['worker1','worker2','worker3','worker4']:
        sql(f"SELECT citus_add_node('{worker}',5432);")


def prepare(experiment, output, small=False):
    folder = ROOT / 'citus_project_team_14' / experiment
    script = (folder / 'run.sh').read_text()
    manifest_path = folder / 'experiment.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    # Dedicated local containers; this reset never touches the SoC installation.
    sql('DROP TABLE IF EXISTS sales_daily CASCADE;')
    functions = '\n'.join(extract_function(script, n) for n in
                          ['create_schema','generate_data','reset_benchmark_sequences'])
    setup = '''set -euo pipefail
PSQL=psql
PGHOST=coordinator
PGPORT=5432
PGUSER=postgres
PGDATABASE=postgres
NUM_MERCHANTS=10
NUM_CUSTOMERS=10000
NUM_PRODUCTS=5000
NUM_ORDERS=50000
NUM_ORDER_ITEMS=150000
HOT_MERCHANT_PERCENT=10
HOT_ORDER_PERCENT=50
DATA_SEED=42
TRUNCATE_FIRST=1
RUN_ANALYZE=1
psqlx() { psql -X -v ON_ERROR_STOP=1 -U postgres -h coordinator "$@"; }
'''
    setup += f'SCRIPT_DIR=/workspace/citus_project_team_14/{experiment}\n' + functions + '\ncreate_schema\n'
    if small:
        setup=setup.replace('NUM_CUSTOMERS=10000','NUM_CUSTOMERS=1000').replace('NUM_PRODUCTS=5000','NUM_PRODUCTS=500')
        setup=setup.replace('NUM_ORDERS=50000','NUM_ORDERS=500').replace('NUM_ORDER_ITEMS=150000','NUM_ORDER_ITEMS=1500')
    for feature, file in [('indexes','indexes.sql'), ('summary','sales_summary_schema.sql'), ('procedure','place_order.sql')]:
        if manifest.get(feature):
            setup += f'psqlx -f "$SCRIPT_DIR/sql/{file}"\n'
    setup += 'generate_data\nreset_benchmark_sequences\n'
    for service in ['coordinator','worker1','worker2','worker3','worker4']:
        settings = f"ALTER SYSTEM SET work_mem='{manifest.get('work_mem','32MB')}';"
        # ALTER SYSTEM cannot share a transaction block with other commands.
        run(COMPOSE + ['exec','-T',service,'psql','-U','postgres','-c',settings])
        run(COMPOSE + ['exec','-T',service,'psql','-U','postgres','-c',
              f"ALTER SYSTEM SET citus.max_adaptive_executor_pool_size={manifest.get('pool',4)};"])
        run(COMPOSE + ['exec','-T',service,'psql','-U','postgres','-c','SELECT pg_reload_conf();'])
    p = run(COMPOSE + ['exec','-T','coordinator','bash','-s'], setup, check=False)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'setup.log').write_text(p.stdout+p.stderr)
    if p.returncode:
        raise RuntimeError(f'{experiment}: setup failed; see {output}/setup.log\n{p.stderr[-3000:]}')
    sources=[folder/'run.sh']+sorted((folder/'transactions').glob('*.sql'))+sorted((folder/'sql').glob('*.sql'))
    (output/'code-sha256.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},indent=2)+'\n')
    (output/'experiment.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (output/'fixture.json').write_text(json.dumps(dict(merchants=10,customers=1000 if small else 10000,
        products=500 if small else 5000,orders=500 if small else 50000,items=1500 if small else 150000),indent=2)+'\n')
    (output/'effective-settings.txt').write_text(sql('SHOW work_mem; SHOW citus.max_adaptive_executor_pool_size; SHOW default_transaction_isolation; SHOW shared_buffers;')+'\n')
    effective=sql('SHOW work_mem; SHOW citus.max_adaptive_executor_pool_size;').splitlines()
    expected=[manifest.get('work_mem','32MB'),str(manifest.get('pool',4))]
    if effective!=expected:
        raise AssertionError(f'{experiment}: effective settings {effective} != intended {expected}')
    return manifest


def verify(summary=False, prefix=''):
    checks = {
        'nonnegative_inventory': 'SELECT count(*) FROM inventory WHERE quantity<0',
        'unique_order_ids': 'SELECT count(*) FROM (SELECT order_id FROM orders GROUP BY order_id HAVING count(*)>1) s',
        'unique_item_ids': 'SELECT count(*) FROM (SELECT order_item_id FROM order_items GROUP BY order_item_id HAVING count(*)>1) s',
        'items_have_matching_orders': '''SELECT count(*) FROM
          (SELECT merchant_id,order_id FROM order_items EXCEPT SELECT merchant_id,order_id FROM orders) missing''',
        'matching_order_totals': '''SELECT count(*) FROM orders o LEFT JOIN
          (SELECT merchant_id,order_id,sum(quantity*unit_price)::numeric(12,2) amount FROM order_items GROUP BY merchant_id,order_id) x
          ON o.order_id=x.order_id AND o.merchant_id=x.merchant_id
          WHERE o.total_amount IS DISTINCT FROM COALESCE(x.amount,0)''',
    }
    if summary:
        checks['exact_daily_summary'] = '''WITH raw AS (SELECT merchant_id,date_trunc('day',created_at) sales_day,count(*) order_count,sum(total_amount) revenue
          FROM orders GROUP BY merchant_id,date_trunc('day',created_at)), mismatch AS
          ((SELECT * FROM raw EXCEPT SELECT * FROM sales_daily) UNION ALL
           (SELECT * FROM sales_daily EXCEPT SELECT * FROM raw)) SELECT count(*) FROM mismatch'''
        template = (ROOT / 'optimizations/T6_sales_summary.sql').read_text()
        # Remove top-20/order for an exact all-merchant equivalence test at one snapshot.
        optimized = template.replace('BEGIN;', '').replace('COMMIT;', '').strip().rstrip(';')
        optimized = optimized.replace(' ORDER BY revenue DESC LIMIT 20', '')
        for days in [0, 1, 30, 365]:
            q = optimized.replace('(:REPORT_DAYS)', f'({days})')
            checks[f'exact_report_{days}_days'] = f'''WITH fast AS ({q}), raw AS (
              SELECT merchant_id,count(*) order_count,sum(total_amount) revenue FROM orders
              WHERE created_at>=CURRENT_TIMESTAMP-INTERVAL '{days} days' AND created_at<CURRENT_TIMESTAMP GROUP BY merchant_id),
              mismatch AS ((SELECT * FROM fast EXCEPT SELECT * FROM raw) UNION ALL
              (SELECT * FROM raw EXCEPT SELECT * FROM fast)) SELECT count(*) FROM mismatch'''
    result = {}
    for name, query in checks.items():
        value = sql(query)
        result[prefix+name] = value == '0'
        if value != '0':
            raise AssertionError(f'{prefix}{name}: {value} mismatches')
    return result


DEFS = dict(DEBUG_MODE=0, NUM_MERCHANTS=10, NUM_CUSTOMERS=10000, NUM_PRODUCTS=5000,
            INITIAL_NUM_ORDERS=50000, HOT_ORDER_PERCENT=50, HOT_MERCHANTS=1,
            MIN_ITEMS_PER_ORDER=1, MAX_ITEMS_PER_ORDER=5, MIN_ORDER_QTY=1,
            MAX_ORDER_QTY=5, INVENTORY_CHANGE_MIN=-5, INVENTORY_CHANGE_MAX=20,
            REPORT_DAYS=30, T7_MIN_TRANSFER_QTY=1, T7_MAX_TRANSFER_QTY=5)
WEIGHTS = [36,20,10,10,10,5,5,2,2]


def benchmark(experiment, output, clients, duration, seed):
    files = sorted((ROOT/'citus_project_team_14'/experiment/'transactions').glob('T*.sql'))
    base = COMPOSE + ['exec','-T','coordinator','pgbench','-U','postgres','-h','coordinator',
                       '-n','-c',str(clients),'-j',str(min(clients,4)), '--random-seed='+str(seed),
                       '--max-tries=3','--failures-detailed']
    for k,v in DEFS.items():
        base += ['-D', f'{k}={v}']
    for file,weight in zip(files,WEIGHTS):
        base += ['-f', '/workspace/'+str(file.relative_to(ROOT))+'@'+str(weight)]
    warm = run(base+['-T','5','postgres'],check=False)
    (output/'warmup.txt').write_text(warm.stdout+warm.stderr)
    if warm.returncode:
        raise RuntimeError(f'{experiment} warmup failed:\n{warm.stderr}')
    prefix = '/workspace/'+str(output.relative_to(ROOT))+'/pgbench'
    measured = run(base+['-T',str(duration),'-l','--log-prefix='+prefix,'--sampling-rate=1.0','postgres'],check=False)
    (output/'pgbench.txt').write_text(measured.stdout+measured.stderr)
    logs = []
    failed = 0
    for file in output.glob('pgbench.*'):
        if file.suffix == '.txt': continue
        for line in file.read_text().splitlines():
            parts = line.split()
            if len(parts)<4: continue
            try:
                logs.append((float(parts[2])/1000,int(parts[3])))
            except ValueError:
                failed += 1
    def metrics(values):
        values=sorted(values)
        if not values: return dict(count=0,avg_ms=None,p95_ms=None,p99_ms=None)
        return dict(count=len(values), avg_ms=sum(values)/len(values),
                    p95_ms=values[int((len(values)-1)*.95)], p99_ms=values[int((len(values)-1)*.99)])
    result = dict(experiment=experiment, clients=clients, duration_seconds=duration, seed=seed,
                  exit_code=measured.returncode, failed_logs=failed,
                  **metrics([x[0] for x in logs]),
                  transactions={f'T{i+1}':metrics([lat for lat,idx in logs if idx==i]) for i in range(9)})
    m=re.search(r'^tps = ([\d.]+)',measured.stdout,re.M)
    result['pgbench_tps']=float(m[1]) if m else None
    result['successful_tps_by_duration']=len(logs)/duration
    (output/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    if measured.returncode:
        raise RuntimeError(f'{experiment} benchmark exit {measured.returncode}; see {output}')
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--experiments',nargs='+',default=['expt_a0']+[f'expt_a{i}' for i in range(101,109)])
    parser.add_argument('--clients',nargs='+',type=int,default=[1,4])
    parser.add_argument('--duration',type=int,default=20)
    parser.add_argument('--seed',type=int,default=42)
    parser.add_argument('--output',required=True)
    parser.add_argument('--setup-only',action='store_true')
    args=parser.parse_args()
    output=ROOT/args.output
    output.mkdir(parents=True,exist_ok=True)
    initialize_cluster()
    environment=dict(environment='LOCAL DOCKER PILOT — not SoC Slurm', scale=.01, workers=4,
      shared_buffers='256MB', work_mem_default='32MB', isolation='serializable',
      default_pool=4, seed=args.seed, warmup_seconds=5, measured_seconds=args.duration,
      versions=sql("SELECT version(); SELECT extversion FROM pg_extension WHERE extname='citus';"),
      dimensions=DEFS, workload_weights=WEIGHTS, log_sample_rate=1.0,
      docker=run(['docker','info','--format','{{.Architecture}} {{.NCPU}} CPUs {{.MemTotal}} bytes']).stdout.strip())
    (output/'environment.json').write_text(json.dumps(environment,indent=2)+'\n')
    for expt in args.experiments:
        for clients in args.clients:
            target=output/expt/f'c{clients}'
            if (target/'verification.json').exists():
                print(f'{expt} c{clients}: already complete',flush=True)
                continue
            if target.exists() and any(target.iterdir()):
                raise RuntimeError(f'Result directory already has data: {target}. Use a fresh --output.')
            print(f'{expt} c{clients}: setting up',flush=True)
            manifest=prepare(expt,target)
            checks=verify(manifest.get('summary',False),'before_')
            if args.setup_only:
                (target/'setup-verification.json').write_text(json.dumps(checks,indent=2)+'\n')
                print(f'{expt}: setup checks passed',flush=True)
                continue
            print(f'{expt} c{clients}: benchmarking',flush=True)
            result=benchmark(expt,target,clients,args.duration,args.seed)
            checks.update(verify(manifest.get('summary',False),'after_'))
            (target/'verification.json').write_text(json.dumps(checks,indent=2)+'\n')
            print(f'{expt} c{clients}: {result["pgbench_tps"]} TPS, checks passed',flush=True)


if __name__=='__main__':
    main()
