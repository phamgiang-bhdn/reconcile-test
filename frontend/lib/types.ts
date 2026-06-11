export type ReconcileStatus = "matched" | "refunded" | "orphan" | "unsettled";

export interface ReconcileRow {
  order_code: string;
  order_status: string | null;
  product_price: number | null;
  order_date: string | null;
  settlement_date: string | null;
  gross_revenue: number | null;
  refund_amount: number | null;
  fee_total: number | null;
  net_received: number | null;
  reconcile_status: ReconcileStatus;
}

export interface Kpi {
  total_gross: number;
  total_net: number;
  total_fees: number;
  reconciliation_rate: number;
  refund_count: number;
  refund_total: number;
  total_orders: number;
  by_status: Record<ReconcileStatus, number>;
}

export interface ListResp<T> {
  data: T[];
  meta: { size: number; total: number };
}
export interface ItemResp<T> {
  data: T;
}
