"""Pure reconciliation logic — no DB, no framework. Money is integer VND.

Phân loại theo SETTLEMENT, không theo order.status (E#5). order.status chỉ hiển thị.
"""

from app.domain.reconciliation.models import Order, Settlement

MATCHED = "matched"
REFUNDED = "refunded"
ORPHAN = "orphan"
UNSETTLED = "unsettled"
ALL_STATUSES = (MATCHED, REFUNDED, ORPHAN, UNSETTLED)


def _natural_key(s: Settlement) -> tuple:
    return (
        s.order_code,
        s.settlement_date,
        s.gross_revenue,
        s.refund_amount,
        s.fee_total,
        s.net_received,
    )


def dedupe_settlements(settlements: list[Settlement]) -> list[Settlement]:
    """Drop byte-identical duplicate settlement lines (F2), preserving order."""
    seen: set[tuple] = set()
    out: list[Settlement] = []
    for s in settlements:
        key = _natural_key(s)
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out


def _classify(has_order: bool, has_settlement: bool, has_refund: bool) -> str:
    if not has_order and has_settlement:
        return ORPHAN
    if has_order and not has_settlement:
        return UNSETTLED
    if has_refund:
        return REFUNDED
    return MATCHED


def reconcile(orders: list[Order], settlements: list[Settlement]) -> list[dict]:
    settlements = dedupe_settlements(settlements)
    orders_by_code = {o.order_code: o for o in orders}
    settles_by_code: dict[str, list[Settlement]] = {}
    for s in settlements:
        settles_by_code.setdefault(s.order_code, []).append(s)

    orphan_codes = [c for c in settles_by_code if c not in orders_by_code]
    rows: list[dict] = []
    for code in [*orders_by_code.keys(), *orphan_codes]:
        order = orders_by_code.get(code)
        stl = settles_by_code.get(code, [])  # nhiều settlement/order → gộp (E#1)
        status = _classify(
            has_order=order is not None,
            has_settlement=bool(stl),
            has_refund=any(s.refund_amount < 0 for s in stl),
        )
        rows.append(
            {
                "order_code": code,
                "order_status": order.status if order else None,
                "product_price": order.product_price if order else None,
                "order_date": order.order_date if order else None,
                "settlement_date": stl[0].settlement_date if stl else None,
                "gross_revenue": sum(s.gross_revenue for s in stl) if stl else None,
                "refund_amount": sum(s.refund_amount for s in stl) if stl else None,
                "fee_total": sum(s.fee_total for s in stl) if stl else None,
                "net_received": sum(s.net_received for s in stl) if stl else None,
                "reconcile_status": status,
            }
        )
    return rows


def compute_kpi(orders: list[Order], settlements: list[Settlement]) -> dict:
    settlements = dedupe_settlements(settlements)

    # tổng trên TOÀN BỘ settlement đã dedupe, gồm cả orphan (E#2)
    total_gross = sum(s.gross_revenue for s in settlements)
    total_net = sum(s.net_received for s in settlements)
    total_fees = sum(s.fee_total for s in settlements)

    refunds = [s for s in settlements if s.refund_amount < 0]
    refund_count = len(refunds)
    refund_total = sum(s.refund_amount for s in refunds)

    rows = reconcile(orders, settlements)
    reconciled = sum(1 for r in rows if r["reconcile_status"] in (MATCHED, REFUNDED))
    total_orders = len(orders)  # mẫu số KHÔNG gồm orphan (E#2)
    reconciliation_rate = round(reconciled / total_orders, 4) if total_orders else 0.0

    by_status = {s: 0 for s in ALL_STATUSES}
    for r in rows:
        by_status[r["reconcile_status"]] += 1

    return {
        "total_gross": total_gross,
        "total_net": total_net,
        "total_fees": total_fees,
        "reconciliation_rate": reconciliation_rate,
        "refund_count": refund_count,
        "refund_total": refund_total,
        "total_orders": total_orders,
        "by_status": by_status,
    }
