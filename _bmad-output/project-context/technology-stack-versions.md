# Technology Stack — Versions

Phiên bản chuẩn cho toàn dự án. Pin version trong `pyproject.toml` / `package.json`; nâng cấp phải qua review.

## Backend
| Thành phần | Version | Ghi chú |
|---|---|---|
| Python | 3.12 | base image `python:3.12-slim` |
| FastAPI | ^0.115 | web framework |
| Uvicorn | ^0.32 | ASGI server (`uvicorn app.main:app`) |
| psycopg | ^3.2 (binary + pool) | driver Postgres, dùng `psycopg_pool` |
| pydantic-settings | ^2.6 | config từ env |
| pytest | ^8.3 | test |
| ruff | ^0.8 | lint + format |

## Database
| Thành phần | Version | Ghi chú |
|---|---|---|
| PostgreSQL | 16 | image `postgres:16-alpine` |

## Frontend
| Thành phần | Version | Ghi chú |
|---|---|---|
| Node | 20 LTS | base image `node:20-alpine` |
| Next.js | 15 | App Router |
| React | 19 | đi kèm Next 15 |
| TypeScript | ^5.6 | strict mode |
| Tailwind CSS | ^4 | styling |

## Hạ tầng
| Thành phần | Version | Ghi chú |
|---|---|---|
| Docker Compose | v2 | `docker compose up` |
| GitHub Actions | — | CI: lint + test + build |

## Nguyên tắc version
- Pin minor; tránh `latest` trong Dockerfile/CI để build reproducible.
- Tiền tệ KHÔNG phụ thuộc thư viện số thực — chỉ `int`/`BIGINT`.
