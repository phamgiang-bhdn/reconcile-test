---
name: data-postgres
description: Chuẩn tầng dữ liệu PostgreSQL cho toàn dự án — kiểu tiền tệ, thiết kế schema, migration đánh số idempotent, ingest/seed idempotent + dedupe theo khóa tự nhiên, xử lý record orphan (không FK cứng), repository pattern psycopg3 (SQL tham số hoá), index. Domain-agnostic — ví dụ dùng bảng placeholder. Dùng khi tạo/sửa schema, migration, repository, hoặc import dữ liệu.
---

# Data Layer — PostgreSQL + psycopg3

## Load Project Context First
Theo `_bmad-output/project-context/index.md`: load `skills/engineering-standards` + `common/architecture.md` (ADR-001/002/003) + `common/security-perf.md` (index, N+1). Schema cụ thể ở story (`_bmad-output/implementation-artifacts/`).

Kế thừa `engineering-standards` (mục 2 luật tài chính, mục 5 bảo mật). Tầng này chỉ lưu/đọc; KHÔNG chứa nghiệp vụ. Schema cụ thể của một feature định nghĩa trong story của feature đó; dưới đây là **khuôn mẫu** áp cho mọi feature.

## 1. Kiểu dữ liệu
| Loại | Kiểu Postgres | Ghi chú |
|------|---------------|---------|
| Tiền (VND nguyên) | `BIGINT` | KHÔNG `NUMERIC`(float), KHÔNG `INTEGER` (tràn ở tổng lớn) |
| Mã/định danh | `TEXT` | khóa tự nhiên khi có làm PK |
| Trạng thái enum | `TEXT` + `CHECK (col IN (...))` | hằng khớp enum tầng app |
| Ngày | `DATE` / `TIMESTAMPTZ` | `DATE` cho ngày thuần; `TIMESTAMPTZ` cho thời điểm |

## 2. Schema pattern — hai bảng điển hình của dự án

Mẫu phổ biến: một **bảng gốc** (thực thể, khóa tự nhiên) + một **bảng dữ liệu nhập** (ingest từ file/đối tác, có thể trùng, có thể trỏ tới thực thể chưa tồn tại). Thay `<entity>`/`<source_record>` bằng tên thật của feature.

```sql
-- migrations/001_init_<noun>.sql   (idempotent, không phá dữ liệu cũ)
CREATE TABLE IF NOT EXISTS <entity> (
    <entity>_code TEXT PRIMARY KEY,
    status        TEXT   NOT NULL CHECK (status IN ('state_a','state_b')),
    amount        BIGINT NOT NULL DEFAULT 0,         -- F1: tiền là BIGINT
    created_date  DATE   NOT NULL
);

-- F3: KHÔNG đặt FK <entity>_code → <entity>: bản ghi nhập có thể là ORPHAN
--     (trỏ tới thực thể chưa có trong sổ). Lưu lại, phân loại ở tầng domain.
CREATE TABLE IF NOT EXISTS <source_record> (
    id            BIGSERIAL PRIMARY KEY,
    <entity>_code TEXT   NOT NULL,
    event_date    DATE   NOT NULL,
    amount        BIGINT NOT NULL,
    adjustment    BIGINT NOT NULL DEFAULT 0,         -- F4: dấu quy ước ở story
    net_amount    BIGINT NOT NULL,
    -- F2 idempotent: khóa tự nhiên = toàn bộ nội dung dòng nhập
    CONSTRAINT uq_<source_record>_natural
        UNIQUE (<entity>_code, event_date, amount, adjustment, net_amount)
);
CREATE INDEX IF NOT EXISTS idx_<source_record>_code ON <source_record> (<entity>_code);
```

