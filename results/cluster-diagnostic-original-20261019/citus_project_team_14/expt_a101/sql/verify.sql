\set ON_ERROR_STOP on
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM inventory WHERE quantity < 0) THEN
    RAISE EXCEPTION 'Correctness: negative inventory';
  END IF;
  IF EXISTS (SELECT order_id FROM orders GROUP BY order_id HAVING count(*) > 1) THEN
    RAISE EXCEPTION 'Correctness: duplicated global order ID';
  END IF;
  IF EXISTS (SELECT order_item_id FROM order_items GROUP BY order_item_id HAVING count(*) > 1) THEN
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
