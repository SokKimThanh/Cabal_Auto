# Pre-Push Component Review - Deep Dive Questions

**Date**: 2026-09-06  
**Focus**: Identify potential issues or gaps BEFORE pushing

---

## Critical Components to Double-Check

### 1. 🎮 Combo Mode → BotManager Integration

**Status**: You implemented AppStateController combo mode methods, but does BotManager actually USE them?

**Questions**:
- [ ] Does BotManager read `app_state._combo_mode_active` to decide execution strategy?
- [ ] When BotManager presses hotkeys, does it call `app_state.update_skill_cooldown()` for each skill?
- [ ] Does BotManager respect the skill sequence order from `skill_slots['attack_combo']` and `skill_slots['buff_lane']`?
- [ ] If a skill fails (target dies, out of range), does BotManager skip or retry?

**Risk**: If BotManager ignores combo mode state, users will see "🟢 COMBO MODE: ACTIVE" but machine won't auto-execute skills.

**Recommendation**: Verify file `lib/features/hunt/bot_manager.py` or wherever skill automation lives:
```python
# Should contain logic like:
if app_state._combo_mode_active:
    skill_to_execute = app_state.skill_slots[current_lane][sequence_index]
    hotkey = skill_to_execute['user_hotkey']
    press_hotkey(hotkey)
    app_state.update_skill_cooldown(lane, position, cooldown_time)
    sleep(cooldown_time)
    sequence_index += 1
```

---

### 2. 📚 Build Tab → Hunt Tab Data Flow

**PROMPT-WL Spec**: Section 3.2a.2 explicitly shows:
```
PHASE 1: BUILD TAB (Skill Build Tab)
  └─ User defines: How many slots? Which skills?
     Result: Preset stored in DB

PHASE 2: HUNT TAB (Hunt Tab - Skill Panel)  
  └─ System loads preset from DB
  └─ Display skills as defined in Build Tab
```

**Questions**:
- [ ] Is there a Build Tab UI where users define "4 attack slots + 2 buff slots"?
- [ ] Does Build Tab store this config in skill_presets as a preset?
- [ ] When Hunt Tab loads, does it load the preset from Build Tab?
- [ ] Or is the number of slots hardcoded (e.g., always 4 attack + 2 buff)?

**Risk**: If hardcoded, users can't customize slot count per class/preset.

**Recommendation**: 
- Verify: `ui/panels/skill_panel.py` - is slot count dynamic or hardcoded?
  ```python
  # WRONG (hardcoded):
  for i in range(4):  # Always 4 slots
      combo = ttk.Combobox(...)
  
  # CORRECT (dynamic):
  attack_count = len(app_state.skill_slots['attack_combo'])
  for i in range(attack_count):  # Load count from preset
      combo = ttk.Combobox(...)
  ```

---

### 3. 🔀 Class Switching During App Runtime

**Scenario**: User is on Hunt Tab with Mage class preset loaded. User switches to Warrior class (e.g., via monster dropdown or class selector).

**Questions**:
- [ ] Does HuntTab detect class change?
- [ ] Does app_state.load_preset_for_class(warrior_class_id) get called?
- [ ] Do skill_slots reload with Warrior skills?
- [ ] Does SkillPanel refresh UI to show new skills?
- [ ] If combo mode was active, does it pause/reset?

**Risk**: User sees stale Mage skills while on Warrior, causing confusion.

**Recommendation**: Verify `HuntTab._build_ui()` or wherever SkillPanel is created:
```python
# Should have listener for class changes:
if hasattr(app, 'on_class_changed'):
    app.on_class_changed.connect(self.on_class_selected)

def on_class_selected(self, new_class_id):
    self.app_state.deactivate_combo_mode()  # Stop if running
    self.app_state.load_preset_for_class(new_class_id)  # Load new preset
    self.skill_panel.refresh()  # Redraw UI
```

---

### 4. ✅ State Consistency After App Crash/Restart

**Scenario**: User saves custom preset, then app crashes. On restart, does state recover?

**Questions**:
- [ ] When app starts, does it restore active_preset_id from user_preset_state table?
- [ ] Or does it always default to is_default=TRUE preset?
- [ ] Is preset_mode persisted? (Should it be?)
- [ ] Are custom presets still in DB after restart?

**Risk**: User loses custom presets or always starts with default.

**Recommendation**: Verify `app_gui.py` initialization:
```python
# On startup, should load persisted state:
def load_persisted_preset_state(class_id):
    state = preset_state_manager.get_preset_mode(class_id)
    active_id = preset_state_manager.get_active_preset(class_id)
    mode = state.get('preset_mode', 'default')
    
    if mode == 'custom' and active_id:
        app_state.apply_preset(active_id, class_id)
    else:
        app_state.apply_default_preset(class_id)
```

---

### 5. 🚫 Duplicate Hotkey Prevention

**Scenario** (if hotkey assignment implemented): User tries to assign hotkey "1" to both Fireball AND Blizzard.

