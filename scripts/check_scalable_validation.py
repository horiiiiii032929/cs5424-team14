#!/usr/bin/env python3
"""Verify exact global-ID checks on valid and deliberately invalid Citus data."""
import argparse
import json
from pathlib import Path

from local_experiments import ROOT, COMPOSE, initialize_cluster, prepare, run, sql


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    target = ROOT / args.output
    if target.exists():
        raise SystemExit('Preserve previous validation evidence; use a fresh output.')
    initialize_cluster()
    prepare('expt_a101', target, small=True)
    source = (ROOT / 'optimizations/verify_scalable.sql').read_text()
    command = COMPOSE + ['exec', '-T', 'coordinator', 'psql', '-X', '-q', '-v',
                         'ON_ERROR_STOP=1', '-U', 'postgres', '-d', 'postgres']
    checks = {}

    def validate(name, expected_error=None):
        result = run(command, source, check=False)
        (target / (name + '.txt')).write_text(result.stdout + result.stderr)
        if expected_error:
            assert result.returncode != 0 and expected_error in result.stderr, (name, result.stdout, result.stderr)
        else:
            assert result.returncode == 0 and 'core invariants passed' in result.stdout, (name, result.stdout, result.stderr)
        checks[name] = True

    validate('valid_data')
    sql("INSERT INTO orders SELECT order_id,9999,customer_id,order_status,0,created_at FROM orders WHERE order_id=1;")
    validate('global_order_duplicate_rejected', 'duplicated global order ID')
    sql('DELETE FROM orders WHERE merchant_id=9999;')
    validate('order_duplicate_removed')
    sql("INSERT INTO order_items SELECT order_item_id,9999,order_id,product_id,quantity,unit_price FROM order_items WHERE order_item_id=1;")
    validate('global_item_duplicate_rejected', 'duplicated global item ID')
    sql('DELETE FROM order_items WHERE merchant_id=9999;')
    validate('item_duplicate_removed')
    sql('UPDATE orders SET total_amount=total_amount+1 WHERE order_id=1;')
    validate('incorrect_order_total_rejected', 'order total does not match items')
    sql('UPDATE orders SET total_amount=total_amount-1 WHERE order_id=1;')
    validate('total_restored')
    (target / 'verification.json').write_text(json.dumps(checks, indent=2) + '\n')
    print(f'{len(checks)} distributed validation checks passed', flush=True)


if __name__ == '__main__':
    main()
