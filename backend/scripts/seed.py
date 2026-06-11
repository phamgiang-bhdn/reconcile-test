import os

import psycopg

from app.config import settings
from app.loaders.csv_loader import load_orders, load_settlements


PLATFORM = os.environ.get("SEED_PLATFORM", "shopee")
INCOME_FILE = os.environ.get("SEED_INCOME_FILE", "income.csv")


def main() -> None:
    orders = load_orders(os.path.join(settings.data_dir, "orders.csv"))
    settlements = load_settlements(os.path.join(settings.data_dir, INCOME_FILE), PLATFORM)

    with psycopg.connect(settings.database_url) as conn:
        with conn.cursor() as cur:
            for o in orders:
                cur.execute(
                    """INSERT INTO orders (order_code, platform, status, product_price, order_date)
                       VALUES (%s, %s, %s, %s, %s)
                       ON CONFLICT (order_code) DO NOTHING""",
                    (o.order_code, o.platform, o.status, o.product_price, o.order_date),
                )
            for s in settlements:
                # E#4: dòng vi phạm bất biến từng dòng -> log cảnh báo nhưng VẪN lưu nguyên
                if s.net_received != s.gross_revenue + s.refund_amount + s.fee_total:
                    print(f"WARN row breaks invariant net=gross+refund+fee, stored as-is: {s.order_code}")
                cur.execute(
                    """INSERT INTO income_settlements
                           (order_code, settlement_date, gross_revenue, refund_amount, fee_total, net_received, platform)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)
                       ON CONFLICT ON CONSTRAINT uq_settlement_natural DO NOTHING""",
                    (s.order_code, s.settlement_date, s.gross_revenue,
                     s.refund_amount, s.fee_total, s.net_received, PLATFORM),
                )
        conn.commit()
    print(f"seeded orders={len(orders)} settlements_raw={len(settlements)} (duplicates deduped by DB)")


if __name__ == "__main__":
    main()
