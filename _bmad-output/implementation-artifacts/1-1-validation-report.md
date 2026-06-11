# Validation Report — Story 1-1 Reconciliation Dashboard

**Ngày:** 2026-06-11 · **Phán quyết:** ✅ PASS (0 BLOCK) · **Phương pháp:** 3 lớp đối kháng song song (edge-case-hunter ∥ bug-hunter ∥ correctness-reviewer), mỗi lớp **tự verify oracle độc lập** (không qua code app).

## Verify oracle độc lập (3 nguồn khớp 100%)
| Nguồn | total_net | cách verify |
|---|---|---|
| pytest (code app) | 1.615.756 | 8/8 pass trong container python:3.12 |
| bug-hunter (Node reimplement) | 1.615.756 | reimplement reconcile bằng Node trên CSV gốc |
| correctness-reviewer (PowerShell) | 1.615.756 | tính thẳng từ CSV, không qua app |

`total_gross=2.724.000 · total_fees=-763.244 · refund_count=3 · refund_total=-345.000 · rate=0.8846 · matched20·refunded3·unsettled3·orphan1 (27 dòng) · bất biến chéo total_net==gross+refund+fees ✓`

## Bảng AC (correctness-reviewer)
| AC | Kết quả | Bằng chứng |
|----|---------|-----------|
| 1 Schema 2 bảng, BIGINT, không FK, UNIQUE khóa tự nhiên | PASS | `migrations/001_init.sql:1-19` |
| 2 Dedupe + idempotent + log vi phạm vẫn lưu (E#4) | PASS | `seed.py:24-30`, `logic.py:26-36`, test dedupe |
| 3 /reconciliation 4 status + filter + 27 dòng + gộp multi | PASS | `api/reconciliation.py:11-20`, `logic.py:39-80` |
| 4 /kpi oracle, total gồm orphan, rate mẫu số=26 (E#2) | PASS | `logic.py:87-98`, test_rate |
| 5 Dashboard KPI + filter, VND số nguyên | PASS | `page.tsx`, `money.ts` |
| 6 pytest đủ nhánh + dedupe + oracle + bất biến chéo | PASS | `test_reconciliation_logic.py` (8/8) |
| 7 docker compose up + seed → /kpi khớp end-to-end | PASS | `docker-compose.yml`, dev-workflow |

## Findings (toàn NOTE — không BLOCK, không kích hoạt trên dataset hiện tại)
| # | Loại | Mô tả | Xử lý |
|---|---|---|---|
| N1 | NOTE | `settlement_date = stl[0]` phụ thuộc thứ tự khi 1 order có nhiều settlement KHÁC nhau (logic.py:72). Dataset không có ca này (0003 chỉ trùng-y-hệt → dedupe còn 1). | Deferred → story sau (multi-settlement). Dùng `max()` khi cần. |
| N2 | NOTE | `meta.total == size` cả khi filter (reconciliation.py:20). Chưa phân trang nên vô hại. | Deferred → khi thêm phân trang. |
| N3 | NOTE | `unsettled` gộp 'completed chờ trả' lẫn 'cancelled'. | Đã khai ở story (E#5), tách story sau. |
| N4 | NOTE | cancelled-CÓ-settlement → matched/refunded không cảnh báo (anomaly). Không có trong data. | Đã khai known-limitation. |
| N5 | NOTE | `compute_kpi` dedupe 2 lần (idempotent, vô hại). | Bỏ qua. |

## Kết luận
0 BLOCK, 0 WARN. 5 NOTE đều cho data/feature tương lai, không ảnh hưởng oracle hay AC story 1-1. Theo policy dự án (review finding ngoài scope = NOTE, không tự áp) → **không sửa code**, ghi nhận để story sau. Story 1-1 → **done**.