## 3. Migration — Goose (SQL thuần, up+down CHUNG 1 file)
- Tool: **Goose** (binary Go, cài trong `Dockerfile` qua release — KHÔNG phải gói Python). Migration là **SQL thuần** trong `backend/migrations/`.
- **Một bảng = một file** `NNNNN_create_<table>.sql`, đánh số tăng dần. Trong file có **cả up lẫn down**:
```sql
-- +goose Up
CREATE TABLE orders ( order_code TEXT PRIMARY KEY, ... );

-- +goose Down
DROP TABLE orders;
```
- Goose tự track version qua bảng `goose_db_version`. Mỗi migration bọc trong transaction (statement không-transaction được: `-- +goose NO TRANSACTION`; statement phức tạp/function: `-- +goose StatementBegin/End`).
- Schema **cuối** đặt thẳng trong file tạo bảng (làm mới thì không tách "add column" lặt vặt); chỉ thêm migration mới khi schema đã chạy production.
- Cột mới `NOT NULL` phải có `DEFAULT`. Đổi `UNIQUE`/`ALTER` → viết đảo ngược ở khối `Down`.
- Cấu hình qua env (đặt trong `docker-compose.yml`): `GOOSE_DRIVER=postgres`, `GOOSE_DBSTRING=postgres://...?sslmode=disable`, `GOOSE_MIGRATION_DIR=migrations`.
- Lệnh (trong backend container): `goose up` · `goose down` (rollback 1) · `goose status` · `goose redo` · `goose create <name> sql`.

## 4. Ingest / Seed idempotent (luật vàng F2)

```python
# scripts/seed.py — import có thể chạy lại nhiều lần, không đếm đôi
def seed_source(conn, rows: list[SourceRecord]) -> None:
    with conn.cursor() as cur:
        for r in rows:
            # F4: validate bất biến từng dòng; dòng sai -> log, không nuốt im
            if r.net_amount != r.amount + r.adjustment:
                logger.warning("source row breaks invariant: %s", r.entity_code)
            cur.execute(
                """
                INSERT INTO <source_record>
                    (<entity>_code, event_date, amount, adjustment, net_amount)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT ON CONSTRAINT uq_<source_record>_natural DO NOTHING
                """,
                (r.entity_code, r.event_date, r.amount, r.adjustment, r.net_amount),
            )
    conn.commit()
```

- **Dedupe ở DB** bằng UNIQUE + `ON CONFLICT DO NOTHING` → dòng trùng-toàn-bộ bị bỏ.
- Chỉ gộp khi **trùng toàn bộ khóa tự nhiên**. Hai bản ghi hợp lệ khác nhau phải giữ cả hai → khóa tự nhiên gồm đủ cột phân biệt.

## 5. Repository pattern (psycopg3, SQL tham số hoá)

```python
# app/repositories/<feature>_repo.py — chỉ truy vấn, trả dataclass; KHÔNG nghiệp vụ
class <Feature>Repo:
    def __init__(self, conn): self._conn = conn

    def fetch_entities(self) -> list[Entity]:
        with self._conn.cursor() as cur:
            cur.execute("SELECT <entity>_code, status, amount, created_date FROM <entity>")
            return [Entity(*row) for row in cur.fetchall()]

    def fetch_source_records(self) -> list[SourceRecord]:
        with self._conn.cursor() as cur:
            cur.execute(
                """SELECT <entity>_code, event_date, amount, adjustment, net_amount
                   FROM <source_record>"""
            )
            return [SourceRecord(*row) for row in cur.fetchall()]
```

- CẤM nối chuỗi vào SQL — luôn `%s` + tuple tham số.
- Repository không gọi repository khác; ráp dữ liệu là việc của domain.
- Đóng cursor/connection (`with`); dùng pool ở `app/db.py`.

## 6. Index & hiệu năng
- Index cột join/filter hay dùng (khóa tự nhiên, cột status nếu lọc nhiều).
- Tránh N+1: lấy theo lô (1 query nhiều dòng) rồi gộp ở domain, không query trong vòng lặp.

## 7. Anti-pattern (CẤM)
- ❌ FK bảng-nhập → bảng-gốc (chặn orphan, mất dữ liệu).
- ❌ `SELECT SUM(amount)` thô khi chưa dedupe.
- ❌ Tiền kiểu `NUMERIC`/`REAL`/`INTEGER`.
- ❌ Migration phá dữ liệu hoặc không idempotent.
- ❌ Nghiệp vụ/phân loại nhét trong SQL phức tạp thay vì domain.
