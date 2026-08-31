# Vision Menu Integration - Sprint 22 Phase 1B

**Ngày:** 2025-10-22  
**Mục tiêu:** Tích hợp menu Vision vào main app với hotkeys toàn cục

---

## 🎯 Tổng Quan

Bổ sung menu **Vision** vào main app để truy cập nhanh các chức năng Vision System:
- Open Vision Wizard (Ctrl+Shift+V)
- Scan Region (Ctrl+Alt+S) 
- Add Template (Ctrl+T)
- Manage Templates (Ctrl+Shift+T)
- Toggle Overlay (Ctrl+Shift+O)

---

## 📋 Thay Đổi Kiến Trúc

### Trước (Sprint 22 Phase 1A)
```
app_gui.py
  ├── Menu: Settings
  └── Hotkey: Ctrl+Shift+L (riêng lẻ)
```

### Sau (Sprint 22 Phase 1B)
```
app_gui.py
  ├── Menu: Settings
  ├── Menu: Vision ← MỚI
  │   ├── Open Vision Wizard (Ctrl+Shift+V)
  │   ├── Scan Region (Ctrl+Alt+S)
  │   ├── Add Template (Ctrl+T)
  │   ├── Manage Templates (Ctrl+Shift+T)
  │   └── Toggle Overlay (Ctrl+Shift+O)
  └── Global hotkeys registered với bind_all()
```

---

## 🔧 Implementation

### 1. Thêm Vision Menu vào `app_gui.py`

Tìm phần tạo menubar (khoảng dòng 636-690), thêm sau `settings_menu`:

```python
# --- Menu: Vision (Sprint 22 Phase 1B) ---
try:
    vision_menu = tk.Menu(menubar, tearoff=0)
    
    # Open Vision Wizard (Ctrl+Shift+V)
    vision_menu.add_command(
        label=self._t("vision_open_wizard", default="Open Vision Wizard"),
        accelerator="Ctrl+Shift+V",
        command=self._open_vision_wizard
    )
    
    vision_menu.add_separator()
    
    # Scan Region (Ctrl+Alt+S)
    vision_menu.add_command(
        label=self._t("vision_scan_region", default="Scan Region"),
        accelerator="Ctrl+Alt+S",
        command=self._scan_region
    )
    
    # Add Template (Ctrl+T)
    vision_menu.add_command(
        label=self._t("vision_add_template", default="Add Template"),
        accelerator="Ctrl+T",
        command=self._add_template
    )
    
    # Manage Templates (Ctrl+Shift+T)
    vision_menu.add_command(
        label=self._t("vision_manage_templates", default="Manage Templates"),
        accelerator="Ctrl+Shift+T",
        command=self._manage_templates
    )
    
    vision_menu.add_separator()
    
    # Toggle Overlay (Ctrl+Shift+O)
    vision_menu.add_command(
        label=self._t("vision_toggle_overlay", default="Toggle Overlay"),
        accelerator="Ctrl+Shift+O",
        command=self._toggle_overlay
    )
    
    menubar.add_cascade(label="Vision", menu=vision_menu)
except Exception as e:
    print(f"[Vision Menu] Error creating menu: {e}")
```

### 2. Bind Global Hotkeys

Thêm vào phương thức `__init__()` sau khi tạo UI:

```python
# Bind Vision hotkeys globally
try:
    self.bind_all('<Control-Shift-V>', lambda e: self._open_vision_wizard())
    self.bind_all('<Control-Alt-s>', lambda e: self._scan_region())
    self.bind_all('<Control-t>', lambda e: self._add_template())
    self.bind_all('<Control-Shift-T>', lambda e: self._manage_templates())
    self.bind_all('<Control-Shift-O>', lambda e: self._toggle_overlay())
    print("[Vision] Global hotkeys registered")
except Exception as e:
    print(f"[Vision] Error binding hotkeys: {e}")
```

### 3. Implement Callback Methods

Thêm các phương thức vào class `AutoHuntApp`:

