\set ON_ERROR_STOP on
BEGIN READ ONLY;
-- Post-measurement only; bound the plan without changing pgbench settings.
SET LOCAL statement_timeout = '5min';
DO $$
DECLARE mismatch_count bigint;
BEGIN
  WITH raw AS (
    SELECT merchant_id,date_trunc('day',created_at) sales_day,count(*) order_count,sum(total_amount) revenue
    FROM orders GROUP BY merchant_id,date_trunc('day',created_at)
  ), summary AS (
    SELECT merchant_id,sales_day,sum(order_count) order_count,sum(revenue) revenue
    FROM sales_daily GROUP BY merchant_id,sales_day
  ), mismatches AS (
    (SELECT * FROM raw EXCEPT SELECT * FROM summary)
    UNION ALL (SELECT * FROM summary EXCEPT SELECT * FROM raw)
  ) SELECT count(*) INTO mismatch_count FROM mismatches;
  IF mismatch_count <> 0 THEN
    RAISE EXCEPTION 'Correctness: % sales-summary mismatches', mismatch_count;
  END IF;
END;
$$;
SELECT 'striped sales summary matches base orders' AS validation;
COMMIT;
