\set ON_ERROR_STOP on
DO $$
DECLARE mismatch_count bigint;
BEGIN
  WITH raw AS (
    SELECT merchant_id,date_trunc('day',created_at) sales_day,count(*) order_count,sum(total_amount) revenue
    FROM orders GROUP BY merchant_id,date_trunc('day',created_at)
  ), mismatches AS (
    (SELECT * FROM raw EXCEPT SELECT * FROM sales_daily)
    UNION ALL (SELECT * FROM sales_daily EXCEPT SELECT * FROM raw)
  ) SELECT count(*) INTO mismatch_count FROM mismatches;
  IF mismatch_count <> 0 THEN
    RAISE EXCEPTION 'Correctness: % sales-summary mismatches', mismatch_count;
  END IF;
END;
$$;
SELECT 'sales summary matches base orders' AS validation;
