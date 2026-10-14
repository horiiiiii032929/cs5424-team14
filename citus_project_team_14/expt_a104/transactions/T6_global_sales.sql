BEGIN;
-- Full calendar days come from exact summaries. Partial days use raw orders,
-- preserving the original [now - REPORT_DAYS, now) interval exactly.
WITH bounds AS (
  SELECT CURRENT_TIMESTAMP - (:REPORT_DAYS)::integer * INTERVAL '1 day' AS lo,
         CURRENT_TIMESTAMP AS hi
), full_days AS (
  SELECT lo, hi,
    date_trunc('day', lo) + CASE WHEN lo = date_trunc('day', lo)
      THEN INTERVAL '0 days' ELSE INTERVAL '1 day' END AS first_day,
    date_trunc('day', hi) AS last_day
  FROM bounds
), parts AS (
  SELECT s.merchant_id, s.order_count, s.revenue
  FROM sales_daily s CROSS JOIN full_days b
  WHERE s.sales_day >= b.first_day AND s.sales_day < b.last_day
  UNION ALL
  SELECT o.merchant_id, count(*) AS order_count, sum(o.total_amount) AS revenue
  FROM orders o CROSS JOIN full_days b
  WHERE o.created_at >= b.lo AND o.created_at < b.hi
    AND NOT (o.created_at >= b.first_day AND o.created_at < b.last_day)
  GROUP BY o.merchant_id
)
SELECT merchant_id, sum(order_count)::bigint AS order_count, sum(revenue) AS revenue
FROM parts GROUP BY merchant_id ORDER BY revenue DESC LIMIT 20;
COMMIT;
