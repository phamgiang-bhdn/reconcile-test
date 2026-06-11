---
name: sprint-status
description: In bảng trạng thái sprint (status print) từ sprint-status.yaml — tổng hợp mỗi epic và story kèm trạng thái, đếm done/review/in-progress/backlog, nêu story tiếp theo nên làm. Dùng khi user nói "sprint status", "show status", "tiến độ tới đâu rồi".
---

# Skill: sprint-status

Đọc `_bmad-output/implementation-artifacts/sprint-status.yaml` và in tóm tắt trạng thái cho người đọc. Read-only — KHÔNG sửa file, KHÔNG code.

## Các bước
1. Đọc `sprint-status.yaml` → parse `development_status`.
2. Nhóm theo epic; với mỗi epic in các story + status (emoji).
3. Đếm tổng theo status; nêu **story tiếp theo** (story `ready-for-dev` đầu tiên, hoặc `backlog` nếu không có).

## Format in ra
```
Sprint Status — <project>  (cập nhật <last_updated>)

Epic 1 — <tên>  [in-progress]
  ✅ 1-1 <slug>            done
  🔍 1-2 <slug>            review
  🛠️ 1-3 <slug>            in-progress
  📝 1-4 <slug>            ready-for-dev
  ⏳ 1-5 <slug>            backlog

Tổng: ✅ done X · 🔍 review Y · 🛠️ in-progress Z · 📝 ready W · ⏳ backlog V
→ Tiếp theo: <story ready-for-dev đầu tiên> (chạy /dev-story <id>)
```

Map emoji: done ✅ · review 🔍 · in-progress 🛠️ · ready-for-dev 📝 · backlog ⏳ · split ➗ · deferred ⏸️ · optional ◽
