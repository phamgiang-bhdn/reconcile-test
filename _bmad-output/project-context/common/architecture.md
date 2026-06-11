# Architecture — Decisions (ADR) · Toàn dự án

Quyết định kiến trúc nền, áp cho mọi feature. Mỗi ADR: bối cảnh → quyết định → hệ quả.

---

## ADR-000 — Phân lớp HTTP → Domain → Repository
**Bối cảnh:** logic tiền tệ phải test được nhanh, không phụ thuộc DB/HTTP.
**Quyết định:** 3 tầng, phụ thuộc một chiều. Domain là module thuần (không import framework/DB). Handler mỏng. Repository chỉ query.
**Hệ quả:** unit-test domain bằng dữ liệu giả; đổi web/DB không đụng nghiệp vụ. Cấm logic trong handler/SQL.

## ADR-001 — Tiền là số nguyên minor unit
**Bối cảnh:** VND không có phần lẻ; float làm tròn sai tiền.
**Quyết định:** mọi tiền là `int` (Python) / `BIGINT` (Postgres). Phép chia (tỉ lệ) chỉ ở tầng trình bày, không lưu float vào trường tiền.
**Hệ quả:** không sai số cộng dồn. Lint/test chặn `float` quanh tiền. [F1]

## ADR-002 — Ingest idempotent + dedupe theo khóa tự nhiên
**Bối cảnh:** dữ liệu từ file/đối tác có thể được nạp lại hoặc chứa dòng trùng y hệt → đếm đôi tiền.
**Quyết định:** mỗi bảng ingest có **khóa tự nhiên** (đủ cột phân biệt) + `UNIQUE` constraint; import bằng `INSERT ... ON CONFLICT DO NOTHING`. Dedupe lặp lại trong domain để test không cần DB.
**Hệ quả:** nạp nhiều lần an toàn; dòng trùng-toàn-bộ bị bỏ; hai bản ghi hợp lệ khác nhau vẫn giữ. [F2]

## ADR-003 — Không FK cứng ở bảng ingest (orphan-safe)
**Bối cảnh:** bản ghi nhập có thể trỏ tới thực thể **chưa tồn tại** trong sổ; FK sẽ chặn insert và làm mất dữ liệu cần đối chiếu.
**Quyết định:** KHÔNG đặt FK từ bảng ingest → bảng gốc. Lưu record orphan, phân loại ở domain.
**Hệ quả:** không mất dữ liệu; toàn vẹn tham chiếu kiểm ở tầng nghiệp vụ, không ở DB. [F3]

## ADR-004 — Response contract đồng nhất
**Bối cảnh:** frontend cần hình dạng response ổn định.
**Quyết định:** list → `{data, meta:{size,total}}`; single → `{data}`; lỗi → `{error:{code,message}}` với `code` là hằng `UPPER_SNAKE`.
**Hệ quả:** client typed một kiểu; lỗi nghiệp vụ map từ `AppError(code,status)`. [ADR-004]

## ADR-005 — Spec-first, oracle-driven
**Bối cảnh:** đúng số tiền quan trọng hơn "chạy được".
**Quyết định:** không code khi chưa có story; mỗi task tài chính có ≥1 **oracle** (con số tổng kỳ vọng) ghi trong story và được test chốt; mọi thay đổi qua panel `/review` đối kháng.
**Hệ quả:** regression số tiền bị test bắt; review tìm edge-case/bug trước khi merge. [F5]

---

### Bảng tham chiếu nhanh
| ADR | Một câu | Luật |
|---|---|---|
| 000 | 3 tầng, domain thuần | — |
| 001 | tiền = int/BIGINT | F1 |
| 002 | ingest idempotent + dedupe | F2 |
| 003 | không FK → orphan-safe | F3 |
| 004 | response contract data/meta/error | — |
| 005 | spec-first + oracle + review | F4/F5 |
