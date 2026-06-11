# Validation Report — Story 1-2 Export Excel

**Ngày:** 2026-06-11 · **Phán quyết:** ✅ PASS (sau fix) · **Panel:** 3 lớp đối kháng (edge-case ∥ bug ∥ correctness), gộp chung với 1-3.

## Bảng AC
| AC | Kết quả | Bằng chứng |
|----|---------|-----------|
| 1 .xlsx + content-type + Content-Disposition | PASS | `api/reconciliation.py:33-46`; e2e: content-type `...spreadsheetml.sheet`, file 5836 bytes magic `PK` |
| 2 2 sheet KPI+ChiTiet, tiền ô numeric | PASS | `reconciliation_export.py:45-58` |
| 3 giữ dấu âm | PASS | `test_export.py` net=-40000 isinstance int |
| 4 sanitize tên sheet | PASS | regex 7 ký tự cấm + cắt 31 + default |
| 5 filter rỗng vẫn hợp lệ | PASS | `test_empty_rows_still_valid` |
| 6 test load workbook | PASS | `test_export.py` (gồm dòng None) |

## Findings & xử lý
| # | Loại | Mô tả | Xử lý |
|---|---|---|---|
| B1 | **BLOCK→fixed** | `reconciliation_rate` xuất Excel `0.8846` thay vì `88.46%` (lệch dashboard) | **Đã sửa**: set `number_format='0.00%'` cho ô rate (giữ numeric) |
| W1 | WARN→accepted | export có `?status=` thì ChiTiet lọc nhưng KPI toàn cục → dễ nhầm | Chấp nhận (KPI = toàn kỳ theo thiết kế); **đã gắn nhãn** cột "Giá trị (KPI toàn kỳ)" |
| N1 | NOTE→fixed | Dev Notes overclaim "sanitize filename" (filename tĩnh) | **Đã sửa** ghi chú story |
| N2 | NOTE→fixed | test export dùng sample bịa, thiếu dòng None | **Đã thêm** dòng unsettled (None) vào test + assert ô trống |

## Verify
- pytest 14/14 (gồm export). E2e: `GET /reconciliation/export` → xlsx hợp lệ 5836 bytes. Oracle 1-1 không ảnh hưởng.
- 0 BLOCK còn lại → **done**.
