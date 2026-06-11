# Mini Reconciliation Dashboard

Đối soát đơn hàng của shop (`orders.csv`) với file thanh toán sàn TMĐT (`income.csv`): phân loại từng đơn, tính KPI và phát hiện chênh lệch. Backend **FastAPI + PostgreSQL**, frontend **Next.js 15**.

## Tính năng

- Đối soát mỗi đơn thành 4 trạng thái: `matched` / `refunded` / `orphan` / `unsettled`.
- API KPI: tổng doanh thu, tiền thực nhận, phí, hoàn tiền, tỉ lệ đối soát.
- Dashboard: thẻ KPI + bảng lọc theo trạng thái + xuất Excel.
- Xử lý dữ liệu bẩn: dòng thanh toán trùng, đơn mồ côi, hoàn tiền âm.

## Stack & yêu cầu

| | |
|---|---|
| Backend | FastAPI (Python 3.12), psycopg3 |
| Database | PostgreSQL 16 |
| Frontend | Next.js 15, TypeScript |
| Migration | Goose (up/down) |
| Hạ tầng | Docker Compose |

**Cần có:** Docker Desktop, Node.js 20. *(Không cần cài Python/Postgres — chạy trong container.)*

## Chạy

**1. Backend + Database**
```bash
docker compose up -d db                                 # PostgreSQL
docker compose run --rm backend goose up                # tạo schema
docker compose run --rm backend python -m scripts.seed  # nạp orders.csv + income.csv
docker compose up -d backend                            # API tại http://localhost:8000
```

**2. Frontend**
```bash
cd frontend
cp .env.example .env.local
npm install && npm run dev                              # http://localhost:3000
```

**3. Test**
```bash
docker compose run --rm backend pytest -q               # 14 passed
```

## Mô hình đối soát

`net_received = gross_revenue + refund_amount + fee_total` (hoàn tiền & phí là số âm).

| Trạng thái | Ý nghĩa |
|---|---|
| `matched` | Đơn có thanh toán, không hoàn tiền — thu đủ |
| `refunded` | Đơn có thanh toán kèm hoàn tiền (`refund_amount < 0`) |
| `orphan` | Có dòng thanh toán nhưng không tìm thấy đơn trong sổ |
| `unsettled` | Đơn tồn tại nhưng sàn chưa thanh toán (gồm đơn đã huỷ) |

## API

| Endpoint | Mô tả |
|---|---|
| `GET /reconciliation[?status=]` | Danh sách đơn kèm `reconcile_status`, lọc theo trạng thái |
| `GET /kpi` | `total_gross, total_net, total_fees, reconciliation_rate, refund_count, refund_total` |
| `GET /reconciliation/export[?status=]` | Xuất Excel (sheet KPI + chi tiết) |
| `GET /health` | Health check |

Định dạng response: `{ data, meta }` (list) · `{ data }` (single) · `{ error: { code, message } }` (lỗi).

## Quyết định thiết kế

- **Tiền là số nguyên VND** (`BIGINT` / `int`), không dùng float → tránh sai số làm tròn.
- **Khử trùng 2 lớp**: ràng buộc `UNIQUE` ở DB + `ON CONFLICT DO NOTHING` khi import, và một lần nữa trong tầng nghiệp vụ → dòng thanh toán trùng lặp không bị cộng đôi.
- **Không đặt khóa ngoại** `income → orders`: cho phép lưu đơn mồ côi (thanh toán không khớp đơn nào) thay vì chặn insert và mất dữ liệu cần đối soát.
- **Tách lớp**: logic đối soát thuần (không phụ thuộc DB/web) → unit-test trực tiếp, không cần dựng database.
- Phân loại dựa trên **dữ liệu thanh toán**; trường `status` của đơn dùng để hiển thị.

## Làm việc với AI

Tôi dùng AI để viết code nhưng **review và kiểm chứng từng con số tiền trước khi tin**. Một vài chỗ AI dễ làm sai mà tôi phát hiện được:

1. **Đơn mồ côi và tổng tiền** — bản nháp đầu lọc `total_net` chỉ trên các đơn khớp, làm thiếu `69.811 ₫` (tiền của đơn mồ côi đã thực về ví). Sửa: tổng tính trên toàn bộ thanh toán đã khử trùng, gồm cả đơn mồ côi.
2. **Mẫu số tỉ lệ đối soát** — suýt lấy `(khớp + hoàn) / tổng số dòng` = 23/27. Đúng phải là `/ số đơn` = 23/26 (đơn mồ côi không phải đơn trong sổ). Đã thêm test khóa mẫu số = 26.
3. **Dòng thanh toán trùng** — đơn `ORD-2026-0003` xuất hiện hai lần giống hệt; nếu cộng thẳng sẽ dư `73.440 ₫`. Đã khử trùng 2 lớp + test riêng.
4. **Định nghĩa trạng thái** — gắn `matched/refunded` cứng với đơn `completed` trong khi thực tế phân loại theo dữ liệu thanh toán. Đã làm rõ và ghi nhận trường hợp ngoại lệ.

Mỗi con số được đối chiếu độc lập với file CSV gốc và kiểm lại bằng `/kpi` khi chạy thật.

> **Self-check:** `Σ net_received = 1.615.756 ₫` — khớp.

## Cấu trúc

```
backend/
  app/        domain (logic đối soát thuần) · api · repositories · loaders
  migrations/ Goose (up/down)
  scripts/    seed dữ liệu
  tests/      pytest (gồm test self-check)
frontend/
  app/ components/ lib/   Next.js 15 (dashboard, UIMap + badge)
```

> Thư mục `_bmad-output/` và `.claude/` chứa tài liệu quy trình phát triển có AI hỗ trợ (đặc tả, ghi chú review) — không bắt buộc để chạy ứng dụng.
