#!/usr/bin/env python3
"""Exercise the actual pgbench scripts, including partial-order rollback."""
import argparse
from decimal import Decimal
import json
from pathlib import Path
from local_experiments import ROOT, COMPOSE, DEFS, initialize_cluster, prepare, run, sql, verify


def pgbench_once(experiment, transaction, overrides, clients=1):
    files = list((ROOT/'citus_project_team_14'/experiment/'transactions').glob(transaction+'_*.sql'))
    assert len(files)==1
    defs=dict(DEFS,DEBUG_MODE=1, DEBUG_MERCHANT_ID=1, DEBUG_CUSTOMER_ID=1,
              DEBUG_ITEM_COUNT=1, DEBUG_INVENTORY_CHANGE=-1000, DEBUG_PRODUCT_ID=1,
              DEBUG_T7_SOURCE_PRODUCT_ID=1, DEBUG_T7_DEST_PRODUCT_ID=2, DEBUG_T7_TRANSFER_QTY=3)
    for j in range(1,6):
        defs[f'DEBUG_PRODUCT_ID_{j}']=1+(j-1)*10
        defs[f'DEBUG_QTY_{j}']=2
    defs.update(overrides)
    args=COMPOSE+['exec','-T','coordinator','pgbench','-U','postgres','-h','coordinator',
                   '-n','-c',str(clients),'-j',str(clients),'-t','1','--max-tries=3','-f','/workspace/'+str(files[0].relative_to(ROOT))]
    for k,v in defs.items(): args+=['-D',f'{k}={v}']
    return run(args+['postgres'])


def state():
    counts=sql('SELECT (SELECT count(*) FROM orders),(SELECT count(*) FROM order_items),(SELECT sum(total_amount) FROM orders);').split('|')
    stock=sql('SELECT product_id,quantity FROM inventory WHERE product_id IN (1,2,11,21,31,41) ORDER BY product_id;')
    return [Decimal(v) for v in counts], stock


