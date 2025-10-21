# 🔄 Global Hotkey Migration Guide

## 📋 Overview

**Date**: October 21, 2025  
**Version**: Sprint 22+  
**Migration**: F8/F9 → Ctrl+Shift+R/E

This guide helps users migrate from the old F8/F9 hotkey system to the new Ctrl+Shift+R/E global hotkey system.

---

## ❓ Why the Change?

### Old System Issues (F8/F9)
- ❌ **Registered Too Late**: F8 hotkey registered at hunt start, not app init
- ❌ **Not Available Until Hunt**: Couldn't use F8 before starting hunt first time
- ❌ **Inconsistent Behavior**: Mix of window-focused (ESC, Alt+Shift+Z) and global (F8)
- ❌ **Single Key Conflicts**: F8/F9 easily conflicts with games and other apps
- ❌ **Not Customizable**: Hardcoded, users couldn't change

### New System Benefits (Ctrl+Shift+R/E)
- ✅ **Available Immediately**: Registered at app startup
- ✅ **Always Working**: Works even when app minimized or not focused
- ✅ **Less Conflicts**: 3-key combo (Ctrl+Shift+Letter) rarely conflicts
- ✅ **Intuitive**: R = Run/Start, E = End/Stop
- ✅ **Customizable**: Users can change in Setup → Global Hotkeys
- ✅ **Proper Lifecycle**: Registered in `__init__()`, cleaned up in `on_close()`

---

## 🔑 Hotkey Comparison

| **Action** | **Old Hotkeys** | **New Hotkeys** |
|------------|----------------|-----------------|
| Start Hunt | Click "Start Hunt" button<br>Alt+Shift+Z (toggle)<br>F8 (toggle - registered late) | Click "Start Hunt" button<br>**Ctrl+Shift+R** (global) |
| Stop Hunt | Click "Stop Hunt" button<br>ESC (window-focused)<br>Alt+Shift+Z (toggle)<br>F8 (toggle) | Click "Stop Hunt" button<br>**Ctrl+Shift+E** (global) |
| Open Skill Manager | Ctrl+K | Ctrl+K *(unchanged)* |
| Switch Tabs | Alt+1, Alt+2 | Alt+1, Alt+2 *(unchanged)* |

---

## 🚀 Migration Steps

### For New Users
1. ✅ **No action needed** - defaults to Ctrl+Shift+R/E
2. 📖 Check Help tab → Keyboard Shortcuts for reference

### For Existing Users
1. **Update Muscle Memory**:
   - ❌ Old: Press F8 to toggle
   - ✅ New: Press Ctrl+Shift+R to start, Ctrl+Shift+E to stop

2. **Customize if Needed** (Optional):
   - Go to **Setup tab** → **Global Hotkeys** section
   - Change Start/Stop keys if desired (F9, F10, F11, F12, etc.)
   - Click **Global Apply** to activate

3. **Test**:
   - Try Ctrl+Shift+R when app is focused → Hunt should start
   - Minimize app → Try Ctrl+Shift+R again → Hunt should still start
   - Try Ctrl+Shift+E → Hunt should stop

---

## ⚙️ Customization

### Available Hotkey Options
- `ctrl+shift+r` (default for Start)
- `ctrl+shift+e` (default for Stop)
- `ctrl+shift+s`
- `ctrl+alt+r`
- `ctrl+alt+s`
- `f9`
- `f10`
- `f11`
- `f12`

### How to Customize
1. Open **Setup tab**
2. Find **⌨️ Global Hotkeys** section (right side)
3. Uncheck **"Enable Global Hotkeys"** if you want to disable
4. Or select different keys from dropdowns
5. Click **Global Apply** button at bottom
6. Test new hotkeys

### Validation
- ✅ Start and Stop keys must be different
- ✅ Changes only apply after clicking "Global Apply"
- ✅ App will show error if keys conflict

---

## 🐛 Troubleshooting

### Hotkeys Not Working?

**Problem**: Pressing Ctrl+Shift+R/E does nothing

