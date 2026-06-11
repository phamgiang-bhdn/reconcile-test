"use client";

import { useEffect, useMemo, useState } from "react";
import { exportUrl, getKpi, getReconciliation } from "@/lib/api";
import { formatPercent, formatVnd } from "@/lib/money";
import {
  ORDER_STATUS_UIMAP,
  RECONCILE_STATUS_ORDER,
  RECONCILE_STATUS_UIMAP,
  type OrderStatus,
} from "@/lib/status";
import { uiOf } from "@/lib/uimap";
import type { Kpi, ReconcileRow, ReconcileStatus } from "@/lib/types";
import { DataBadge } from "@/components/DataBadge";

type Filter = ReconcileStatus | "all";

function moneyCell(n: number | null) {
  const cls = n != null && n < 0 ? "num neg" : "num";
  return <td className={cls}>{formatVnd(n)}</td>;
}

export default function Page() {
  const [kpi, setKpi] = useState<Kpi | null>(null);
  const [rows, setRows] = useState<ReconcileRow[]>([]);
  const [filter, setFilter] = useState<Filter>("all");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getKpi()
      .then((r) => setKpi(r.data))
      .catch((e) => setError(String(e.message ?? e)));
  }, []);

  useEffect(() => {
    setLoading(true);
    getReconciliation(filter === "all" ? undefined : filter)
      .then((r) => setRows(r.data))
      .catch((e) => setError(String(e.message ?? e)))
      .finally(() => setLoading(false));
  }, [filter]);

  const totalRows = useMemo(
    () =>
      kpi
        ? RECONCILE_STATUS_ORDER.reduce((s, k) => s + (kpi.by_status[k] ?? 0), 0)
        : 0,
    [kpi],
  );

  const chips: { key: Filter; label: string; count: number }[] = [
    { key: "all", label: "Tất cả", count: totalRows },
    ...RECONCILE_STATUS_ORDER.map((k) => ({
      key: k as Filter,
      label: RECONCILE_STATUS_UIMAP[k].label,
      count: kpi?.by_status[k] ?? 0,
    })),
  ];

  return (
    <main className="wrap">
      <header className="hd">
        <div>
          <h1>Đối soát thanh toán sàn TMĐT</h1>
          <p className="sub">
            So khớp đơn hàng với tiền sàn thực trả — phát hiện chênh lệch, phí và đơn chưa thanh toán.
          </p>
        </div>
        <a className="btn-export" href={exportUrl(filter === "all" ? undefined : filter)}>
          ⬇ Xuất Excel
        </a>
      </header>

      {error && <p className="banner err">Lỗi tải dữ liệu: {error}</p>}

      <section className="cards">
        <KpiCard label="Tiền thực nhận" value={kpi && formatVnd(kpi.total_net)} accent="net" loading={!kpi} hint="Đã về ví shop" />
        <KpiCard label="Doanh thu gộp" value={kpi && formatVnd(kpi.total_gross)} loading={!kpi} hint="Giá trị hàng" />
        <KpiCard label="Tổng phí sàn" value={kpi && formatVnd(kpi.total_fees)} neg loading={!kpi} hint="Sàn thu" />
        <KpiCard
          label="Tỉ lệ đối soát"
          value={kpi && formatPercent(kpi.reconciliation_rate)}
          loading={!kpi}
          hint={kpi ? `${(kpi.by_status.matched ?? 0) + (kpi.by_status.refunded ?? 0)}/${kpi.total_orders} đơn đã khớp` : undefined}
        />
        <KpiCard
          label="Hoàn tiền"
          value={kpi && `${kpi.refund_count} đơn`}
          loading={!kpi}
          hint={kpi ? formatVnd(kpi.refund_total) : undefined}
          accent="refund"
        />
      </section>

      <div className="chips">
        {chips.map((c) => (
          <button
            key={c.key}
            className={`chip ${filter === c.key ? "chip--on" : ""}`}
            onClick={() => setFilter(c.key)}
          >
            {c.label}
            <span className="chip-count">{c.count}</span>
          </button>
        ))}
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Mã đơn</th>
              <th>Trạng thái đơn</th>
              <th>Ngày TT</th>
              <th className="num">Gross</th>
              <th className="num">Hoàn</th>
              <th className="num">Phí</th>
              <th className="num">Thực nhận</th>
              <th>Đối soát</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={8} className="state">Đang tải…</td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={8} className="state">Không có đơn nào ở trạng thái này.</td>
              </tr>
            ) : (
              rows.map((r) => (
                <tr key={r.order_code}>
                  <td className="code">{r.order_code}</td>
                  <td><DataBadge entry={uiOf(ORDER_STATUS_UIMAP, r.order_status as OrderStatus | null)} /></td>
                  <td className="muted">{r.settlement_date ?? "—"}</td>
                  {moneyCell(r.gross_revenue)}
                  {moneyCell(r.refund_amount)}
                  {moneyCell(r.fee_total)}
                  {moneyCell(r.net_received)}
                  <td><DataBadge entry={uiOf(RECONCILE_STATUS_UIMAP, r.reconcile_status)} /></td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}

function KpiCard({
  label,
  value,
  hint,
  neg,
  accent,
  loading,
}: {
  label: string;
  value: string | null | false;
  hint?: string;
  neg?: boolean;
  accent?: "net" | "refund";
  loading?: boolean;
}) {
  return (
    <div className={`card ${accent ? `card--${accent}` : ""}`}>
      <div className="card-label">{label}</div>
      <div className={`card-value ${neg ? "neg" : ""}`}>
        {loading ? <span className="skeleton" /> : value || "—"}
      </div>
      {hint && <div className="card-hint">{hint}</div>}
    </div>
  );
}
