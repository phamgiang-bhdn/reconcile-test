---
name: engineering-standards
description: Chuẩn kỹ thuật cross-cutting cho TOÀN dự án — kiến trúc phân lớp, luật dữ liệu tài chính (tiền nguyên, ingest idempotent/dedupe, orphan-safe, quy ước dấu, bất biến tổng), error model & response contract, logging, bảo mật, quy ước đặt tên/file, code quality & anti-pattern, Definition of Done. Đọc TRƯỚC mọi thay đổi code, ở mọi tầng và mọi task. Domain-agnostic — ví dụ dùng placeholder <feature>/<Entity>.
---

# Engineering Standards (toàn dự án)

## Load Project Context First
Trước khi sửa code, load theo `_bmad-output/project-context/index.md` (loading guide). Tối thiểu: `common/architecture.md` (ADR), `common/code-quality.md` (anti-pattern). Nghiệp vụ + oracle của task ở story tương ứng (`_bmad-output/implementation-artifacts/`).

Chuẩn nền cho mọi task. Skill stack (`backend-fastapi`, `data-postgres`, `frontend-nextjs`) kế thừa và bổ sung chi tiết theo tầng. Khi xung đột, **engineering-standards thắng**. Định nghĩa nghiệp vụ cụ thể (thực thể, trạng thái, con số kỳ vọng) sống trong **story của task**, không ở đây.

## 1. Kiến trúc phân lớp (bắt buộc mọi feature)

```
HTTP/UI  →  Application (router/handler)  →  Domain (logic thuần)  →  Repository (SQL)  →  DB
                     │                              │                        │
              parse/validate                 nghiệp vụ, KHÔNG               truy vấn,
              gọi domain, map                 import framework/DB           KHÔNG nghiệp vụ
              ra response contract
```

- **Domain logic THUẦN**: nhận/trả dataclass hoặc dict, **không import** framework/DB/HTTP. Đây là thứ unit-test, chạy không cần DB.
- **Handler mỏng**: decode → validate → gọi domain → map response. Không nghiệp vụ trong handler.
- **Repository ngu**: chỉ CRUD/query. Mọi ráp nối/phân loại/tính toán ở domain.
- **Phụ thuộc một chiều**: HTTP → domain → repo. Domain không biết HTTP; repo không biết domain.

> Vì sao: tách lớp cho phép test nghiệp vụ (đặc biệt tiền tệ) bằng dữ liệu giả, không cần dựng DB/HTTP; thay hạ tầng không đụng nghiệp vụ.

## 2. Luật dữ liệu tài chính (bất biến — vi phạm = bug chặn merge)

Dự án xử lý tiền của người bán, nên các luật này áp cho **mọi** feature đụng tiền.

| # | Luật | Lý do | Kiểm bằng |
|---|------|-------|-----------|
| F1 | Tiền là **số nguyên minor unit** (VND → `int`/`BIGINT`). Cấm `float` / phép chia thật ở tính tiền. | float làm tròn sai tiền | test + grep `float(` quanh tiền |
| F2 | **Ingest idempotent**: dữ liệu nguồn (file/đối tác) có thể trùng → dedupe theo **khóa tự nhiên** (UNIQUE + `ON CONFLICT DO NOTHING`) và/hoặc trong logic. | tránh đếm đôi tiền | UNIQUE constraint + test dedupe |
| F3 | **Orphan-safe**: record trỏ tới thực thể chưa tồn tại vẫn lưu được — **không FK cứng** chặn. Phân loại nó, đừng vứt. | dữ liệu cần đối chiếu không được mất | test orphan |
| F4 | **Quy ước dấu** (khoản giảm/phí âm hay dương) định nghĩa rõ ở story và giữ nhất quán toàn pipeline. | cộng nhầm dấu = lệch tiền | test bất biến chéo |
| F5 | **Bất biến tổng** (oracle): mỗi task tài chính có ≥1 con số tổng kỳ vọng (lấy từ story); mọi thay đổi phải giữ. | self-check chống regression | test oracle |

Khi cần chia (tỉ lệ %), chỉ chia ở tầng trình bày — không lưu kết quả float vào trường tiền.

## 3. Error model & Response contract

Mọi API trả **một** trong các hình dạng (đồng nhất toàn dự án):

```json
{ "data": [ ... ], "meta": { "size": 30, "total": 150 } }   // list
{ "data": { ... } }                                          // single
{ "error": { "code": "INVALID_INPUT", "message": "..." } }   // error
```

- Lỗi nghiệp vụ → exception có **code + http status** (xem `backend-fastapi` `AppError`). Handler map ra `error` contract.
- Mã lỗi là hằng `UPPER_SNAKE`, không hardcode chuỗi rải rác.
- **Không nuốt lỗi im lặng** ở luồng tiền; dữ liệu vi phạm bất biến phải log cảnh báo.

## 4. Logging
- Log có cấu trúc (key=value/JSON), không `print`.
- Luồng tiền: log mỗi khi **bỏ/sửa** dữ liệu (dòng trùng bị dedupe, dòng vi phạm bất biến) — phải truy vết được vì sao tổng ra con số đó.
- Không log secret/PII.

## 5. Bảo mật
- SQL **tham số hoá**; CẤM nối chuỗi vào câu lệnh.
- Validate input ở biên: kiểu, enum, NULL/empty, khoảng trắng thừa, BOM khi đọc file.
- Cấu hình/credential qua **env**, không hardcode, không commit secret.
- CORS whitelist origin cụ thể, không `*` ở prod.

## 6. Quy ước đặt tên & file
| Thứ | Quy ước | Ví dụ (placeholder) |
|-----|---------|---------------------|
| Module domain | `app/domain/<feature>/logic.py`, `models.py` | `domain/<feature>/logic.py` |
| Router | `app/api/<feature>.py` | `api/<feature>.py` |
| Repository | `app/repositories/<feature>_repo.py` | `repositories/<feature>_repo.py` |
| Migration | `migrations/NNN_<verb>_<noun>.sql` | `001_init_<noun>.sql` |
| Test | `tests/test_<feature>_<layer>.py` | `tests/test_<feature>_logic.py` |
| Hằng enum | `UPPER_SNAKE` | `STATUS_A`, `STATUS_B` |

## 7. Code quality — anti-pattern (CẤM)
- ❌ Logic nghiệp vụ trong handler/router hoặc rải rác trong SQL string.
- ❌ `float` cho tiền; `SELECT SUM(amount)` khi chưa dedupe.
- ❌ FK cứng chặn orphan.
- ❌ Ternary lồng > 1 tầng; thay bằng if/else hoặc lookup map.
- ❌ Magic string trạng thái rải rác — dùng hằng.
- ❌ Comment thừa/doc-header/TODO; comment chỉ giải thích **WHY** khi non-obvious. Không nhét mã story vào code.
- ❌ Bắt user nhập field suy ra được từ ngữ cảnh.

## 8. Definition of Done (mọi task)
1. Mọi AC của story đạt; có `_bmad-output/implementation-artifacts/<task>-validation-report.md` đối chiếu claim vs code.
2. Unit-test logic lõi xanh, **gồm test oracle** chốt con số tổng của story (F5).
3. `/review` (panel đối kháng) không còn finding `BLOCK`.
4. `docker compose up` chạy; endpoint trả đúng response contract.
5. README cập nhật cách chạy.
