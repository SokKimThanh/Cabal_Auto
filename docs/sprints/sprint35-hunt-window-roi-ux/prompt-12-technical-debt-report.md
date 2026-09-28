# Prompt 12 — Báo cáo technical debt & tổng kết Sprint 35

## Mục tiêu
Tổng hợp kết quả 11 prompt, ghi nhận nợ còn lại, đề xuất Sprint 36.

## Phạm vi
- Tạo file: `docs/sprints/sprint35-hunt-window-roi-ux/final-report.md`.
- KHÔNG SỬA CODE.

## Công việc
1. Tổng hợp từ `audit-01` → `audit-05`.
2. Liệt kê:
   - Đã fix: (list prompt 06–11).
   - Chưa fix / còn nợ: (từ ô UNKNOWN của prompt-04).
   - Rủi ro còn lại: multi-monitor, DPI scaling, capture latency.
3. Đề xuất Sprint 36:
   - Auto-detect DPI scaling.
   - Multi-monitor support.
   - Auto-tune threshold cho skills detection.
4. Chạy toàn bộ test suite liên quan:
   ```bash
   pytest tests/integration/vision/ tests/unit/features/hunt/ -v
   ```

## Output
- File `final-report.md` với các mục trên.
- Danh sách commit hash của cả 11 prompt.
- Xác nhận tất cả test pass.

## Commit
```
docs(sprint35): final report and technical debt registry
```
