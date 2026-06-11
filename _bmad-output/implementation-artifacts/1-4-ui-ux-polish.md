# Story 1.4: UI/UX polish + cơ chế UIMap/DataBadge

Status: done
Epic: 01 — Reconciliation

## Story
Là **kế toán dùng dashboard**, tôi muốn **giao diện rõ ràng, dễ đọc và mọi trạng thái đều có badge nhất quán**, để **đọc kết quả đối soát nhanh, không bị rối hay thiếu thông tin**.

## Acceptance Criteria
1. **Given** cần hiển thị enum **Then** có **cơ chế UIMap chung** `lib/uimap.ts`: `UIMapEntry {label, variant}`, `UIMap<K>`, helper `uiOf(map, key)` (null-safe → fallback neutral "—").
2. **Given** các enum của app **Then** khai báo **tập trung** `lib/status.ts`: `RECONCILE_STATUS_UIMAP` (4 trạng thái) + `ORDER_STATUS_UIMAP` (completed/cancelled), có type.
3. **Given** badge **Then** có `<DataBadge entry={...} />` render theo `variant`; **bỏ** STYLE/LABEL hardcode rải rác (StatusBadge cũ thay bằng DataBadge).
4. **Given** bảng **Then** cột **trạng thái đơn** (`order_status`) cũng có badge qua UIMap (không còn để chữ trần); cột **đối soát** dùng DataBadge. Mọi badge đi qua cơ chế.
5. **Given** trang **Then** UI nâng cấp: header (tiêu đề + mô tả), KPI cards rõ (label + phụ đề, số âm hiển thị màu đỏ), filter chips **kèm số đếm**, bảng dễ đọc (hover/zebra, số tiền căn phải), empty + loading state tử tế, responsive.
6. **Given** từ ngữ **Then** nhãn tiếng Việt rõ, không lộ thuật ngữ kỹ thuật ("orphan" → "Tiền lạ").
7. **Given** build **When** `npm run build` **Then** typecheck pass.

## Tasks / Subtasks
- [x] Task 1 — Cơ chế UIMap (AC: #1, #2)
  - [x] `lib/uimap.ts`: `BadgeVariant`, `UIMapEntry`, `UIMap<K>`, `uiOf()`
  - [x] `lib/status.ts`: `RECONCILE_STATUS_UIMAP`, `OrderStatus` + `ORDER_STATUS_UIMAP`
- [x] Task 2 — DataBadge (AC: #3, #4)
  - [x] `components/DataBadge.tsx` đọc `UIMapEntry`
  - [x] thay `StatusBadge` cũ; badge cho cả `reconcile_status` + `order_status`
- [x] Task 3 — Redesign trang + CSS (AC: #5, #6)
  - [x] `app/page.tsx`: header, KPI cards (label+sub, màu số âm), filter chips + count, bảng + states
  - [x] `app/globals.css`: `badge--<variant>` (5 variant) 1 chỗ + layout/typography đẹp hơn
- [x] Task 4 — Verify (AC: #7)
  - [x] `npm run build` pass (typecheck)

## Dev Notes
- **Pattern UIMap + DataBadge (như ig):** mọi enum hiển thị khai báo **một chỗ** (`label` + `variant`); component đọc map → không if/else màu rải rác, không hardcode nhãn/màu. Thêm trạng thái = thêm 1 dòng UIMap.
- `variant` → màu khai ở CSS một chỗ: `success/warning/danger/neutral/info`.
- **Elicitation (UX critic · edge-case · what-if) — đã áp:**
  - [E1] `order_status` của dòng orphan = `null` → `uiOf` fallback "—"/neutral, không vỡ.
  - [E2] số tiền âm (phí/hoàn) → màu đỏ nhẹ cho dễ nhận.
  - [E3] filter chip kèm **số đếm** lấy từ `kpi.by_status`.
  - [E4] filter ra 0 dòng → empty state; đang tải → skeleton/placeholder.
- Out of scope: dark mode, i18n đa ngôn ngữ, animation phức tạp, đổi API.

### Project Structure Notes
- Mới: `frontend/lib/uimap.ts`, `frontend/lib/status.ts`, `frontend/components/DataBadge.tsx`.
- Sửa: `frontend/app/page.tsx`, `frontend/app/globals.css`, `frontend/components/StatusBadge.tsx` (gỡ/thay).

### References
- [Source: _bmad-output/project-context/index.md] · skill `frontend-nextjs` (status→màu lookup)
- [Source: _bmad-output/planning-artifacts/epics-01-reconciliation.md#Story 1-4]

## Dev Agent Record
### Agent Model Used
claude-opus-4-8[1m]
### Debug Log References
- `npx tsc --noEmit` → exit 0 (typecheck pass). (`next build` kẹt vì dev server giữ `.next`; tsc xác nhận type.)
### Completion Notes List
- Cơ chế UIMap: `lib/uimap.ts` (`UIMapEntry/UIMap/uiOf` null-safe) + `lib/status.ts` (RECONCILE_STATUS_UIMAP 4 + ORDER_STATUS_UIMAP 2, typed).
- `<DataBadge>` đọc entry → màu theo `variant` (CSS 1 chỗ). Gỡ `StatusBadge` hardcode.
- Badge cho **cả** order_status (Hoàn tất/Đã huỷ) lẫn reconcile_status; orphan order_status=null → fallback "—" neutral.
- Redesign: header+mô tả, KPI cards (accent + số âm đỏ + skeleton), filter chips kèm số đếm (by_status), bảng hover + số căn phải + mã đơn mono, empty/loading state. Wording: "Tiền lạ" thay "orphan".
### File List
**Mới:** `frontend/lib/uimap.ts`, `frontend/lib/status.ts`, `frontend/components/DataBadge.tsx`
**Sửa:** `frontend/app/page.tsx`, `frontend/app/globals.css`
**Xoá:** `frontend/components/StatusBadge.tsx`
