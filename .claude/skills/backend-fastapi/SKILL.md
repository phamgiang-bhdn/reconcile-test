---
name: backend-fastapi
description: Chuẩn code backend cho toàn dự án — FastAPI + psycopg3 + Postgres. Layout phân lớp (api → domain → repository), config qua env, DB pool, AppError + exception handler, response contract, endpoint pattern, CORS, pytest + test oracle, commands, anti-pattern. Domain-agnostic — ví dụ dùng placeholder <feature>/<Entity>. Dùng khi thêm/sửa bất kỳ API, logic, hay test backend nào.
---

# Backend — FastAPI + psycopg3

## Load Project Context First
Theo `_bmad-output/project-context/index.md`: load `skills/engineering-standards` + `common/architecture.md` (ADR-000/001/004) + `common/code-quality.md`. Nghiệp vụ + oracle ở story (`_bmad-output/implementation-artifacts/`).

Kế thừa `engineering-standards` (phân lớp, luật tiền, response contract) và `data-postgres` (repository). Handler mỏng, domain thuần, repo ngu. Tên thực thể/trạng thái/oracle cụ thể lấy từ **story của feature** — dưới đây là khuôn mẫu.

## 1. Layout (mọi feature theo khuôn)

```
backend/
  app/
    main.py                       # tạo FastAPI app, CORS, lifespan(pool), include router
    config.py                     # Settings từ env (DATABASE_URL, CORS_ORIGINS)
    db.py                         # psycopg connection pool
    errors.py                     # AppError + register_exception_handlers
    api/
      health.py                   # GET /health
      <feature>.py                # router của feature (HTTP layer)
    domain/
      <feature>/
        models.py                 # dataclass thuần (Entity, SourceRecord, ...)
        logic.py                  # nghiệp vụ THUẦN — không import db/fastapi
    repositories/
      <feature>_repo.py           # SQL (xem skill data-postgres)
    loaders/
      source_loader.py            # nguồn (file/đối tác) → dataclass; dùng chung seed + test
  migrations/                     # raw SQL idempotent (xem data-postgres)
  scripts/
    seed.py                       # import dữ liệu, dedupe ON CONFLICT
    migrate.py                    # chạy migrations theo thứ tự
  tests/
    conftest.py
    test_<feature>_logic.py       # test domain thuần (không cần DB)
  pyproject.toml
  Dockerfile
```

| Path | Vai trò |
|------|---------|
| `app/api/` | HTTP layer: parse/validate → gọi domain → map response. KHÔNG nghiệp vụ. |
| `app/domain/<f>/logic.py` | Nghiệp vụ thuần, unit-test trực tiếp |
| `app/domain/<f>/models.py` | `@dataclass(frozen=True)` cho input/output domain |
| `app/repositories/` | Query SQL tham số hoá |
| `app/errors.py` | `AppError` + handler → error contract |

## 2. Config (env, không hardcode)

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://app:app@db:5432/app"
    cors_origins: list[str] = ["http://localhost:3000"]

settings = Settings()  # đọc env: DATABASE_URL, CORS_ORIGINS
```

## 3. DB pool

```python
# app/db.py
from psycopg_pool import ConnectionPool
from app.config import settings

pool = ConnectionPool(settings.database_url, min_size=1, max_size=10, open=False)
```

## 4. Error model + handler (response contract)

```python
# app/errors.py
from fastapi import Request
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code, self.message, self.status = code, message, status

def register_exception_handlers(app):
    @app.exception_handler(AppError)
    async def _handle(_: Request, exc: AppError):
        return JSONResponse(status_code=exc.status,
                            content={"error": {"code": exc.code, "message": exc.message}})
```

## 5. App bootstrap

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import pool
from app.errors import register_exception_handlers
from app.api import health, <feature>

@asynccontextmanager
async def lifespan(_: FastAPI):
    pool.open(); yield; pool.close()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_methods=["*"], allow_headers=["*"])
register_exception_handlers(app)
app.include_router(health.router)
app.include_router(<feature>.router)
```

