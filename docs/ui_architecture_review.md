# UI Architecture Review & Technical Debt Report

*Đánh giá tổng quan: Dự án có nền tảng kiến trúc khá (đã chia Controller, View, Service, có i18n), nhưng đang xuất hiện các dấu hiệu "phình to". Nếu tiếp tục thêm tính năng theo cách hiện tại thì việc bảo trì sẽ ngày càng khó khăn. Điểm đánh giá: 7.5/10 (Dự án cá nhân) / 6.5/10 (Thương mại).*

## 1. God Class (Lớp App) - Ưu tiên hàng đầu (🔴 Rất cao)

**Thực trạng:** Lớp `App` trong `app_gui.py` dài hơn 3000 dòng.
Nó đang đóng vai trò như một nhân viên phải làm đủ mọi việc: Lễ tân, Kế toán, Bảo vệ, Tài xế, Giám đốc, Nhân viên IT... Lớp `App` hiện đang ôm đồm: quản lý window, state, tạo UI, điều hướng view, xử lý monster, skill, hunt, scan, dialog, i18n, icon cache.

**Hậu quả:** Bất cứ khi nào muốn sửa giao diện, sửa Hunt, sửa Monster hay Language, đều phải mở file `App`. Mọi thứ dồn về một chỗ khiến rủi ro khi sửa đổi là cực kỳ cao.

**Đề xuất:** Đây là vấn đề lớn nhất. Phải chia nhỏ lớp `App` xuống dưới 1000 dòng bằng cách tách thành các phần tử chuyên trách (`AppShell`, `NavigationController`, `WindowStatusController`, v.v.). Khi App nhỏ lại, 50% các vấn đề khác sẽ tự động dễ giải quyết.

## 2. Timer/after phân tán (🔴 Rất cao)

**Thực trạng:** Hàng chục lời gọi `self.after(100, ...)` và `Thread()` nằm rải rác.
Giống như việc thuê rất nhiều đồng hồ báo thức rồi để khắp nhà. Ít thì không sao, nhưng nhiều thì quên tắt, chuông reo liên tục.

**Hậu quả:** Frame bị đóng nhưng Timer vẫn chạy, dẫn đến rò rỉ bộ nhớ (memory leak), timer orphan, hoặc lỗi luồng (race condition).

**Đề xuất:** Xây dựng `TimerManager`, `TaskScheduler` tập trung thay vì để các Frame tự quản lý.

## 3. Service Locator Anti-Pattern (Lạm dụng hasattr/getattr) (🔴 Rất cao)

**Thực trạng:** Code chứa rất nhiều `if hasattr(self, "skill_service")` hoặc `getattr(self, "hunt_selected", {})`.

**Hậu quả:** Code đang nói rằng "Tôi không chắc đối tượng này có skill_service hay không", hoặc "Tôi không biết thuộc tính này có tồn tại không". Đây là dấu hiệu "Object Contract" không rõ ràng, kiến trúc đang mất kiểm soát.

## 4. Hardcoded View Registry (🟠 Cao)

**Thực trạng:** `App` phải ghi nhớ mọi View (HuntView, SetupView, StatsView...).
Giống như một ông giám đốc phải nhớ tên toàn bộ 100 nhân viên trong công ty.

**Đề xuất:** Cần một `ViewRegistry` hoặc `NavigationService` để đứng giữa, giảm độ kết dính (coupling).

## 5. State Management (Quản lý trạng thái UI) (🟠 Cao)

**Thực trạng:** Trạng thái đang bị phân tán: `App` giữ state, `Controller` giữ state, `Frame` giữ state.
Giống như tiền để trong ví, trong túi áo, trong balo, trong ngăn kéo. Muốn biết còn bao nhiêu tiền phải đi kiểm tra khắp nơi.

**Hậu quả:** Sửa một chỗ có thể hỏng chỗ khác, cập nhật state này quên cập nhật state kia.
**Đề xuất:** Gom State về một kho lưu trữ (Store) duy nhất.

## 6. Dialog Service (🟠 Cao)

**Thực trạng:** `messagebox.showinfo()` nằm khắp nơi trong logic.
Giống như mỗi phòng tự mua loa riêng để thông báo. Sau này muốn đổi loa mới (Toast/Popup), phải sửa hàng trăm chỗ.

**Đề xuất:** Đóng gói thành `DialogService`.

## 7. Component Lifecycle (Vòng đời đối tượng và __init__) (🟡 Trung bình)

**Thực trạng:** Tạo thuộc tính (`self.b = []`) bên ngoài `__init__`.
Giống như mua xe rồi mới nhớ ra quên lắp bánh.

**Đề xuất:** Gán trước giá trị (`self.b = None`) trong `__init__`. Đây là lỗi Pylint dễ sửa nhưng không nên ưu tiên bằng các vấn đề kiến trúc phía trên.

---

## Lộ Trình Hành Động (Action Plan) Tóm Tắt

1. **Tách nhỏ God Class (App):** Mục tiêu tối thượng là giảm App xuống < 1000 dòng.
2. **Quản lý Timer/Task tập trung:** Chặn đứng rò rỉ bộ nhớ.
3. **Làm rõ Object Contract:** Loại bỏ `hasattr/getattr` bừa bãi.
4. **Tách View Registry & State:** Tách State và Navigation ra khỏi UI.
5. **Dọn dẹp Lifecycle:** Khởi tạo mọi thứ trong `__init__`.
