---
name: advanced-elicitation
description: Đẩy LLM soát lại, tinh chỉnh, cải thiện output vừa tạo (story/spec/AC) bằng các method phản biện sâu — pre-mortem, red-team, first-principles, edge-case enumeration, oracle cross-check. Chain tự động sau create-story; cũng dùng khi user muốn critique sâu một artifact.
---

# Skill: advanced-elicitation

Mục tiêu: ép suy nghĩ lại để **lộ giả định ngầm, edge-case, rủi ro số tiền** trong nội dung vừa tạo (thường là story/AC), trước khi dev. Mirror `bmad-advanced-elicitation` của ig.

## Khi được gọi gián tiếp (từ create-story)
1. Nhận nội dung vừa sinh (story file).
2. Áp method phản biện lặp để nâng chất nội dung đó.
3. Khi user chọn `x` → trả bản đã tinh chỉnh, ghi đè story.

## FLOW

### Bước 1 — Smart Selection
- Đọc `methods.csv` (registry). Phân tích ngữ cảnh: loại nội dung (story tài chính?), độ phức tạp, rủi ro tiền tệ, edge-case dữ liệu.
- Chọn **5 method** hợp nhất với ngữ cảnh (mix risk + domain + core). Với story đối soát: ưu tiên Pre-mortem, Edge Case Enumeration, Oracle Cross-Check, Red Team, First Principles.

### Bước 2 — Present Options
```
**Advanced Elicitation — soát story <NN-M>**
Chọn số (1-5), [r] đổi 5 method khác, [a] xem tất cả, [x] xong / không cần nữa:

1. [Method] — <một dòng method làm gì>
2. ...
3. ...
4. ...
5. ...
```

### Bước 3 — Handle Response
- **1-5**: chạy method đó trên story (theo `output_pattern`), nêu phát hiện cụ thể (dẫn chứng AC/dòng dữ liệu), rồi **đề xuất sửa story** (AC mới, định nghĩa rõ hơn, test bổ sung). Hỏi áp dụng không → cập nhật story file. Quay lại Bước 2.
- **r**: chọn 5 method khác.
- **a**: liệt kê toàn bộ method kèm mô tả.
- **x**: dừng, chốt story (đã tinh chỉnh), tiếp tục flow gọi (create-story → ready-for-dev).

## Nguyên tắc
- Mỗi method phải ra **phát hiện cụ thể + đề xuất sửa kiểm chứng được**, không nói chung chung.
- Với story tài chính, luôn kết bằng kiểm `total = Σ thành phần` (Oracle Cross-Check) trước khi cho qua.
- Không tự ý đổi nghiệp vụ — đề xuất, user chốt.
