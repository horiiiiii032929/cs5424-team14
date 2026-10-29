BEGIN READ ONLY;

SELECT
  LOCALTIMESTAMP - (:REPORT_DAYS)::integer * INTERVAL '1 day' AS window_start,
  LOCALTIMESTAMP AS window_end
\gset t6_

SELECT
  merchant_id,
  COUNT(*) AS order_count,
  SUM(total_amount) AS revenue
FROM orders
WHERE created_at >= TIMESTAMP ':t6_window_start'
  AND created_at < TIMESTAMP ':t6_window_end'
GROUP BY merchant_id
ORDER BY revenue DESC
LIMIT 20;

COMMIT;
