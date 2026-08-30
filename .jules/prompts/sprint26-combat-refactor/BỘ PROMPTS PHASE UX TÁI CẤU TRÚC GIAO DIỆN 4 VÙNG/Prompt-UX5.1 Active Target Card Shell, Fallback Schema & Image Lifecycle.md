# Session Prompt UX5.1: Active Target Card Shell, Multi-Tier Fallback & Image Disposal

Timebox: 20–25 minutes.  
Priority: High – Establishes resilient monster metadata presentation with zero memory leaks.

---

## Objective
Xây dựng khung hiển thị Thẻ Mục Tiêu (Active Target Card) tại Panel 2 bên phải Vùng B (kích thước chuẩn 776 x 552 px). Tích hợp cơ chế Fallback an toàn 3 tầng (kể cả khi mất sạch file ảnh), giải phóng bộ nhớ hình ảnh Tkinter chuyên sâu, hỗ trợ DPI 100% – 200% và song ngữ i18n đầy đủ.

## Target Files
- Modify: `ui/tabs/hunt_tab.py` (Panel Mục Tiêu & Trạng Thái)
- Modify: `lib/features/monsters/monster_repo.py`
- Modify: `lib/system/i18n.py`
- Reference: `lib/ui_style.py`

---

## Implementation Details

### 1. Fallback Toàn Diện Cho CSDL (Full Schema Fallback Adapter)
- Khai báo schema chuẩn:
  ```python
  DEFAULT_MONSTER_SCHEMA = {
      "id": "0",
      "name": "Unknown Target",
      "level": "N/A",
      "hp": 10000,
      "defense": 0,
      "image_path": None
  }
Triển khai safe_get_monster_data(raw_data: Optional[dict]) -> dict:Sử dụng fallback cho từng trường nếu dữ liệu từ monsters.db bị None hoặc sai kiểu.  2. Giao Diện Thẻ Mục Tiêu & Quản Lý Bộ Nhớ Ảnh (776 x 552 px)Header Bar:Status Badge lớn (🏃 Đang tiếp cận... / ⚔️ Đang tấn công... / ✓ Sẵn sàng săn) kèm Target ID (Target: #<id>).Nếu dùng dữ liệu fallback: Đổi màu badge sang UIStyle.STATE_WARN và gắn tooltip cảnh báo dữ liệu mặc định.Thẻ Quái Vật (Active Target Card Container):Cột trái - Khung ảnh đại diện:Co giãn theo DPI: Kích thước int(120 * scale_factor).Cơ chế Fallback 3 tầng: Nạp ảnh quái $\rightarrow$ Nạp default_monster.png $\rightarrow$ Tự vẽ Canvas xám [ NO IMAGE ] nếu thiếu toàn bộ file ảnh.Xử lý giải phóng RAM triệt để:Pythondef clear_target_photo(self):
    if hasattr(self, 'image_label') and self.image_label:
        self.image_label.configure(image="")
    if hasattr(self, '_current_target_photo') and self._current_target_photo:
        del self._current_target_photo
        self._current_target_photo = None
Cột phải - Thông tin chỉ số:Tên quái vật (hỗ trợ wraplength tự xuống dòng khi DPI $\ge 175\%$), Cấp độ, Máu tối đa, Chỉ số thủ.3. Đa Ngôn Ngữ Tường Minh (i18n Namespace)Đăng ký đầy đủ key trong GLOBAL_TRANSLATIONS:target_card.level, target_card.max_hp, target_card.defense, target_card.status_idle, target_card.status_approaching, target_card.status_attacking, target_card.unknown_mob.Validation & Testing (tests/unit/test_target_card_shell.py)1. Automated TestsTest Schema Fallback: Truy vấn dữ liệu rỗng {} -> Assert trả về đầy đủ các trường mặc định, không ném KeyError.Test Zero-Asset Fallback: Giả lập xóa cả file ảnh quái lẫn file default_monster.png -> Assert thẻ mục tiêu tự vẽ Canvas [ NO IMAGE ] an toàn mà không crash app.Test High-Load Memory Stability: Giả lập tải liên tục 500 ảnh trong 30 giây -> Assert clear_target_photo() thu hồi bộ nhớ hiệu quả, dung lượng RAM không tăng lũy tiến.2. Visual & DPI CheckKiểm tra hiển thị bố cục thẻ mục tiêu sắc nét ở các mức DPI: 100%, 125%, 150%, 175%, 200%.Kiểm tra chuyển đổi ngôn ngữ vi <-> en cập nhật tức thì toàn bộ nhãn.Session Boundary GatePASSED nếu:Thẻ mục tiêu hiển thị sắc nét, cơ chế giải phóng ảnh Tkinter hoạt động hoàn hảo không rò rỉ RAM.Xử lý an toàn 100% các trường hợp mất file ảnh (kể cả zero-asset).Vượt qua toàn bộ automated unit tests.REVERTED nếu:Tràn bộ nhớ khi chuyển đổi ảnh liên tục hoặc lỗi layout ở DPI cao.Báo cáo kết quả PASSED/REVERTED ở phút thứ 20.