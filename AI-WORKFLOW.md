# Quy trình phát triển có AI hỗ trợ (có kiểm soát)

Tài liệu này mô tả **cách tôi dùng AI để xây dự án mà vẫn kiểm soát chất lượng** — phần đề bài quan tâm: *"làm việc cùng AI một cách có kiểm soát (review & verify trước khi tin)"*.

Nguyên tắc: **không để AI tự sinh code rồi tin ngay**. Tôi tự dựng một bộ **đặc tả AI** (các file chỉ thị/chuẩn mực ở dưới) để AI bám theo, và mỗi tính năng đi qua quy trình cố định: đặc tả → test trước → AI review đối kháng → kiểm chứng số liệu.

---

## 1. Các file đặc tả AI (mở ra xem)

Đây là phần cốt lõi — những file **cấu hình & chỉ thị cho AI**, không phải code chạy. Người chấm mở trực tiếp để thấy AI được điều khiển thế nào:

### Chỉ thị toàn dự án
- [`CLAUDE.md`](CLAUDE.md) — chỉ thị chính cho AI: stack, quy ước, luật tiền tệ, quy trình.
- [`AGENTS.md`](AGENTS.md) — điểm vào rút gọn cho bất kỳ AI agent nào tiếp nhận dự án.

### Chuẩn code AI phải tuân (`.claude/skills/`)
- [`engineering-standards`](.claude/skills/engineering-standards/SKILL.md) — kiến trúc phân lớp, luật dữ liệu tài chính, error model, anti-pattern.
- [`backend-fastapi`](.claude/skills/backend-fastapi/SKILL.md) · [`data-postgres`](.claude/skills/data-postgres/SKILL.md) · [`frontend-nextjs`](.claude/skills/frontend-nextjs/SKILL.md) — convention từng tầng (kèm code mẫu, anti-pattern).

### Quy trình AI (`.claude/skills/`)
- [`create-story`](.claude/skills/create-story/SKILL.md) · [`dev-story`](.claude/skills/dev-story/SKILL.md) · [`code-review`](.claude/skills/code-review/SKILL.md) · [`advanced-elicitation`](.claude/skills/advanced-elicitation/SKILL.md) · [`sprint-status`](.claude/skills/sprint-status/SKILL.md) — các bước trong vòng đời một tính năng.

### Reviewer đối kháng (`.claude/agents/`)
- [`edge-case-hunter`](.claude/agents/edge-case-hunter.md) — truy tình huống dữ liệu chưa xử lý.
- [`bug-hunter`](.claude/agents/bug-hunter.md) — săn bug lập trình.
- [`correctness-reviewer`](.claude/agents/correctness-reviewer.md) — đối chiếu từng acceptance criteria + bất biến tiền tệ.

### Quyết định kiến trúc & bối cảnh (`_bmad-output/project-context/`)
- [`architecture.md`](_bmad-output/project-context/common/architecture.md) — các ADR (tiền nguyên, khử trùng, orphan-safe, response contract).
- [`index.md`](_bmad-output/project-context/index.md) — chỉ mục + quy tắc nhanh.

## 2. Quy trình một tính năng

```
tạo story (create-story)        → đặc tả + acceptance criteria + con số kỳ vọng (oracle)
  ↓ advanced-elicitation         → ép AI tự soi lại đặc tả tìm lỗ hổng TRƯỚC khi code
dev (dev-story, TDD)            → test trước (gồm test khóa con số tổng) → implement
review đối kháng (code-review)  → 3 agent AI độc lập soi bug/edge-case song song
  ↓ sửa theo finding
kiểm chứng                      → chạy test + docker thật, đối chiếu số liệu → done
```

Mỗi story có **đặc tả** (acceptance criteria + checklist công việc) và **báo cáo review** riêng trong `_bmad-output/implementation-artifacts/`. Ví dụ mở xem:
- Đặc tả: [`1-1-reconciliation-dashboard.md`](_bmad-output/implementation-artifacts/1-1-reconciliation-dashboard.md)
- Báo cáo review: [`1-1-validation-report.md`](_bmad-output/implementation-artifacts/1-1-validation-report.md)
- Trạng thái mọi story: [`sprint-status.yaml`](_bmad-output/implementation-artifacts/sprint-status.yaml)

## 3. Kiểm soát hoạt động thế nào — bằng chứng

Khâu **AI review đối kháng** bắt được bug thật **trước khi merge** (chi tiết trong các `*-validation-report.md`):

- **Xuất Excel sai hiển thị tỉ lệ** — ghi `0.8846` thay vì `88.46%`. → sửa định dạng ô phần trăm.
- **Khóa chống trùng thiếu cột `platform`** — đa sàn có cùng (mã đơn, ngày, tiền) sẽ bị khử trùng nhầm, **mất một dòng tiền**. → đưa `platform` vào khóa tự nhiên.
- **Tổng tiền bỏ sót đơn mồ côi** — thiếu `69.811 ₫`. → tính tổng gồm cả đơn mồ côi.
- **Ép kiểu nuốt trạng thái lạ** thành "—", mất thông tin. → fallback hiển thị giá trị gốc.

Mỗi con số tiền được **kiểm chứng độc lập** với CSV gốc và đối chiếu lại qua API `/kpi` khi chạy thật. Self-check `Σ net_received = 1.615.756 ₫` giữ nguyên qua mọi thay đổi (kể cả khi đổi schema/đổi công cụ migration).

## 4. Phạm vi

4 tính năng: dashboard đối soát · xuất Excel · hỗ trợ đa sàn · hoàn thiện UI. **Dashboard là phần cốt lõi của đề**; ba phần còn lại minh hoạ mở rộng an toàn trên cùng codebase qua đúng quy trình trên — mỗi cái đều có đặc tả, review và kiểm chứng riêng.
