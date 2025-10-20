# Window Selection & Hunt Controls - Topbar Enhancement

**Date:** 2025-10-21  
**Status:** ✅ Completed  
**Sprint:** Sprint 20 - UX Enhancements

## 📋 Overview

Major UI redesign to move window selection and hunt controls to the topbar for quick access. This enhancement streamlines the hunt workflow and improves user experience for both new and experienced users.

## 🎯 User Requirements (Vietnamese)

> "thiết kế lại form app, phần hiển thị danh sách của sổ đưa vào combobox, và chọn sẵn cabal đúng với pid đã thiết lập, trường hợp là người mới mà hủy chọn setup thì cũng phải tự bắt đc pid của cabal. đặt nút bắt đầu dừng săn lên cạnh chọn cửa sổ, bỏ label đi và thay bằng tooltip global vào combobox chọn cửa sổ game. tích hợp cả nút đưa lên trước vào thao tác chọn cửa sổ game để chắc rằng cửa sổ game đã đc chọn thật sự. lúc khởi động app thì cũng phải chọn và đưa lên trước tự động."

## ✨ Key Features

### 1. Window Selection Combobox (BATCH 2)
- **Changed:** Entry field → Combobox (readonly)
- **Location:** Topbar, after language selector
- **Auto-Selection:** Automatically selects window matching saved PID
- **Tooltip:** i18n-enabled tooltip explaining window selection
- **Auto Bring-to-Front:** Window automatically brought to front when selected

**Code Changes:**
```python
# app_gui.py line 617-625
self.win_combo = ttk.Combobox(top, textvariable=self.win_combo_var, state='readonly', width=35)
self.win_combo.bind('<<ComboboxSelected>>', self.on_window_combo_selected)
attach_i18n_tooltip(self.win_combo, key='window_select_tooltip', ns=I18N_GLOBAL, lang_provider=lambda: self.lang)
```

### 2. Auto PID Detection (BATCH 3)
- **Trigger:** When new user cancels Setup Wizard
- **Behavior:** Automatically detects Cabal windows and saves first match
- **Config Save:** Saves PID/HWND to `hunt_config.json`
- **UI Update:** Populates combobox with detected window

**Code Changes:**
```python
# app_gui.py line 2045-2090
def _auto_detect_and_save_cabal_window(self):
    """Auto-detect Cabal window PID and save to config when user skips setup."""
    items = self._enum_windows()
    cabal_windows = [w for w in items if 
                    'cabal' in w['title'].lower() or 
                    (w.get('proc') and 'cabal' in w['proc'].lower())]
    # Select first match and save to config
```

### 3. Start/Stop Buttons in Topbar (BATCH 4)
- **Moved From:** Hunt tab control_frame
- **Moved To:** Topbar (after Find Windows button)
- **Design:** Enhanced contrast ratio buttons (CR: 5.8:1 and 6.3:1)
- **Size:** Slightly smaller for topbar (padx=16, pady=6, font=10pt)

**Code Changes:**
```python
# app_gui.py line 631-671
# Buttons now in topbar 'top' frame instead of control_frame
self.hunt_start_btn = tk.Button(top, ...)  # Green button
self.hunt_stop_btn = tk.Button(top, ...)   # Red button
```

### 4. Removed Legacy Components (BATCH 4)
- **Deleted:** `win_listbox` (Listbox widget in Hunt tab)
- **Deleted:** All `win_listbox` references throughout codebase
- **Kept:** Setup Wizard and Save Hunt buttons in control_frame

### 5. Auto Bring-to-Front on Startup (BATCH 5)
- **Trigger:** 1 second after app launch
- **Behavior:** Automatically brings saved Cabal window to front
- **Status Update:** Shows confirmation message for 3 seconds
- **Error Handling:** Gracefully handles missing/closed windows

**Code Changes:**
```python
# app_gui.py line 548
self.after(1000, self._auto_bring_to_front_on_startup)

# app_gui.py line 2144-2179
def _auto_bring_to_front_on_startup(self):
    """Auto bring saved Cabal window to front on app startup."""
    hwnd = self.hunt_selected.get('hwnd')
    ok = self._bring_window_to_front_by_hwnd(hwnd)
```

## 🗂️ File Changes

### Modified Files
1. **`app_gui.py`**
   - Lines 617-671: Topbar redesign (combobox + hunt buttons)
   - Lines 693-708: Removed window listbox section
   - Lines 1670-1705: Updated `on_hunt_find_windows()` for combobox
   - Lines 1771-1790: New `on_window_combo_selected()` handler
   - Lines 2045-2090: New `_auto_detect_and_save_cabal_window()`
   - Lines 2144-2179: New `_auto_bring_to_front_on_startup()`
   - Removed: All `win_listbox` and `win_title_var` references

2. **`lib/i18n/translations.py`**
   - Added `window_select_tooltip` (EN & VI)

## 📊 UI Layout Changes

### Before (Old Layout)
```
[Topbar]
  Language: [vi/en ▼] | 🪟 Window: [____Entry____] [Find] [Bring to Front]

[Hunt Tab]
  ┌─ Select Game Window ────────────┐
  │ [Listbox showing windows]       │
  └─────────────────────────────────┘
  
  ┌─ Monster Rotation ──────────────┐
  │ ...                             │
  └─────────────────────────────────┘
  
  [Setup Wizard] [Save] [▶ Start] [■ Stop]
```

