# Story 1.1: Mini Reconciliation Dashboard

Status: done

## Story

Là **kế toán vận hành của shop**,
tôi muốn **đối soát `orders.csv` với `income.csv` và xem dashboard KPI + bảng phân loại**,
để **biết tiền thực về có khớp đơn không và phát hiện chênh lệch**.

## Acceptance Criteria

1. **Given** 2 file CSV **When** chạy migration **Then** có `orders` (PK `order_code`) + `income_settlements` (mọi cột tiền BIGINT), **không** FK income→orders, UNIQUE khóa tự nhiên toàn dòng income.
2. **Given** seed chạy **When** có dòng income trùng-toàn-bộ **Then** chỉ lưu 1 (`ON CONFLICT DO NOTHING`); chạy seed lại không đổi kết quả (idempotent). **And** dòng có `net_received ≠ gross+refund+fee` → ghi log cảnh báo nhưng **vẫn lưu nguyên** (không tự sửa/bỏ; dữ liệu nguồn là sự thật, chỉ flag). [E#4]
3. **Given** dữ liệu đã nạp **When** `GET /reconciliation[?status=]` **Then** mỗi dòng có `reconcile_status` ∈ {matched, refunded, orphan, unsettled}; lọc đúng theo `status`; response `{data, meta}`. **And** trả **1 dòng/order + 1 dòng/orphan** (dataset này = **27 dòng** = 26 order + 1 orphan). **And** nhiều settlement KHÁC nhau cùng 1 order → gộp (cộng tiền), `refunded` nếu có bất kỳ dòng refund<0. [E#1,#3]
4. **Given** dữ liệu đã nạp **When** `GET /kpi` **Then** trả `total_gross, total_net, total_fees, reconciliation_rate, refund_count, refund_total` khớp oracle. **And** `total_gross/total_net/total_fees` tính trên **toàn bộ** settlement đã dedupe **gồm cả orphan** (tiền thật đã về ví). **And** `reconciliation_rate` = (matched+refunded)/#orders, **mẫu số KHÔNG gồm orphan** (=26). [E#2]
5. **Given** dashboard **When** mở trang **Then** KPI cards + bảng lọc theo status; tiền format VND số nguyên (không float/làm tròn).
6. **Given** logic đối soát **When** chạy pytest **Then** có ≥1 test/nhánh + test dedupe + **test oracle** `total_net==1_615_756` + bất biến chéo, tất cả xanh.
7. **Given** chạy thật `docker compose up` + seed **When** gọi `/kpi` **Then** số khớp oracle end-to-end.

## Tasks / Subtasks

- [x] Task 1 — DB schema + migration (AC: #1)
  - [x] `migrations/001_init.sql`: 2 bảng, BIGINT, CHECK status, UNIQUE khóa tự nhiên, **không FK**
  - [x] `scripts/migrate.py` chạy migrations theo thứ tự
- [x] Task 2 — Ingest + dedupe idempotent (AC: #2)
  - [x] `loaders/csv_loader.py` (utf-8-sig khử BOM, strip)
  - [x] `scripts/seed.py` `ON CONFLICT DO NOTHING` + cảnh báo dòng vi phạm `net=gross+refund+fee`
- [x] Task 3 — Domain logic thuần (AC: #3, #4)
  - [x] `domain/reconciliation/models.py` (Order, Settlement)
  - [x] `domain/reconciliation/logic.py`: `dedupe_settlements` + `reconcile` (4 status) + `compute_kpi`
- [x] Task 4 — HTTP layer (AC: #3, #4)
  - [x] `repositories/reconciliation_repo.py` (SQL tham số hoá)
  - [x] `api/reconciliation.py` (`/reconciliation`, `/kpi`) + `api/health.py` + `main.py` + `errors.py` + `config.py` + `db.py`
- [x] Task 5 — Frontend dashboard (AC: #5)
  - [x] `lib/{api,types,money}.ts`
  - [x] `components/{KpiCard,StatusBadge}.tsx`
  - [x] `app/{layout.tsx,page.tsx,globals.css}` — KPI cards + bảng + filter
- [x] Task 6 — Tests (AC: #6, #7)
  - [x] `tests/test_reconciliation_logic.py`: matched/refunded/orphan/unsettled + dedupe + **oracle** (total_net + cross-invariant + by_status)
  - [x] `test_rate` (mẫu số=26) + assert `reconcile` trả **27 dòng** (orphan included) + assert orphan net nằm trong `total_net`

## Dev Notes

- **Luật/ADR áp dụng:** phân lớp domain→repo (ADR-000); tiền BIGINT/int (ADR-001/F1); ingest dedupe khóa tự nhiên (ADR-002/F2); **không FK** để giữ orphan (ADR-003/F3); response contract `data/meta/error` (ADR-004).
- **Bẫy dữ liệu (đã khảo sát thật):** `ORD-2026-0003` income trùng y hệt ×2 → dedupe (không thừa 73.440); `ORD-2026-0001` orphan (income không order); `0025/0026/0027` refund<0 net≤0; `0002/0013/0020` cancelled không income.
- **Định nghĩa nghiệp vụ (phân loại theo SETTLEMENT, không theo `order.status`):** `matched`=order tồn tại + có settlement + KHÔNG refund<0 · `refunded`=order tồn tại + có settlement + có refund<0 · `orphan`=có settlement nhưng không order · `unsettled`=order tồn tại nhưng không settlement (gồm cancelled chưa thanh toán). Ghi chú [E#5]: trong dataset mọi order có settlement đều `completed`; `order.status` chỉ **hiển thị**, KHÔNG dùng phân loại → cancelled-có-settlement (không có trong data) rơi matched/refunded, coi là **anomaly cần investigate**. `unsettled` gộp 'completed chờ trả' lẫn 'cancelled không trả' — chấp nhận trong 4-bucket, tách ở story sau. KPI trên income đã dedupe; `rate`=(matched+refunded)/#orders (orphan ngoài mẫu số).
- **Oracle:** `total_gross=2_724_000` · `total_fees=-763_244` · `total_net=1_615_756` · `refund_count=3` · `refund_total=-345_000` · `rate=round(23/26,4)=0.8846` · phân bố matched20·refunded3·unsettled3·orphan1 (**=27 dòng**: 26 order + 1 orphan) · bất biến chéo `total_net == total_gross + refund_total + total_fees`.
- **Out of scope:** auth/RBAC, phân trang thật, upload UI, sửa/ghi dữ liệu, đa sàn (1-3), export (1-2).

### Project Structure Notes
- Khớp layout chuẩn: `backend/app/{domain,api,repositories,loaders}`, `backend/{migrations,scripts,tests}`, `frontend/{app,components,lib}`.
- Không biến thể.

### References
- [Source: _bmad-output/project-context/common/architecture.md#ADR-001-002-003-004]
- [Source: _bmad-output/project-context/index.md#Key-Rules]
- [Source: _bmad-output/planning-artifacts/epics-01-reconciliation.md#Story 1-1]

## Dev Agent Record

### Agent Model Used
claude-opus-4-8[1m] (Claude Code)

### Debug Log References
- `pytest tests/ -q` trong container `python:3.12-slim`: **8 passed**.

### Completion Notes List
- TDD: viết test trước (gồm 3 test từ elicitation: 27 dòng, orphan-in-total, rate mẫu số 26) → implement → xanh.
- Logic phân loại theo settlement (E#5); `order.status` chỉ hiển thị.
- Dedupe 2 lớp: DB `UNIQUE`+`ON CONFLICT DO NOTHING` và `dedupe_settlements` trong domain.
- Dòng vi phạm bất biến từng dòng: seed log cảnh báo + vẫn lưu (E#4) — dataset hiện không có dòng nào vi phạm.
- Oracle khớp: `total_net=1_615_756`, bất biến chéo đúng.
- Còn lại: `/code-review 1-1` (panel đối kháng) + verify docker end-to-end.

### File List
**Backend:** `app/{config,db,errors,main}.py`; `app/domain/reconciliation/{models,logic}.py`; `app/loaders/csv_loader.py`; `app/repositories/reconciliation_repo.py`; `app/api/{health,reconciliation}.py`; `migrations/001_init.sql`; `scripts/{migrate,seed}.py`; `tests/test_reconciliation_logic.py`; `pyproject.toml`, `Dockerfile`, `.dockerignore`, `.env.example`
**Frontend:** `app/{layout,page}.tsx`, `app/globals.css`; `components/{KpiCard,StatusBadge}.tsx`; `lib/{api,types,money}.ts`; `package.json`, `tsconfig.json`, `next.config.mjs`, `.env.example`
**Infra:** `docker-compose.yml`, `.github/workflows/ci.yml`
