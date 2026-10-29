-- Idea 4: exact daily totals, maintained synchronously by T1.
-- T5 changes status only; the supplied T6 counts every status.
CREATE TABLE sales_daily (
  merchant_id bigint NOT NULL,
  sales_day timestamp NOT NULL,
  order_count bigint NOT NULL CHECK (order_count >= 0),
  revenue numeric NOT NULL CHECK (revenue >= 0),
  PRIMARY KEY (merchant_id, sales_day)
);
SELECT create_distributed_table('sales_daily', 'merchant_id');
CREATE INDEX idx_orders_report_time ON orders (created_at);
