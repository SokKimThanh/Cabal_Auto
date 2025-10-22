# Vision Wizard Framework - Khung Code Chuẩn Bị

**Sprint 22 - Phase 1: Setup Framework**  
**Ngày tạo:** 2025-10-22  
**Trạng thái:** ✅ Hoàn thành khung code cơ bản

---

## 📋 Tổng Quan

Module `setup_wizard_vision.py` được tạo để quản lý Vision System, tách biệt hoàn toàn khỏi form chính (`setup_wizard.py`). Module này cung cấp:

- ✅ Giao diện Tkinter độc lập
- ✅ Singleton pattern (chỉ mở một instance)
- ✅ Topmost mode (luôn hiển thị trên game)
- ✅ Hỗ trợ đa ngôn ngữ (i18n)
- ✅ Layout sạch sẽ, dễ mở rộng
- ⏳ Sẵn sàng tích hợp OpenCV (TODO)

---

## 🎯 Vị Trí File

```
ui/
  └── setup_wizard_vision.py   ← Module mới được tạo
```

Đặt cùng thư mục với `setup_wizard.py` để dễ quản lý.

---

## 🏗️ Cấu Trúc Class

### 1. VisionWizard (tk.Toplevel)

Class chính quản lý giao diện:

```python
class VisionWizard(tk.Toplevel):
    """
    Vision Wizard - Giao diện quản lý vision system.
    
    Features:
    - Singleton pattern
    - Topmost mode
    - Quản lý template và threshold
    - Preview và overlay (TODO)
    """
```

#### Attributes chính:

| Attribute | Type | Mô tả |
|-----------|------|-------|
| `templates` | `List[Dict]` | Danh sách template đang dùng |
| `current_template` | `Dict \| None` | Template đang được chọn |
| `search_mode` | `str` | Chế độ tìm kiếm (position/fullscreen/region) |
| `search_mode_combo` | `ttk.Combobox` | Combobox chọn chế độ |
| `threshold_entry` | `tk.Entry` | Entry nhập ngưỡng |
| `template_tree` | `ttk.Treeview` | Treeview hiển thị danh sách template |
| `preview_canvas` | `tk.Canvas` | Canvas để preview ảnh |

#### Methods chính:

| Method | Mô tả |
|--------|-------|
| `setup_ui()` | Thiết lập giao diện |
| `bind_events()` | Kết nối sự kiện |
| `load_templates()` | Tải danh sách template |
| `load_thresholds()` | Tải ngưỡng nhận diện |
| `add_template()` | Thêm template mới |
| `remove_template()` | Xóa template |
| `save_threshold()` | Lưu ngưỡng |
| `test_recognition()` | Test nhận diện (TODO) |

---

## 🎨 Layout Giao Diện

```
┌──────────────────────────────────────────────────┐
│  Header (Tiêu đề + Subtitle)                     │
├──────────────────────────────────────────────────┤
│  Top Panel: Chế độ tìm kiếm + Threshold          │
│  ┌──────────────────────────────────────────┐    │
│  │ Combobox: Tìm tại vị trí chỉ định       │    │
│  │ Entry: 0.7 (ngưỡng)                      │    │
│  └──────────────────────────────────────────┘    │
├──────────────────────────────────────────────────┤
│  Middle Panel: Danh sách Template (Treeview)     │
│  ┌──────────────────────────────────────────┐    │
│  │ Tên         │ Đường dẫn        │ Ngưỡng  │    │
│  ├─────────────┼──────────────────┼─────────┤    │
│  │ Monster_HP  │ assets/...       │ 0.8     │    │
│  │ Skill_Icon  │ assets/...       │ 0.75    │    │
│  └──────────────────────────────────────────┘    │
├──────────────────────────────────────────────────┤
│  Bottom Panel: Buttons                           │
│  [Thêm] [Xóa]        [Lưu] [Test] [Đóng]        │
├──────────────────────────────────────────────────┤
│  Preview Panel: Canvas (150px height)            │
│  ┌──────────────────────────────────────────┐    │
│  │   Vùng preview sẽ hiển thị ở đây        │    │
│  └──────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
```

