# Security & Performance — Toàn dự án

## Bảo mật — checklist
- [ ] SQL **tham số hoá** mọi nơi (`%s` + tuple); không nối chuỗi/f-string vào câu lệnh.
- [ ] Input validate ở biên: kiểu, enum (`status` whitelist), NULL/empty, khoảng trắng thừa, BOM khi đọc file.
- [ ] Credential/secret qua **env**; không hardcode; không commit `.env*`.
- [ ] CORS whitelist origin cụ thể (`CORS_ORIGINS`); không `*` ở prod.
- [ ] Không trả stack trace/SQL ra client — chỉ `{error:{code,message}}`.
- [ ] Không log secret/PII; log dữ liệu tiền ở mức cần để truy vết, không lộ nhạy cảm.
- [ ] File ingest: giới hạn kích thước, kiểm header/cột trước khi parse.

## Hiệu năng — bẫy thường gặp
- **N+1**: không query trong vòng lặp. Lấy entities + source records theo **lô** (mỗi loại 1 query) rồi gộp ở domain bằng dict theo khóa.
- **Index**: cột join/filter (khóa tự nhiên, `status` nếu lọc nhiều) phải có index.
- **Dedupe đúng chỗ**: làm khi ingest (DB `ON CONFLICT`) hoặc một lần ở domain — không lặp lại mỗi request nếu dữ liệu đã sạch ở DB.
- **Tổng hợp**: với tập nhỏ, gộp ở domain (Python) rõ ràng + test được. Tập lớn mới cân nhắc đẩy aggregate xuống SQL — nhưng vẫn phải dedupe trước.
- **Pool**: dùng `ConnectionPool`, đóng connection bằng `with`; không mở/đóng mỗi truy vấn.

## Observability
- Log có cấu trúc; mỗi lần bỏ/sửa dữ liệu (dedupe, vi phạm bất biến) phải log để giải thích con số tổng.
- `GET /health` cho readiness.

## Quy mô hiện tại
Dữ liệu task khởi đầu nhỏ (hàng chục–trăm dòng) → ưu tiên **đúng + rõ + test được** hơn tối ưu sớm. Tối ưu khi có số đo, không đầu cơ.
