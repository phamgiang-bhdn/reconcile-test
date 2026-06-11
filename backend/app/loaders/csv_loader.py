import csv

from app.domain.reconciliation.models import Order, Settlement

# Ánh xạ field canonical -> tên cột trong file income của từng sàn.
# Thêm sàn mới = thêm 1 entry, KHÔNG đụng domain logic.
_CANONICAL = ("order_code", "settlement_date", "gross_revenue", "refund_amount", "fee_total", "net_received")
PLATFORM_COLUMNS: dict[str, dict[str, str]] = {
    "shopee": {c: c for c in _CANONICAL},
    "lazada": {
        "order_code": "orderNumber",
        "settlement_date": "payoutDate",
        "gross_revenue": "itemPrice",
        "refund_amount": "refund",
        "fee_total": "commission",
        "net_received": "payout",
    },
}


def _rows(path: str):
    # utf-8-sig strips a BOM if present
    with open(path, newline="", encoding="utf-8-sig") as f:
        yield from csv.DictReader(f)


def load_orders(path: str) -> list[Order]:
    return [
        Order(
            order_code=r["order_code"].strip(),
            platform=r["platform"].strip(),
            status=r["status"].strip(),
            product_price=int(r["product_price"]),
            order_date=r["order_date"].strip(),
        )
        for r in _rows(path)
    ]


def load_settlements(path: str, platform: str = "shopee") -> list[Settlement]:
    col = PLATFORM_COLUMNS[platform]
    return [
        Settlement(
            order_code=r[col["order_code"]].strip(),
            settlement_date=r[col["settlement_date"]].strip(),
            gross_revenue=int(r[col["gross_revenue"]]),
            refund_amount=int(r[col["refund_amount"]]),
            fee_total=int(r[col["fee_total"]]),
            net_received=int(r[col["net_received"]]),
        )
        for r in _rows(path)
    ]
