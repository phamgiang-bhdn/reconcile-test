# Code Quality & Anti-patterns — Toàn dự án

---

## Anti-pattern: Python / Domain
- ❌ Logic nghiệp vụ trong router/handler — phải ở `domain/<feature>/logic.py`.
- ❌ Domain import `psycopg`/`fastapi` — domain phải thuần, test không cần DB.
- ❌ `float` hoặc `/` thật cho tiền — luôn `int` (xem ADR-001).
- ❌ Cộng tiền khi chưa dedupe nguồn — đếm đôi (xem ADR-002).
- ❌ Hằng trạng thái hardcode rải rác — dùng `logic.STATUS_*`.
- ❌ Ternary lồng > 1 tầng — if/else hoặc lookup map.
- ❌ Nuốt exception ở luồng tiền — phải log dòng bị bỏ/sửa.

## Anti-pattern: SQL / Postgres
- ❌ Nối chuỗi vào SQL — luôn tham số hoá `%s`.
- ❌ FK bảng-ingest → bảng-gốc — chặn orphan (ADR-003).
- ❌ Tiền kiểu `NUMERIC`/`REAL`/`INTEGER` — dùng `BIGINT`.
- ❌ Migration không idempotent / phá dữ liệu cũ.
- ❌ `SELECT SUM(amount)` thô khi nguồn có thể trùng.
- ❌ Query trong vòng lặp (N+1) — lấy theo lô, gộp ở domain.

## Anti-pattern: TypeScript / Next.js
- ❌ `any` cho response API — khai type khớp response contract.
- ❌ Hardcode URL backend trong component — qua `lib/api.ts` + `NEXT_PUBLIC_API_URL`.
- ❌ Tự format/round/chia tiền ở client — dùng `formatVnd`, tiền là số nguyên.
- ❌ if/else màu trạng thái rải rác — lookup `Record<Status, ...>`.
- ❌ Lọc toàn bộ phía client khi backend đã có filter param.

## Anti-pattern: Chung
- ❌ Comment thừa / doc-header / TODO / ascii-art — comment chỉ giải thích **WHY** khi non-obvious.
- ❌ Nhét mã story / "per AC" vào source code — thuộc PR description.
- ❌ Tách helper chỉ để "đẹp" khi 1 call site — inline.
- ❌ Trừu tượng đầu cơ — độ phức tạp khớp đúng task.
- ❌ Bắt user nhập field suy ra được từ ngữ cảnh.

## Quy tắc diff & file
- Diff < ~400 dòng (trừ file sinh tự động/seed).
- Một file / một endpoint hoặc một method.
- Response struct trong handler là cục bộ, không dùng lại chéo file.
- Đặt tên/file theo `engineering-standards` mục 6.

## Definition of Done (nhắc lại)
AC đạt + validation-report · test oracle xanh · `/review` hết `BLOCK` · `docker compose up` chạy · README cập nhật.
