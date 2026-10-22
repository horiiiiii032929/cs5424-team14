-- a115: the report-window index a104/a114 add, without a summary table.
CREATE INDEX idx_orders_report_time ON orders (created_at);
ANALYZE;
