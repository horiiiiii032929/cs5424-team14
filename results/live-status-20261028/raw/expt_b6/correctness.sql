\set ON_ERROR_STOP on

BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;

SELECT 'inventory_quantity_negative' AS check_name,
       COUNT(*) AS violations
FROM inventory
WHERE quantity < 0;

SELECT 'order_total_mismatch' AS check_name,
       COUNT(*) AS violations
FROM orders o
LEFT JOIN (
  SELECT order_id, SUM(quantity * unit_price)::numeric(12,2) AS computed_total
  FROM order_items
  GROUP BY order_id
) oi USING (order_id)
WHERE o.total_amount <> COALESCE(oi.computed_total, 0.00);

SELECT 'duplicate_inventory_id' AS check_name,
       COALESCE(SUM(duplicate_count - 1), 0) AS violations
FROM (
  SELECT inventory_id, COUNT(*) AS duplicate_count
  FROM inventory
  GROUP BY inventory_id
  HAVING COUNT(*) > 1
) d;

SELECT 'duplicate_order_item_id' AS check_name,
       COALESCE(SUM(duplicate_count - 1), 0) AS violations
FROM (
  SELECT order_item_id, COUNT(*) AS duplicate_count
  FROM order_items
  GROUP BY order_item_id
  HAVING COUNT(*) > 1
) d;

COMMIT;

