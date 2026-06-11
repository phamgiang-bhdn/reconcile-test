---
name: create-epic
description: Tạo một epic mới cho dự án theo chuẩn BMad — file epic trong _bmad-output/planning-artifacts/ với Overview + Progress Snapshot + danh sách story (backlog) + AC Given/When/Then, rồi đăng ký epic + stories vào sprint-status.yaml ở trạng thái backlog. Dùng khi user nói "tạo epic", "thêm epic", hoặc bắt đầu một mảng tính năng mới.
---

# Skill: create-epic

Tạo epic theo đúng layout ig/BMad. Epic = nhóm story cùng một mảng nghiệp vụ. Đối soát là story của epic-1; epic sau cứ đánh số tăng dần.

## Inputs cần làm rõ trước khi viết
- Tên/mục tiêu epic (1 câu).
- Các story dự kiến (mỗi story 1 dòng mô tả) — chưa cần chi tiết, để backlog.
- Số epic kế tiếp: đọc `_bmad-output/planning-artifacts/` lấy `NN` lớn nhất + 1.

## Các bước
1. Đọc `_bmad-output/project-context/index.md` (chuẩn dự án) để epic bám đúng kiến trúc/luật.
2. Tạo `_bmad-output/planning-artifacts/epics-NN-<slug>.md` theo template dưới.
3. Cập nhật `_bmad-output/implementation-artifacts/sprint-status.yaml`:
   - thêm `epic-NN: backlog`
   - thêm mỗi story `NN-M-<slug>: backlog`
   - thêm `epic-NN-retrospective: optional`
4. KHÔNG viết code. KHÔNG tạo story file chi tiết (đó là việc của `create-story`).

## Template epic
```markdown
---
stepsCompleted: ['step-02-design-epics']
inputDocuments:
  - <nguồn: chat/đề bài/meeting ngày ...>
---

# Epic NN — <Tên>

## Overview
<2-4 câu: mảng nghiệp vụ này giải quyết gì, khác epic khác chỗ nào, OPEN hay đóng.>

## Progress Snapshot (cập nhật <ngày>)
| Story | Trạng thái | Notes |
|---|---|---|
| NN-1 — <tên> | ⏳ Backlog | <1 dòng> |
| NN-2 — <tên> | ⏳ Backlog | <1 dòng> |

## Story NN-1 — <tên>
**Status:** ⏳ Backlog
**Context:** <bối cảnh + bẫy dữ liệu nếu có>
**Acceptance:**
**Given** <tiền đề> **When** <hành động> **Then** <kết quả kiểm chứng được>
... (mỗi AC một khối Given/When/Then)
**Affected layers / files:**
| Tầng | Change |
|---|---|
| DB | ... |
| Backend | ... |
| Frontend | ... |
**Oracle (nếu task tài chính):** <con số tổng kỳ vọng>

---
## Story NN-2 — <tên>
...
```

## Quy ước
- Epic mở (OPEN) thì ghi rõ "append story mới khi phát sinh".
- AC viết Given/When/Then, kiểm chứng được; task tài chính bắt buộc có **Oracle**.
- Status transition: epic `backlog → in-progress` tự động khi story đầu tiên được `create-story`.
