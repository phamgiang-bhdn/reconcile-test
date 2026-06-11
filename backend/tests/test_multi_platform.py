import os

from app.domain.reconciliation import logic
from app.loaders.csv_loader import PLATFORM_COLUMNS, load_orders, load_settlements


def _data_path(name: str) -> str:
    base = os.environ.get("DATA_DIR")
    if base and os.path.exists(os.path.join(base, name)):
        return os.path.join(base, name)
    return os.path.join(os.path.dirname(__file__), "..", "..", name)


def test_lazada_column_mapping(tmp_path):
    # file income sàn lazada với tên cột KHÁC shopee
    f = tmp_path / "lazada_income.csv"
    f.write_text(
        "orderNumber,payoutDate,itemPrice,refund,commission,payout\n"
        "LZD-1,2026-06-01,200000,0,-30000,170000\n",
        encoding="utf-8",
    )
    settlements = load_settlements(str(f), platform="lazada")
    assert len(settlements) == 1
    s = settlements[0]
    assert s.order_code == "LZD-1"
    assert s.gross_revenue == 200000
    assert s.fee_total == -30000
    assert s.net_received == 170000


def test_registry_extensible_without_touching_logic():
    # thêm sàn = thêm entry; field canonical đồng nhất
    for platform, cols in PLATFORM_COLUMNS.items():
        assert set(cols.keys()) == {
            "order_code", "settlement_date", "gross_revenue",
            "refund_amount", "fee_total", "net_received",
        }, platform


def test_shopee_oracle_regression():
    # AC#4: thêm đa sàn KHÔNG làm lệch oracle shopee
    orders = load_orders(_data_path("orders.csv"))
    income = load_settlements(_data_path("income.csv"))  # default shopee
    kpi = logic.compute_kpi(orders, income)
    assert kpi["total_net"] == 1_615_756
