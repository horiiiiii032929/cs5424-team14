\if :DEBUG_MODE
\set merchant_id :DEBUG_MERCHANT_ID
\else
\set merchant_id CASE WHEN random(1, 100) <= :HOT_ORDER_PERCENT THEN random(1, :HOT_MERCHANTS) ELSE random((:HOT_MERCHANTS + 1), :NUM_MERCHANTS) END
\endif

\if :DEBUG_MODE
\set customer_id :DEBUG_CUSTOMER_ID
\set item_count :DEBUG_ITEM_COUNT
\else
\set customer_slot random(0, ((:NUM_CUSTOMERS - :merchant_id) / :NUM_MERCHANTS))
\set customer_id :merchant_id + (:customer_slot * :NUM_MERCHANTS)
\set item_count random(:MIN_ITEMS_PER_ORDER, :MAX_ITEMS_PER_ORDER)
\endif

\set product_id_1 0
\set qty_1 0
\if :item_count >= 1
\if :DEBUG_MODE
\set product_id_1 :DEBUG_PRODUCT_ID_1
\set qty_1 :DEBUG_QTY_1
\else
\set product_slot_1 random(0, ((:NUM_PRODUCTS - :merchant_id) / :NUM_MERCHANTS))
\set product_id_1 :merchant_id + (:product_slot_1 * :NUM_MERCHANTS)
\set qty_1 random(:MIN_ORDER_QTY, :MAX_ORDER_QTY)
\endif
\endif
\set product_id_2 0
\set qty_2 0
\if :item_count >= 2
\if :DEBUG_MODE
\set product_id_2 :DEBUG_PRODUCT_ID_2
\set qty_2 :DEBUG_QTY_2
\else
\set product_slot_2 random(0, ((:NUM_PRODUCTS - :merchant_id) / :NUM_MERCHANTS))
\set product_id_2 :merchant_id + (:product_slot_2 * :NUM_MERCHANTS)
\set qty_2 random(:MIN_ORDER_QTY, :MAX_ORDER_QTY)
\endif
\endif
\set product_id_3 0
\set qty_3 0
\if :item_count >= 3
\if :DEBUG_MODE
\set product_id_3 :DEBUG_PRODUCT_ID_3
\set qty_3 :DEBUG_QTY_3
\else
\set product_slot_3 random(0, ((:NUM_PRODUCTS - :merchant_id) / :NUM_MERCHANTS))
\set product_id_3 :merchant_id + (:product_slot_3 * :NUM_MERCHANTS)
\set qty_3 random(:MIN_ORDER_QTY, :MAX_ORDER_QTY)
\endif
\endif
\set product_id_4 0
\set qty_4 0
\if :item_count >= 4
\if :DEBUG_MODE
\set product_id_4 :DEBUG_PRODUCT_ID_4
\set qty_4 :DEBUG_QTY_4
\else
\set product_slot_4 random(0, ((:NUM_PRODUCTS - :merchant_id) / :NUM_MERCHANTS))
\set product_id_4 :merchant_id + (:product_slot_4 * :NUM_MERCHANTS)
\set qty_4 random(:MIN_ORDER_QTY, :MAX_ORDER_QTY)
\endif
\endif
\set product_id_5 0
\set qty_5 0
\if :item_count >= 5
\if :DEBUG_MODE
\set product_id_5 :DEBUG_PRODUCT_ID_5
\set qty_5 :DEBUG_QTY_5
\else
\set product_slot_5 random(0, ((:NUM_PRODUCTS - :merchant_id) / :NUM_MERCHANTS))
\set product_id_5 :merchant_id + (:product_slot_5 * :NUM_MERCHANTS)
\set qty_5 random(:MIN_ORDER_QTY, :MAX_ORDER_QTY)
\endif
\endif
BEGIN;
SELECT place_order((:merchant_id)::bigint, (:customer_id)::bigint,
    (ARRAY[:product_id_1,:product_id_2,:product_id_3,:product_id_4,:product_id_5]::bigint[])[1: :item_count],
    (ARRAY[:qty_1,:qty_2,:qty_3,:qty_4,:qty_5]::integer[])[1: :item_count],
    true);
COMMIT;
