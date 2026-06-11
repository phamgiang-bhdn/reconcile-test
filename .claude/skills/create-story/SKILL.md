---
name: create-story
description: Tạo story file chi tiết (ready-for-dev) từ một story đang ở backlog trong epic, theo chuẩn BMad — file trong _bmad-output/implementation-artifacts/ với Status, Context, định nghĩa nghiệp vụ, AC Given/When/Then, Affected layers, Oracle, Test plan, rồi cập nhật sprint-status (story → ready-for-dev, epic → in-progress). Dùng khi user nói "tạo story", "create story NN-M", "story tiếp theo".
---

# Skill: create-story

Biến một dòng story ở backlog (trong epic) thành **story file đầy đủ context** để dev implement không phải hỏi lại. Đây là spec-first gate của pipeline.

## Inputs
- ID story `NN-M` (epic NN, story M). Nếu user không nêu → đọc sprint-status, lấy story `backlog` tiếp theo của epic đang `in-progress`.

## Các bước
1. Đọc epic `_bmad-output/planning-artifacts/epics-NN-*.md` lấy bối cảnh + AC nháp của story.
2. Đọc `_bmad-output/project-context/index.md` + skill liên quan (chuẩn dự án) + dữ liệu nguồn nếu có (thống kê thật: số dòng, trùng, orphan, âm…).
3. Viết `_bmad-output/implementation-artifacts/NN-M-<slug>.md` theo template.
4. **Chain `advanced-elicitation`** trên story vừa viết (BẮT BUỘC, như ig): smart-select 5 method phản biện, present menu, áp method user chọn để lộ giả định ngầm/edge-case/rủi ro số tiền → cập nhật story. Lặp tới khi user chọn `x`. Với story tài chính phải qua Oracle Cross-Check trước khi chốt.
5. Cập nhật `sprint-status.yaml`: `NN-M-<slug>: ready-for-dev`; nếu epic đang `backlog` → đổi `epic-NN: in-progress`.
6. Cập nhật ô Status của story trong file epic → `📝 Ready for dev`.
7. KHÔNG code.

## Template story file
Dùng `./template.md` (cùng thư mục skill) — khuôn chuẩn ig. Các mục bắt buộc:
- **Status:** `ready-for-dev`.
- **Story:** Là <vai trò> / tôi muốn / để.
- **Acceptance Criteria:** đánh số, BDD Given/When/Then, kiểm chứng được. Phủ: schema/migration, ingest+dedupe, từng endpoint, UI, test, **oracle**.
- **Tasks / Subtasks:** ⭐ checklist `- [ ]` thực thi, **mỗi task map vào AC** `(AC: #)`, có subtask. Dev-story tick dần. Task cuối luôn là "Viết test (test/nhánh + dedupe + test oracle)".
- **Dev Notes:** luật/ADR áp dụng, bẫy dữ liệu + định nghĩa nghiệp vụ (status/công thức/dấu), **Oracle** + bất biến chéo, out of scope. Kèm `### Project Structure Notes` + `### References` ([Source: ...]).
- **Dev Agent Record:** để trống (Agent Model / Debug Log / Completion Notes / File List) — dev-story điền khi implement.

## Status flow (đồng bộ sprint-status.yaml)
`backlog → ready-for-dev` (skill này) `→ in-progress` (dev bắt đầu) `→ review` (dev xong) `→ done` (review pass).
Mỗi lần đổi status, ghi 1 dòng `# last_updated` ở đầu sprint-status.yaml mô tả ngắn thay đổi.
