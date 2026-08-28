# Hotkey Handler Package

Package chứa các handler cho phím tắt toàn cục (global hotkeys).

## Sprint 24 - Code Reorganization

### Mục đích

Tách logic phím tắt ra khỏi `app_gui.py` để:
- Giảm kích thước file chính
- Dễ maintain và test
- Tái sử dụng code
- Tách biệt concerns

### Cấu trúc

```
lib/hotkey/
├── __init__.py                    # Package exports
├── README.md                      # Documentation
└── monster_editor_handler.py     # Ctrl+Shift+M handler
```

## Monster Editor Handler

### Chức năng

Handler cho phím tắt Ctrl+Shift+M để mở Quick Monster Editor.

### Features

- ✅ Singleton pattern validation
- ✅ Double-open prevention  
- ✅ Thread-safe main thread scheduling
- ✅ Detailed debug logging (configurable)
- ✅ Stale instance cleanup
- ✅ Parent window validation

### Sử dụng

```python
from lib.hotkey.monster_editor_handler import create_monster_editor_handler

# Trong App.__init__():
self._monster_editor_handler = create_monster_editor_handler(self, debug=False)

# Đăng ký hotkey:
keyboard.add_hotkey(
    'ctrl+shift+m', 
    self._monster_editor_handler.on_hotkey_pressed, 
    suppress=False
)

# Hoặc gọi trực tiếp từ menu:
self._monster_editor_handler.open_monster_editor()
```

### Debug Mode

Bật debug logging:

```python
self._monster_editor_handler = create_monster_editor_handler(self, debug=True)
```

Debug mode sẽ log:
- Process ID
- Window state
- Toplevel windows
- Singleton validation steps

## Tương lai

Các hotkey khác có thể được tách ra tương tự:
- Vision Wizard (Ctrl+Shift+V)
- Library Manager (Ctrl+Shift+L)
- Setup Wizard (Ctrl+Shift+N)
- Hunt Start/Stop (Ctrl+Shift+R/E)

## Testing

```python
# Test singleton pattern
handler = create_monster_editor_handler(app)
handler.open_monster_editor()  # Mở lần 1
handler.open_monster_editor()  # Should reuse instance

# Test hotkey
handler.on_hotkey_pressed()  # Should schedule open in main thread
```

## Notes

- Handler tự động sử dụng `app._on_monster_saved()` callback nếu có
- Module import lazy để tránh circular dependencies
- Singleton instance được quản lý bởi `monster_manager_win.py`
