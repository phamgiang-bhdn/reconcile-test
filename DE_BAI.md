# Bài test kỹ thuật — Mini Reconciliation Dashboard

Chào bạn, cảm ơn bạn đã ứng tuyển! Đây là một bài test nhỏ, sát với công việc thực tế của tụi mình (đối soát đơn sàn TMĐT).

- **Thời lượng:** ~60 phút.
- **Được dùng AI coding** (Claude Code / Cursor / Copilot…) thoải mái. Tụi mình khuyến khích — nhưng bạn phải **tự giải thích được code** khi phỏng vấn.
- **Stack:** Backend dùng **FastAPI (Python)** hoặc **Node/NestJS** (bạn tự chọn) · Frontend **Next.js** · Database **PostgreSQL**.

---

## 1. Bối cảnh

Một shop bán hàng trên sàn TMĐT. Mỗi kỳ, sàn gửi về **file thanh toán** (income) ghi số tiền thực nhận cho từng đơn. Nhiệm vụ: **đối soát** file đơn hàng với file thanh toán, rồi hiển thị **dashboard KPI** + bảng kết quả.

Bạn nhận được 2 file (đính kèm):

### `orders.csv` — danh sách đơn hàng

| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `order_code` | text | Mã đơn (khóa chính) |
| `platform` | text | Sàn (shopee) |
| `status` | text | `completed` / `cancelled` |
| `product_price` | số nguyên (VND) | Giá trị hàng |
| `order_date` | ngày | Ngày đặt |

### `income.csv` — tiền sàn thanh toán

| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `order_code` | text | Mã đơn (liên kết với orders) |
| `settlement_date` | ngày | Ngày thanh toán |
| `gross_revenue` | số nguyên (VND) | Giá sản phẩm |
| `refund_amount` | số nguyên (VND) | Tiền hoàn (số âm nếu có) |
| `fee_total` | số nguyên (VND) | Tổng phí sàn (số âm) |
| `net_received` | số nguyên (VND) | Tiền thực về ví |

> Quan hệ: `net_received = gross_revenue + refund_amount + fee_total`.
> ⚠️ Tiền là VND (không có phần lẻ) — hãy lưu bằng kiểu **NUMERIC/INTEGER**, không dùng float.

---

## 2. Yêu cầu

### MUST (bắt buộc)

1. **Migration / schema** PostgreSQL cho 2 bảng `orders` và `income_settlements`, import dữ liệu từ 2 file.
2. **API `GET /reconciliation`** — trả về mỗi đơn kèm `reconcile_status`, gồm 4 loại:
   - `matched` — đơn `completed` có thanh toán, không hoàn tiền
   - `refunded` — đơn `completed` có thanh toán, có hoàn tiền (`refund_amount < 0`)
   - `orphan` — có dòng thanh toán nhưng **không có** đơn tương ứng trong `orders`
   - `unsettled` — đơn tồn tại nhưng **chưa có** thanh toán
3. **API `GET /kpi`** — trả về JSON:
   `{ total_gross, total_net, total_fees, reconciliation_rate, refund_count, refund_total }`

### SHOULD (nên có)

4. **Trang Next.js**: các KPI card + bảng đơn hàng có **lọc theo trạng thái**.
5. **Ít nhất 1 test** cho hàm đối soát.

### BONUS (điểm cộng)

6. Xử lý gọn gàng các **trường hợp đặc biệt** trong dữ liệu (gợi ý: dữ liệu thật thường không "sạch").
7. File **`README.md`** ghi: cách chạy (backend/frontend/DB) + một đoạn ngắn **"AI đã sinh code sai chỗ nào và bạn phát hiện/sửa thế nào"**.
8. (Tuỳ chọn) Kèm file **`CLAUDE.md` hoặc `AGENTS.md`** mô tả repo để một AI agent khác có thể tiếp tục dự án.

---

## 3. Tự kiểm tra (self-check)

Nếu xử lý dữ liệu đúng, tổng tiền thực nhận của bạn phải khớp:

> **Σ `net_received` = 1.615.756 ₫**

Nếu con số của bạn lệch số này → có khả năng còn sót một tình huống dữ liệu chưa xử lý đúng. (Đây là gợi ý để bạn tự đối chiếu, không phải để hard-code.)

---

## 4. Bàn giao

Vui lòng nộp **link repo Git (public)** hoặc file **`.zip`**, gồm:

- Source code (backend + frontend) + file migration/SQL.
- `README.md`: hướng dẫn chạy + ghi chú phần AI (mục 7).
- Lệnh chạy test (nếu có).

Khi phỏng vấn, bạn sẽ được hỏi để **giải thích code của chính mình** — nên dù dùng AI, hãy đảm bảo bạn hiểu rõ những gì đã viết.

---

## 5. Tụi mình đánh giá gì

Không chỉ "chạy được". Tụi mình quan tâm: **tính đúng của số liệu tiền tệ**, cách bạn **xử lý các tình huống dữ liệu thực tế**, chất lượng thiết kế API/DB, và đặc biệt là cách bạn **làm việc cùng AI một cách có kiểm soát** (review & verify trước khi tin).

Chúc bạn làm bài vui vẻ! Có gì chưa rõ cứ hỏi tụi mình nhé.
