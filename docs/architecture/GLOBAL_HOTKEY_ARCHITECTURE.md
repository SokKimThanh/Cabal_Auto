# Global Hotkey System - Architecture Analysis & Design

## 📋 Current State Analysis | Phân tích hiện trạng

### Existing Hotkeys (As of Oct 21, 2025)

#### 1. **Tkinter Window Bindings** (app_gui.py line 651-655)
```python
self.bind('<Escape>', lambda e: self.on_hunt_stop())              # ESC: Stop hunt
self.bind('<Ctrl-k>', lambda e: self._open_skill_manager())       # Ctrl+K: Manage skills
self.bind('<Alt-Key-1>', lambda e: self._switch_to_tab(0))        # Alt+1: Hunt tab
self.bind('<Alt-Key-2>', lambda e: self._switch_to_tab(1))        # Alt+2: Setup tab
self.bind('<Alt-Shift-Key-Z>', lambda e: self._toggle_hunt())     # Alt+Shift+Z: Toggle hunt
```

**Scope**: Window-focused only (app must be active)

#### 2. **Global Keyboard Hotkey** (app_gui.py line 5283-5288)
```python
# During hunt start
if keyboard is not None and self._stop_hotkey is None:
    try:
        self._stop_hotkey = keyboard.add_hotkey('f8', self._toggle_hunt)
    except Exception:
        self._stop_hotkey = None
```

**Scope**: Global (works even when app is minimized)

---

## 🔍 Issues Identified | Vấn đề phát hiện

### Issue 1: F9/F8 Không hoạt động
**Root Cause**: 
- F8 hotkey chỉ được register khi hunt **start** (line 5283)
- Nếu chưa start hunt → F8 chưa được register → Không hoạt động
- Cleanup không đúng → Có thể bị conflict

**Impact**: Users report F9/F8 không response khi bấm

### Issue 2: Hotkey Inconsistency
- **Alt+Shift+Z**: Window-focused (Tkinter binding)
- **F8**: Global (keyboard library)
- **ESC**: Window-focused (Tkinter binding)

**Impact**: Confusing UX - một số hotkey cần focus, một số không

### Issue 3: No Centralized Config
- Hotkeys hardcoded trong code
- Không có UI để customize
- Không lưu trong config file

**Impact**: Users không thể thay đổi hotkeys theo ý thích

### Issue 4: Cleanup Issues
```python
# Cleanup chỉ remove nếu hunt running
if self._stop_hotkey:
    keyboard.remove_hotkey(self._stop_hotkey)
```

**Impact**: Memory leak potential, hotkey conflicts

---

## 🎯 Design Goals | Mục tiêu thiết kế

### Primary Goals
1. ✅ **Simplify**: 2 hotkeys duy nhất - Start (Ctrl+Shift+R) và Stop (Ctrl+Shift+E)
2. ✅ **Global**: Hoạt động khi app minimize
3. ✅ **Configurable**: UI để thay đổi hotkeys
4. ✅ **Persistent**: Lưu config, persist qua restarts
5. ✅ **Clean**: Proper registration/cleanup lifecycle

### Secondary Goals
1. ✅ Remove legacy hotkeys (Alt+Shift+Z, F8, F9, ESC for hunt)
2. ✅ Keep useful hotkeys (Alt+1/2 for tabs, Ctrl+K for skills)
3. ✅ Add enable/disable toggle
4. ✅ Error handling & fallback

---

## 🏗️ New Architecture | Kiến trúc mới

### 1. Config Structure (hunt_config.json)
```json
{
  "global_hotkeys": {
    "enabled": true,
    "start_key": "ctrl+shift+r",
    "stop_key": "ctrl+shift+e"
  }
}
```

### 2. UI Structure (Setup Tab)
```
Setup Tab
├── Window Settings
├── Hunt Settings
├── Advanced Settings
└── Global Hotkeys ← NEW
    ├── [✓] Enable Global Hotkeys
    ├── Start Hunt: [Ctrl+Shift+R] [Test] [Clear]
    ├── Stop Hunt:  [Ctrl+Shift+E] [Test] [Clear]
    └── ℹ️ Tip: These hotkeys work even when app is minimized
```

