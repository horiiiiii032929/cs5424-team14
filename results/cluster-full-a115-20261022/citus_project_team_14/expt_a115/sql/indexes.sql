-- Idea 2: selective lookups; benchmark writes as well as reads.
CREATE INDEX idx_orders_customer_recent ON orders (merchant_id, customer_id, created_at DESC);
CREATE INDEX idx_items_order ON order_items (order_id);
CREATE INDEX idx_inventory_product ON inventory (product_id);
ANALYZE;
