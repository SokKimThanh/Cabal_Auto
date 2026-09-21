# Task 3: Phát triển Component `SkillTimelineStrip`

## Bối cảnh (Context)
Cần thay thế các khung Combobox bằng một dải thanh ngang hiển thị các Icon kỹ năng, mang tính hiện đại và nhỏ gọn hơn.

## Yêu cầu (Requirements)
1. Tạo file `ui/components/skill_timeline_strip.py` định nghĩa class `SkillTimelineStrip`.
2. Component nhận danh sách skill (tên, icon_key, hotkey) và render ngang. BẮT BUỘC có cơ chế Scroll khi vượt quá 8 skill (Max slots), hỗ trợ thao tác kéo thả (Reorder) và Nút Undo để khôi phục vị trí cũ (Chỉ hỗ trợ Undo 1 bước gần nhất - Single-level Undo).
3. Mỗi ô (slot) hiển thị: Icon (trung tâm), Hotkey (ở góc dưới nhỏ), và một viền sáng nếu đang trong thời gian hồi chiêu (Cooldown).
4. Cung cấp API `update_cooldown(skill_name, ratio)` để vẽ một lớp phủ (overlay) xám mờ đè lên Icon tương ứng (mô phỏng đồng hồ hồi chiêu).

## Rủi ro (Risks & Pitfalls)
- **Hiệu năng ảnh (Image Rendering):** Tkinter `PhotoImage` có thể bị garbage collected nếu không giữ reference (tham chiếu). Phải lưu ảnh icon vào một dict nội bộ (`self._images`).
- **Canvas vs Frame:** Lớp phủ hồi chiêu (Cooldown overlay) rất khó làm nếu chỉ dùng `tk.Label`. Bắt buộc mỗi slot nên là một `tk.Canvas` nhỏ để có thể vẽ ảnh, vẽ text, và vẽ hình chữ nhật bán trong suốt chồng lên nhau.

## Unit Tests Cần Thêm (Unit Tests to Add)
- Khởi tạo component với 3 kỹ năng mẫu. Gọi `update_cooldown` và đảm bảo tỷ lệ (ratio) được giới hạn trong khoảng 0.0 - 1.0.
## Hướng dẫn trả Nợ Kỹ Thuật (Technical Debt Paydown)
- **Quản lý Bộ nhớ Ảnh (Image Memory GC):** Khi gỡ bỏ các ô Combobox cũ, hãy đảm bảo rằng Component mới sử dụng cơ chế lưu trữ reference ảnh (như `self._images_ref`) một cách thống nhất. Tuyệt đối không để xảy ra tình trạng "load ảnh mỗi lần render" (gây giật) hoặc "quên giữ reference" (gây mất icon).
