-- a114: exact daily totals, maintained synchronously by T1, split into eight
-- stripes per merchant/day so concurrent orders for one hot merchant rarely
-- upsert the same row. T1 writes stripe order_id % 8; the loader uses stripe 0.
-- T6 sums every stripe, so totals stay exact. T5 changes status only, and the
-- supplied T6 counts every status.
CREATE TABLE sales_daily (
  merchant_id bigint NOT NULL,
  sales_day timestamp NOT NULL,
  stripe smallint NOT NULL CHECK (stripe >= 0 AND stripe < 8),
  order_count bigint NOT NULL CHECK (order_count >= 0),
  revenue numeric NOT NULL CHECK (revenue >= 0),
  PRIMARY KEY (merchant_id, sales_day, stripe)
);
SELECT create_distributed_table('sales_daily', 'merchant_id');
CREATE INDEX idx_orders_report_time ON orders (created_at);