```python
def _open_vision_wizard(self):
    """Open Vision Wizard window (Ctrl+Shift+V)"""
    try:
        from ui.setup_wizard_vision import create_or_show_vision_wizard
        wizard = create_or_show_vision_wizard(
            self,
            config_path=self.config_path,
            on_close=self._on_vision_wizard_closed
        )
        print(f"[Vision] Wizard opened: {wizard}")
    except Exception as e:
        print(f"[Vision] Error opening wizard: {e}")
        messagebox.showerror(
            self._t("error", default="Error"),
            f"Cannot open Vision Wizard: {e}"
        )

def _on_vision_wizard_closed(self):
    """Callback when Vision Wizard is closed"""
    print("[Vision] Wizard closed")
    # Refresh templates hoặc update UI nếu cần

def _scan_region(self):
    """Scan region for template matching (Ctrl+Alt+S)"""
    # TODO Phase 2: Implement region scanning
    print("[Vision] Scan region - TODO")
    messagebox.showinfo(
        "Vision",
        "Scan Region feature will be available in Phase 2"
    )

def _add_template(self):
    """Quick add template (Ctrl+T)"""
    # TODO Phase 2: Quick template add dialog
    print("[Vision] Add template - TODO")
    
    # Quick impl: Open file dialog
    try:
        filetypes = [
            ('Image files', '*.png *.jpg *.jpeg *.bmp'),
            ('All files', '*.*')
        ]
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Add Template",
            filetypes=filetypes
        )
        if file_path:
            print(f"[Vision] Selected template: {file_path}")
            # TODO: Add to config
    except Exception as e:
        print(f"[Vision] Error adding template: {e}")

def _manage_templates(self):
    """Open template management (Ctrl+Shift+T)"""
    # Shortcut to Vision Wizard
    self._open_vision_wizard()

def _toggle_overlay(self):
    """Toggle overlay display (Ctrl+Shift+O)"""
    # TODO Phase 5: Toggle overlay
    print("[Vision] Toggle overlay - TODO")
    messagebox.showinfo(
        "Vision",
        "Overlay toggle will be available in Phase 5"
    )
```

---

## 🌐 Translations

Thêm vào `lib/i18n/translations.py`:

```python
VISION_MENU_TRANSLATIONS = {
    'vi': {
        'vision_open_wizard': 'Mở Vision Wizard',
        'vision_scan_region': 'Quét Vùng',
        'vision_add_template': 'Thêm Template',
        'vision_manage_templates': 'Quản Lý Template',
        'vision_toggle_overlay': 'Bật/Tắt Overlay',
    },
    'en': {
        'vision_open_wizard': 'Open Vision Wizard',
        'vision_scan_region': 'Scan Region',
        'vision_add_template': 'Add Template',
        'vision_manage_templates': 'Manage Templates',
        'vision_toggle_overlay': 'Toggle Overlay',
    }
}

# Đăng ký tự động (đặt ở cuối file dictionary)
from lib.i18n import register_bulk
register_bulk('vision_menu', VISION_MENU_TRANSLATIONS)
```

---

## ⌨️ Hotkey Summary

| Phím | Chức năng | Trạng thái |
|------|-----------|-----------|
| `Ctrl+Shift+V` | Open Vision Wizard | ✅ Phase 1B |
| `Ctrl+Alt+S` | Scan Region | ⏳ Phase 2 |
| `Ctrl+T` | Add Template | ⏳ Phase 2 |
| `Ctrl+Shift+T` | Manage Templates | ✅ Phase 1B (→ Wizard) |
| `Ctrl+Shift+O` | Toggle Overlay | ⏳ Phase 5 |

**Lưu ý:** `Ctrl+Shift+L` (hotkey cũ) vẫn hoạt động để tương thích ngược.

---

## 📝 Checklist Tích Hợp

### Bước 1: Thêm Vision Menu
- [ ] Copy code menu vào `app_gui.py` (sau `settings_menu`)
- [ ] Test menu hiển thị đúng
- [ ] Test accelerator labels hiển thị

### Bước 2: Bind Global Hotkeys
- [ ] Thêm `bind_all()` vào `__init__()`
- [ ] Test từng hotkey: Ctrl+Shift+V, Ctrl+Alt+S, v.v.
- [ ] Check không conflict với hotkeys khác