### Components chi tiết:

1. **Header Frame**
   - Background: `UI.COLOR_PRIMARY` (xanh dương)
   - Title: Font `UI.FONT_TITLE`, màu trắng
   - Subtitle: Font `UI.FONT_LABEL`, màu trắng

2. **Top Panel (LabelFrame)**
   - **Search Mode Combobox**: 3 chế độ
     - Tìm tại vị trí chỉ định
     - Tìm toàn màn hình
     - Tìm trong vùng (ROI)
   - **Threshold Entry**: Nhập ngưỡng 0.0 - 1.0
     - Validation: chỉ số và dấu chấm
     - Tooltip: giải thích ý nghĩa

3. **Middle Panel (LabelFrame)**
   - **Treeview** với 3 cột:
     - `name`: Tên template
     - `path`: Đường dẫn file
     - `threshold`: Ngưỡng nhận diện
   - Scrollbar dọc + ngang
   - Select mode: `browse` (chọn 1 dòng)

4. **Bottom Panel**
   - Left: Thêm, Xóa
   - Right: Lưu, Test, Đóng
   - Tooltips cho từng button

5. **Preview Panel (LabelFrame)**
   - Canvas 860x150px
   - Background: `#f0f0f0`
   - Placeholder text
   - TODO: Hiển thị ảnh và overlay

---

## 🔌 Tích Hợp Với Form Chính

### Cách 1: Import và gọi trực tiếp

Trong `setup_wizard.py` hoặc `app_gui.py`:

```python
from ui.setup_wizard_vision import create_or_show_vision_wizard

# Bind hotkey
root.bind('<Control-Shift-L>', lambda e: create_or_show_vision_wizard(root))

# Hoặc gọi từ button
def open_vision_wizard():
    create_or_show_vision_wizard(root)
```

### Cách 2: Sử dụng helper function

```python
from ui.setup_wizard_vision import open_vision_wizard_from_parent

# Bind hotkey
root.bind('<Control-Shift-L>', lambda e: open_vision_wizard_from_parent(root))
```

### Singleton Pattern

Module tự động đảm bảo chỉ có 1 instance:

```python
# Lần 1: Tạo mới
wizard1 = create_or_show_vision_wizard(root)

# Lần 2: Lift instance cũ lên, không tạo mới
wizard2 = create_or_show_vision_wizard(root)

assert wizard1 is wizard2  # True
```

---

## 🌐 Đa Ngôn Ngữ (i18n)

Module hỗ trợ đầy đủ đa ngôn ngữ:

### Namespace: `vision_wizard`

Tất cả keys được đăng ký trong namespace `vision_wizard`:

```python
i18n_t('vision_wizard_title', ns='vision_wizard')
# → Tiếng Việt: "Trình Quản Lý Vision System"
# → Tiếng Anh: "Vision System Manager"
```

### Danh sách keys đã định nghĩa:

| Key | Tiếng Việt | Tiếng Anh |
|-----|-----------|-----------|
| `vision_wizard_title` | Trình Quản Lý Vision System | Vision System Manager |
| `search_mode_label` | Chế độ tìm kiếm: | Search Mode: |
| `threshold_label` | Ngưỡng nhận diện (0.0 - 1.0): | Recognition Threshold (0.0 - 1.0): |
| `btn_add_template` | Thêm Template | Add Template |
| `btn_remove_template` | Xóa | Remove |
| `btn_save_threshold` | Lưu Ngưỡng | Save Threshold |
| `btn_test_recognition` | Test Nhận Diện | Test Recognition |
| ... | ... | ... |

Xem đầy đủ trong biến `VISION_WIZARD_TRANSLATIONS`.

---

## ⌨️ Keyboard Shortcuts

Module hỗ trợ các phím tắt:

