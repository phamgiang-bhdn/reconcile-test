---
name: code-review
description: Review một story bằng panel ĐỐI KHÁNG song song (edge-case-hunter ∥ bug-hunter ∥ correctness-reviewer), hợp nhất finding, fix BLOCK, ghi validation-report, rồi chuyển story sang done. Dùng khi user nói "code review", "review story NN-M", "soát story".
---

# Skill: code-review

Cổng chất lượng cuối của pipeline — 3 lớp review đối kháng độc lập (kiểu blind/edge/auditor của ig), không khen, cố làm vỡ.

## Inputs
- ID story `NN-M` (mặc định story đang `review` trong sprint-status).

## Các bước
1. Đọc story (AC + oracle) + diff/code liên quan + dữ liệu nguồn.
2. Chạy **song song** 3 subagent (gửi cùng một message để chạy đồng thời), mỗi agent một góc độc lập:
   - `edge-case-hunter` — tình huống dữ liệu/biên chưa xử lý.
   - `bug-hunter` — bug lập trình trong code.
   - `correctness-reviewer` — đối chiếu từng AC + bất biến tiền tệ + oracle.
   Mỗi agent nhận: đường dẫn story, file code, dữ liệu nguồn; bắt buộc dẫn chứng file:dòng + dữ liệu cụ thể, cấm bịa.
3. **Hợp nhất & khử trùng** finding → gom `BLOCK` / `WARN` / `NOTE`.
4. Với mỗi `BLOCK`: xác minh nhanh (đọc code/chạy test) rồi **fix**.
5. Ghi `_bmad-output/implementation-artifacts/NN-M-validation-report.md`:
   - bảng AC (claim vs code, PASS/BLOCK)
   - danh sách finding + cách xử lý (applied/deferred + lý do)
   - lệnh + số đã verify oracle
6. Nếu hết `BLOCK` và oracle khớp → cập nhật sprint-status `NN-M-*: done` (+ dòng `# last_updated` ghi "CODE REVIEW DONE: 3 adversarial layers, N ACs PASS, k findings applied"). Còn `BLOCK` → giữ `review`.

## Nguyên tắc
- 3 lớp phải **độc lập** (đừng để agent đọc kết luận của nhau trước khi tự soát).
- Finding ngoài scope story = `NOTE`, không chặn merge.
- "Review xong" chỉ tính trong scope story đang soát.
