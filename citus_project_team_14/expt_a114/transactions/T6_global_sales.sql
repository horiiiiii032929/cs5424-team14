BEGIN READ ONLY;
-- Full calendar days come from exact summaries. Partial days use raw orders,
-- preserving the original [now - REPORT_DAYS, now) interval exactly. Bounds are
-- computed once; the raw branch scans only the two partial-day ranges
-- [lo, first_day) and [last_day, hi), which are empty when REPORT_DAYS is 0.
WITH b AS (
  SELECT lo, hi,
    date_trunc('day', lo) + CASE WHEN lo = date_trunc('day', lo)
      THEN INTERVAL '0 days' ELSE INTERVAL '1 day' END AS first_day,
    date_trunc('day', hi) AS last_day
  FROM (SELECT CURRENT_TIMESTAMP - (:REPORT_DAYS)::integer * INTERVAL '1 day' AS lo,
               CURRENT_TIMESTAMP AS hi) now_bounds
)
SELECT merchant_id, sum(order_count)::bigint AS order_count, sum(revenue) AS revenue
FROM (
  SELECT s.merchant_id, s.order_count, s.revenue
  FROM sales_daily s, b
  WHERE s.sales_day >= b.first_day AND s.sales_day < b.last_day
  UNION ALL
  SELECT o.merchant_id, count(*), sum(o.total_amount)
  FROM orders o, b
  WHERE (o.created_at >= b.lo AND o.created_at < LEAST(b.first_day, b.hi))
     OR (o.created_at >= GREATEST(b.last_day, b.lo) AND o.created_at < b.hi)
  GROUP BY o.merchant_id
) parts
GROUP BY merchant_id ORDER BY revenue DESC LIMIT 20;
COMMIT;
