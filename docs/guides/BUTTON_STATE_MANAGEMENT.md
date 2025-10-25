# Button State Management System

## Tổng Quan

Hệ thống quản lý trạng thái button tự động dựa trên selection state. Sử dụng mixin pattern để tái sử dụng code và đảm bảo tính nhất quán.

## Kiến Trúc

```
ui/mixins/
├── __init__.py
└── button_state_mixin.py    # Core mixin class

ui/windows/
├── quick_monster_editor.py  # Đã tích hợp
└── library_manager.py        # Cần tích hợp
```

## Cách Sử Dụng

### 1. Import Mixin

```python
from ui.mixins import ButtonStateMixin

class MyWindow(tk.Toplevel, ButtonStateMixin):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        ButtonStateMixin.__init__(self)
```

### 2. Đăng Ký Widgets

```python
# Đăng ký selection widgets (Treeview/Listbox)
self.register_selection_widget('monster_list', self.monster_tree)
self.register_selection_widget('template_list', self.template_tree)
```

### 3. Đăng Ký Buttons

```python
# Đăng ký buttons cần quản lý state
self.register_button('add_monster', self.add_monster_btn)
self.register_button('edit_monster', self.edit_monster_btn)
self.register_button('delete_monster', self.delete_monster_btn)
```

### 4. Định Nghĩa Rules

```python
# Định nghĩa các rule cho buttons
self.register_button_rules({
    'add_monster': {
        'always': True  # Luôn enabled
    },
    'edit_monster': {
        'requires_selection': 'monster_list'  # Cần chọn monster
    },
    'delete_monster': {
        'requires_selection': 'monster_list'
    },
    'add_template': {
        'requires_parent': 'monster_list'  # Cần chọn monster trước
    },
    'edit_template': {
        'requires_selection': 'template_list'  # Cần chọn template
    },
    'test_template': {
        'requires_multiple': ['monster_list', 'template_list']  # Cần cả 2
    },
    'custom_button': {
        'custom': lambda: self.some_condition()  # Custom logic
    }
})
```

### 5. Update Button States

```python
# Gọi sau mỗi thay đổi state
self.update_button_states()

# Hoặc bind tự động
self.bind_auto_update('monster_list', '<<TreeviewSelect>>')
self.bind_auto_update('template_list', '<<TreeviewSelect>>')
```

## Hierarchical Setup (Parent-Child)

Cho các trường hợp có relationship cha-con (Monster-Template, Category-Item):

```python
self.setup_hierarchical_buttons(
    parent_widget='monster_list',
    child_widget='template_list',
    parent_buttons={
        'add': self.add_monster_btn,
        'edit': self.edit_monster_btn,
        'delete': self.delete_monster_btn
    },
    child_buttons={
        'add': self.add_template_btn,
        'edit': self.edit_template_btn,
        'delete': self.delete_template_btn
    }
)
```

Tự động tạo rules:
- Parent Add: Luôn enabled
- Parent Edit/Delete: Cần chọn parent
- Child Add: Cần chọn parent
- Child Edit/Delete: Cần chọn child

## Button Rule Types

### 1. `always: bool`
Button luôn enabled/disabled

```python
'add_button': {'always': True}
```

### 2. `requires_selection: str`
Button enabled khi có selection trong widget

```python
'edit_button': {'requires_selection': 'item_list'}
```

### 3. `requires_parent: str`
Button enabled khi có selection trong parent widget (hierarchical)

```python
'add_child': {'requires_parent': 'parent_list'}
```

### 4. `requires_multiple: List[str]`
Button enabled khi TẤT CẢ widgets có selection

```python
'test_button': {
    'requires_multiple': ['monster_list', 'template_list']
}
```

### 5. `custom: Callable`
Custom logic function trả về bool

```python
'special_button': {
    'custom': lambda: self.is_admin and self.has_permission()
}
```

## Ví Dụ Hoàn Chỉnh

