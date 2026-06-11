# Dev Workflow — Toàn dự án

## Prerequisites
```bash
docker --version          # Docker Desktop chạy
docker compose version    # v2
node --version            # 20 LTS (cho frontend)
```
Không cần cài Python local — backend + DB chạy trong container.

## Cấu hình
- `backend/.env` (hoặc env trong compose): `DATABASE_URL`, `CORS_ORIGINS`.
- `frontend/.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8000`.
- KHÔNG commit `.env*` (xem `.gitignore`). Mẫu để ở `.env.example`.

## Chạy local
```bash
docker compose up -d db                                   # Postgres
docker compose run --rm backend goose up                  # migrate (Goose: up/down 1 file SQL)
docker compose run --rm backend python -m scripts.seed    # nạp dữ liệu (idempotent)
docker compose up backend                                 # API :8000
cd frontend && npm install && npm run dev                 # UI :3000
```
`docker compose up` (không tham số) dựng cả DB + backend; migrate/seed có thể gắn vào entrypoint backend.

## Vòng đời một task (bám pipeline harness)
```
/investigate <task>   → khoanh vùng + thống kê dữ liệu thật
/create-story <id>    → docs/stories/<id>.md (AC + oracle)
/dev-story <id>       → TDD: test trước → code theo skill
/review               → panel đối kháng (edge-case ∥ bug ∥ correctness) → fix → validation-report
verify                → pytest + docker up, đối chiếu oracle
```

## Test trước commit
```bash
docker compose run --rm backend pytest -q     # backend
cd frontend && npm run build                  # typecheck + build FE
```
Chạm hàm domain → cập nhật test hàm đó. Oracle phải xanh.

## Branching & commit
- Nhánh: `feat/<task-id>`, `fix/<...>`. Không commit thẳng nhánh chính.
- Commit nhỏ, message mệnh lệnh ngắn. Không commit `.env`, file rác, `__pycache__`, `node_modules`.
- PR: title 1 dòng; mô tả task + cách verify oracle. CI (lint + test + build) phải xanh.

## CI (GitHub Actions)
- `lint`: ruff (backend), tsc/next build (frontend).
- `test`: pytest (gồm test oracle).
- `build`: docker build backend + `next build`.
Đỏ CI = không merge.
