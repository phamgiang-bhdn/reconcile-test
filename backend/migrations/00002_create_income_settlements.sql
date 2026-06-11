-- +goose Up
-- KHÔNG FK order_code → orders (phải chứa record orphan). Khóa tự nhiên gồm platform (đa sàn).
CREATE TABLE income_settlements (
    id              BIGSERIAL PRIMARY KEY,
    order_code      TEXT   NOT NULL,
    settlement_date DATE   NOT NULL,
    gross_revenue   BIGINT NOT NULL,
    refund_amount   BIGINT NOT NULL DEFAULT 0,
    fee_total       BIGINT NOT NULL DEFAULT 0,
    net_received    BIGINT NOT NULL,
    platform        TEXT   NOT NULL DEFAULT 'shopee',
    CONSTRAINT uq_settlement_natural UNIQUE
        (platform, order_code, settlement_date, gross_revenue, refund_amount, fee_total, net_received)
);
CREATE INDEX idx_income_order_code ON income_settlements (order_code);

-- +goose Down
DROP TABLE income_settlements;
