\set ON_ERROR_STOP on
BEGIN READ ONLY;
-- Validation runs after timing. Bound a broken/poor validator plan without
-- imposing a statement timeout or different planner settings on pgbench.
SET LOCAL statement_timeout = '5min';
DO $$
DECLARE
  row_count bigint;
  unique_count bigint;
BEGIN
  IF EXISTS (SELECT 1 FROM inventory WHERE quantity < 0) THEN
    RAISE EXCEPTION 'Correctness: negative inventory';
  END IF;
  -- IDs are NOT NULL in every submission schema. Exact COUNT(DISTINCT) tests
  -- the same global uniqueness as GROUP BY ... HAVING count(*) > 1, avoiding
  -- the expensive coordinator hash aggregate over millions of count groups.
  SELECT count(*), count(DISTINCT order_id) INTO row_count, unique_count FROM orders;
  IF row_count <> unique_count THEN
    RAISE EXCEPTION 'Correctness: duplicated global order ID';
  END IF;
  SELECT count(*), count(DISTINCT order_item_id) INTO row_count, unique_count FROM order_items;
  IF row_count <> unique_count THEN
    RAISE EXCEPTION 'Correctness: duplicated global item ID';
  END IF;
  IF EXISTS (
    SELECT 1 FROM orders o LEFT JOIN
      (SELECT merchant_id,order_id,sum(quantity*unit_price)::numeric(12,2) amount
       FROM order_items GROUP BY merchant_id,order_id) x
    ON o.order_id=x.order_id AND o.merchant_id=x.merchant_id
    WHERE o.total_amount IS DISTINCT FROM COALESCE(x.amount,0)
  ) THEN
    RAISE EXCEPTION 'Correctness: order total does not match items';
  END IF;
END;
$$;
SELECT 'core invariants passed' AS validation;
COMMIT;
