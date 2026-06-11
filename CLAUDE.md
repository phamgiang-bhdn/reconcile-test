# Project Standard — E-commerce Seller Platform

Dự án dùng quy trình **BMad có AI hỗ trợ, chuẩn hoá** (như bộ ig) để làm mọi tính năng. Công việc tổ chức theo **epic → story**, trạng thái track trong `sprint-status.yaml`. Tính năng đầu — *Reconciliation* — là **epic 01, story 1-1**; còn nhiều epic/story khác sẽ thêm dần.

## Stack chuẩn
- **Backend**: FastAPI (Python 3.12) + psycopg3, raw SQL. Nghiệp vụ tách khỏi web/DB để unit-test.
- **DB**: PostgreSQL 16 (Docker). Tiền lưu **số nguyên minor unit** (VND: BIGINT), không float.
- **Frontend**: Next.js 15 (App Router) + TypeScript.
- **Hạ tầng**: `docker compose` (DB + backend); frontend chạy node. CI: GitHub Actions.

## Layout (chuẩn BMad)
```
_bmad-output/
  project-context/        # single source of truth: index + common (ADR/workflow/quality/security) + stack
  planning-artifacts/     # epics-NN-*.md (epic + story Given/When/Then)
  implementation-artifacts/
    sprint-status.yaml     # trạng thái mọi epic/story (backlog→ready-for-dev→in-progress→review→done)
    NN-M-*.md              # story file (ready-for-dev trở đi)
    NN-M-validation-report.md
.claude/
  skills/   coding: engineering-standards · backend-fastapi · data-postgres · frontend-nextjs
            workflow: create-epic · create-story · sprint-planning · sprint-status · dev-story · code-review
  agents/   panel đối kháng: edge-case-hunter · bug-hunter · correctness-reviewer
backend/ frontend/   mã nguồn
orders.csv income.csv  seed data (đề cung cấp)
```

## Quy trình BMad (mỗi story)
```
/create-epic <tên>     → epic + danh sách story (backlog) trong planning-artifacts
/create-story NN-M     → story file đầy đủ (AC + oracle) → ready-for-dev
/dev-story NN-M        → TDD: test trước → implement theo skill → review
/code-review NN-M      → panel ĐỐI KHÁNG (edge-case ∥ bug ∥ correctness) → validation-report → done
/sprint-status         → in tiến độ mọi epic/story
```
Kiến thức **chung** (cách build, luật tiền) ở `.claude/skills/` + `_bmad-output/project-context/`. Kiến thức **riêng story** (nghiệp vụ, oracle) ở story file — KHÔNG nhét vào skill.

## Bất biến toàn dự án (mọi story tài chính)
1. **Tiền = số nguyên minor unit** (BIGINT/int). Cấm float. [F1, ADR-001]
2. **Ingest idempotent**: dedupe khóa tự nhiên, không đếm đôi. [F2, ADR-002]
3. **Orphan-safe**: không FK cứng chặn record mồ côi. [F3, ADR-003]
4. **Spec trước, code sau**: không story thì không dev; mọi thay đổi qua `/code-review` (hết BLOCK) + giữ oracle. [F5, ADR-005]

## Definition of Done
AC đạt + validation-report · test oracle xanh · `/code-review` hết BLOCK · `docker compose up` chạy · README cập nhật · sprint-status = `done`.