**Questions**:
- [ ] Does app_state.set_skill_hotkey() validate no duplicates?
- [ ] Does UI prevent selecting duplicate hotkeys?
- [ ] What's the error message to user?

**Risk**: User assigns same hotkey to 2 skills → undefined behavior on execution.

**Recommendation**: Add validation in app_state:
```python
def set_skill_hotkey(self, lane: str, position: int, hotkey: str):
    # Check if hotkey already used
    for lane_name in ['attack_combo', 'buff_lane']:
        for slot in self.skill_slots[lane_name]:
            if slot['user_hotkey'] == hotkey and \
               not (slot['lane_type'] == lane and slot['position'] == position):
                raise ValueError(f"Hotkey {hotkey} already assigned to {slot['skill_name']}")
    
    self.skill_slots[lane][position]['user_hotkey'] = hotkey
    self.set_custom_mode()
```

---

### 6. 🧵 Thread Safety: Combo Mode Execution

**Scenario**: Main UI thread updates skill_slots while BotManager thread is reading them.

**Questions**:
- [ ] Is skill_slots access protected by locks?
- [ ] Or is it assumed BotManager only reads during hunt (no updates)?
- [ ] If user pauses/resumes hunt, does state sync correctly?
- [ ] Can UI update preset while hunt running?

**Risk**: Race conditions causing stale data or crashes.

**Recommendation**: Verify `skill_slots` is read-only during hunt:
```python
# SAFE approach:
def update_skill_cooldown(self, lane: str, position: int, remaining: float):
    # BotManager thread calls this - should be atomic
    with self._skill_slots_lock:  # Lock!
        slot = self.skill_slots[lane][position]
        slot['cooldown_remaining'] = remaining
        slot['is_ready'] = (remaining == 0)
```

---

### 7. 🗄️ Database Transaction Handling

**Scenario**: User saves custom preset (multi-row insert: skill_presets + preset_skills) while DB is read by another operation.

**Questions**:
- [ ] Are multi-table operations wrapped in BEGIN TRANSACTION / COMMIT?
- [ ] What happens if preset_skills insert fails after skill_presets inserted?
- [ ] Is rollback automatic or manual?

**Risk**: Orphaned preset rows or inconsistent state.

**Recommendation**: Verify SkillPresetService.create_custom_preset():
```python
def create_custom_preset(self, preset_name: str, class_id: int, skill_slots: Dict):
    conn, is_local = get_connection()
    try:
        conn.execute("BEGIN TRANSACTION")  # Start transaction
        
        # Insert preset
        cursor = conn.execute(
            "INSERT INTO skill_presets (class_id, name, is_default, created_at) VALUES (?, ?, ?, ?)",
            (class_id, preset_name, False, datetime.now())
        )
        preset_id = cursor.lastrowid
        
        # Insert skills
        for lane, slots in skill_slots.items():
            for slot in slots:
                conn.execute(
                    "INSERT INTO preset_skills (preset_id, skill_id, lane, position) VALUES (?, ?, ?, ?)",
                    (preset_id, slot['skill_id'], lane, slot['position'])
                )
        
        conn.commit()  # Commit all or nothing
        return preset_id
    except Exception as e:
        conn.rollback()  # Undo everything
        raise
    finally:
        if is_local and conn:
            conn.close()
```

---

### 8. 🎯 Skill Validity: class_skill_assignments Validation