```python
from ui.mixins import ButtonStateMixin
import tkinter as tk
from tkinter import ttk

class MonsterEditor(tk.Toplevel, ButtonStateMixin):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        ButtonStateMixin.__init__(self)
        
        # Create UI
        self.monster_tree = ttk.Treeview(self)
        self.template_tree = ttk.Treeview(self)
        
        self.add_monster_btn = tk.Button(self, text="Add Monster")
        self.edit_monster_btn = tk.Button(self, text="Edit Monster")
        self.add_template_btn = tk.Button(self, text="Add Template")
        self.test_template_btn = tk.Button(self, text="Test Template")
        
        # Setup button management
        self._setup_button_management()
        
        # Initial update
        self.update_button_states()
        
    def _setup_button_management(self):
        # Register widgets
        self.register_selection_widget('monsters', self.monster_tree)
        self.register_selection_widget('templates', self.template_tree)
        
        # Register buttons
        self.register_button('add_monster', self.add_monster_btn)
        self.register_button('edit_monster', self.edit_monster_btn)
        self.register_button('add_template', self.add_template_btn)
        self.register_button('test_template', self.test_template_btn)
        
        # Define rules
        self.register_button_rules({
            'add_monster': {'always': True},
            'edit_monster': {'requires_selection': 'monsters'},
            'add_template': {'requires_parent': 'monsters'},
            'test_template': {
                'requires_multiple': ['monsters', 'templates']
            }
        })
        
        # Auto-update on selection change
        self.bind_auto_update('monsters')
        self.bind_auto_update('templates')
```

## Migration Guide

### Chuyển Đổi Code Hiện Tại

**Trước (Manual):**
```python
def _update_button_states(self):
    has_monster = bool(self.current_monster_id)
    has_template = bool(self.template_listbox.selection())
    
    if self.add_monster_btn:
        self.add_monster_btn.configure(state='normal')
    if self.edit_monster_btn:
        state = 'normal' if has_monster else 'disabled'
        self.edit_monster_btn.configure(state=state)
    if self.add_template_btn:
        state = 'normal' if has_monster else 'disabled'
        self.add_template_btn.configure(state=state)
    # ... 20+ more lines
```

**Sau (Mixin):**
```python
# In __init__:
ButtonStateMixin.__init__(self)
self.setup_hierarchical_buttons(
    parent_widget='monsters',
    child_widget='templates',
    parent_buttons={'add': self.add_monster_btn, ...},
    child_buttons={'add': self.add_template_btn, ...}
)

# Everywhere else:
self.update_button_states()  # One line!
```

## Lợi Ích

### 1. **Lazy Developer Friendly** 🦥
- Chỉ setup 1 lần
- Tự động update ở mọi nơi
- Không cần remember logic ở mỗi method

### 2. **Consistent Behavior**
- Tất cả windows cùng logic
- Không bị miss edge case
- Easy to maintain

### 3. **Reusable**
- Dùng cho bất kỳ window nào
- Không depend on specific code
- Mix & match với other mixins

### 4. **Easy to Test**
- Logic tập trung
- Mock được widgets
- Test rules độc lập

## API Reference

### ButtonStateMixin

#### Methods

##### `register_button_rules(rules: Dict[str, Dict[str, Any]])`
Đăng ký rules cho buttons

##### `register_selection_widget(name: str, widget: Union[tk.Listbox, ttk.Treeview])`
Đăng ký selection widget

##### `register_button(name: str, button: Union[tk.Button, ttk.Button])`
Đăng ký button cần quản lý

##### `has_selection(widget_name: str) -> bool`
Kiểm tra widget có selection không

##### `get_selection_value(widget_name: str) -> Optional[Any]`
Lấy giá trị selection hiện tại

##### `should_enable_button(button_name: str) -> bool`
Kiểm tra button có nên enabled không

##### `update_button_states()`
Update tất cả button states

##### `bind_auto_update(widget_name: str, event: str = '<<TreeviewSelect>>')`
Tự động update khi selection change

##### `setup_hierarchical_buttons(...)`
Setup nhanh cho parent-child relationship

## Testing

Chạy demo:
```bash
python ui/mixins/button_state_mixin.py
```

## TODO

- [ ] Tích hợp vào LibraryManagerWindow
- [ ] Tích hợp vào AutoHunt window (nếu có buttons)
- [ ] Tạo NotificationMixin tương tự
- [ ] Tạo DirtyStateMixin cho unsaved changes
- [ ] Unit tests

## Tác Giả

SokKimThanh - 2025-10-25
