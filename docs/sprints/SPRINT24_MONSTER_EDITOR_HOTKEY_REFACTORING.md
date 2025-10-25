# Sprint 24 - Monster Editor Hotkey Refactoring

## Tổng quan

Tách toàn bộ logic Ctrl+Shift+M (Monster Editor) ra khỏi `app_gui.py` vào module riêng `lib/hotkey/monster_editor_handler.py`.

## Ngày thực hiện

25 October 2025

## Lý do

1. **Giảm kích thước file**: `app_gui.py` quá lớn (~9800 dòng)
2. **Separation of Concerns**: Tách logic hotkey ra khỏi UI code
3. **Reusability**: Handler có thể được test và tái sử dụng
4. **Maintainability**: Dễ tìm và sửa code liên quan đến Monster Editor

## Các thay đổi

### 1. File mới tạo

#### `lib/hotkey/monster_editor_handler.py`
- **Class**: `MonsterEditorHandler`
- **Methods**:
  - `on_hotkey_pressed()`: Callback khi nhấn Ctrl+Shift+M
  - `open_monster_editor()`: Logic mở Monster Editor
- **Features**:
  - Singleton pattern validation
  - Double-open prevention
  - Thread-safe scheduling
  - Debug logging (configurable)

#### `lib/hotkey/__init__.py`
- Package exports
- Public API: `create_monster_editor_handler()`

#### `lib/hotkey/README.md`
- Documentation đầy đủ
- Usage examples
- Future improvements

### 2. Thay đổi trong `app_gui.py`

#### Import (dòng ~48)
```python
# Monster Editor hotkey handler
from lib.hotkey.monster_editor_handler import create_monster_editor_handler
```

#### __init__ (dòng ~834)
**Trước:**
```python
self._monster_editor_opening = False  # Flag to prevent double opening Monster Editor
```

**Sau:**
```python
# Monster Editor Handler (Sprint 24 - Extracted to separate module)
self._monster_editor_handler = create_monster_editor_handler(self, debug=False)
```

#### Menu Command (dòng ~802)
**Trước:**
```python
command=self._open_monster_editor
```

**Sau:**
```python
command=lambda: self._monster_editor_handler.open_monster_editor()
```

#### Hotkey Registration (dòng ~5365)
**Trước:**
```python
self._global_monster_hotkey = keyboard.add_hotkey(
    monster_key, self._on_monster_editor_hotkey, suppress=False
)
```

**Sau:**
```python
self._global_monster_hotkey = keyboard.add_hotkey(
    monster_key, self._monster_editor_handler.on_hotkey_pressed, suppress=False
)
```

#### Methods Removed (dòng ~5130-5285)
- ❌ `_on_monster_editor_hotkey()` - 38 dòng
- ❌ `_open_monster_editor()` - 155 dòng

**Tổng code đã xóa**: ~193 dòng

#### Methods Kept
- ✅ `_on_monster_saved()` - Callback vẫn ở app_gui.py vì cần access app state

### 3. Cấu trúc thư mục

```
lib/
├── hotkey/                         # NEW PACKAGE
│   ├── __init__.py                # Package exports
│   ├── README.md                  # Documentation
│   └── monster_editor_handler.py  # Handler implementation
└── ...
```

## Lợi ích

### 1. Giảm complexity
- `app_gui.py`: -193 dòng code
- Tách concerns rõ ràng (UI vs Hotkey logic)

### 2. Testability
```python
# Test handler độc lập
handler = create_monster_editor_handler(mock_app)
handler.open_monster_editor()
```

### 3. Reusability
```python
# Có thể dùng ở nhiều nơi
from lib.hotkey import create_monster_editor_handler

handler1 = create_monster_editor_handler(app1)
handler2 = create_monster_editor_handler(app2, debug=True)
```

### 4. Debug mode
```python
# Bật debug logging khi cần
self._monster_editor_handler = create_monster_editor_handler(self, debug=True)
```

## Testing checklist

- [x] Import module thành công
- [x] `app_gui.py` compile không lỗi
- [ ] Chạy app và test Ctrl+Shift+M
- [ ] Test mở từ menu
- [ ] Test singleton pattern (mở 2 lần)
- [ ] Test khi app chưa init xong

## Tương lai

Có thể tách thêm các hotkey khác:
1. Vision Wizard (Ctrl+Shift+V)
2. Library Manager (Ctrl+Shift+L)
3. Setup Wizard (Ctrl+Shift+N)
4. Hunt Start/Stop (Ctrl+Shift+R/E)

Mỗi handler sẽ:
- Nằm trong `lib/hotkey/`
- Có class riêng với interface rõ ràng
- Có debug mode
- Có documentation

## Notes

- Handler giữ reference đến `self.app` để gọi methods
- Lazy import `quick_monster_editor` để tránh circular dependency
- Singleton instance vẫn được quản lý bởi `quick_monster_editor.py`
- Flag `_opening_flag` được quản lý trong handler, không còn trong app

## Breaking Changes

Không có - tất cả public API vẫn giữ nguyên.

## Migration Guide

Nếu có code khác gọi `app._open_monster_editor()`:

**Trước:**
```python
app._open_monster_editor()
```

**Sau:**
```python
app._monster_editor_handler.open_monster_editor()
```

## Tác giả

Sprint 24 - Code Reorganization Team
