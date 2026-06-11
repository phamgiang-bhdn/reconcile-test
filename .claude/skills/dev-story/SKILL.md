---
name: dev-story
description: Implement một story ready-for-dev theo TDD và skill convention, rồi chuyển story sang review. Dùng khi user nói "dev story NN-M", "implement story", "code story tiếp theo".
---

# Skill: dev-story

Thực thi một story đã `ready-for-dev`. Spec-first: story là hợp đồng; bám AC, không thêm ngoài scope.

## Inputs
- ID story `NN-M`. Không nêu → lấy story `ready-for-dev` đầu tiên trong sprint-status.

## Các bước
1. Đọc story `_bmad-output/implementation-artifacts/NN-M-*.md` (AC + oracle + affected layers).
2. Đọc skill stack liên quan (`backend-fastapi`, `data-postgres`, `frontend-nextjs`) + `engineering-standards` + project-context.
3. Cập nhật sprint-status: `NN-M-*: in-progress` (+ dòng `# last_updated`).
4. **TDD**: viết test logic lõi TRƯỚC, gồm **test oracle** chốt con số tổng của story. Test phải đỏ trước khi có implementation.
5. Implement theo phân lớp: domain thuần (test được, không DB) → migration/seed → tầng web → UI. **Tick `Tasks / Subtasks`** `- [x]` trong story file khi xong từng task.
6. Giữ mọi bất biến tài chính (F1–F5). Không nhét nghiệp vụ vào handler; SQL tham số hoá.
7. Chạy test tới xanh; đối chiếu oracle.
8. **Điền `Dev Agent Record`** trong story file: Agent Model Used, Completion Notes List, **File List** (mọi file tạo/sửa). Đổi `Status: review`; cập nhật sprint-status `NN-M-*: review` + ô Status trong epic. Báo cáo file đã tạo/sửa + trạng thái test.
9. Tiếp theo: chạy `/code-review NN-M`.

## Ràng buộc
- KHÔNG mở rộng scope ngoài AC. Phát sinh ngoài scope → ghi vào epic làm story mới, không làm lén.
- KHÔNG đổi định nghĩa nghiệp vụ trong story mà không cập nhật test + status.
- Diff gọn; không comment thừa; không nhét mã story vào source.
