# Task 5: Áp dụng Animation & Font Mono cho Target Status và Stats

## Bối cảnh (Context)
Làm cho hiển thị các con số mượt mà, chuyên nghiệp hơn, giảm hiện tượng giật cục (jitter) khi săn.

## Yêu cầu (Requirements)
1. Trong `ui/panels/target_status_panel.py`:
   - Hàm `_on_target_hp_updated`: Không cập nhật tọa độ Canvas HP/MP ngay lập tức. Chỉ nội suy (tweening) THANH BAR đồ họa bằng `UIAnimationManager` (để mượt mắt). CON SỐ TEXT HP phải được cập nhật tức thời (instant) để đảm bảo không bị sai lệch dữ liệu với màn hình game.
   - Thay đổi font của Label hiển thị HP, MP, Defense sang dùng `UIStyleV2.resolve_font_family("mono")` để chữ có độ rộng bằng nhau (Monospaced).

2. Trong `ui/panels/skill_stats_panel.py`:
   - GIỮ NGUYÊN cấu trúc `Treeview` (cấm đổi sang list frame) để đảm bảo hiệu năng. Giới hạn tần suất refresh dữ liệu (ví dụ 1s/lần) và giới hạn lưu trữ tối đa 50 bản ghi.
   - Cột `success_rate` hiển thị số `%` căn đều bằng font mono. KHÔNG dùng Unicode progress bar vì Treeview không hỗ trợ custom cell render và Unicode block render không nhất quán giữa các OS.

## Rủi ro (Risks & Pitfalls)
- **Animation Queue:** Nếu quái vật mất máu liên tục (nhanh hơn tốc độ 200ms animation), hàm nội suy phải cập nhật điểm mục tiêu (target width) mới ngay lập tức chứ không xếp hàng (queue) sinh ra hiệu ứng chạy ngược hoặc chạy chậm trễ so với thực tế (ghosting).
- **Crashes:** Gọi Canvas coords trong lúc tab đã bị đóng (destroyed) sẽ văng lỗi `_tkinter.TclError`. Cần kiểm tra `self.winfo_exists()` trước khi thay đổi UI trong callback của `UIAnimationManager`.

## Unit Tests Cần Thêm (Unit Tests to Add)
- (Khó test tự động phần animation), nhưng cần test xem hàm helper update target value có ném lỗi khi object đã bị hủy hay không.
## Phụ lục (Important Note from Review):
- **Đối với Skill Stats:** File `ui/panels/skill_stats_panel.py` hiện tại *chưa* có logic subscribe event `SkillStatsUpdatedEvent`! Bạn cần thêm phương thức `_bind_events` (như cách làm của TargetStatusPanel), nhận dữ liệu từ `EventBus` (Event `SkillStatsUpdatedEvent` được publish từ vòng lặp chính của `HuntOrchestrator`, payload `all_stats` bao gồm `cast_count`, `last_cast`, `success_rate`) rồi loop qua để `tree.insert()` hoặc `tree.item()` update cho Treeview, lúc đó mới dùng format text % với font mono để vẽ giá trị `success_rate`.
- **Đối với Animation Tween:** Scanner bắn HP event bằng hàm `time.sleep` trung bình 100-200ms mỗi khung hình. Hãy đăng ký với `UIAnimationManager` để animate sự chênh lệch máu giữa 2 lần quét mà không gây lag.

## Hướng dẫn trả Nợ Kỹ Thuật (Technical Debt Paydown)
- **Quy tụ Logic Nội Suy (Tweening):** Tìm và xóa mọi đoạn code gọi `self.after()` liên quan đến hiệu ứng đồ họa bên trong `TargetStatusPanel`. Thay vào đó, gọi method từ `UIAnimationManager`. Việc này để đảm bảo rằng khi có quá nhiều thông tin cập nhật máu, hệ thống tự động ghi đè (cancel/override) animation cũ chứ không sinh ra hàng chục luồng chạy ngầm gây lag.
