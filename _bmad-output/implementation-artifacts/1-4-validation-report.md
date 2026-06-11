# Validation Report — Story 1-4 UI/UX polish + UIMap/DataBadge

**Ngày:** 2026-06-11 · **Phán quyết:** ✅ PASS (sau fix) · **Panel:** 2 lớp đối kháng (correctness AC ∥ edge-case/UX).

## Bảng AC (correctness-reviewer)
| AC | Kết quả | Bằng chứng |
|----|---------|-----------|
| 1 cơ chế UIMap chung null-safe | PASS | `lib/uimap.ts` |
| 2 enum khai báo tập trung (4+2, typed) | PASS | `lib/status.ts` |
| 3 DataBadge theo variant, bỏ hardcode | PASS | `DataBadge.tsx`; StatusBadge xoá, 0 import |
| 4 badge cả order_status + reconcile_status | PASS | `page.tsx` `uiOf(ORDER...)` + `uiOf(RECONCILE...)` |
| 5 header/KPI số âm đỏ/chips count/empty+loading/responsive | PASS | `page.tsx` + `globals.css` |
| 6 wording sạch ("Tiền lạ" thay orphan) | PASS | `status.ts` |
| 7 typecheck | PASS | `tsc --noEmit` exit 0 |

## Findings & xử lý
| # | Loại | Mô tả | Xử lý |
|---|---|---|---|
| B1 | BLOCK→**bác** | `key={order_code}` nghi trùng (orphan + order cùng mã) | **Verified không xảy ra**: `reconcile()` trả order-PK (unique) + orphan-code (định nghĩa = không thuộc orders) → disjoint. Không sửa. |
| W1 | WARN→**fixed** | cast `as OrderStatus` nuốt status lạ thành "—" | `uiOf` fallback hiện **raw key** thay vì "—" |
| W2 | WARN→**fixed** | KPI hint thiếu `?? 0` → NaN nếu backend thiếu key | thêm `?? 0` cả 2 số hạng |
| W3 | WARN→**fixed** | `.table-wrap overflow:hidden` cắt bảng ở 641–820px | `overflow-x:auto` mặc định |
| N1 | NOTE→**fixed** | `KpiCard.tsx` dead code | xoá file |
| N2 | NOTE→accepted | chip count flash "0" trước khi KPI về | cosmetic, để lại |
| N3 | NOTE→accepted | dấu `fee_total`/a11y caption | quy ước dấu đã chốt ở story 1-1; a11y nâng cao = story sau |

## Verify
- `tsc --noEmit` exit 0 sau fix. `net=0` không tô đỏ (đúng), `null` → "—" không đỏ (đúng).
- 0 BLOCK còn lại → **done**.