**Scenario**: User tries to add skill_id=999 (doesn't exist for Mage class) to custom preset.

**Questions**:
- [ ] Does app_state.set_skill_hotkey() or SkillPanel.on_skill_changed() validate skill belongs to class?
- [ ] Does SkillPresetService.create_custom_preset() validate all skills exist?
- [ ] Where is class_skill_assignments checked?

**Risk**: Invalid skill_ids silently stored, hunt fails later.

**Recommendation**: Add validation layer:
```python
# In SkillPresetService:
def validate_skill_for_class(self, skill_id: int, class_id: int) -> bool:
    # Check class_skill_assignments table
    conn, is_local = get_connection()
    try:
        result = conn.execute(
            "SELECT 1 FROM class_skill_assignments WHERE class_id = ? AND skill_id = ?",
            (class_id, skill_id)
        ).fetchone()
        return result is not None
    finally:
        if is_local and conn:
            conn.close()

def create_custom_preset(self, ...):
    # Validate all skills before inserting
    for lane, slots in skill_slots.items():
        for slot in slots:
            if not self.validate_skill_for_class(slot['skill_id'], class_id):
                raise ValueError(f"Skill {slot['skill_id']} not valid for class {class_id}")
```

---

### 9. 📊 Event Callback Chain: Do All Listeners Fire?

**Scenario**: User saves custom preset. Expected chain:
1. SkillPresetService.create_custom_preset() → DB insert
2. app_state calls on_preset_changed()
3. SkillPanel.on_preset_changed() fired
4. SkillPanel updates UI

**Questions**:
- [ ] Is register_callback() implemented and working?
- [ ] Does app_state emit events after state changes?
- [ ] Does SkillPanel listen to all relevant events?
- [ ] Do listeners update UI correctly?

**Risk**: UI doesn't refresh after DB updates (appears broken).

**Recommendation**: Verify AppStateController callback system:
```python
class AppStateController:
    def __init__(self, ...):
        self._callbacks = {
            'on_skill_slots_changed': [],
            'on_preset_changed': [],
            'on_preset_mode_changed': [],
            'on_combo_mode_activated': [],
            'on_combo_mode_deactivated': [],
            # ...
        }
    
    def register_callback(self, event: str, handler):
        if event in self._callbacks:
            self._callbacks[event].append(handler)
    
    def _emit(self, event: str, *args, **kwargs):
        for handler in self._callbacks.get(event, []):
            try:
                handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def apply_preset(self, preset_id, class_id):
        # ... logic ...
        self._emit('on_preset_changed', preset_id)  # Notify listeners
```

---

### 10. 🧹 Cleanup on App Exit

**Scenario**: User closes app while hunt running + combo mode active.

**Questions**:
- [ ] Does background BotManager thread terminate cleanly?
- [ ] Are database connections properly closed?
- [ ] Is state persisted to disk (for next session)?
- [ ] Any dangling OS handles (windows, processes)?

**Risk**: Database locked on next startup, memory leaks.

**Recommendation**: Verify app_gui.py cleanup:
```python
def on_app_closing():
    # Stop active hunt/combo mode
    if hasattr(app, 'hunt_thread') and app.hunt_thread:
        app.hunt_thread.join(timeout=2)  # Wait gracefully
    
    # Close DB connections
    from database import close_all_connections
    close_all_connections()
    
    # Save session state (optional)
    # save_session_state()
    
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_app_closing)
```

---

## Recommended Validation Actions (Before Push)

### Quick Validation (15 minutes)
```bash
# 1. Check for hardcoded slot counts
grep -r "range(4)" ui/panels/skill_panel.py  # Should be dynamic

# 2. Check for BotManager integration
grep -r "combo_mode_active\|update_skill_cooldown" lib/features/hunt/

# 3. Check for class change listeners
grep -r "on_class_changed\|class_id" ui/tabs/hunt_tab.py

# 4. Check transaction handling
grep -r "BEGIN TRANSACTION\|COMMIT\|ROLLBACK" lib/db/repositories/
```

### Manual Testing (30 minutes)
1. **Class Switching**: Select Mage → change skill → switch to Warrior → verify skills update
2. **Combo Mode**: Start hunt → click START COMBO MODE → verify skills execute sequence
3. **Custom Preset**: Load preset → modify skill → click Save → close app → reopen → verify saved
4. **PresetDialog**: Open Presets → apply custom → verify skill_slots update immediately
5. **Edge Case**: Try to delete default preset → should be disabled or show error

### Code Review (20 minutes)
- [ ] BotManager actually calls update_skill_cooldown?
- [ ] skill_slots built dynamically from preset (not hardcoded)?
- [ ] Transactions wrap multi-table operations?
- [ ] Lock/race conditions protected?
- [ ] Event callbacks fire on all state changes?

---

## Sign-Off Checklist

**Before you push, verify:**
- [ ] BotManager integration with combo mode exists and working
- [ ] Slot counts dynamic, not hardcoded
- [ ] Class switching triggers preset reload
- [ ] Custom presets persist across restarts
- [ ] No duplicate hotkey issues
- [ ] Thread-safe skill_slots access
- [ ] Multi-table transactions have COMMIT/ROLLBACK
- [ ] skill_id validity checked against class_skill_assignments
- [ ] Event callback chain complete
- [ ] Cleanup on app exit working

**If you find ANY issues above, document them and plan fixes BEFORE pushing.**

---

## Summary: Most Likely Issues to Find

**Ranked by probability**:

1. 🔴 **HIGH**: BotManager doesn't integrate with combo_mode_active flag
   - Fix: 30 minutes - add combo mode checks to skill execution loop

2. 🔴 **HIGH**: Slot counts hardcoded as 4 + 2
   - Fix: 30 minutes - make dynamic from preset

3. 🟡 **MEDIUM**: No class switching detection in HuntTab
   - Fix: 1 hour - add listener and reload on class change

4. 🟡 **MEDIUM**: No transaction handling for multi-row inserts
   - Fix: 30 minutes - wrap in BEGIN/COMMIT/ROLLBACK

5. 🟡 **MEDIUM**: skill_id validity not checked against class_skill_assignments
   - Fix: 30 minutes - add validation layer

6. 🟢 **LOW**: App crash on exit (cleanup issues)
   - Fix: 15 minutes - add protocol handler

---

**Total time to fix if found**: ~3-4 hours (worst case: all 6 issues)

Would you like me to run any of these validation checks against your code?