### 3. Code Structure
```python
class App(tk.Tk):
    def __init__(self):
        # Hotkey state
        self._global_start_hotkey = None
        self._global_stop_hotkey = None
        self._hotkeys_enabled = True
        
    def _register_global_hotkeys(self):
        """Register global hotkeys from config."""
        if not self._hotkeys_enabled:
            return
            
        config = self.hunt_cfg.get('global_hotkeys', {})
        start_key = config.get('start_key', 'ctrl+shift+r')
        stop_key = config.get('stop_key', 'ctrl+shift+e')
        
        try:
            self._global_start_hotkey = keyboard.add_hotkey(
                start_key, self.on_hunt_start
            )
            self._global_stop_hotkey = keyboard.add_hotkey(
                stop_key, self.on_hunt_stop
            )
        except Exception as e:
            print(f"Failed to register hotkeys: {e}")
    
    def _unregister_global_hotkeys(self):
        """Cleanup global hotkeys."""
        if self._global_start_hotkey:
            keyboard.remove_hotkey(self._global_start_hotkey)
            self._global_start_hotkey = None
        if self._global_stop_hotkey:
            keyboard.remove_hotkey(self._global_stop_hotkey)
            self._global_stop_hotkey = None
    
    def on_close(self):
        """Cleanup on app close."""
        self._unregister_global_hotkeys()
        # ... other cleanup
```

---

## 🔄 Migration Strategy | Chiến lược chuyển đổi

### Phase 1: Cleanup (Batch 1-2)
1. Remove `<Alt-Shift-Key-Z>` binding
2. Remove `<Escape>` hunt stop binding (keep for other uses)
3. Remove F8 keyboard.add_hotkey
4. Remove `_toggle_hunt()` method (no longer needed)

### Phase 2: Implement Core (Batch 3-5)
1. Add config structure to hunt_config.json
2. Implement `_register_global_hotkeys()`
3. Implement `_unregister_global_hotkeys()`
4. Call register in `__init__()` after config load
5. Call unregister in `on_close()`

### Phase 3: UI & Settings (Batch 6-7)
1. Add Global Hotkeys section in Setup tab
2. Add enable/disable checkbox
3. Add hotkey entry fields with validation
4. Add Test & Clear buttons
5. Integrate with `on_global_apply()`

### Phase 4: Testing & Docs (Batch 8-10)
1. Test all scenarios
2. Update translations (EN/VI)
3. Update README.md
4. Create migration guide

---

## 📊 Comparison: Old vs New

| Feature | Old System | New System |
|---------|-----------|------------|
| **Hotkeys** | Alt+Shift+Z, F8, F9, ESC | Ctrl+Shift+R, Ctrl+Shift+E |
| **Registration** | Mixed (Tkinter + keyboard lib) | Unified (keyboard lib only) |
| **Scope** | Mixed (focused + global) | Fully global |
| **Lifecycle** | Start hunt → register F8 | App init → register all |
| **Cleanup** | Partial (only F8) | Complete (all hotkeys) |
| **Config** | Hardcoded | Configurable (UI + config file) |
| **Customizable** | ❌ No | ✅ Yes (via Setup tab) |
| **Enable/Disable** | ❌ No | ✅ Yes (checkbox) |
| **Error Handling** | Minimal | Robust (try-except + fallback) |

---

## 🧪 Testing Strategy | Chiến lược kiểm tra

### Test Matrix

| Scenario | Steps | Expected Result |
|----------|-------|-----------------|
| **Basic Start** | Press Ctrl+Shift+R | Hunt starts |
| **Basic Stop** | Press Ctrl+Shift+E while hunting | Hunt stops |
| **Minimized Start** | Minimize app → Press Ctrl+Shift+R | Hunt starts (app can restore to front) |
| **Minimized Stop** | Hunt running, minimize → Press Ctrl+Shift+E | Hunt stops |
| **Disabled Hotkeys** | Uncheck "Enable" → Press hotkeys | No action (hotkeys disabled) |
| **Custom Hotkeys** | Change to Ctrl+Alt+S/E → Apply → Test | Custom hotkeys work |
| **Config Persistence** | Set custom hotkeys → Restart app | Hotkeys persist |
| **Cleanup** | Close app during hunt | Hotkeys properly unregistered |
| **Conflict Detection** | Set conflicting hotkey (e.g., Ctrl+C) | Error message shown |

