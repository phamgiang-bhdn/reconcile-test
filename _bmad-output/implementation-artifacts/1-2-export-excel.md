# Story 1.2: Export Excel kết quả đối soát

Status: done
Epic: 01 — Reconciliation

## Story
Là **kế toán vận hành**, tôi muốn **xuất bảng đối soát + KPI ra file Excel**, để **lưu trữ và đối chiếu ngoài hệ thống**.

## Acceptance Criteria
1. **Given** dữ liệu đã nạp **When** `GET /reconciliation/export[?status=]` **Then** trả file `.xlsx` (content-type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`) + `Content-Disposition` filename hợp lệ.
2. **Given** file xuất **Then** có 2 sheet: **"KPI"** (6 chỉ số) và **"ChiTiet"** (các dòng đối soát theo filter); cột tiền là **ô số** (numeric), KHÔNG phải text → Excel cộng/SUM được.
3. **Given** dấu âm (phí/hoàn) **Then** giữ nguyên dấu trong ô số (không format mất dấu).
4. **Given** tên sheet **Then** sanitize ký tự cấm `* ? : \ / [ ]` và cắt ≤ 31 ký tự (giới hạn Excel).
5. **Given** filter rỗng (0 dòng) **Then** file vẫn hợp lệ (chỉ header).
6. **Given** builder export **When** test **Then** load lại workbook assert: 2 sheet, số dòng ChiTiet = số dòng /reconciliation, 1 ô tiền đúng kiểu số + đúng giá trị.

## Tasks / Subtasks
- [x] Task 1 — Builder export thuần (AC: #2,#3,#4,#5)
  - [x] `app/exports/reconciliation_export.py`: `build_workbook_bytes(rows, kpi) -> bytes` (openpyxl)
  - [x] `sanitize_sheet_name(name)` loại ký tự cấm + cắt 31
- [x] Task 2 — Endpoint (AC: #1)
  - [x] `GET /reconciliation/export` trả `Response`(bytes) + headers content-type + Content-Disposition
- [x] Task 3 — Frontend (AC: #1)
  - [x] Nút "Xuất Excel" trên dashboard (link tải, kèm filter hiện tại)
- [x] Task 4 — Test (AC: #6)
  - [x] `tests/test_export.py`: build → load workbook → assert sheet/số dòng/ô tiền numeric + sanitize

## Dev Notes
- Export là **tầng trình bày** → `app/exports/`, nhận `rows`+`kpi` (output của `domain.reconciliation.logic`), KHÔNG tự truy DB/đối soát lại.
- **Tiền là ô số nguyên** trong Excel (không string) — tái khẳng định F1 ở tầng export.
- Thêm dependency `openpyxl` vào `pyproject.toml`.
- **Elicitation đã chạy (edge-case, pre-mortem, identify-risks):**
  - [E1] tiền dạng text trong Excel → không SUM được → ép ô **numeric** (AC#2).
  - [E2] tên sheet chứa `/ \ : * ? [ ]` → workbook hỏng → `sanitize_sheet_name` (AC#4). (filename Content-Disposition hiện tĩnh `reconciliation.xlsx` nên chưa cần sanitize.)
  - [E3] filter rỗng → vẫn xuất file header (AC#5), không lỗi.
  - [E4] dấu âm phí/hoàn phải giữ trong ô số (AC#3).
- Out of scope: định dạng đẹp (màu/merge), nhiều ngôn ngữ cột, stream cho file lớn.

### Project Structure Notes
- Mới: `backend/app/exports/reconciliation_export.py`, `backend/tests/test_export.py`. Sửa: `api/reconciliation.py`, `pyproject.toml`, `frontend/app/page.tsx`.

### References
- [Source: _bmad-output/implementation-artifacts/1-1-reconciliation-dashboard.md] (rows/kpi shape)
- [Source: _bmad-output/planning-artifacts/epics-01-reconciliation.md#Story 1-2]

## Dev Agent Record
### Agent Model Used
claude-opus-4-8[1m]
### Debug Log References
- `pytest tests/ -q` (container, +openpyxl): **11 passed** (8 cũ + 3 export).
### Completion Notes List
- Builder thuần `build_workbook_bytes(rows, kpi)` (openpyxl) + `sanitize_sheet_name`; tiền là ô int (numeric, E1/E4).
- Endpoint `GET /reconciliation/export[?status=]` tái dùng `_fetch_rows` chung với list; trả `Response` bytes + Content-Disposition.
- FE: nút "⬇ Xuất Excel" theo filter hiện tại.
### File List
**Mới:** `app/exports/{__init__,reconciliation_export}.py`, `tests/test_export.py`
**Sửa:** `app/api/reconciliation.py` (export endpoint + tách `_fetch_rows`), `pyproject.toml` (+openpyxl), `frontend/lib/api.ts` (exportUrl), `frontend/app/page.tsx` (nút), `frontend/app/globals.css`
