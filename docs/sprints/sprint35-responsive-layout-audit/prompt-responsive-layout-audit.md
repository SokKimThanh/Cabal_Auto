# Audit Report: Responsive Layout & Scrolling
## Hiện trạng
### PanedWindow đang được dùng ở đâu
- `ui/tabs/hunt_tab.py`: Dùng làm layout chính (chia 2 cột trái phải cho Workspace). Các pane đã có bọc `ResponsiveGridBase` nhưng vẫn tồn tại nguy cơ chồng chéo rủi ro.
- `ui/views/icon_manager_frame.py`: Chia đôi màn hình giữa danh sách icon và form chi tiết.
- `ui/views/skill_manager_frame.py`: Chia đôi danh sách kỹ năng và form cấu hình.
- `ui/components/category_manager_component.py`: Dùng để split Tree và Form (tỷ lệ 1:1).
- `ui/components/vision_snapshot_debugger.py`: Tách Canvas hiển thị hình ảnh và Scrollable Area chứa ROI cards.

### ExpandedPanel đang được mô phỏng ở đâu
- `ui/views/monster_manager_frame.py`: Mô phỏng thủ công qua cờ `self.type_panel_expanded`, tự ẩn/hiện widget và thay đổi text (▼/▲) trên Label (`type_title_lbl`).
- `ui/components/action_bar_view.py`: `Screen State Panel (inside expanded)`.

### ResponsiveGridBase đang được dùng ở đâu
- Là xương sống cho hầu hết các View/Tab/Panel lớn: `AppShell`, `IconManagerFrame`, `BuildManagerFrame`, `SkillManagerFrame`, `ScanHistoryFrame`, `ClassManagerFrame`, `MonsterManagerFrame`, `LanguageManagerFrame`, `SkillStatsPanel`, `HuntTab`, `SetupTab`.

### Các implementation scroll khác tồn tại ở đâu
- `ui/dialogs/create_preset_dialog.py`: Tự tạo `Canvas`, `Scrollbar`, tự bind scroll event.
- `ui/dialogs/icon_picker.py`: Tự triển khai Canvas/Scrollbar cho Grid.
- `ui/components/vision_snapshot_debugger.py`: Tạo `roi_canvas` và `roi_scrollbar` thủ công.
- `ui/components/skill_timeline_strip.py`: Canvas ngang (`SkillSlotCanvas`) - Dù nằm ngoài phạm vi ResponsiveGridBase (scroll dọc), nhưng cũng cần để ý.
- `ui/windows/setup_wizard_vision.py` và `library_manager.py`: Các canvas preview riêng.

## Root Cause
### Vị trí không tuân thủ ResponsiveGridBase
Các Dialog phụ (như `create_preset_dialog.py`, `icon_picker.py`) và một số component phức tạp (`vision_snapshot_debugger.py`) vẫn đang tái phát minh bánh xe bằng cách tự tạo Canvas và Scrollbar.

### Vấn đề propagation
`ResponsiveGridBase` hiện đang dùng `bind_all("<MouseWheel>")` (và `<Button-4/5>`) trên Canvas khi chuột nằm trong Component (`<Enter>`) và bỏ khi chuột đi ra (`<Leave>`).
**Rủi ro:**
- Gây lỗi TclError nếu widget bị xóa trước khi xử lý.
- Có thể "cướp" quyền cuộn của các widget con: Text widget, Treeview có thanh cuộn riêng, Combobox dropdown. Nếu chuột nằm trong `ResponsiveGridBase` nhưng trên mặt một `Treeview`, cuộn chuột sẽ kích hoạt cả Treeview lẫn lưới cha (hoặc cha chặn con).
- Thử nghiệm workaround (tránh unbind nếu di chuột lên widget con) dẫn đến tình huống unbind bị trượt (rác sự kiện).

### Layout không responsive
- Các Panel "tự mở rộng" đang đóng cứng chiều cao hoặc ẩn hiện làm vỡ flow layout.

### Scroll chồng chéo
- `create_preset_dialog.py` có bind event mouse wheel lặp lại. Xung đột nếu dùng cùng lúc nhiều Responsive container lồng nhau.

## Đề xuất kiến trúc
```text
ResponsiveGridBase
├── PanedWindow Integration
│   └── (Quy định: Các Pane con chứa nội dung cuộn phải luôn dùng ResponsiveGridBase thay vì tk.Frame cứng)
├── ExpandedPanel Integration
│   └── Component chuẩn: `ui.components.expanded_panel.ExpandedPanel` (Gắn Header và bọc Body bằng ResponsiveGridBase)
├── Scroll Management
│   └── Tái sử dụng `ResponsiveGridBase` làm container duy nhất cho scroll dọc.
└── Event Propagation
    └── Gỡ bỏ `bind_all` tại `ResponsiveGridBase`. Chuyển sang bind trực tiếp trên Widget và Canvas, dùng `winfo_containing` để quyết định có delegate sự kiện lên cha không, đảm bảo nguyên tắc: Widget con xử lý trước -> Container xử lý sau.
```

## Kế hoạch triển khai
- **Batch 1: Audit propagation** (Cập nhật logic Scroll & Event Delegation trong `ResponsiveGridBase` và loại bỏ `bind_all` bừa bãi).
- **Batch 2: Standardize PanedWindow** (Đảm bảo quy chuẩn ResponsiveGridBase nằm trong các Pane của `HuntTab` và các module Manager).
- **Batch 3: Standardize ExpandedPanel** (Tạo class `ExpandedPanel` và áp dụng thay cho các panel chế thủ công).
- **Batch 4: Cleanup custom scroll implementation** (Refactor `create_preset_dialog.py`, `vision_snapshot_debugger.py` sử dụng `ResponsiveGridBase`).
- **Batch 5: ResponsiveGridBase adoption** (Rà soát chót và làm sạch UI style).
