"""Interleaved T6 timing rounds on the already-loaded scale-0.2 fixture."""
import json, re, sys, statistics
from pathlib import Path
repo = Path(sys.argv[1]); sys.path.insert(0, str(repo/'scripts'))
import local_experiments as le
q = repo/'results/t6-plan-check-20261019/queries'
def lat(name):
    p = le.run(le.COMPOSE+['exec','-T','coordinator','pgbench','-U','postgres','-h','coordinator','-n','-c','1',
        '-t','50','-D','REPORT_DAYS=30','-f','/workspace/'+str((q/(name+'.sql')).relative_to(repo)),'postgres'])
    return float(re.search(r'latency average = ([\d.]+) ms', p.stdout)[1])
rounds = {k: [] for k in ['original_with_created_at_index','a104_summary','a114_two_range','original_as_in_a112']}
le.sql('CREATE INDEX idx_orders_report_time ON orders (created_at);')
for _ in range(3):
    rounds['original_with_created_at_index'].append(lat('a112_original'))
    rounds['a104_summary'].append(lat('a104_summary'))
    rounds['a114_two_range'].append(lat('a114_two_range'))
le.sql('DROP INDEX idx_orders_report_time;')
for _ in range(3):
    rounds['original_as_in_a112'].append(lat('a112_original'))
le.sql('CREATE INDEX idx_orders_report_time ON orders (created_at);')
res = {k: dict(rounds_ms=v, median_ms=statistics.median(v)) for k, v in rounds.items()}
(repo/'results/t6-plan-check-20261019/latency-rounds.json').write_text(json.dumps(res, indent=2)+'\n')
print(json.dumps({k: v['median_ms'] for k, v in res.items()}))
