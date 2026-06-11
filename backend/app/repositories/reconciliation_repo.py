from app.domain.reconciliation.models import Order, Settlement


class ReconciliationRepo:
    def __init__(self, conn):
        self._conn = conn

    def fetch_orders(self) -> list[Order]:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT order_code, platform, status, product_price, order_date FROM orders"
            )
            return [
                Order(code, platform, status, int(price), str(date))
                for (code, platform, status, price, date) in cur.fetchall()
            ]

    def fetch_settlements(self) -> list[Settlement]:
        with self._conn.cursor() as cur:
            cur.execute(
                """SELECT order_code, settlement_date, gross_revenue,
                          refund_amount, fee_total, net_received
                   FROM income_settlements"""
            )
            return [
                Settlement(code, str(sdate), int(gross), int(refund), int(fee), int(net))
                for (code, sdate, gross, refund, fee, net) in cur.fetchall()
            ]
