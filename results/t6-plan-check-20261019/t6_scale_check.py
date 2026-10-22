"""Time T6 variants at scale 0.2 (1M orders) on the local Docker cluster."""
import json, re, shutil, sys
from pathlib import Path
repo, scratch = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(repo/'scripts'))
import local_experiments as le
SCALE = {'NUM_MERCHANTS=10\n':'NUM_MERCHANTS=200\n','NUM_CUSTOMERS=10000\n':'NUM_CUSTOMERS=200000\n',
         'NUM_PRODUCTS=5000\n':'NUM_PRODUCTS=100000\n','NUM_ORDERS=50000\n':'NUM_ORDERS=1000000\n',
         'NUM_ORDER_ITEMS=150000\n':'NUM_ORDER_ITEMS=3000000\n'}
real_run = le.run
def run(args, text=None, check=True):
    if text and 'generate_data' in text:
        for a, b in SCALE.items():
            assert a in text, a
            text = text.replace(a, b)
    return real_run(args, text, check)
le.run = run
out = repo/'results/t6-plan-check-20261019'
le.prepare('expt_a114', out/'setup')
(out/'setup'/'fixture.json').write_text(json.dumps(dict(scale=0.2, merchants=200, customers=200000,
    products=100000, orders=1000000, items=3000000), indent=2)+'\n')
variants = {'a112_original': repo/'citus_project_team_14/expt_a112/transactions/T6_global_sales.sql',
            'a104_summary': repo/'citus_project_team_14/expt_a104/transactions/T6_global_sales.sql',
            'a114_two_range': scratch/'t6_ranges.sql'}
workdir = repo/'results/t6-plan-check-20261019/queries'; workdir.mkdir(exist_ok=True)
results = {}
def bench(name, path):
    dest = workdir/(name+'.sql'); shutil.copy(path, dest)
    p = le.run(le.COMPOSE+['exec','-T','coordinator','pgbench','-U','postgres','-h','coordinator','-n','-c','1',
        '-t','30','-D','REPORT_DAYS=30','-f','/workspace/'+str(dest.relative_to(repo)),'postgres'])
    (workdir/(name+'-pgbench.txt')).write_text(p.stdout+p.stderr)
    lat = float(re.search(r'latency average = ([\d.]+) ms', p.stdout)[1])
    body = dest.read_text()
    body = re.sub(r'BEGIN( READ ONLY)?;', '', body).replace('COMMIT;','').strip().rstrip(';').replace('(:REPORT_DAYS)','(30)')
    (workdir/(name+'-explain.txt')).write_text(le.sql('EXPLAIN (ANALYZE, COSTS OFF) '+body+';')+'\n')
    results[name] = lat; print(name, lat, 'ms', flush=True)
for name, path in variants.items(): bench(name, path)
bench('a112_original_with_created_at_index', variants['a112_original'])
le.sql('DROP INDEX idx_orders_report_time;')
bench('a112_original_as_in_a112', variants['a112_original'])
(out/'latency-ms.json').write_text(json.dumps(results, indent=2)+'\n')