**Solutions**:
1. ✅ Check if enabled: Setup → Global Hotkeys → "Enable Global Hotkeys" is checked
2. ✅ Check if saved: Did you click "Global Apply" after changing?
3. ✅ Restart app: Close and reopen to reload hotkeys
4. ✅ Check conflicts: Another app might be using the same hotkey
5. ✅ Try different keys: Use F9/F10 instead if Ctrl+Shift conflicts

### Hotkeys Working Partially?

**Problem**: Works when focused, not when minimized

**Solution**: Check Windows permissions - some antivirus software blocks global hotkeys. Run app as administrator if needed.

### Want Old F8 Back?

**Solution**: 
1. Go to Setup → Global Hotkeys
2. Change Start key to `f8`
3. Change Stop key to `f9` (or any other key)
4. Click Global Apply
5. **Note**: F8 will now work immediately (unlike before)

---

## 📊 Technical Changes

### For Developers

**Architecture Changes**:
```python
# OLD (Problematic)
def on_hunt_start(self):
    # ... hunt logic ...
    if keyboard is not None:
        self._stop_hotkey = keyboard.add_hotkey('f8', self._toggle_hunt)
    # Registered DURING hunt start ❌

# NEW (Correct)
def __init__(self):
    # ... initialization ...
    self._register_global_hotkeys()  # Registered IMMEDIATELY ✅

def _register_global_hotkeys(self):
    start_key = self.hunt_cfg.get('global_hotkeys', {}).get('start_key', 'ctrl+shift+r')
    stop_key = self.hunt_cfg.get('global_hotkeys', {}).get('stop_key', 'ctrl+shift+e')
    self._global_start_hotkey = keyboard.add_hotkey(start_key, self.on_hunt_start)
    self._global_stop_hotkey = keyboard.add_hotkey(stop_key, self.on_hunt_stop)
```

**Config Structure**:
```json
{
  "global_hotkeys": {
    "enabled": true,
    "start_key": "ctrl+shift+r",
    "stop_key": "ctrl+shift+e"
  }
}
```

**Removed Code**:
- ❌ `_toggle_hunt()` method
- ❌ `_stop_hotkey` variable
- ❌ F8 registration in `on_hunt_start()`
- ❌ F8 cleanup in hunt stop
- ❌ Alt+Shift+Z window-focused binding
- ❌ ESC hunt stop binding

---

## 📚 Related Documentation

- [GLOBAL_HOTKEY_ARCHITECTURE.md](./GLOBAL_HOTKEY_ARCHITECTURE.md) - Technical architecture analysis
- [HOTKEY_F8_TOGGLE.md](./HOTKEY_F8_TOGGLE.md) - ⚠️ **DEPRECATED** - Old F9→F8 migration (superseded by this doc)
- [SINGLE_INSTANCE_LOCK.md](./SINGLE_INSTANCE_LOCK.md) - Single instance enforcement
- [INDEX.md](./INDEX.md) - Documentation index

---

## ✅ Migration Checklist

- [ ] Read this migration guide
- [ ] Update muscle memory: Ctrl+Shift+R (start), Ctrl+Shift+E (stop)
- [ ] Test hotkeys when app focused
- [ ] Test hotkeys when app minimized
- [ ] (Optional) Customize hotkeys in Setup tab
- [ ] (Optional) Read architecture doc for technical details
- [ ] Report issues on GitHub if problems persist

---

## 🎯 Summary

| **Aspect** | **Before** | **After** |
|------------|-----------|-----------|
| Start Hunt | F8 (toggle, late registration) | **Ctrl+Shift+R** (immediate) |
| Stop Hunt | F8 (toggle, late registration) | **Ctrl+Shift+E** (immediate) |
| Availability | After first hunt start | **Immediately on app launch** |
| Customization | None | **Setup → Global Hotkeys** |
| Conflicts | High (single key) | **Low (3-key combo)** |
| Minimize Support | Yes (when registered) | **Yes (always)** |

**Bottom Line**: Ctrl+Shift+R to start, Ctrl+Shift+E to stop. Works immediately, works everywhere. 🚀

---

**Questions?** Check Help tab → Keyboard Shortcuts or open an issue on GitHub!
