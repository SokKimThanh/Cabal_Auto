# ConfirmationWidget - Inline Confirmation Component

## 🎯 Mục đích

Widget xác nhận thao tác inline (Yes/No) thay thế cho popup messagebox. Giúp người dùng xác nhận hành động trực tiếp trên giao diện mà không bị gián đoạn bởi hộp thoại popup.

## ✨ Tính năng

- ✅ **Icon-only buttons**: Nút Yes (accept.ico) và No (cancel.ico)
- ✅ **Auto-hide**: Tự động ẩn sau thời gian chờ (mặc định 5 giây)
- ✅ **Không popup**: Không làm gián đoạn luồng thao tác
- ✅ **Tái sử dụng**: Import và nhúng vào bất kỳ đâu
- ✅ **Callback linh hoạt**: Có thể thay đổi callback động
- ✅ **Lightweight**: Kích thước nhỏ gọn (20x20 buttons)

## 📦 Import

```python
from ui.components.confirmation_widget import ConfirmationWidget
```

## 🚀 Cách sử dụng cơ bản

### 1. Tạo widget

```python
def on_confirm():
    print("User confirmed!")
    # Thực hiện hành động

def on_cancel():
    print("User cancelled")
    # Tùy chọn: xử lý khi hủy

confirmation = ConfirmationWidget(
    parent=some_frame,
    on_confirm=on_confirm,
    on_cancel=on_cancel,  # Optional
    auto_hide_seconds=5,   # Tự động ẩn sau 5 giây
    bg='#F2F2F2'           # Màu nền
)
```

### 2. Hiển thị xác nhận

```python
# Hiển thị widget
confirmation.show()

# Hoặc với tùy chọn vị trí
confirmation.show(side='left', padx=(0, 5), pady=0)
```

### 3. Ẩn widget

```python
# Ẩn thủ công
confirmation.hide()

# Widget tự động ẩn sau timeout hoặc khi click Yes/No
```

## 📝 Ví dụ thực tế

### Ví dụ 1: Xác nhận xóa monster

```python
class MonsterEditor:
    def __init__(self, parent):
        # Tạo confirmation widget
        self.confirmation = ConfirmationWidget(
            parent=self.header_frame,
            on_confirm=lambda: None,  # Sẽ set động
            auto_hide_seconds=5,
            bg='#F2F2F2'
        )
    
    def delete_monster(self, monster):
        """Xóa monster với xác nhận inline."""
        def do_delete():
            # Logic xóa monster
            self.monsters.remove(monster)
            self.refresh_list()
            print(f"Deleted {monster['name']}")
        
        # Set callback và hiển thị xác nhận
        self.confirmation.set_confirm_callback(do_delete)
        self.confirmation.show()
```

### Ví dụ 2: Xác nhận ghi đè file

```python
def save_with_confirmation(self):
    """Lưu file với xác nhận nếu file tồn tại."""
    if os.path.exists(self.filepath):
        # File tồn tại, cần xác nhận
        def do_save():
            self.write_file(self.filepath)
            print("File overwritten")
        
        self.confirmation.set_confirm_callback(do_save)
        self.confirmation.show()
    else:
        # File chưa tồn tại, lưu trực tiếp
        self.write_file(self.filepath)
```

### Ví dụ 3: Thay đổi callback động

```python
# Thay đổi callback cho hành động khác
self.confirmation.set_confirm_callback(lambda: self.delete_all())
self.confirmation.show()

# Sau đó có thể thay đổi cho hành động khác
self.confirmation.set_confirm_callback(lambda: self.reset_settings())
self.confirmation.show()
```

## 🎨 Thiết kế UI

```
┌─────────────────────────────────┐
│ [✓] [✗]                         │  ← Confirmation Widget
└─────────────────────────────────┘
  Yes  No
  
- Background: #F2F2F2 (xám nhạt)
- Button size: 20x20
- Icon size: 16x16
- Yes button: accept.ico (green)
- No button: cancel.ico (gray)
```

## ⚙️ API Reference

### Constructor

```python
ConfirmationWidget(
    parent: tk.Widget,              # Parent widget
    on_confirm: Callable[[], None], # Callback khi Yes
    on_cancel: Optional[Callable],  # Callback khi No (optional)
    auto_hide_seconds: int = 5,     # Thời gian auto-hide (0 = disable)
    bg: str = '#F2F2F2',           # Màu nền
    **kwargs                        # Frame kwargs khác
)
```

