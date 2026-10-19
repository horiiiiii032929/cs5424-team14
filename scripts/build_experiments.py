#!/usr/bin/env python3
"""Build self-contained submission experiments from the preserved team baseline.

No cluster files are changed. Reserve new experiment IDs with teammates before merging
into the shared account. Rebuilds replace generated code, never result folders.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'citus_project_team_14'
SOURCE = OUT / 'expt_a0'
OPTIONS = {
    'expt_a101': dict(name='Merchant colocation', colocate=True),
    'expt_a102': dict(name='Lookup indexes', indexes=True),
    'expt_a103': dict(name='One-call place order', procedure=True),
    'expt_a104': dict(name='Exact sales summaries', summary=True),
    'expt_a105': dict(name='work_mem 64MB', work_mem='64MB'),
    'expt_a106': dict(name='Executor pool 2', pool=2),
    'expt_a107': dict(name='Executor pool 8', pool=8),
    'expt_a108': dict(name='Colocation + indexes + one-call order + summary',
                      colocate=True, indexes=True, procedure=True, summary=True),
    'expt_a109': dict(name='Merchant colocation + declared read-only queries',
                      colocate=True, read_only=True, derives_from='expt_a101'),
    'expt_a110': dict(name='Combined design + declared read-only queries',
                      colocate=True, indexes=True, procedure=True, summary=True,
                      read_only=True, derives_from='expt_a108'),
    'expt_a111': dict(name='Lookup indexes + product/order join colocation',
                      indexes=True, join_colocation=True, derives_from='expt_a102',
                      attribution='Hikaru A adaptation of Dessi B b1/b2 placement'),
    'expt_a112': dict(name='Product/order join colocation + read-only queries',
                      indexes=True, join_colocation=True, read_only=True,
                      derives_from='expt_a111',
                      attribution='Hikaru A adaptation of Dessi B b1/b2 placement'),
    'expt_a113': dict(name='Product/order join colocation + READ ONLY DEFERRABLE',
                      indexes=True, join_colocation=True, read_only=True,
                      read_only_deferrable=True, derives_from='expt_a112',
                      attribution='Hikaru A adaptation of Dessi B b1/b2 placement'),
    'expt_a114': dict(name='a112 + exact daily sales summaries (8 stripes)',
                      indexes=True, join_colocation=True, read_only=True,
                      summary=True, summary_stripes=8,
                      summary_report='T6_sales_summary_ranges.sql', derives_from='expt_a112',
                      attribution='Hikaru A adaptation of Dessi B b1/b2 placement'),
}


def function_script(summary):
    s = (SOURCE / 'transactions/T1_place_order.sql').read_text()
    prefix = s[:s.index('\\set order_ok')]
    blocks = [prefix]
    for j in range(1, 6):
        blocks.append(f'''\\set product_id_{j} 0
\\set qty_{j} 0
\\if :item_count >= {j}
\\if :DEBUG_MODE
\\set product_id_{j} :DEBUG_PRODUCT_ID_{j}
\\set qty_{j} :DEBUG_QTY_{j}
\\else
\\set product_slot_{j} random(0, ((:NUM_PRODUCTS - :merchant_id) / :NUM_MERCHANTS))
\\set product_id_{j} :merchant_id + (:product_slot_{j} * :NUM_MERCHANTS)
\\set qty_{j} random(:MIN_ORDER_QTY, :MAX_ORDER_QTY)
\\endif
\\endif
''')
    products = ','.join(f':product_id_{j}' for j in range(1, 6))
    quantities = ','.join(f':qty_{j}' for j in range(1, 6))
    blocks.append(f'''BEGIN;
SELECT place_order((:merchant_id)::bigint, (:customer_id)::bigint,
    (ARRAY[{products}]::bigint[])[1: :item_count],
    (ARRAY[{quantities}]::integer[])[1: :item_count],
    {'true' if summary else 'false'});
COMMIT;
''')
    return ''.join(blocks)


def build(name, opts):
    dest = OUT / name
    dest.mkdir(exist_ok=True)
    shutil.copytree(SOURCE / 'transactions', dest / 'transactions', dirs_exist_ok=True)
    sql_dir = dest / 'sql'
    sql_dir.mkdir(exist_ok=True)
    # Rebuilding must not leave old feature scripts enabled.
    for old in sql_dir.glob('*.sql'):
        old.unlink()
    script = (SOURCE / 'run.sh').read_text()
    script = script.replace('#SBATCH --mail-type=BEGIN,END,FAIL', '# Mail notifications disabled for Hikaru experiments.')
    script = re.sub(r'^#SBATCH --mail-user=.*$', '', script, flags=re.M)
    setup = []
    postload = []
    if opts.get('colocate'):
        for table, key in [('customers','customer_id'), ('products','product_id'),
                           ('inventory','inventory_id'), ('orders','order_id'),
                           ('order_items','order_item_id')]:
            script = script.replace(f'{table}({key} BIGINT PRIMARY KEY,', f'{table}({key} BIGINT,')
            line = next(line for line in script.splitlines() if line.startswith(f'CREATE TABLE IF NOT EXISTS {table}('))
            script = script.replace(line, line[:-2] + f', PRIMARY KEY (merchant_id, {key}));')
            script = script.replace(f"create_distributed_table('{table}','{key}')",
                                    f"create_distributed_table('{table}','merchant_id')")
        # Include merchant in joins during deterministic data generation too.
        script = script.replace('FROM y JOIN products p USING(product_id)',
                                'FROM y JOIN products p USING(product_id,merchant_id)')
        script = script.replace('SELECT order_id,SUM(quantity*unit_price)',
                                'SELECT merchant_id,order_id,SUM(quantity*unit_price)')
        script = script.replace('FROM order_items GROUP BY order_id) x WHERE o.order_id=x.order_id;',
                                'FROM order_items GROUP BY merchant_id,order_id) x WHERE o.order_id=x.order_id AND o.merchant_id=x.merchant_id;')
        t3 = dest / 'transactions/T3_order_history.sql'
        t3.write_text(t3.read_text().replace('ON oi.order_id = o.order_id',
                                           'ON oi.order_id = o.order_id AND oi.merchant_id = o.merchant_id'))
        t1 = dest / 'transactions/T1_place_order.sql'
        t1.write_text(t1.read_text().replace('WHERE order_id = (:new_order_id)::bigint;',
                         'WHERE order_id = (:new_order_id)::bigint AND merchant_id = (:merchant_id)::bigint;'))
        # T5 accepts only an order ID; retain the exact operation (fan-out).
        # T7 accepts product IDs; retain the general cross-merchant transfer.
    if opts.get('join_colocation'):
        # Adapt the pair-wise placement described in Dessi's B report, retaining
        # orders/order_id and products/product_id instead of moving all tables
        # onto merchant_id. Every added routing predicate uses the product ID
        # used to look up that inventory row, not inventory_id == product_id.
        for table, old_key, new_key, peer in [
            ('inventory', 'inventory_id', 'product_id', 'products'),
            ('order_items', 'order_item_id', 'order_id', 'orders'),
        ]:
            script = script.replace(f'{table}({old_key} BIGINT PRIMARY KEY,',
                                    f'{table}({old_key} BIGINT,')
            line = next(line for line in script.splitlines() if line.startswith(f'CREATE TABLE IF NOT EXISTS {table}('))
            script = script.replace(line, line[:-2] + f', PRIMARY KEY ({new_key}, {old_key}));')
            script = script.replace(f"create_distributed_table('{table}','{old_key}')",
                                    f"create_distributed_table('{table}','{new_key}', colocate_with => '{peer}')")
        path = dest / 'transactions/T7_inventory_transfer.sql'
        transaction = path.read_text()
        for side in ['source', 'dest']:
            predicate = f'WHERE inventory_id = (:{side}_inventory_id)::bigint'
            transaction = transaction.replace(predicate,
                predicate + f' AND product_id = (:{side}_product_id)::bigint')
        path.write_text(transaction)
    if opts.get('indexes'):
        shutil.copy(ROOT / 'optimizations/indexes.sql', sql_dir / 'indexes.sql')
        setup.append('indexes.sql')
    stripes = opts.get('summary_stripes')
    if opts.get('summary'):
        # Striped variants keep the same file names so run.sh and the local
        # harness load them through the existing summary hooks.
        for f in ['sales_summary_schema.sql', 'sales_summary_load.sql']:
            source = f.replace('sales_summary_', 'sales_summary_striped_') if stripes else f
            shutil.copy(ROOT / 'optimizations' / source, sql_dir / f)
        if stripes and f'stripe < {stripes})' not in (sql_dir / 'sales_summary_schema.sql').read_text():
            raise ValueError(f'Striped summary schema does not allow exactly {stripes} stripes')
        setup.append('sales_summary_schema.sql')
        postload.append('sales_summary_load.sql')
        script = script.replace('DROP TABLE IF EXISTS order_items CASCADE;',
                                'DROP TABLE IF EXISTS sales_daily CASCADE; DROP TABLE IF EXISTS order_items CASCADE;')
        # a114 scans only the two partial-day order ranges instead of the full
        # report window minus whole days (same result, fewer raw rows).
        shutil.copy(ROOT / 'optimizations' / opts.get('summary_report', 'T6_sales_summary.sql'),
                    dest / 'transactions/T6_global_sales.sql')
        t1 = dest / 'transactions/T1_place_order.sql'
        transaction = t1.read_text()
        if transaction.count('COMMIT;') != 1:
            raise ValueError(f'Expected exactly one commit in {t1}')
        if stripes:
            # Same exact upsert, last before COMMIT, on one of the merchant's
            # day stripes. Consecutive order IDs spread concurrent hot orders.
            upsert = f'''INSERT INTO sales_daily VALUES
  ((:merchant_id)::bigint, date_trunc('day', CURRENT_TIMESTAMP),
   ((:new_order_id)::bigint % {stripes})::smallint, 1, (:order_total)::numeric(12,2))
ON CONFLICT (merchant_id,sales_day,stripe) DO UPDATE
SET order_count=sales_daily.order_count+1,revenue=sales_daily.revenue+EXCLUDED.revenue;
COMMIT;'''
        else:
            upsert = '''INSERT INTO sales_daily VALUES
  ((:merchant_id)::bigint, date_trunc('day', CURRENT_TIMESTAMP), 1, (:order_total)::numeric(12,2))
ON CONFLICT (merchant_id,sales_day) DO UPDATE
SET order_count=sales_daily.order_count+1,revenue=sales_daily.revenue+EXCLUDED.revenue;
COMMIT;'''
        t1.write_text(transaction.replace('COMMIT;', upsert))
    if opts.get('procedure'):
        shutil.copy(ROOT / 'optimizations/place_order.sql', sql_dir / 'place_order.sql')
        setup.append('place_order.sql')
        (dest / 'transactions/T1_place_order.sql').write_text(function_script(opts.get('summary', False)))
    if opts.get('work_mem'):
        script = script.replace('PG_WORK_MEM:-32MB', 'PG_WORK_MEM:-' + opts['work_mem'])
    if opts.get('pool'):
        script = script.replace('CITUS_MAX_ADAPTIVE_EXECUTOR_POOL_SIZE:-4',
                                'CITUS_MAX_ADAPTIVE_EXECUTOR_POOL_SIZE:-' + str(opts['pool']))
    if opts.get('read_only'):
        # Access mode is independent of isolation. Keep SERIALIZABLE, queries,
        # weights, durability and retry limits unchanged. a113 independently
        # tests waiting for safe read-only snapshots with DEFERRABLE.
        for transaction in ['T3_order_history.sql', 'T4_product_lookup.sql', 'T6_global_sales.sql']:
            path = dest / 'transactions' / transaction
            original = path.read_text()
            if original.count('BEGIN;') != 1:
                raise ValueError(f'Expected exactly one transaction in {path}')
            access_mode = 'BEGIN READ ONLY DEFERRABLE;' if opts.get('read_only_deferrable') else 'BEGIN READ ONLY;'
            path.write_text(original.replace('BEGIN;', access_mode, 1))
    if opts.get('read_only') or opts.get('join_colocation'):
        script = script.replace('#SBATCH --partition=normal',
                                '#SBATCH --partition=normal\n#SBATCH --constraint=xcnf')
    validation=['verify.sql']
    if opts.get('summary'): validation.append('verify_summary.sql')
    for file in validation:
        source = 'verify_scalable.sql' if file == 'verify.sql' and (opts.get('colocate') or opts.get('join_colocation')) else file
        if file == 'verify_summary.sql' and stripes:
            source = 'verify_summary_striped.sql'
        shutil.copy(ROOT/'optimizations'/source,sql_dir/file)
    validation_commands='\n'.join(f'\t\tpsqlx -f "$SCRIPT_DIR/sql/{f}" >> "$JOB_RESULT_DIR/validation.log"' for f in validation)
    needle='\t\tanalyze_run "$clients" "$prefix" "$RUN_DIR/result-c${clients}.txt" "$pgbench_rc"'
    script=script.replace(needle,needle+'\n'+validation_commands)
    hooks = '\n'.join(f'psqlx -f "$SCRIPT_DIR/sql/{f}"' for f in setup)
    script = script.replace('create_schema &>"$JOB_RESULT_DIR/schema-create.log"',
                            'create_schema &>"$JOB_RESULT_DIR/schema-create.log"\n' + hooks)
    hooks = '\n'.join(f'\tpsqlx -f "$SCRIPT_DIR/sql/{f}"' for f in postload)
    script = script.replace('\techo "Synthetic data generation complete.',
                            hooks + '\n\techo "Synthetic data generation complete.')
    # Record the actual code alongside every Slurm result, including overrides.
    script = script.replace('record_server_versions || true', '''record_server_versions || true
cp "$SCRIPT_DIR/experiment.json" "$JOB_RESULT_DIR/experiment.json"
sha256sum "$SCRIPT_DIR/run.sh" "$TX_DIR/"*.sql "$SCRIPT_DIR/sql/"*.sql > "$JOB_RESULT_DIR/code-sha256.txt"
''')
    (dest / 'run.sh').write_text(script)
    (dest / 'run.sh').chmod(0o755)
    manifest = dict(experiment=name, owner='Hikaru', workload='A', status='implemented; see results for validation',
                    baseline='expt_a0', **opts)
    if opts.get('colocate') or opts.get('join_colocation'):
        manifest['validator'] = 'exact-count-distinct; post-measurement only'
    manifest['baseline_script_sha256'] = hashlib.sha256((SOURCE / 'run.sh').read_bytes()).hexdigest()
    (dest / 'experiment.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (dest / 'README.md').write_text(f'''# {name}: {opts['name']}

Hikaru — Task 2 / workload A. Generated by `scripts/build_experiments.py`.
All nine transaction weights, input distributions, isolation, durability and
full log sampling remain the baseline defaults. No performance win is assumed.
Run `sbatch run.sh` from this directory on the course cluster.
See the repository results for measured evidence and its environment.
''')


def main():
    OUT.mkdir(exist_ok=True)
    if not SOURCE.exists():
        for expt in ['expt_a0', 'expt_b0']:
            shutil.copytree(ROOT / 'team_snapshot' / expt, OUT / expt)
        shutil.copy(ROOT / 'team_snapshot/install_citus_slurm.sh', OUT / 'install_citus_slurm.sh')
    for name, opts in OPTIONS.items():
        build(name, opts)
    (OUT / 'README.md').write_text('''# Team 14 experiments

`expt_a0` and `expt_b0` are Dessi's preserved baseline snapshots (jobs 918524 and
918781). `expt_a101`–`expt_a114` are Hikaru's proposed Task 2 experiments. Each
folder contains a complete run.sh, transactions and any supporting SQL.
New IDs must be checked against current team work. a109/a110 isolate the
read-only access declaration relative to a101/a108. a111 adapts Dessi's B b1/b2
placement on a102; a112 adds read-only access declarations to a111. All new
variants require xcnf nodes. a113 adds DEFERRABLE to a112's read-only transactions
to test safe-snapshot waits without lowering isolation. a114 adds a104's exact
daily sales summaries to a112, striped eight ways per merchant/day to limit
hot-row upsert conflicts; T6 reads the summary plus only the two partial-day
order ranges under READ ONLY.

| Experiment | Change from baseline |
|---|---|
''' + ''.join(f'| {name} | {opts["name"]} |\n' for name, opts in OPTIONS.items()))


if __name__ == '__main__':
    main()
