TRUNCATE sales_daily;
INSERT INTO sales_daily
SELECT merchant_id, date_trunc('day', created_at), 0, count(*), sum(total_amount)
FROM orders GROUP BY merchant_id, date_trunc('day', created_at);
ANALYZE sales_daily;