def check(expt, target):
    manifest=prepare(expt,target,small=True)
    checks=verify(manifest.get('summary',False),'initial_')
    cases=[
      ('one_item',{},True,1),
      ('five_items',{'DEBUG_ITEM_COUNT':5},True,5),
      ('duplicate_product',{'DEBUG_ITEM_COUNT':2,'DEBUG_PRODUCT_ID_2':1},True,2),
      ('missing_customer',{'DEBUG_CUSTOMER_ID':99999999},False,0),
      ('missing_second_product',{'DEBUG_ITEM_COUNT':2,'DEBUG_PRODUCT_ID_2':99999991},False,0),
      ('second_item_out_of_stock',{'DEBUG_ITEM_COUNT':2,'DEBUG_QTY_2':1000},False,0),
      ('duplicate_exceeds_combined_stock',{'DEBUG_ITEM_COUNT':2,'DEBUG_PRODUCT_ID_2':1,
                                         'DEBUG_QTY_1':60,'DEBUG_QTY_2':60},False,0),
    ]
    for name,defs,success,items in cases:
        sql('UPDATE inventory SET quantity=100 WHERE product_id IN (1,2,11,21,31,41);')
        before,stock_before=state()
        p=pgbench_once(expt,'T1',defs)
        (target/(name+'.txt')).write_text(p.stdout+p.stderr)
        after,stock_after=state()
        assert after[0]-before[0]==int(success), (expt,name,'order count')
        assert after[1]-before[1]==items, (expt,name,'item count')
        if not success:
            assert before==after and stock_before==stock_after, (expt,name,'partial write survived rollback')
        else:
            wanted=Decimal(0)
            expected_stock={int(k):int(v) for k,v in (line.split('|') for line in stock_before.splitlines())}
            for j in range(1,items+1):
                pid=defs.get(f'DEBUG_PRODUCT_ID_{j}',1+(j-1)*10)
                qty=defs.get(f'DEBUG_QTY_{j}',2)
                price=Decimal(sql(f'SELECT price FROM products WHERE product_id={pid};'))
                wanted+=price*qty
                expected_stock[pid]-=qty
            assert after[2]-before[2]==wanted, (expt,name,'order amount')
            actual_stock={int(k):int(v) for k,v in (line.split('|') for line in stock_after.splitlines())}
            assert actual_stock==expected_stock, (expt,name,'stock deductions')
        checks[name]=True
    sql('UPDATE inventory SET quantity=10 WHERE product_id=1;')
    before,_=state()
    pgbench_once(expt,'T1',{'DEBUG_QTY_1':7},clients=2)
    after,_=state()
    assert after[0]-before[0]==1 and sql('SELECT quantity FROM inventory WHERE product_id=1;')=='3'
    checks['competing_orders_do_not_oversell']=True
    sql('UPDATE inventory SET quantity=100 WHERE product_id IN (1,2);')
    pgbench_once(expt,'T2',{})
    assert sql('SELECT quantity FROM inventory WHERE product_id=1;')=='100'
    checks['negative_inventory_update_rejected']=True
    pgbench_once(expt,'T7',{})
    assert sql('SELECT quantity FROM inventory WHERE product_id IN (1,2) ORDER BY product_id;')=='97\n103'
    checks['cross_merchant_transfer_conserves_stock']=True
    pgbench_once(expt,'T7',{'DEBUG_T7_TRANSFER_QTY':1000})
    assert sql('SELECT quantity FROM inventory WHERE product_id IN (1,2) ORDER BY product_id;')=='97\n103'
    checks['transfer_insufficient_stock_rolls_back']=True
    pgbench_once(expt,'T7',{'DEBUG_T7_DEST_PRODUCT_ID':1})
    assert sql('SELECT quantity FROM inventory WHERE product_id IN (1,2) ORDER BY product_id;')=='97\n103'
    checks['same_product_transfer_no_change']=True
    if manifest.get('join_colocation'):
        # Inventory identifiers are not routing keys in this design. Exercise
        # real T7 with IDs different from the product IDs instead of relying on
        # the starter loader's incidental equality of those two columns.
        sql('UPDATE inventory SET inventory_id=inventory_id+1000000 WHERE product_id IN (1,2);')
        pgbench_once(expt,'T7',{})
        assert sql('SELECT quantity FROM inventory WHERE product_id IN (1,2) ORDER BY product_id;')=='94\n106'
        checks['transfer_routes_with_distinct_inventory_ids']=True
        for table, peer, key in [('inventory','products','product_id'), ('order_items','orders','order_id')]:
            assert sql(f"SELECT column_to_column_name(logicalrelid,partkey)='{key}' AND colocationid=(SELECT colocationid FROM pg_dist_partition WHERE logicalrelid='{peer}'::regclass) FROM pg_dist_partition WHERE logicalrelid='{table}'::regclass;") == 't'
            checks[table+'_placement_matches_'+peer]=True
    # Exercise the actual read scripts after changing transaction access modes.
    for transaction in ['T3', 'T4', 'T6']:
        before = state()
        p = pgbench_once(expt, transaction, {})
        (target/(transaction+'_read_query.txt')).write_text(p.stdout+p.stderr)
        assert state() == before, (expt, transaction, 'read query changed data')
        checks[transaction+'_read_query_preserves_state'] = True
    checks.update(verify(manifest.get('summary',False),'final_'))
    for file in sorted((ROOT/'citus_project_team_14'/expt/'sql').glob('verify*.sql')):
        sql(file.read_text())
        checks[file.name]=True
    if manifest.get('procedure'):
        for args in ['NULL,NULL', "ARRAY[]::bigint[],ARRAY[]::integer[]", 'ARRAY[1,11]::bigint[],ARRAY[1]::integer[]']:
            p=run(COMPOSE+['exec','-T','coordinator','psql','-v','ON_ERROR_STOP=1','-U','postgres',
                          '-c',f'SELECT place_order(1,1,{args});'],check=False)
            assert p.returncode!=0 and 'Invalid order arrays' in p.stderr
        checks['invalid_arrays_rejected']=True
    (target/'verification.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(f'{expt}: {len(checks)} correctness checks passed',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True)
    parser.add_argument('--experiments',nargs='+',default=['expt_a0','expt_a101','expt_a103','expt_a104','expt_a108'])
    args=parser.parse_args()
    initialize_cluster()
    for expt in args.experiments:
        print(f'{expt}: checking transactions',flush=True)
        check(expt, ROOT/args.output/expt)