### Edge Cases
1. **Keyboard library not available** → Graceful fallback (disable hotkeys, show warning)
2. **Invalid hotkey string** → Validation error, prevent save
3. **System hotkey conflict** → Catch exception, show error
4. **Rapid press** → Debounce logic to prevent double-trigger

---

## 🔒 Security & Safety | An toàn

### Considerations
1. **System-wide hotkeys**: Can trigger from any app → Need clear visual feedback
2. **Accidental trigger**: Ctrl+Shift+R/E less likely than F8 to press accidentally
3. **Disable option**: Users can turn off if conflicts with other apps
4. **Clear indication**: Status bar shows "Hunt Started (Ctrl+Shift+E to stop)"

---

## 📝 Implementation Checklist | Danh sách triển khai

### Pre-Implementation
- [x] Analyze current hotkey system
- [x] Identify issues (F8/F9 not working)
- [x] Design new architecture
- [x] Create TODO batches (10 tasks)
- [x] Document migration strategy

### Implementation (TODO Batches 1-10)
- [ ] Batch 1: Remove old hotkeys code
- [ ] Batch 2: Implement new Ctrl+Shift+R/E
- [ ] Batch 3: Create UI in Setup tab
- [ ] Batch 4: Add config structure
- [ ] Batch 5: Integrate Global Apply
- [ ] Batch 6: Update translations
- [ ] Batch 7: Update README
- [ ] Batch 8: Testing
- [ ] Batch 9: Migration guide
- [ ] Batch 10: Final validation

### Post-Implementation
- [ ] User acceptance testing
- [ ] Performance monitoring
- [ ] Gather feedback
- [ ] Iterate if needed

---

## 🚀 Benefits | Lợi ích

### For Users
1. ✅ **Simpler**: 2 hotkeys instead of 4-5
2. ✅ **More intuitive**: Ctrl+Shift+R (Run), Ctrl+Shift+E (End)
3. ✅ **Always work**: Global scope, no focus needed
4. ✅ **Customizable**: Can change via UI
5. ✅ **Reliable**: Proper lifecycle management

### For Developers
1. ✅ **Cleaner code**: Centralized registration/cleanup
2. ✅ **Maintainable**: Config-driven, not hardcoded
3. ✅ **Testable**: Clear test matrix
4. ✅ **Debuggable**: Proper error handling
5. ✅ **Extensible**: Easy to add more hotkeys later

---

## 📚 References | Tài liệu tham khảo

- **keyboard library**: https://github.com/boppreh/keyboard
- **Tkinter bindings**: https://tkdocs.com/tutorial/events.html
- **Current implementation**: app_gui.py lines 651-655, 5283-5288
- **Issue report**: "khi bắt đầu start thì không bấm f9 để dừng lại được"

---

## ✅ Success Criteria | Tiêu chí thành công

### Must Have
1. ✅ Ctrl+Shift+R starts hunt (global)
2. ✅ Ctrl+Shift+E stops hunt (global)
3. ✅ Hotkeys work when app minimized
4. ✅ Old hotkeys (Alt+Shift+Z, F8, F9) removed
5. ✅ Config UI in Setup tab
6. ✅ Settings persist across restarts

### Nice to Have
1. ✅ Visual feedback when hotkey pressed
2. ✅ Conflict detection
3. ✅ Test button in UI
4. ✅ Hotkey recording (press to capture)

---

**Status**: Architecture design complete ✅  
**Next Step**: Start Batch 1 - Remove old hotkeys  
**Estimated Timeline**: 2-3 hours for full implementation  
**Priority**: High (user-reported issue)

---

**Author**: GitHub Copilot + SokKimThanh  
**Date**: October 21, 2025  
**Version**: 1.0
