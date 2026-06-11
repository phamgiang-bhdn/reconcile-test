import type { ItemResp, Kpi, ListResp, ReconcileRow, ReconcileStatus } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export const getKpi = () => getJson<ItemResp<Kpi>>("/kpi");

export const getReconciliation = (status?: ReconcileStatus) =>
  getJson<ListResp<ReconcileRow>>(
    `/reconciliation${status ? `?status=${status}` : ""}`,
  );

export const exportUrl = (status?: ReconcileStatus) =>
  `${BASE}/reconciliation/export${status ? `?status=${status}` : ""}`;
