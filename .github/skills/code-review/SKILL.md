# Code Review Skill Guide for Copilot AI

## 🎯 Mục tiêu
- Đảm bảo chất lượng code Python & Tkinter trong dự án Cabal Auto Hunt v2.0.
- Giữ chuẩn kiến trúc 3 lớp (Data – Logic – UI).
- Nâng cao trải nghiệm người dùng (UX/UI).
- Hỗ trợ developer bằng feedback ngắn gọn, cụ thể, mang tính xây dựng.

---

## ✅ Checklist Review

### 1. Kiến trúc & Tổ chức
- Code phải tuân thủ kiến trúc 3 lớp:
  - `lib/data/` → Data Access
  - `lib/features/` → Business Logic
  - `ui/windows/`, `ui/components/` → UI Presentation
- Không trộn lẫn logic và UI trong cùng file.

### 2. Python Code Quality
- Dùng **PEP8** và **type hints** đầy đủ.
- Kiểm tra `None` trước khi gọi phương thức/thuộc tính.
- Viết docstring ngắn gọn cho hàm/class quan trọng.

### 3. Tkinter Best Practices
- Luôn gọi `super().__init__(parent)` trước khi tạo `StringVar`.
- Kiểm tra `widget.winfo_exists()` trước khi thao tác widget.
- Không để nhiều dialog trùng nhau (Singleton Dialog).

### 4. UX/UI
- Tiêu đề cửa sổ rõ ràng: `Sửa Quái Vật: {name} (ID: #id)`.
- Tab “Cài đặt” đổi thành **“Hiển thị”**.
- Bỏ nút bánh răng (gear) ở header.
- Phím tắt: `Ctrl+S` để lưu, `Esc` để đóng.
- Thông báo inline bằng `NotificationWidget`, tránh popup gây gián đoạn.

### 5. Logic Dữ liệu
- Kiểm tra trùng tên quái khi lưu:
  - Nếu trùng → hỏi người dùng có muốn thêm số tự động (VD: “Quái (1)”).
  - Nếu từ chối → giữ nguyên để người dùng tự sửa.
- Sử dụng `monster_service.py` (`check_duplicate_name`, `generate_unique_name`).

### 6. Testing
- Unit test đầy đủ cho:
  - Logic xử lý trùng tên.
  - Luồng mở/sửa/lưu quái.
  - Phím tắt và singleton dialog.
- Tất cả test phải **PASS**.

---

## 💡 Cách Copilot AI phản hồi khi review
- **Ngắn gọn, cụ thể**: chỉ ra file/hàm/dòng liên quan.
- **Mang tính gợi ý**: đưa ra cách sửa hoặc cải thiện.
- **Thân thiện**: dùng giọng điệu hỗ trợ, không phán xét.
- **Ưu tiên lỗi nghiêm trọng trước**: bug, crash → sau đó mới đến style.

---

## 📚 Tài liệu & Ghi chú
- Ghi lại bài học kỹ thuật vào `.jules/palette.md`.
- Luôn cập nhật checklist khi có thay đổi trong dự án.
