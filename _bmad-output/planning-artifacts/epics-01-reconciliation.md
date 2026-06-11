---
stepsCompleted: ['step-02-design-epics']
inputDocuments:
  - Đề bài "Mini Reconciliation Dashboard" (DE_BAI.md)
---

# Epic 01 — Reconciliation (Đối soát thanh toán sàn)

## Overview
Mảng **đối soát**: so khớp đơn hàng của shop với file thanh toán sàn TMĐT, phơi bày KPI + chênh lệch để kế toán vận hành kiểm soát tiền thực về. Đây là epic mở (OPEN) — đối soát là một mảng nghiệp vụ lớn của nền tảng người bán; story 1-1 dựng dashboard nền, các story sau bổ sung export/đa sàn/cảnh báo. Tiền theo luật tài chính toàn dự án (ADR-001/002/003).

## Progress Snapshot (cập nhật 2026-06-11)
| Story | Trạng thái | Notes |
|---|---|---|
| 1-1 — Mini Reconciliation Dashboard | ✅ Done | Full-stack done. Elicitation 5 method + code-review 3 lớp đối kháng (7/7 AC PASS, 0 BLOCK). Oracle `total_net=1.615.756` verify 3 nguồn. Test 8/8. |
| 1-2 — Export Excel kết quả đối soát | ✅ Done | `GET /reconciliation/export` 2 sheet (KPI %+ChiTiet), tiền ô numeric, sanitize sheet. Review bắt rate-float → fix. |
| 1-3 — Đa sàn (Lazada/TikTok) | ✅ Done | Registry `PLATFORM_COLUMNS` + cột/seed platform. Review bắt UNIQUE thiếu platform + seed hardcode → fix. Oracle shopee giữ. |
| 1-4 — UI/UX polish + cơ chế UIMap/DataBadge | ✅ Done | UIMap (label+variant) + `<DataBadge>` tái dùng cho cả `reconcile_status` + `order_status`; redesign trang + từ ngữ. Review (2 lớp) → 3 WARN + dead-code fix, 1 BLOCK bác. tsc pass. |

---

## Story 1-1 — Mini Reconciliation Dashboard
**Status:** ⏳ Backlog — chờ `/create-story 1-1`. Full-stack: `backend` (FastAPI+Postgres) + `frontend` (Next.js).

**Context:** Mỗi kỳ sàn gửi `income.csv` (tiền thực nhận từng đơn). Cần đối soát với `orders.csv`. Dữ liệu thật có bẫy: dòng income **trùng y hệt** (`ORD-2026-0003` ×2 → đếm đôi nếu không dedupe), **orphan** (`ORD-2026-0001` có income không có order), **refund** (`0025/0026/0027` refund<0, net≤0), **cancelled** không income (`0002/0013/0020`).

**Định nghĩa nghiệp vụ:** 4 `reconcile_status` = matched / refunded / orphan / unsettled (chi tiết ở story file). Tiền là BIGINT VND. `net = gross + refund + fee`; refund/fee ≤ 0.

**Acceptance:**

**Given** 2 file CSV **When** chạy migration + seed **Then** có bảng `orders` (PK order_code) + `income_settlements` (mọi cột tiền BIGINT, **không** FK, UNIQUE khóa tự nhiên); dòng income trùng-toàn-bộ bị dedupe; seed chạy lại không đổi kết quả.

**Given** dữ liệu đã nạp **When** `GET /reconciliation` **Then** mỗi dòng có `reconcile_status` đúng 4 loại; `?status=` lọc được; response `{data,meta}`.

**Given** dữ liệu đã nạp **When** `GET /kpi` **Then** trả `total_gross/total_net/total_fees/reconciliation_rate/refund_count/refund_total` đúng oracle.

**Given** dashboard **When** mở trang **Then** KPI cards + bảng lọc theo status; tiền format VND số nguyên.

**Given** logic đối soát **When** chạy test **Then** ≥1 test/nhánh + test dedupe + **test oracle** `total_net==1_615_756` + bất biến chéo, tất cả xanh.

**Oracle:** `total_net=1.615.756` · `total_gross=2.724.000` · `total_fees=-763.244` · `refund_count=3` · `refund_total=-345.000` · `rate=23/26` · phân bố matched20·refunded3·unsettled3·orphan1 · bất biến `total_net == total_gross + refund_total + total_fees`.

**Affected layers / files:**
| Tầng | Change |
|---|---|
| DB | `migrations/001_init.sql` (2 bảng, UNIQUE khóa tự nhiên, không FK); `scripts/seed.py` (ON CONFLICT DO NOTHING) |
| Backend | `app/domain/reconciliation/{models,logic}.py`; `app/repositories/reconciliation_repo.py`; `app/api/{reconciliation,health}.py`; `app/main.py` |
| Frontend | `app/page.tsx`; `components/{KpiCard,StatusBadge}.tsx`; `lib/{api,types,money}.ts` |
| Test | `tests/test_reconciliation_logic.py` (6 case gồm oracle) |

---

## Story 1-2 — Export Excel kết quả đối soát
**Status:** ⏳ Backlog
**Context:** Kế toán cần tải bảng đối soát + KPI ra Excel để lưu/đối chiếu ngoài.
**Acceptance (nháp):** **Given** trang dashboard **When** bấm "Xuất Excel" **Then** tải .xlsx gồm sheet KPI + sheet chi tiết; tên sheet sanitize ký tự cấm (`* ? : \ / [ ]`, ≤31 ký tự).

---

## Story 1-3 — Đa sàn (Lazada/TikTok)
**Status:** ⏳ Backlog
**Context:** Hiện chỉ shopee. Tổng quát hoá để nạp income nhiều sàn với mapping cột khác nhau.
**Acceptance (nháp):** **Given** file income của sàn X **When** chọn sàn lúc import **Then** map đúng cột theo cấu hình sàn; `platform` lưu theo sàn; đối soát/KPI tách được theo sàn.