### Methods

| Method | Mô tả |
|--------|-------|
| `show(side='left', padx=(0,5), pady=0)` | Hiển thị widget |
| `hide()` | Ẩn widget |
| `is_visible()` | Kiểm tra widget có đang hiển thị không |
| `set_confirm_callback(callback)` | Thay đổi callback Yes |
| `set_cancel_callback(callback)` | Thay đổi callback No |
| `destroy()` | Dọn dẹp resources |

## 🔄 Workflow

```
User clicks Delete
       ↓
Show Confirmation Widget
       ↓
   ┌───┴───┐
   │       │
  Yes     No / Timeout (5s)
   │       │
Execute   Hide
Action   Widget
   │
  Hide
 Widget
```

## 💡 Best Practices

### ✅ DO

```python
# 1. Set callback trước khi show
confirmation.set_confirm_callback(delete_action)
confirmation.show()

# 2. Sử dụng lambda cho action đơn giản
confirmation.set_confirm_callback(lambda: self.delete_item(item_id))
confirmation.show()

# 3. Đặt widget ở vị trí dễ nhìn
left_panel.pack(side='left')
confirmation = ConfirmationWidget(parent=left_panel, ...)
```

### ❌ DON'T

```python
# 1. Không gọi show() nhiều lần liên tục
confirmation.show()
confirmation.show()  # ❌ Không cần thiết

# 2. Không forget cleanup khi destroy parent
# Widget tự động cleanup khi destroy()

# 3. Không hardcode callback trong constructor cho nhiều actions
# Nên set_confirm_callback() động
```

## 🔧 Customization

### Thay đổi màu sắc

```python
confirmation = ConfirmationWidget(
    parent=frame,
    on_confirm=action,
    bg='#E8F5E9'  # Light green background
)
```

### Thay đổi timeout

```python
# No auto-hide
confirmation = ConfirmationWidget(
    parent=frame,
    on_confirm=action,
    auto_hide_seconds=0  # Disable auto-hide
)

# Quick hide (2 seconds)
confirmation = ConfirmationWidget(
    parent=frame,
    on_confirm=action,
    auto_hide_seconds=2
)
```

## 🧪 Testing

Run the built-in test:

```bash
python ui/components/confirmation_widget.py
```

Hoặc test trong code:

```python
if __name__ == "__main__":
    import tkinter as tk
    from ui.components.confirmation_widget import ConfirmationWidget
    
    root = tk.Tk()
    confirmation = ConfirmationWidget(
        root,
        on_confirm=lambda: print("Confirmed!"),
        on_cancel=lambda: print("Cancelled")
    )
    
    tk.Button(root, text="Show", command=confirmation.show).pack()
    root.mainloop()
```

## 📊 Integration Example

Tích hợp vào Monster Editor:

```python
# In __init__
self.confirmation = ConfirmationWidget(
    parent=self.left_panel,
    on_confirm=lambda: None,
    auto_hide_seconds=5,
    bg='#F2F2F2'
)

# In delete method
def _on_delete_monster(self):
    selected = self.get_selected_monster()
    if not selected:
        return
    
    # Set delete action and show confirmation
    self.confirmation.set_confirm_callback(
        lambda: self._do_delete_monster(selected)
    )
    self.confirmation.show()

def _do_delete_monster(self, monster):
    """Actual delete logic."""
    self.monsters.remove(monster)
    self.refresh_list()
```

## 🎯 Benefits

- **No popup interruption**: Không che cửa sổ chính
- **Fast workflow**: Nhanh hơn popup (không phải move chuột xa)
- **Visual clarity**: Luôn ở vị trí cố định, dễ tìm
- **Reusable**: Một widget cho nhiều actions
- **Customizable**: Dễ dàng thay đổi style, timeout, callbacks

## 📝 Notes

- Widget tự động cleanup khi destroy parent
- Chỉ một confirmation widget hiển thị tại một thời điểm
- Auto-hide có thể disable bằng cách set `auto_hide_seconds=0`
- Callback có thể là lambda hoặc function reference
- Widget không block UI thread (non-modal)

## 🔗 Related Components

- `create_icon_button`: Tạo icon buttons
- `ui.helpers.tooltip`: Tooltip system
- `lib.i18n`: Internationalization

## 📄 License

Part of Cabal_Auto project - Internal use only
