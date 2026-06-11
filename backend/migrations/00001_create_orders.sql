-- +goose Up
CREATE TABLE orders (
    order_code    TEXT PRIMARY KEY,
    platform      TEXT   NOT NULL,
    status        TEXT   NOT NULL CHECK (status IN ('completed', 'cancelled')),
    product_price BIGINT NOT NULL DEFAULT 0,
    order_date    DATE   NOT NULL
);

-- +goose Down
DROP TABLE orders;
