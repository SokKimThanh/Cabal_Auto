# Monster Editor Window Selectors Update

**Date:** 2025-10-25  
**Component:** `ui/windows/quick_monster_editor.py`  
**Related:** `ui/components/window_position_selector.py`, `ui/components/game_window_mode_selector.py`

## 📋 Summary

Updated Monster Editor to use improved window position selectors with:
- No labels (cleaner UI)
- Optimized widths
- Enhanced tooltips
- Show/hide/toggle capabilities

## 🎨 Visual Changes

### Before
```
[Title] [App:][combobox↓] [Game:][combobox↓] [💾 Save][✖ Cancel]
```

### After
```
[Title] [combobox🪟][combobox⬇️] [💾][✖]
```

## 🔧 Technical Changes

### 1. Component Updates

**window_position_selector.py:**
- Width calculation: `max(8, min(max_mode_len + 1, 12))`
- App selector: ~10 characters (normal, topmost, minimized, maximized)
- Added methods: `show()`, `hide()`, `is_visible()`, `toggle()`

**game_window_mode_selector.py:**
- Width reduced: `10 → 8` characters
- Added methods: `show()`, `hide()`, `is_visible()`, `toggle()`

### 2. Monster Editor Updates

**quick_monster_editor.py** (_create_top_panel):

```python
# Before
self.app_mode_selector = create_app_window_selector(
    parent=windows_frame,
    config_path=str(self.hunt_config_path),
    on_mode_change=self._on_app_mode_change,
    show_label=True,                          # ← Removed
    initial_mode='normal'                      # ← Removed (uses config)
)
self.app_mode_selector.pack(side='left', padx=(0, 10))  # ← Changed spacing

# After
self.app_mode_selector = create_app_window_selector(
    parent=windows_frame,
    config_path=str(self.hunt_config_path),
    on_mode_change=self._on_app_mode_change
)
self.app_mode_selector.pack(side='left', padx=(0, 8))
```

**game_window_mode_selector:**
```python
# Before
self.game_mode_selector = create_game_window_selector(
    parent=windows_frame,
    config_path=str(self.hunt_config_path),
    on_mode_change=self._on_game_mode_change,
    show_label=True                           # ← Removed
)

# After
self.game_mode_selector = create_game_window_selector(
    parent=windows_frame,
    config_path=str(self.hunt_config_path),
    on_mode_change=self._on_game_mode_change
)
```

## 📊 Width Comparison

| Selector | Before | After | Reason |
|----------|--------|-------|--------|
| App      | Variable | 10 | Longest mode: "minimized" (9 chars) |
| Game     | 10 | 8 | Longest mode: "below" (5 chars) |

## 🎯 Features

### Enhanced Tooltips

**App Selector:**
```
Điều khiển vị trí cửa sổ ứng dụng
• Normal: Bình thường
• Topmost: Luôn ở trên
• Minimized: Thu nhỏ
• Maximized: Phóng to
```

**Game Selector:**
```
Điều khiển vị trí cửa sổ game
• None: Không làm gì
• Below: Đặt dưới app
• Above: Đặt trên tất cả
```

### New Methods

```python
# Show selector
self.app_mode_selector.show()
self.game_mode_selector.show()

# Hide selector
self.app_mode_selector.hide()
self.game_mode_selector.hide()

# Toggle visibility
self.app_mode_selector.toggle()
self.game_mode_selector.toggle()

# Check visibility
if self.app_mode_selector.is_visible():
    print("App selector is visible")
```

## 🧪 Testing

### Manual Test
```bash
cd e:\Cabal_Auto
python tests/demos/demo_monster_editor_selectors.py
```

### Test Cases

1. **Launch Monster Editor**
   - Verify selectors appear without labels
   - Verify width looks optimal (not too wide)

2. **Tooltip Test**
   - Hover over app selector combobox
   - Verify tooltip shows 4 modes with descriptions
   - Hover over game selector combobox
   - Verify tooltip shows 3 modes with descriptions

3. **Mode Change Test**
   - Change app mode to "topmost"
   - Verify Monster Editor stays on top
   - Change app mode to "minimized"
   - Verify Monster Editor minimizes
   - Change game mode to "below"
   - Verify config saved

4. **Visibility Test**
   ```python
   editor = show_quick_monster_editor(parent=root)
   editor.app_mode_selector.hide()  # Hide app selector
   editor.game_mode_selector.show() # Show game selector
   editor.app_mode_selector.toggle() # Toggle app selector
   ```

## 📝 Integration Points

### Main App (app_gui.py)
Similar pattern applied:
- Topbar selectors updated
- Same width optimization
- Same show/hide methods

### Other Windows
Can apply same pattern to:
- Setup Wizard
- Library Manager
- Vision Wizard
- Any modal dialogs

## 🔍 Key Improvements

1. **Cleaner UI**: No redundant labels, tooltips explain everything
2. **Space Efficient**: Narrower widths, more topbar space
3. **Flexible**: Can hide/show selectors dynamically
4. **Consistent**: Same pattern across all windows
5. **Accessible**: Detailed tooltips for all modes

## 📚 Related Files

- `ui/components/window_position_selector.py` - Universal selector
- `ui/components/game_window_mode_selector.py` - Game-specific selector
- `ui/windows/quick_monster_editor.py` - Monster Editor window
- `app_gui.py` - Main application window
- `tests/demos/demo_monster_editor_selectors.py` - Demo script
- `tests/demos/demo_window_selector_toggle.py` - Toggle demo

## ✅ Checklist

- [x] Remove labels from selectors
- [x] Optimize widths (app: 10, game: 8)
- [x] Add show/hide/toggle methods
- [x] Update tooltips with mode descriptions
- [x] Update Monster Editor integration
- [x] Create demo script
- [x] Test all modes
- [x] Document changes

## 🎓 Usage Examples

### Basic Usage
```python
from ui.windows.quick_monster_editor import show_quick_monster_editor

editor = show_quick_monster_editor(
    parent=main_window,
    monster_id="mon_123",
    on_save=lambda data: print(f"Saved: {data}")
)
```

### Advanced Control
```python
# Hide game selector if not needed
editor.game_mode_selector.hide()

# Only show when hunt starts
def on_hunt_start():
    editor.game_mode_selector.show()

# Toggle based on user preference
if user_wants_simple_ui:
    editor.app_mode_selector.hide()
    editor.game_mode_selector.hide()
```

## 🚀 Next Steps

1. Apply same pattern to other dialogs
2. Add keyboard shortcuts to toggle selectors
3. Consider adding selector visibility to user preferences
4. Add animation for show/hide transitions