| Phím | Chức năng |
|------|-----------|
| `Escape` | Đóng cửa sổ |
| `Ctrl+S` | Lưu ngưỡng |
| `Ctrl+T` | Test nhận diện |
| `Delete` | Xóa template |

---

## 📝 TODO: Các Chức Năng Cần Bổ Sung

### Phase 2: OpenCV Integration

```python
def test_recognition(self) -> None:
    """
    TODO: Bổ sung logic test nhận diện:
    - Chụp màn hình game
    - Chạy OpenCV template matching
    - Hiển thị kết quả trong preview canvas
    - Show overlay với vị trí tìm thấy
    """
```

**Các bước:**
1. Import `lib.vision.template_matcher`
2. Chụp màn hình game (sử dụng `pyautogui` hoặc Win32 API)
3. Gọi `template_matcher.match_template()`
4. Vẽ kết quả lên `preview_canvas`
5. Hiển thị overlay bán trong suốt trên game

### Phase 3: Template Management

```python
def load_templates(self) -> None:
    """
    TODO: Load từ:
    - File config JSON: lib/data/config.json
    - Thư mục: assets/images/templates/
    - Database (nếu có)
    """
```

**Các bước:**
1. Đọc `lib/data/config.json`
2. Parse section `templates`
3. Validate paths tồn tại
4. Load vào `self.templates`

### Phase 4: ROI Selection

```python
def _on_search_mode_changed(self, event=None) -> None:
    """
    TODO: Khi chọn "region":
    - Hiện control để chọn vùng ROI
    - Cho phép user drag-select trên màn hình
    - Lưu coordinates vào config
    """
```

**Các bước:**
1. Thêm frame cho ROI selection
2. Buttons: "Select Region", "Clear Region"
3. Khi click, mở overlay transparent để user chọn vùng
4. Lưu `(x, y, width, height)` vào template config

### Phase 5: Preview & Overlay

```python
def _on_template_selected(self, event=None) -> None:
    """
    TODO: 
    - Load và hiển thị preview ảnh template trong canvas
    - Sử dụng PIL.Image và PIL.ImageTk
    """
```

**Các bước:**
1. Load ảnh bằng `PIL.Image.open()`
2. Resize nếu cần (fit vào canvas 860x150)
3. Convert sang `ImageTk.PhotoImage`
4. Vẽ lên canvas: `canvas.create_image()`

### Phase 6: Monster Tracking

```python
def start_tracking(self) -> None:
    """
    TODO: Bắt đầu tracking quái vật real-time
    - Chạy loop nhận diện liên tục
    - Update overlay position
    - Giao tiếp với skill system
    """
```

**Các bước:**
1. Tạo thread riêng cho tracking loop
2. Mỗi 100ms: chụp màn hình → match template → update overlay
3. Gửi signal đến skill system khi tìm thấy target
4. Buttons: "Start Tracking", "Stop Tracking"

---

## 🧪 Testing

### Test độc lập module

Chạy file trực tiếp:

```powershell
cd e:\Cabal_Auto
python -m ui.setup_wizard_vision
```

Sẽ mở một test window với button để mở wizard.

### Test từ form chính

Thêm vào `app_gui.py`:

```python
# Import
from ui.setup_wizard_vision import open_vision_wizard_from_parent

# Trong __init__:
self.root.bind('<Control-Shift-L>', lambda e: open_vision_wizard_from_parent(self.root))

# Hoặc thêm menu item:
vision_menu.add_command(
    label='Open Vision Wizard',
    command=lambda: open_vision_wizard_from_parent(self.root)
)
```

---

## 📊 Data Structure

### Template Object

```python
{
    'name': str,          # Tên template (vd: "Monster_HP_Bar")
    'path': str,          # Đường dẫn file (vd: "assets/images/monsters/hp_bar.png")
    'threshold': float,   # Ngưỡng 0.0-1.0 (vd: 0.8)
    'search_mode': str,   # Optional: "position" | "fullscreen" | "region"
    'roi': tuple,         # Optional: (x, y, width, height) nếu search_mode = "region"
}
```

