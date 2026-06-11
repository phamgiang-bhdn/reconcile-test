from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    order_code: str
    platform: str
    status: str  # 'completed' | 'cancelled' — chỉ hiển thị, KHÔNG dùng phân loại (E#5)
    product_price: int
    order_date: str


@dataclass(frozen=True)
class Settlement:
    order_code: str
    settlement_date: str
    gross_revenue: int
    refund_amount: int  # <= 0
    fee_total: int      # <= 0
    net_received: int
