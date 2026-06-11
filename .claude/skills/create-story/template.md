# Story {{epic_num}}.{{story_num}}: {{story_title}}

Status: ready-for-dev

## Story

Là {{role}},
tôi muốn {{action}},
để {{benefit}}.

## Acceptance Criteria

<!-- Đánh số, BDD Given/When/Then, kiểm chứng được. Task tài chính bắt buộc có AC oracle. -->
1. **Given** ... **When** ... **Then** ...
2. ...

## Tasks / Subtasks

<!-- Checklist thực thi, mỗi task map vào AC (AC: #). Dev-story tick dần khi làm. -->
- [ ] Task 1 — ... (AC: #1)
  - [ ] Subtask 1.1
  - [ ] Subtask 1.2
- [ ] Task 2 — ... (AC: #2, #3)
  - [ ] Subtask 2.1
- [ ] Task N — Viết test (test/nhánh + dedupe + **test oracle**) (AC: #N)

## Dev Notes

- Kiến trúc/luật áp dụng: phân lớp domain→repo, ADR-001/002/003, skill liên quan.
- Bẫy dữ liệu + định nghĩa nghiệp vụ (status/công thức/dấu) — RIÊNG story này.
- **Oracle** (con số tổng kỳ vọng) + bất biến chéo.
- Out of scope.

### Project Structure Notes

- Khớp layout chuẩn (`backend/app/domain/<f>`, `app/api/<f>`, `repositories/`, `frontend/...`).
- Lệch/biến thể (nếu có) + lý do.

### References

- [Source: _bmad-output/project-context/index.md]
- [Source: _bmad-output/project-context/common/architecture.md#ADR-...]
- [Source: _bmad-output/planning-artifacts/epics-{{epic_num}}-*.md#Story {{epic_num}}-{{story_num}}]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
