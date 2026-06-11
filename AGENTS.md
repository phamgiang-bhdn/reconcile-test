# AGENTS.md

Điểm vào cho bất kỳ AI agent nào làm việc trên repo. Đọc `CLAUDE.md` cho chuẩn dự án; file này là bản rút gọn.

## Quy trình BMad (epic → story → review)
1. `/create-epic <tên>` — epic + story (backlog) trong `_bmad-output/planning-artifacts/`.
2. `/create-story NN-M` — story file đầy đủ (AC + oracle) → `ready-for-dev`.
3. `/dev-story NN-M` — TDD: test trước → code theo skill → `review`.
4. `/code-review NN-M` — panel đối kháng (edge-case ∥ bug ∥ correctness) → validation-report → `done`.
5. `/sprint-status` — xem tiến độ.

Trạng thái mọi epic/story ở `_bmad-output/implementation-artifacts/sprint-status.yaml`.

## Bất biến (mọi story)
- Tiền là **số nguyên minor unit** — không float. [ADR-001]
- Ingest **idempotent**: dedupe khóa tự nhiên, không đếm đôi. [ADR-002]
- Giữ record **orphan**; không FK cứng. [ADR-003]
- Không đổi định nghĩa nghiệp vụ trong story mà không cập nhật test + sprint-status.

## Nguồn sự thật
- Cách build chung → `.claude/skills/*` + `_bmad-output/project-context/*`.
- Nghiệp vụ + oracle của một story → story file trong `_bmad-output/implementation-artifacts/`.
- Trạng thái → `sprint-status.yaml`.
