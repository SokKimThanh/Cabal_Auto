# Kế Hoạch Sprint 32 - Chuẩn Hóa Dữ Liệu và Translation Key

Dựa trên Báo cáo Đánh giá tính khả thi (`sprint32_report.md`), Sprint 32 sẽ được thực hiện thông qua các phiên độc lập (dưới 30 phút). Lộ trình chi tiết:

## Mục tiêu
Dọn dẹp triệt để các văn bản cứng (hardcoded text) nằm rải rác ở tầng UI. Chuẩn hóa toàn bộ thành định dạng Metadata `text_key` và `tooltip_key`.

## Các Bước Triển Khai (Các phiên Prompt)
*Các file prompt chi tiết nằm trong thư mục `prompt-localization-driven-ui/`*

- **Phiên 1 (Prompt 001):** Khởi tạo từ điển chuẩn (Translation Dictionary Template). Rà soát và định nghĩa bộ Key chuẩn (`btn.*`, `lbl.*`, `col.*`, `tab.*`).
- **Phiên 2 (Prompt 002):** Refactor các nhãn dán (Labels) và nút bấm (Buttons) trên các khung quản lý dữ liệu chính (Manager Frames: `build_manager_frame.py`, `class_manager_frame.py`, ...).
- **Phiên 3 (Prompt 003):** Refactor toàn bộ tiêu đề cột (Treeview Headings) ở các Manager Frames và Tabs.
- **Phiên 4 (Prompt 004):** Refactor các văn bản động và ký hiệu Text trên các Panels (Target, Skill, Stats, Setup). Thay thế việc gắn chữ "1 / 1", "—" thành cơ chế dùng key dịch thuật chứa tham số.
- **Phiên 5 (Prompt 005):** Kiểm tra và tích hợp `TranslationBinder` (nếu cần) vào các điểm vừa refactor để đảm bảo việc bind sự kiện đổi ngôn ngữ hoạt động không lỗi.

## Rủi Ro Cần Lưu Ý
- Do đang thay đổi rất nhiều hiển thị Text bằng Key, một số giao diện có thể hiển thị mã key chưa dịch nếu từ điển chưa hoàn thiện. (Sẽ có fallback language hoặc cảnh báo thiếu từ khóa).
- Cần chú ý các text liên quan đến các biểu tượng (như "➕", "✓") không nên ép vào hệ thống translation nếu chúng thực chất là biểu tượng (nên chuyển sang Icon Key sau này).
