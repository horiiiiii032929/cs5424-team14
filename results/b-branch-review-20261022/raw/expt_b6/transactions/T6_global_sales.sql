BEGIN READ ONLY;

-- Split the window [window_start, window_end) into three parts that cover it exactly:
--   [window_start, first_whole_day)     partial first day, read from orders
--   [first_whole_day, cutoff_day)       whole days, read from merchant_daily_sales
--   [tail_start, window_end)            everything since the cutoff, read from orders
SELECT
  window_start,
  window_end,
  first_whole_day,
  cutoff_day,
  GREATEST(cutoff_day, first_whole_day) AS tail_start
FROM (
  SELECT
    w.window_start,
    w.window_end,
    CASE WHEN w.window_start = date_trunc('day', w.window_start)
         THEN w.window_start::date
         ELSE w.window_start::date + 1
    END AS first_whole_day,
    c.cutoff_day
  FROM (
    SELECT
      LOCALTIMESTAMP - (:REPORT_DAYS)::integer * INTERVAL '1 day' AS window_start,
      LOCALTIMESTAMP AS window_end
  ) AS w
  CROSS JOIN merchant_daily_sales_cutoff AS c
) AS t
\gset t6_

SELECT
  merchant_id,
  SUM(order_count)::bigint AS order_count,
  SUM(revenue) AS revenue
FROM (
  SELECT merchant_id, SUM(order_count)::bigint AS order_count, SUM(revenue) AS revenue
  FROM merchant_daily_sales
  WHERE sales_day >= DATE ':t6_first_whole_day'
    AND sales_day < DATE ':t6_cutoff_day'
  GROUP BY merchant_id
  UNION ALL
  SELECT merchant_id, COUNT(*), SUM(total_amount)
  FROM orders
  WHERE created_at >= TIMESTAMP ':t6_window_start'
    AND created_at < TIMESTAMP ':t6_first_whole_day'
  GROUP BY merchant_id
  UNION ALL
  SELECT merchant_id, COUNT(*), SUM(total_amount)
  FROM orders
  WHERE created_at >= TIMESTAMP ':t6_tail_start'
    AND created_at < TIMESTAMP ':t6_window_end'
  GROUP BY merchant_id
) AS parts
GROUP BY merchant_id
ORDER BY revenue DESC
LIMIT 20;

COMMIT;
