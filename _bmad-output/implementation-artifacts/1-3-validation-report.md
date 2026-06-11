# Validation Report — Story 1-3 Multi-platform

**Ngày:** 2026-06-11 · **Phán quyết:** ✅ PASS (sau fix) · **Panel:** 3 lớp đối kháng (gộp với 1-2).

## Bảng AC
| AC | Kết quả | Bằng chứng |
|----|---------|-----------|
| 1 registry PLATFORM_COLUMNS ánh xạ cột | PASS | `csv_loader.py:8-18,40-52` |
| 2 thêm sàn = thêm entry, không sửa domain logic | PASS | `test_multi_platform.py` enforce key set; logic không đổi |
| 3 cột platform migration idempotent + seed ghi | PASS | `002_add_platform.sql`; `seed.py` (env platform) |
| 4 oracle shopee 1.615.756 không đổi | PASS | e2e `/kpi`=1.615.756 sau đổi constraint; `test_shopee_oracle_regression` |
| 5 test mapping lazada + regression | PASS | `test_lazada_column_mapping` + regression |

## Findings & xử lý
| # | Loại | Mô tả | Xử lý |
|---|---|---|---|
| B1 | **BLOCK→fixed** | `uq_settlement_natural` thiếu `platform` → 2 sàn trùng (order/date/tiền) sẽ dedupe **nuốt mất tiền** | **Đã sửa**: migration 002 drop+recreate UNIQUE **gồm platform** |
| B2 | **BLOCK→fixed** | `seed.py` hardcode shopee → không ingest được sàn khác (AC#3 chỉ đúng shopee) | **Đã sửa**: seed nhận `SEED_PLATFORM` + `SEED_INCOME_FILE` qua env |
| W1 | WARN→accepted | platform/cột lạ → `KeyError` thô | Chấp nhận (fail-fast đúng chủ ý); bọc message = cải tiến tương lai |

## Verify
- migrate chạy lại OK (drop+recreate constraint idempotent); reseed giữ oracle.
- e2e `/kpi` → **total_net=1.615.756** sau khi constraint đổi → regression an toàn.
- 0 BLOCK còn lại → **done**.

> Lưu ý phạm vi: per-platform KPI/filter vẫn out-of-scope (story sau). Ingest đa sàn end-to-end giờ đã khả thi (env + natural key gồm platform).