## 6. Domain thuần (thứ được test)

```python
# app/domain/<feature>/models.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Entity:
    entity_code: str; status: str; amount: int; created_date: str

@dataclass(frozen=True)
class SourceRecord:
    entity_code: str; event_date: str; amount: int; adjustment: int; net_amount: int
```

```python
# app/domain/<feature>/logic.py  — KHÔNG import db/fastapi
# Trạng thái cụ thể + công thức tổng hợp định nghĩa ở STORY của feature.
STATUS_A, STATUS_B = "state_a", "state_b"

def classify(entities: list[Entity], sources: list[SourceRecord]) -> list[dict]: ...
def compute_summary(entities: list[Entity], sources: list[SourceRecord]) -> dict: ...
```
> Logic miền (định nghĩa từng status, công thức, oracle) lấy từ story; **không** hardcode vào skill.

## 7. HTTP layer (handler mỏng)

```python
# app/api/<feature>.py
from fastapi import APIRouter, Query
from app.db import pool
from app.repositories.<feature>_repo import <Feature>Repo
from app.domain.<feature> import logic
from app.errors import AppError

router = APIRouter(prefix="/<feature>", tags=["<feature>"])
VALID = {logic.STATUS_A, logic.STATUS_B}

@router.get("")
def list_<feature>(status: str | None = Query(default=None)):
    if status is not None and status not in VALID:
        raise AppError("INVALID_INPUT", f"unknown status: {status}", 400)
    with pool.connection() as conn:
        repo = <Feature>Repo(conn)
        rows = logic.classify(repo.fetch_entities(), repo.fetch_source_records())
    if status:
        rows = [r for r in rows if r["status"] == status]
    return {"data": rows, "meta": {"size": len(rows), "total": len(rows)}}
```

Quy tắc HTTP layer:
- REST danh từ số nhiều; filter qua query param; luôn có `GET /health`.
- Validate enum/biên ở đây, ném `AppError` cho input sai.
- Trả đúng response contract (`data`/`meta` cho list, `data` cho single).
- KHÔNG tính nghiệp vụ ở đây — chỉ gọi `logic.*`.

## 8. Testing (pytest + test oracle)

Chạm hàm domain → thêm/cập nhật test cho hàm đó. Tối thiểu mỗi feature: 1 test/nhánh phân loại · 1 test dữ liệu bẩn (trùng/thiếu/sai bất biến) · 1 test oracle (F5).

```python
# tests/test_<feature>_logic.py
from app.domain.<feature> import logic
from app.domain.<feature>.models import SourceRecord
from app.loaders.source_loader import load_entities, load_sources

def test_dedupe_counts_once():
    s = SourceRecord("A", "2026-05-29", 91000, 0, 91000)
    summary = logic.compute_summary([], [s, s])      # dòng trùng y hệt
    assert summary["total_net"] == 91000             # đếm 1 lần, không 182000

def test_oracle_total_net():                          # F5 — con số chốt từ story
    entities = load_entities("<entity>.csv")
    sources = load_sources("<source>.csv")
    summary = logic.compute_summary(entities, sources)
    assert summary["total_net"] == EXPECTED_TOTAL_FROM_STORY
    assert summary["total_net"] == summary["total_gross"] + summary["total_adjustment"]
```

## 9. Commands
```bash
docker compose up backend db                 # chạy API + DB
docker compose run --rm backend pytest -q    # test
docker compose run --rm backend python -m scripts.migrate   # migrate
docker compose run --rm backend python -m scripts.seed      # seed (idempotent)
```

## 10. Anti-pattern (CẤM)
- ❌ Nghiệp vụ trong router; ❌ domain import psycopg/fastapi.
- ❌ `float` cho tiền; ❌ SQL nối chuỗi.
- ❌ Response không theo contract; ❌ nuốt lỗi luồng tiền.
- ❌ Hằng status hardcode rải rác thay vì `logic.STATUS_*`.
