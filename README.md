# Mini Reconciliation Dashboard

Đối soát đơn hàng shop (`orders.csv`) với file thanh toán sàn (`income.csv`) → KPI + bảng phân loại 4 trạng thái. Backend **FastAPI + PostgreSQL**, frontend **Next.js 15**.

> Self-check: `Σ net_received = 1.615.756 ₫` — đã verify **3 nguồn độc lập** (pytest, reimplement Node, PowerShell) + chạy thật `docker compose`.

## Cách chạy

### Backend + DB (Docker)
```bash
docker compose up -d db                                       # PostgreSQL 16
docker compose run --rm backend goose up                      # migrate (Goose: up/down chung 1 file SQL)
docker compose run --rm backend python -m scripts.seed        # nạp 2 CSV (idempotent)
docker compose up -d backend                                  # API :8000
# rollback 1 bước: docker compose run --rm backend goose down   ·   trạng thái: goose status
# kiểm: curl http://localhost:8000/kpi
```

### Frontend
```bash
cd frontend
cp .env.example .env.local          # NEXT_PUBLIC_API_URL=http://localhost:8000
npm install && npm run dev          # http://localhost:3000
```

### Test
```bash
docker compose run --rm backend pytest -q   # 8 passed (gồm test oracle)
```

## API
| Endpoint | Mô tả |
|---|---|
| `GET /reconciliation[?status=]` | mỗi dòng + `reconcile_status` ∈ {matched, refunded, orphan, unsettled}; lọc theo status |
| `GET /kpi` | `total_gross, total_net, total_fees, reconciliation_rate, refund_count, refund_total` |
| `GET /reconciliation/export[?status=]` | xuất `.xlsx` (sheet KPI + ChiTiet), tiền là ô số (story 1-2) |
| `GET /health` | readiness |

> Đa sàn (story 1-3): nạp file sàn khác bằng `SEED_PLATFORM=lazada SEED_INCOME_FILE=lazada.csv` — loader ánh xạ cột qua `PLATFORM_COLUMNS`, không sửa logic đối soát.

Response contract: `{data, meta}` (list) · `{data}` (single) · `{error:{code,message}}`.

## Quyết định thiết kế (vì sao đúng tiền)
- **Tiền = số nguyên VND** (`BIGINT`/`int`), không float → không sai số làm tròn.
- **Dedupe 2 lớp**: DB `UNIQUE(khóa tự nhiên) + ON CONFLICT DO NOTHING` và `dedupe_settlements` ở domain → dòng income trùng y hệt (`ORD-2026-0003` ×2) không bị đếm đôi.
- **Không FK** income→orders → giữ được **orphan** (`ORD-2026-0001`: thanh toán không có đơn) thay vì mất dữ liệu.
- **Phân lớp**: logic đối soát thuần (không import DB/web) → unit-test không cần DB.
- 4 trạng thái phân loại **theo settlement**; `order.status` chỉ hiển thị (mọi đơn có thanh toán đều `completed`).

## AI đã sinh code sai chỗ nào & tôi phát hiện/sửa thế nào

Dự án làm theo quy trình **AI có kiểm soát** (xem `_bmad-output/` + `.claude/`): viết story → *advanced-elicitation* → dev (TDD) → review đối kháng 3 lớp. Chính các bước "ép AI tự phản biện" đã bắt lỗi:

1. **Bản nháp đầu của AI bỏ sót: orphan có tính vào `total_net` không?** Khi tính thử, AI dễ lọc `total_net` chỉ trên đơn khớp → **thiếu 69.811 ₫** (net của orphan `ORD-2026-0001`), lệch self-check. Bước *pre-mortem* ("giả định sai số tiền, vì sao?") bắt được → chốt AC: total tính trên **toàn bộ** settlement đã dedupe, **gồm orphan**.
2. **Mẫu số `reconciliation_rate`**: AI suýt tính `(matched+refunded)/tổng-số-dòng` = 23/27. Đúng phải là `/số-order` = 23/26 (orphan **không** phải order). *Edge-case enumeration* phát hiện → thêm `test_rate` chốt mẫu số = 26.
3. **Dòng income trùng y hệt** (`ORD-2026-0003`): nếu `SUM` thô thì thừa **73.440 ₫**. Bắt từ khâu khảo sát dữ liệu → dedupe 2 lớp + `test_dedupe_counts_once`.
4. **Định nghĩa trạng thái mơ hồ**: AC ban đầu gắn `matched/refunded` với "completed", nhưng code phân loại theo settlement. *First-principles* gỡ tiền đề sai → ghi rõ `order.status` chỉ hiển thị, và `cancelled-có-settlement` là anomaly (known limitation).

**Cách verify**: mỗi con số được đối chiếu độc lập 3 nguồn (pytest / reimplement Node / PowerShell từ CSV gốc) + chạy thật `docker compose` → `/kpi` trả đúng `1.615.756`. Review 3 lớp đối kháng: 0 BLOCK, 5 NOTE (deferred cho tính năng tương lai — multi-settlement, phân trang). Chi tiết: [`_bmad-output/implementation-artifacts/1-1-validation-report.md`](_bmad-output/implementation-artifacts/1-1-validation-report.md).

## Cấu trúc
```
backend/   app/{domain,api,repositories,loaders}, migrations, scripts, tests
frontend/  app, components, lib (Next.js 15)
_bmad-output/   quy trình AI: project-context (ADR/chuẩn) + epic + story + sprint-status + validation-report
.claude/   harness: skills (create-story, dev-story, code-review, advanced-elicitation, ...) + agents đối kháng
```