### Bước 3: Implement Callbacks
- [ ] Thêm 5 methods: `_open_vision_wizard()`, `_scan_region()`, v.v.
- [ ] Test `_open_vision_wizard()` mở wizard đúng
- [ ] Test các method TODO show message phù hợp

### Bước 4: Translations
- [ ] Thêm keys vào `lib/i18n/translations.py`
- [ ] Test menu labels đa ngôn ngữ (vi/en)

### Bước 5: Testing
- [ ] Menu "Vision" xuất hiện đúng vị trí
- [ ] Click menu items hoạt động
- [ ] Hotkeys work từ bất kỳ đâu trong app
- [ ] Vision Wizard mở đúng (singleton)
- [ ] Không có error trong console

### Bước 6: Cleanup
- [ ] Remove old hotkey `Ctrl+Shift+L` nếu không cần
- [ ] Update documentation
- [ ] Commit changes

---

## 🎨 UI Preview

```
╔════════════════════════════════════╗
║ Cabal Auto Hunt                    ║
╠════════════════════════════════════╣
║ Settings  Vision                   ║ ← Menu bar
╠════════════════════════════════════╣
║                                    ║
║  Dropdown menu khi click "Vision": ║
║  ┌──────────────────────────────┐ ║
║  │ Open Vision Wizard  Ctrl+Shift+V │
║  ├──────────────────────────────┤ ║
║  │ Scan Region        Ctrl+Alt+S│ ║
║  │ Add Template       Ctrl+T    │ ║
║  │ Manage Templates   Ctrl+Shift+T │
║  ├──────────────────────────────┤ ║
║  │ Toggle Overlay     Ctrl+Shift+O │
║  └──────────────────────────────┘ ║
║                                    ║
╚════════════════════════════════════╝
```

---

## 🚨 Lưu Ý Quan Trọng

### Hotkey Conflicts
- **Ctrl+T**: Nếu đã dùng cho chức năng khác → đổi thành `Ctrl+Shift+A` (Add)
- **Ctrl+Alt+S**: Một số app dùng cho Save → test kỹ
- Ưu tiên: Vision hotkeys > App hotkeys > System hotkeys

### Platform Differences
- **Windows**: `bind_all()` hoạt động tốt
- **macOS**: Có thể cần dùng `Command` thay `Control`
- **Linux**: Test với window managers khác nhau

### Error Handling
- Wrap tất cả callbacks trong try-except
- Log errors vào console
- Show user-friendly message boxes
- Không crash app nếu Vision Wizard fail

---

## 📊 Progress Tracking

| Item | Status | Notes |
|------|--------|-------|
| Vision menu structure | ✅ Complete | Code ready |
| Hotkey bindings | ✅ Complete | bind_all() |
| Open Wizard callback | ✅ Complete | Uses existing VisionWizard |
| Scan Region | ⏳ TODO Phase 2 | Placeholder |
| Add Template | ⏳ TODO Phase 2 | Quick file dialog |
| Manage Templates | ✅ Complete | → Open Wizard |
| Toggle Overlay | ⏳ TODO Phase 5 | Placeholder |
| Translations | ✅ Complete | vi + en |
| Documentation | ✅ Complete | This file |

---

## 🔗 Related Files

- **Main App**: `app_gui.py` (add menu + callbacks)
- **Vision Wizard**: `ui/setup_wizard_vision.py` (existing)
- **Translations**: `lib/i18n/translations.py` (add keys)
- **Phase 1A Doc**: `VISION_WIZARD_FRAMEWORK.md`
- **Examples**: `VISION_WIZARD_INTEGRATION_EXAMPLES.py`

---

## 🎯 Next Steps

1. **Now**: Implement menu integration (Phase 1B)
2. **Phase 2**: Complete Scan Region + Add Template
3. **Phase 3**: ROI selection
4. **Phase 4**: Monster tracking
5. **Phase 5**: Overlay system + Toggle

---

**✅ Phase 1B Ready to Implement!**