### Config JSON Structure (TODO)

```json
{
  "vision": {
    "templates": [
      {
        "name": "Monster_HP_Bar",
        "path": "assets/images/monsters/hp_bar.png",
        "threshold": 0.8,
        "search_mode": "region",
        "roi": [100, 100, 200, 50]
      },
      {
        "name": "Skill_Icon_1",
        "path": "assets/images/skills/skill_1.png",
        "threshold": 0.75,
        "search_mode": "position"
      }
    ],
    "default_threshold": 0.7,
    "preview_size": [860, 150]
  }
}
```

---

## 🎨 UI Style Guide

Module sử dụng `lib.ui_style.UIStyle` để đảm bảo tính nhất quán:

| Component | Style |
|-----------|-------|
| Header background | `UI.COLOR_PRIMARY` (#2196F3) |
| Title font | `UI.FONT_TITLE` (Segoe UI, 12, bold) |
| Label font | `UI.FONT_LABEL` (Segoe UI, 10) |
| Button font | `UI.FONT_BUTTON` (Segoe UI, 10) |
| Text color | `UI.COLOR_TEXT` (#212121) |
| Panel background | `UI.BG_DEFAULT` (#FFFFFF) |

Tham khảo: `lib/ui_style.py`

---

## 🔄 Workflow Người Dùng

1. **Mở wizard**: Nhấn `Ctrl+Shift+L` hoặc click menu
2. **Chọn chế độ tìm kiếm**: Dropdown "Chế độ tìm kiếm"
3. **Thêm template**: Click "Thêm Template" → chọn file ảnh
4. **Chỉnh threshold**: Chọn template → nhập ngưỡng → "Lưu Ngưỡng"
5. **Test**: Click "Test Nhận Diện" → xem kết quả trong preview
6. **Tracking** (TODO): Click "Start Tracking" → overlay hiển thị real-time
7. **Đóng**: Click "Đóng" hoặc nhấn `Escape`

---

## 🚀 Next Steps

### Sprint 22 - Phase 2: OpenCV Integration

1. ✅ Tạo khung code ← **Hoàn thành**
2. ⏳ Tích hợp `lib.vision.template_matcher`
3. ⏳ Implement `test_recognition()`
4. ⏳ Preview ảnh trong canvas

### Sprint 22 - Phase 3: Advanced Features

5. ⏳ ROI selection
6. ⏳ Monster tracking loop
7. ⏳ Overlay bán trong suốt
8. ⏳ Giao tiếp với skill system

---

## 📖 References

- `ui/setup_wizard.py` - Form chính (tham khảo cấu trúc)
- `lib/ui_style.py` - Style guide
- `lib/i18n.py` - Hệ thống đa ngôn ngữ
- `lib/vision/template_matcher.py` - OpenCV template matching (TODO: tích hợp)
- `lib/ui/tooltip.py` - Tooltip helper

---

## ✅ Checklist

- [x] Tạo file `ui/setup_wizard_vision.py`
- [x] Implement class `VisionWizard(tk.Toplevel)`
- [x] Singleton pattern
- [x] Topmost mode
- [x] Layout cơ bản (Header, Top, Middle, Bottom, Preview)
- [x] Search mode combobox
- [x] Threshold entry với validation
- [x] Template treeview
- [x] Buttons (Thêm, Xóa, Lưu, Test, Đóng)
- [x] Preview canvas (placeholder)
- [x] Event bindings
- [x] Keyboard shortcuts
- [x] i18n translations (vi + en)
- [x] Helper functions (create_or_show, open_from_parent)
- [x] Test mode (main block)
- [x] Docstrings và comments
- [ ] Tích hợp OpenCV (Phase 2)
- [ ] Load/save config (Phase 2)
- [ ] ROI selection (Phase 3)
- [ ] Tracking loop (Phase 3)
- [ ] Overlay (Phase 3)

---

**🎉 Khung code đã sẵn sàng để bổ sung các chức năng chính!**

