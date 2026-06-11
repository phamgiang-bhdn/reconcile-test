---
name: frontend-nextjs
description: Chuẩn code frontend cho toàn dự án — Next.js 15 (App Router) + TypeScript. Cấu trúc app/, API client typed, env config, format tiền tệ VND, KPI cards, bảng dữ liệu + lọc theo query param, status→màu lookup, loading/empty/error state, anti-pattern. Domain-agnostic — ví dụ dùng placeholder <Feature>. Dùng khi thêm/sửa bất kỳ trang hay component nào.
---

# Frontend — Next.js 15 (App Router) + TypeScript

## Load Project Context First
Theo `_bmad-output/project-context/index.md`: load `skills/engineering-standards` (response contract) + `common/code-quality.md` (mục Frontend). Trạng thái/nhãn cụ thể ở story (`_bmad-output/implementation-artifacts/`).

Kế thừa `engineering-standards` (response contract `data`/`meta`/`error`, luật tiền). UI chỉ trình bày; không tự tính lại tiền. Trạng thái/nhãn cụ thể của một feature lấy từ story; dưới đây là khuôn mẫu.

## 1. Cấu trúc

```
frontend/
  app/
    layout.tsx
    page.tsx                     # vỏ trang
    globals.css
  components/
    KpiCard.tsx
    <Feature>Table.tsx
    StatusBadge.tsx
    StatusFilter.tsx
  lib/
    api.ts                       # client gọi backend, TYPED
    money.ts                     # format VND
    types.ts                     # type khớp response contract
  next.config.ts
  package.json
```

| Path | Vai trò |
|------|---------|
| `lib/api.ts` | Mọi fetch tới backend qua đây; đọc `NEXT_PUBLIC_API_URL` |
| `lib/types.ts` | Type khớp response contract; KHÔNG `any` |
| `components/*` | Trình bày thuần, props đã typed |

## 2. Config & API client (typed)

```ts
// lib/types.ts  — thay <Feature>Status/Row bằng type thật của feature (định nghĩa khớp story)
export type RowStatus = "state_a" | "state_b";
export interface Row { code: string; net_amount: number | null; status: RowStatus; }
export interface Summary {
  total_gross: number; total_net: number; /* ...các KPI theo story... */
}
export interface ListResp<T> { data: T[]; meta: { size: number; total: number } }
export interface ItemResp<T> { data: T }
```

```ts
// lib/api.ts
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.error?.message ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export const getSummary = () => getJson<ItemResp<Summary>>("/<feature>/summary");
export const getRows = (status?: RowStatus) =>
  getJson<ListResp<Row>>(`/<feature>${status ? `?status=${status}` : ""}`);
```

- Không hardcode URL trong component — luôn qua `lib/api.ts`.
- Lọc gửi lại backend qua query param, không lọc ngầm client (dữ liệu có thể lớn).

## 3. Tiền tệ (VND, số nguyên)

```ts
// lib/money.ts
const vnd = new Intl.NumberFormat("vi-VN");
export const formatVnd = (n: number | null) => (n == null ? "—" : `${vnd.format(n)} ₫`);
```
- Tiền là **số nguyên** từ backend — không chia, không `toFixed` làm tròn.
- Số âm hiển thị nguyên dấu.

## 4. Enum hiển thị: UIMap + DataBadge (BẮT BUỘC — không hardcode bừa)

Mọi enum hiển thị (status, loại, trạng thái…) phải khai báo **một chỗ** qua **UIMap** (`label` + `variant`); component dùng chung **`<DataBadge>`** đọc map. Cấm `if/else`/STYLE/LABEL màu rải rác trong từng component.

**Cơ chế chung** (`lib/uimap.ts`):
```ts
export type BadgeVariant = "success" | "warning" | "danger" | "neutral" | "info";
export interface UIMapEntry { label: string; variant: BadgeVariant; hint?: string }
export type UIMap<K extends string> = Record<K, UIMapEntry>;
// null/lạ → fallback: key có nhưng chưa khai → hiện raw key (không nuốt thành "—")
export function uiOf<K extends string>(map: UIMap<K>, key: K | null | undefined): UIMapEntry {
  return (key && map[key]) ? map[key] : { label: key ?? "—", variant: "neutral" };
}
```

**Khai báo enum tập trung** (`lib/status.ts`) — thêm trạng thái = thêm 1 dòng:
```ts
export const RECONCILE_STATUS_UIMAP: UIMap<ReconcileStatus> = {
  matched:   { label: "Khớp",           variant: "success" },
  refunded:  { label: "Hoàn tiền",       variant: "warning" },
  orphan:    { label: "Tiền lạ",         variant: "danger"  },
  unsettled: { label: "Chưa thanh toán", variant: "neutral" },
};
```

**Component dùng chung** (`components/DataBadge.tsx`) + cách dùng:
```tsx
export function DataBadge({ entry }: { entry: UIMapEntry }) {
  return <span className={`badge badge--${entry.variant}`} title={entry.hint}>{entry.label}</span>;
}
// dùng: <DataBadge entry={uiOf(RECONCILE_STATUS_UIMAP, row.reconcile_status)} />
```

`variant` → màu khai **một chỗ** ở CSS (`.badge--success/warning/danger/neutral/info`). Nhãn user-facing tiếng Việt, không lộ thuật ngữ kỹ thuật (vd `orphan` → "Tiền lạ").

## 5. Khuôn trang dashboard
- Hàng **KPI cards** từ `getSummary()`; tỉ lệ % nhân 100, 2 số lẻ + `%`.
- **Bảng** từ `getRows(status)` + thanh **lọc** (tabs): "Tất cả" = không truyền status.
- **State**: loading skeleton, empty ("không có dòng nào"), error (hiện message từ contract).
- Quy mô nhỏ → client fetch trong `useEffect` là đủ; chỉ thêm state lib khi thật cần.

## 6. Anti-pattern (CẤM)
- ❌ `any` cho response; ❌ hardcode URL backend trong component.
- ❌ Tính lại/round tiền ở client; ❌ chia 100.
- ❌ if/else hoặc STYLE/LABEL màu trạng thái rải rác trong component — phải qua **UIMap + `<DataBadge>`** (mục 4).
- ❌ Lọc toàn bộ ở client khi backend đã có filter param.

## 7. Commands
```bash
cd frontend && npm install && npm run dev    # http://localhost:3000
npm run build                                 # kiểm typecheck + build
```
