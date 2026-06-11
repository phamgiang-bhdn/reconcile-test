---
name: sprint-planning
description: Sinh/đồng bộ file sprint-status.yaml từ toàn bộ epic trong _bmad-output/planning-artifacts/ — liệt kê mọi epic + story với trạng thái hiện tại, định nghĩa status, thứ tự ưu tiên. Dùng khi user nói "sprint planning", "tạo sprint status", hoặc sau khi thêm nhiều epic.
---

# Skill: sprint-planning

Tạo hoặc làm mới `_bmad-output/implementation-artifacts/sprint-status.yaml` — nguồn sự thật về trạng thái mọi epic/story.

## Các bước
1. Quét `_bmad-output/planning-artifacts/epics-*.md`, lấy danh sách epic + story.
2. Với mỗi story, giữ status hiện có trong sprint-status.yaml nếu đã có; story mới → `backlog`.
3. Ghi lại file theo template; thêm dòng `# last_updated` mô tả thay đổi.

## Template sprint-status.yaml
```yaml
# last_updated: "<ngày>" # <mô tả ngắn>
project: <tên dự án>
tracking_system: file-system
story_location: _bmad-output/implementation-artifacts

# STATUS DEFINITIONS
# Epic:  backlog | in-progress | done
# Story: backlog | ready-for-dev | in-progress | review | done   (+ split, deferred)
# Retro: optional | done

development_status:
  # Epic 1: <tên>
  epic-1: in-progress
  1-1-<slug>: review
  epic-1-retrospective: optional

  # Epic 2: <tên>
  epic-2: backlog
  2-1-<slug>: backlog
```

## Quy ước
- Thứ tự trong file = thứ tự ưu tiên; story nào dev trước để trên.
- Không xoá lịch sử: status cũ đổi thì cập nhật giá trị + thêm dòng `# last_updated`.
- Đây là file người + máy cùng đọc; giữ comment epic-header để dễ quét.
