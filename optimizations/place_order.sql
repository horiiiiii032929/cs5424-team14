-- Idea 3: one client call; function executes on the coordinator.
-- Deliberately not worker-delegated: ID sequences live on the coordinator.
CREATE OR REPLACE FUNCTION place_order(
  p_merchant bigint, p_customer bigint, p_products bigint[], p_quantities integer[],
  p_summary boolean DEFAULT false
) RETURNS bigint LANGUAGE plpgsql AS $$
DECLARE
  v_order bigint;
  v_item bigint;
  v_price numeric(12,2);
  v_total numeric(12,2) := 0;
  v_rows integer;
  j integer;
BEGIN
  IF p_products IS NULL OR p_quantities IS NULL
     OR cardinality(p_products) NOT BETWEEN 1 AND 5
     OR cardinality(p_products) IS DISTINCT FROM cardinality(p_quantities)
     OR array_position(p_products, NULL) IS NOT NULL
     OR array_position(p_quantities, NULL) IS NOT NULL THEN
    RAISE EXCEPTION 'Invalid order arrays' USING ERRCODE = '22023';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM customers
                 WHERE merchant_id=p_merchant AND customer_id=p_customer) THEN
    RETURN NULL;
  END IF;
  -- A business rejection rolls back this whole block, including earlier items.
  -- Serialization/deadlock exceptions propagate to pgbench for whole-tx retry.
  BEGIN
    v_order := nextval('benchmark_order_id_seq');
    INSERT INTO orders VALUES
      (v_order, p_merchant, p_customer, 'PENDING', 0, CURRENT_TIMESTAMP);
    FOR j IN 1..cardinality(p_products) LOOP
      IF p_quantities[j] <= 0 THEN
        RAISE EXCEPTION 'Quantity must be positive' USING ERRCODE = '22023';
      END IF;
      SELECT price INTO v_price FROM products
      WHERE merchant_id=p_merchant AND product_id=p_products[j];
      IF NOT FOUND THEN RAISE EXCEPTION 'Unknown product' USING ERRCODE='P0002'; END IF;
      UPDATE inventory SET quantity=quantity-p_quantities[j], updated_at=CURRENT_TIMESTAMP
      WHERE merchant_id=p_merchant AND inventory_id=p_products[j]
        AND product_id=p_products[j] AND quantity>=p_quantities[j];
      GET DIAGNOSTICS v_rows = ROW_COUNT;
      IF v_rows <> 1 THEN RAISE EXCEPTION 'Insufficient stock' USING ERRCODE='P0002'; END IF;
      v_item := nextval('benchmark_order_item_id_seq');
      INSERT INTO order_items VALUES
        (v_item, p_merchant, v_order, p_products[j], p_quantities[j], v_price);
      v_total := v_total + p_quantities[j]*v_price;
    END LOOP;
    UPDATE orders SET total_amount=v_total
    WHERE merchant_id=p_merchant AND order_id=v_order;
    IF p_summary THEN
      INSERT INTO sales_daily VALUES (p_merchant, date_trunc('day', CURRENT_TIMESTAMP), 1, v_total)
      ON CONFLICT (merchant_id, sales_day) DO UPDATE
      SET order_count=sales_daily.order_count+1, revenue=sales_daily.revenue+EXCLUDED.revenue;
    END IF;
    RETURN v_order;
  EXCEPTION WHEN no_data_found THEN
    RETURN NULL;
  END;
END;
$$;
