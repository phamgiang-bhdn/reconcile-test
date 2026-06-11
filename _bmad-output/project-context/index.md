# Project Context — Master Index

**Project:** E-commerce Seller Platform | **Stack:** FastAPI · PostgreSQL · Next.js

Điểm vào cho AI agent. **Chỉ load file liên quan tới task** — đừng load tất cả.

Quan hệ với `.claude/skills/`: skill là "cách code nhanh theo tầng"; `project-context/common/*` là **single source of truth** cho quyết định kiến trúc, quy trình, chất lượng, bảo mật, version. Nghiệp vụ + con số của một task ở **story** (`docs/stories/`), không ở đây.

---

## Loading Guide (token-efficient)

| Bối cảnh task | File nên load |
|---|---|
| Sửa **API/handler backend** | `skills/backend-fastapi` + `common/architecture` + `common/code-quality` |
| Sửa **schema/migration/ingest** | `skills/data-postgres` + `common/architecture` (ADR-001/002/003) |
| Sửa **UI** | `skills/frontend-nextjs` + `common/code-quality` (mục Frontend) |
| **Cross-cutting** (DB → API → UI) | cả 3 skill + `common/architecture` |
| Viết/ sửa **test** | `skills/backend-fastapi` (mục 8) + `common/code-quality` |
| Câu hỏi **quy trình / chạy / commit** | `common/dev-workflow` |
| **Bảo mật / hiệu năng** | `common/security-perf` |
| **Anti-pattern** | `common/code-quality` |
| Version thư viện | `technology-stack-versions.md` |

---

## Common Files — Single Source of Truth

| File | Phạm vi | Chủ đề |
|---|---|---|
| [architecture.md](common/architecture.md) | Toàn dự án | ADR: phân lớp, tiền=int, dedupe idempotent, không-FK orphan, response contract |
| [dev-workflow.md](common/dev-workflow.md) | Toàn dự án | Prereq, docker compose, migrate/seed, test trước commit, branching |
| [code-quality.md](common/code-quality.md) | Toàn dự án | Anti-pattern theo tầng (Python/SQL/TS), quy tắc diff |
| [security-perf.md](common/security-perf.md) | Toàn dự án | Checklist bảo mật, bẫy hiệu năng (N+1, index), observability |

## Skills — cách code theo tầng
`engineering-standards` (cross-cutting) · `backend-fastapi` · `data-postgres` · `frontend-nextjs`.

## Agents — panel review đối kháng
`edge-case-hunter` · `bug-hunter` · `correctness-reviewer` (chạy qua `/review`).

---

## Key Rules (Quick Reference)
1. Tiền là **số nguyên minor unit** (BIGINT/int) — không float ở phép tính tiền. [F1]
2. Ingest **idempotent**: UNIQUE khóa tự nhiên + `ON CONFLICT DO NOTHING`; dedupe trùng-toàn-bộ, không đếm đôi. [F2]
3. **Không FK cứng** ở bảng ingest → giữ được orphan; phân loại ở domain. [F3]
4. **Quy ước dấu** (giảm/phí) định nghĩa ở story, nhất quán toàn pipeline. [F4]
5. **Oracle**: mỗi task tài chính có ≥1 con số tổng kỳ vọng; test phải chốt; giữ qua mọi thay đổi. [F5]
6. Nghiệp vụ ở **domain thuần** (không import db/fastapi); handler mỏng; repo chỉ query.
7. Mọi API theo **response contract** `data`/`meta`/`error`.
8. SQL **tham số hoá**; mã lỗi là hằng `UPPER_SNAKE`.
9. Mỗi feature: ≥1 test/nhánh + 1 test dữ liệu bẩn + 1 test oracle.
10. Mọi thay đổi nghiệp vụ qua `/review` (hết `BLOCK`) trước khi commit.