### After (New Layout)
```
[Topbar]
  Language: [vi/en ▼] | [Window Selection Combobox ▼] [Find] | [▶ Start] [■ Stop]
                        ⓘ Tooltip: Select your Cabal window...

[Hunt Tab]
  ┌─ Monster Rotation ──────────────┐
  │ ...                             │
  └─────────────────────────────────┘
  
  [Setup Wizard] [Save]
```

## 🔄 Workflow Changes

### Window Selection Workflow

**Old Flow:**
1. User clicks "Find Windows" button
2. List populates in Hunt tab listbox
3. User selects from listbox
4. User clicks "Bring to Front" button

**New Flow:**
1. User clicks "Find Windows" button
2. Combobox populates in topbar
3. Auto-selects window matching saved PID
4. Window automatically brought to front when selected

### First-Time User Flow

**Old Behavior:**
- Setup Wizard cancellation → No action
- User must manually find and select window

**New Behavior:**
- Setup Wizard cancellation → Auto PID detection
- Automatically finds Cabal window
- Saves PID/HWND to config
- Populates combobox with detected window
- Shows confirmation dialog

### App Startup Flow

**Old Behavior:**
- App loads saved config
- Window data shown but not active
- User must manually bring window to front

**New Behavior:**
- App loads saved config
- Window data populates combobox
- **After 1 second:** Window automatically brought to front
- Status message confirms action

## 🎨 Design Decisions

### Why Combobox Instead of Listbox?
- **Compact:** Takes less space in topbar
- **Familiar:** Standard UI pattern for selection
- **Clean:** No extra section in Hunt tab needed

### Why Auto Bring-to-Front on Selection?
- **Convenience:** One-click action
- **User Intent:** Selecting window implies wanting to use it
- **Immediate Feedback:** User sees window appear

### Why Remove "Bring to Front" Button?
- **Redundant:** Now automatic on selection
- **Simpler UI:** Fewer buttons to understand
- **Space Saving:** More room for hunt controls

### Why Tooltip Instead of Label?
- **Space Efficient:** No permanent label taking space
- **On-Demand Info:** Shows when user hovers
- **Cleaner UI:** Less visual clutter

## 🧪 Testing

### Test Scenarios

1. **New User - Accepts Setup Wizard**
   - ✅ Wizard saves window PID
   - ✅ Combobox populates with window
   - ✅ Window auto brings to front

2. **New User - Cancels Setup Wizard**
   - ✅ Auto PID detection triggers
   - ✅ Finds Cabal windows
   - ✅ Saves first match to config
   - ✅ Shows confirmation dialog
   - ✅ Combobox populated

3. **App Startup - Existing User**
   - ✅ Loads saved window from config
   - ✅ Populates combobox
   - ✅ Auto brings window to front after 1s
   - ✅ Shows status message for 3s

4. **Manual Window Selection**
   - ✅ Click "Find Windows" refreshes list
   - ✅ Combobox shows all Cabal windows
   - ✅ Auto-selects window matching saved PID
   - ✅ Selecting different window brings it to front

5. **Hunt Controls**
   - ✅ Start button accessible in topbar
   - ✅ Stop button accessible in topbar
   - ✅ Visual states work correctly
   - ✅ Buttons maintain enhanced contrast ratio

### Edge Cases Handled

- **No Cabal Window Found:** Shows warning dialog
- **Window Closed After Save:** Gracefully skips bring-to-front
- **Multiple Cabal Windows:** User can select from combobox
- **PID Mismatch:** Selects first window as fallback

## 📈 Benefits

### User Experience
- ✅ **Faster workflow:** Hunt controls in topbar (no scrolling)
- ✅ **Less clicks:** Auto bring-to-front on selection
- ✅ **Better onboarding:** Auto PID detection for new users
- ✅ **Cleaner UI:** Removed redundant listbox section
- ✅ **Immediate readiness:** Window ready on app startup

### Code Quality
- ✅ **Removed legacy code:** Deleted `win_listbox` references
- ✅ **Simplified state:** Single source (combobox + hunt_selected)
- ✅ **Better separation:** Topbar for controls, tabs for content
- ✅ **Consistent patterns:** i18n tooltips throughout

## 🚀 Future Enhancements

### Possible Improvements
- [ ] Add icon for Start/Stop buttons (when icons available)
- [ ] Remember window size/position per PID
- [ ] Multi-window support for multiple characters
- [ ] Window process name in combobox display

### Known Limitations
- Icons skipped (no play/stop/pause icons available)
- Single window support only (no multi-window hunting)

## 📝 Migration Notes

### For Users
- **No action required:** Existing configs auto-migrate
- **What changed:** Window list now in topbar combobox
- **What's removed:** Hunt tab window listbox section

### For Developers
- **Removed:** `self.win_listbox` and `self.win_title_var`
- **Added:** `self.win_combo` and `self.win_combo_var`
- **Changed:** `on_hunt_find_windows()` populates combobox
- **New:** `on_window_combo_selected()` handler
- **New:** `_auto_detect_and_save_cabal_window()` method
- **New:** `_auto_bring_to_front_on_startup()` method

## 🔗 Related Documents

- `ENHANCEMENT_DIALOG_SAVE_ICONS.md` - Save icon enhancement
- `ENHANCEMENT_SAVE_BUTTON_DYNAMIC_TOOLTIP.md` - Save tooltip enhancement
- `COMPLETE_SYSTEM_INTEGRATION.md` - Full system integration guide
- `test_hunt_button_design.py` - Hunt button design tests

---

**Summary:** This enhancement successfully redesigns the window selection and hunt controls UI, moving them to the topbar for quick access. It includes auto PID detection for new users, auto bring-to-front on selection and startup, and removes redundant UI elements for a cleaner, more efficient interface.
