# Story 1.3: Đa sàn (Multi-platform ingest)

Status: done
Epic: 01 — Reconciliation

## Story
Là **kế toán đối soát nhiều sàn**, tôi muốn **nạp file thanh toán của các sàn khác (Lazada/TikTok) dù tên cột khác nhau**, để **đối soát tập trung mà không phải sửa logic mỗi lần thêm sàn**.

## Acceptance Criteria
1. **Given** mỗi sàn có tên cột income khác nhau **When** ingest **Then** loader dùng registry `PLATFORM_COLUMNS[platform]` ánh xạ cột nguồn → field canonical (Settlement), không hardcode tên cột shopee.
2. **Given** thêm sàn mới **Then** chỉ cần thêm 1 entry vào `PLATFORM_COLUMNS`, KHÔNG sửa `domain.logic` (đối soát/KPI).
3. **Given** bảng `income_settlements` **Then** có cột `platform` (migration 002 idempotent, default `shopee`); seed ghi đúng platform.
4. **Given** dữ liệu shopee cũ **Then** oracle **KHÔNG đổi**: `total_net=1_615_756` vẫn pass (regression).
5. **Given** test **Then** mapping một sàn có tên cột khác (vd lazada) load ra Settlement canonical đúng; oracle shopee giữ nguyên.

## Tasks / Subtasks
- [x] Task 1 — Registry cột theo platform (AC: #1,#2)
  - [x] `PLATFORM_COLUMNS` trong `csv_loader.py`; `load_settlements(path, platform="shopee")` ánh xạ cột
- [x] Task 2 — Schema platform (AC: #3)
  - [x] `migrations/002_add_platform.sql` ALTER ADD COLUMN IF NOT EXISTS `platform`
  - [x] `seed.py` ghi `platform`
- [x] Task 3 — Test (AC: #4,#5)
  - [x] `tests/test_multi_platform.py`: mapping lazada load đúng; shopee oracle regression

## Dev Notes
- **Mở rộng không sửa lõi**: ánh xạ cột là việc của **ingest** (loader), domain `logic` vẫn nhận `Settlement` canonical → đối soát/KPI không đổi (đúng "thêm sàn = thêm cấu hình").
- `load_settlements` thêm tham số `platform` mặc định `shopee` → backward-compatible, oracle test cũ không đổi.
- **Elicitation (identify-risks, what-if):** thêm sàn không được làm lệch shopee oracle (AC#4 regression test); cột thiếu ở file sàn → `KeyError` rõ ràng (fail-fast, không nuốt). Per-platform KPI/filter = out of scope (story sau).

### Project Structure Notes
- Sửa: `csv_loader.py`, `scripts/seed.py`. Mới: `migrations/002_add_platform.sql`, `tests/test_multi_platform.py`.

### References
- [Source: _bmad-output/implementation-artifacts/1-1-reconciliation-dashboard.md] (Settlement canonical)
- [Source: _bmad-output/planning-artifacts/epics-01-reconciliation.md#Story 1-3]

## Dev Agent Record
### Agent Model Used
claude-opus-4-8[1m]
### Debug Log References
- `pytest tests/ -q`: xem panel verify.
### Completion Notes List
- Registry `PLATFORM_COLUMNS` (shopee identity + lazada ví dụ tên cột khác); `load_settlements(path, platform)` ánh xạ.
- Migration 002 thêm `platform` (idempotent, default shopee); seed ghi platform.
- Domain `logic` KHÔNG đổi → oracle shopee giữ nguyên.
### File List
**Mới:** `migrations/002_add_platform.sql`, `tests/test_multi_platform.py`
**Sửa:** `app/loaders/csv_loader.py`, `scripts/seed.py`
