import os

from app.domain.reconciliation import logic
from app.domain.reconciliation.models import Order, Settlement
from app.loaders.csv_loader import load_orders, load_settlements


def _data_path(name: str) -> str:
    base = os.environ.get("DATA_DIR")
    if base and os.path.exists(os.path.join(base, name)):
        return os.path.join(base, name)
    return os.path.join(os.path.dirname(__file__), "..", "..", name)


def _order(code, status="completed"):
    return Order(code, "shopee", status, 91000, "2026-05-29")


def _settle(code, refund=0, net=73440):
    return Settlement(code, "2026-06-01", 91000, refund, -17560, net)


# --- per-branch (AC#3) ---
def test_matched():
    assert logic.reconcile([_order("A")], [_settle("A")])[0]["reconcile_status"] == logic.MATCHED


def test_refunded():
    rows = logic.reconcile([_order("A")], [_settle("A", refund=-91000, net=-17560)])
    assert rows[0]["reconcile_status"] == logic.REFUNDED


def test_orphan():
    assert logic.reconcile([], [_settle("Z")])[0]["reconcile_status"] == logic.ORPHAN


def test_unsettled_includes_cancelled():
    rows = logic.reconcile([_order("A", status="cancelled")], [])
    assert rows[0]["reconcile_status"] == logic.UNSETTLED


# --- dedupe (AC#2) ---
def test_dedupe_counts_once():
    s = _settle("A")
    kpi = logic.compute_kpi([_order("A")], [s, s])  # identical duplicate line
    assert kpi["total_net"] == 73440  # counted once, not 146880


# --- elicitation E#1/E#2: row count + orphan in total (AC#3/#4) ---
def test_real_data_row_count_and_orphan_in_total():
    orders = load_orders(_data_path("orders.csv"))
    income = load_settlements(_data_path("income.csv"))
    rows = logic.reconcile(orders, income)
    assert len(rows) == 27  # 26 orders + 1 orphan
    orphan = [r for r in rows if r["reconcile_status"] == logic.ORPHAN]
    assert len(orphan) == 1
    kpi = logic.compute_kpi(orders, income)
    # orphan net is included in total_net
    assert orphan[0]["net_received"] == 69811
    assert kpi["total_net"] == 1_615_756


# --- oracle (AC#6/#7) ---
def test_oracle():
    orders = load_orders(_data_path("orders.csv"))
    income = load_settlements(_data_path("income.csv"))
    kpi = logic.compute_kpi(orders, income)

    assert kpi["total_gross"] == 2_724_000
    assert kpi["total_fees"] == -763_244
    assert kpi["total_net"] == 1_615_756
    assert kpi["refund_count"] == 3
    assert kpi["refund_total"] == -345_000
    # cross invariant
    assert kpi["total_net"] == kpi["total_gross"] + kpi["refund_total"] + kpi["total_fees"]
    assert kpi["by_status"] == {"matched": 20, "refunded": 3, "unsettled": 3, "orphan": 1}


# --- elicitation E#2: rate denominator excludes orphan (=26) ---
def test_rate_denominator_excludes_orphan():
    orders = load_orders(_data_path("orders.csv"))
    income = load_settlements(_data_path("income.csv"))
    kpi = logic.compute_kpi(orders, income)
    assert kpi["total_orders"] == 26  # orphan not counted as an order
    assert kpi["reconciliation_rate"] == round(23 / 26, 4)
