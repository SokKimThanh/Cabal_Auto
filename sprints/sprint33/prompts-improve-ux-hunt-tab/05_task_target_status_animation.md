# Task 5: Áp dụng Animation & Font Mono cho Target Status và Stats

## Bối cảnh (Context)
Làm cho hiển thị các con số mượt mà, chuyên nghiệp hơn, giảm hiện tượng giật cục (jitter) khi săn.

## Yêu cầu (Requirements)
1. Trong `ui/panels/target_status_panel.py`:
   - Hàm `_on_target_hp_updated`: Không cập nhật tọa độ Canvas HP/MP ngay lập tức. Hãy viết một helper function (hoặc đăng ký với UIAnimationManager) để nội suy (interpolate) từ vị trí cũ tới vị trí mới trong ~200ms.
   - Thay đổi font của Label hiển thị HP, MP, Defense sang dùng `UIStyleV2.resolve_font_family("mono")` để chữ có độ rộng bằng nhau (Monospaced).
   - Thêm trạng thái nhấp nháy đỏ khi máu dưới 20%.
2. Trong `ui/panels/skill_stats_panel.py`:
   - Nếu có thể, hãy vẽ một đoạn mã hex Unicode progress bar (ví dụ: `[██████░░░░]`) để đại diện cho cột `success_rate` thay vì chỉ để số `%`. Hoặc dùng Font Monospace để canh đều.

## Rủi ro (Risks & Pitfalls)
- **Animation Queue:** Nếu quái vật mất máu liên tục (nhanh hơn tốc độ 200ms animation), hàm nội suy phải cập nhật điểm mục tiêu (target width) mới ngay lập tức chứ không xếp hàng (queue) sinh ra hiệu ứng chạy ngược hoặc chạy chậm trễ so với thực tế (ghosting).
- **Crashes:** Gọi Canvas coords trong lúc tab đã bị đóng (destroyed) sẽ văng lỗi `_tkinter.TclError`. Cần kiểm tra `self.winfo_exists()` trước khi thay đổi UI trong callback của `UIAnimationManager`.

## Unit Tests Cần Thêm (Unit Tests to Add)
- (Khó test tự động phần animation), nhưng cần test xem hàm helper update target value có ném lỗi khi object đã bị hủy hay không.
## Phụ lục (Important Note from Review):
- **Đối với Skill Stats:** File `ui/panels/skill_stats_panel.py` hiện tại *chưa* có logic subscribe event `SkillStatsUpdatedEvent`! Bạn cần thêm phương thức `_bind_events` (như cách làm của TargetStatusPanel), nhận dữ liệu từ `EventBus` (dictionary `all_stats`) rồi loop qua để `tree.insert()` hoặc `tree.item()` update cho Treeview, lúc đó mới dùng thanh Mini Progress Bar (Unicode bar) để vẽ giá trị `success_rate`.
- **Đối với Animation Tween:** Scanner bắn HP event bằng hàm `time.sleep` trung bình 100-200ms mỗi khung hình. Hãy đăng ký với `UIAnimationManager` để animate sự chênh lệch máu giữa 2 lần quét mà không gây lag.
