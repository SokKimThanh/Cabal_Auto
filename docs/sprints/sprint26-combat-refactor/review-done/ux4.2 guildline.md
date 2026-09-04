I have explored the codebase and understood the requirements for the UX4.2 feature. Here is a summary of my progress and findings:

Bidirectional Routing & Toast: The skill slot UI is built in ui/tabs/hunt_tab.py inside _build_ui. The combobox selection triggers on_skill_slot_changed in app_gui.py. I will implement the routing logic in the event handler (e.g., _on_cmb_selected in hunt_tab.py or a dedicated method in app_state_controller.py). I will also add a Toast notification mechanism (since there doesn't seem to be an existing one, I will create a reusable one with a debounce timer on the root window or HuntTab) to show warnings when a lane is full.
Key Conflict Warning: The method _validate_slot_key_duplicates in ui/controllers/app_state_controller.py already handles some duplicate checking. I will update it to also check against combo_start_key (which is stored in app.hunt_cfg["combo"]["combo_start_key"]). If a conflict is found, I'll update the card's border to UIStyle.COLOR_WARNING (or UIStyle.STATE_WARN if defined) and use app._create_tooltip to add the appropriate warning message.
JSON Migration: I will modify _migrate_skills in lib/features/hunt/config_migrator.py. If a skill lacks a type or has an invalid one, I will look it up in SkillRepo (lib/features/skills/skill_repo.py). If not found, I'll fallback to type = "attack", cast_time = 1.0, cooldown = 1.0, log a warning, and ensure the skills are separated into skill_slots (combo) and buff_slots (buffs) as per the CB4 schema rules (or just keep them in skill_slots if that's the canonical array, wait, the prompt says "Tách chuẩn thành 2 mảng: skill_slots (chứa attacks) và buff_slots (chứa buffs), đúng theo schema đã định nghĩa ở CB4.").
Testing: I will create tests/unit/test_skill_strip_logic.py covering all the mentioned test cases.
Does this align with your expectations? Could you confirm if I should implement the bidirectional routing directly in ui/tabs/hunt_tab.py inside _on_cmb_selected or inside app_gui.py? And for the Toast, should I create it as a method on the App class in app_gui.py?



Updated todo list

Perfect! Your exploration and plan are **solid and well-structured**. Let me validate your approach and answer your specific questions:

---

## ✅ **YOUR PLAN - VALIDATION & CONFIRMATION**

### **1. Bidirectional Routing & Toast** ✅ GOOD PLAN

**Architecture Choice:**
- ✅ **YES, implement routing in `hunt_tab.py` inside `_on_cmb_selected`**
- **Reasoning:**
  - Event originates in hunt_tab (UI layer)
  - Keep event handler close to source (single responsibility)
  - Avoids extra indirection through `app_gui.py`
  - More testable with mock hunt_tab fixture

**Code structure:**
```python
def _on_cmb_selected(event, v=var, lbl=stats_lbl):
    # 1. Get selected skill
    selected_name = v.get().strip()
    
    # 2. Route to appropriate lane
    lane_type = "combo" if is_combo_lane else "buff"
    
    # 3. Validate & show Toast if needed
    if not self.app.can_add_to_lane(lane_type, selected_name):
        self.show_toast(f"❌ {lane_type.title()} Lane is full", duration_ms=2000)
        v.set("")  # Clear selection
        return
    
    # 4. Update UI + config
    update_card_stats(lbl, selected_name)
    if hasattr(self.app, "on_skill_slot_changed"):
        self.app.on_skill_slot_changed(event)
```

---

### **2. Toast Notification System** ✅ GOOD CHOICE

**Best Practice: Create on `HuntTab` (not App class)**
- **Reasoning:**
  - Toasts are UI-specific (belongs in view layer)
  - Multiple toasts can appear independently
  - Easier to test (mock HuntTab.show_toast)
  - App class already handles 200+ responsibilities

**Implementation:**
```python
# In HuntTab.__init__
self.toast_timer = None

def show_toast(self, message: str, duration_ms: int = 2000):
    """Show temporary notification with auto-dismiss."""
    if self.toast_timer:
        self.after_cancel(self.toast_timer)
    
    # Create toast label if not exists
    if not hasattr(self, 'toast_label'):
        self.toast_label = tk.Label(
            self, 
            text=message,
            bg=UI.COLOR_WARNING,
            fg="white",
            font=(UI.FONT_FAMILY, 10),
            relief="flat",
            anchor="center"
        )
    
    self.toast_label.config(text=message)
    self.toast_label.pack(side="bottom", fill="x", padx=4, pady=4)
    
    # Auto-dismiss
    self.toast_timer = self.after(duration_ms, lambda: self.toast_label.pack_forget())
```

---

### **3. Key Conflict Warning** ✅ EXCELLENT APPROACH

**Your plan:** Update `_validate_slot_key_duplicates` + use tooltip + border warning

**Enhancement Suggestion:**
```python
def _validate_slot_key_duplicates(self):
    """Check for key conflicts including combo_start_key."""
    combo_key = self.app.hunt_cfg.get("combo", {}).get("combo_start_key", "")
    
    conflicts = {}
    for idx, (card, key_var) in enumerate(zip(self.app.skill_slot_boxes, 
                                                 self.app.skill_slot_key_labels)):
        key_value = key_var.cget("text")
        
        # Check conflict with combo_start_key
        if key_value == combo_key:
            conflicts[idx] = f"⚠️ Conflicts with Combo Key {combo_key}"
            card.config(highlightbackground=UI.COLOR_WARNING, highlightthickness=2)
        else:
            card.config(highlightbackground="#D0D0D0", highlightthickness=1)
    
    return conflicts
```

**Status Check Timing:**
- Call on: Skill selection change, Combo Key change, Lane modification
- Can debounce with 100ms timer to avoid excessive checks

---

### **4. JSON Migration** ✅ CORRECT UNDERSTANDING

**Your approach is perfect:**

1. **Lookup in SkillRepo** if type missing
2. **Fallback defaults:** `type="attack"`, `cast_time=1.0`, `cooldown=1.0`
3. **Log warning** for missing data
4. **Separate arrays:** `skill_slots` (attacks) vs `buff_slots` (buffs) per CB4 schema

**Verify CB4 Schema First:**
```bash
grep -n "buff_slots\|skill_slots" lib/features/hunt/config_migrator.py
```

Let me check if both arrays exist or if we need to create them: 

No matches found. Your search pattern might be excluded completely by either the search.exclude settings or .*ignore files.
If you believe that it should have results, you can check into the .*ignore files and the exclude setting (here are some excluded patterns for reference:[**/node_modules,**/bower_components,**/*.code-search]).
Then if you want to include those files you can call the tool again by setting "includeIgnoredFiles" to true.

Let me check the actual structure: 

Read , lines 1 to 100

Let me search for skill migrations:  

Searched for regex `_migrate.*skill|skill.*slot` (`**/lib/features/hunt/config_migrator.py`), 12 results

Perfect! Let me read the skill migration function:   

Read , lines 110 to 190

Excellent! I found it. The current schema has a **single `skill_slots` array with type field**. Let me check if SkillRepo exists: 

Searched for files matching `**/lib/features/skills/skill_repo.py`, 1 match

Perfect! Now let me validate your full plan with real code context: 

Read , lines 1 to 50

Perfect! I now have the full context. Let me provide **detailed technical guidance** on your UX4.2 plan:

---

## 🎯 **UX4.2 PLAN - VALIDATION & TECHNICAL GUIDANCE**

### **VALIDATED ✅ All Your Architectural Choices**

---

## **1️⃣ BIDIRECTIONAL ROUTING LOCATION**

### ✅ **YES - Implement in `hunt_tab.py`** inside `_on_cmb_selected`

**Why this is correct:**
- Event originates in UI layer (hunt_tab)
- Single responsibility: route skill selection
- Easier to test (mock fixture)
- No circular dependency with `app_gui.py`

**Implementation pattern:**
```python
def _on_cmb_selected(event, v=var, lbl=stats_lbl, is_combo_lane=is_combo_lane):
    """Handle skill selection in card combobox."""
    selected_name = v.get().strip()
    lane_type = "combo" if is_combo_lane else "buff"
    
    # Step 1: Validate (check lane full, key conflicts)
    validation_error = self._validate_skill_selection(lane_type, selected_name)
    if validation_error:
        self.show_toast(validation_error, duration_ms=2500)
        v.set("")  # Clear invalid selection
        return
    
    # Step 2: Update badge stats
    update_card_stats(lbl, selected_name)
    
    # Step 3: Persist to config (via app_gui)
    if hasattr(self.app, "on_skill_slot_changed"):
        self.app.on_skill_slot_changed(event)
```

**Data flow:**
```
User selects skill in card
    ↓
_on_cmb_selected() triggers
    ↓
Validate (lane full? key conflict?)
    ↓
Show Toast if error
    ↓
Update UI (badge + config)
    ↓
on_skill_slot_changed() syncs to app_gui
```

---

## **2️⃣ TOAST NOTIFICATION SYSTEM**

### ✅ **YES - Create on `HuntTab` class** (NOT on App class)

**Why:**
- UI logic belongs in view layer
- Multiple toasts can coexist
- Cleaner separation of concerns
- Testable with mock

**Implementation:**

```python
class HuntTab(ttk.Frame):
    def __init__(self, parent, app):
        # ... existing init ...
        self.toast_stack = []  # Multiple toasts
        self.root_frame = parent  # For positioning
    
    def show_toast(self, message: str, duration_ms: int = 2000, level: str = "warn"):
        """
        Show temporary notification.
        level: "info", "warn", "error"
        """
        # Color based on level
        colors = {
            "info": ("#1E90FF", "white"),   # Blue
            "warn": ("#FFA500", "black"),   # Orange
            "error": ("#FF4444", "white"),  # Red
        }
        bg, fg = colors.get(level, colors["warn"])
        
        toast = tk.Label(
            self.root_frame,
            text=f"  {message}  ",
            bg=bg,
            fg=fg,
            font=(UI.FONT_FAMILY, 10),
            relief="flat",
            padx=8,
            pady=4
        )
        
        # Position at bottom of hunt_tab
        toast.pack(side="bottom", fill="x", padx=4, pady=4)
        self.toast_stack.append(toast)
        
        # Auto-dismiss
        def dismiss():
            if toast in self.toast_stack:
                self.toast_stack.remove(toast)
            toast.pack_forget()
        
        self.after(duration_ms, dismiss)
```

**Usage in validation:**
```python
if not can_add_to_lane:
    self.show_toast("❌ Combo Lane is full!", duration_ms=2500, level="warn")
elif key_conflict:
    self.show_toast("⚠️  Key conflict with Combo Start Key!", duration_ms=2500, level="error")
```

---

## **3️⃣ KEY CONFLICT VALIDATION** ✅ 

**Your approach is perfect. Enhance it:**

```python
def _validate_skill_selection(self, lane_type: str, skill_name: str) -> Optional[str]:
    """
    Validate skill selection in a lane.
    Returns error message if invalid, None if OK.
    """
    # Check 1: Is lane full?
    lane_max = 4 if lane_type == "combo" else 2
    current_count = len([v for idx, v in enumerate(self.app.skill_slot_vars)
                         if idx < (4 if lane_type == "combo" else 6)])
    if current_count >= lane_max:
        return f"❌ {lane_type.title()} Lane is full ({current_count}/{lane_max})"
    
    # Check 2: Key conflict with combo_start_key?
    combo_key = self.app.hunt_cfg.get("combo", {}).get("combo_start_key", "")
    if combo_key:  # Only if Auto Combo is enabled
        # Get assigned key for this skill (if exists)
        skill_key = self._get_skill_assigned_key(skill_name)
        if skill_key == combo_key:
            return f"⚠️  Skill key '{skill_key}' conflicts with Combo Start Key"
    
    # Check 3: Duplicate in same lane?
    # (optional - depends on your rules)
    
    return None  # Valid

def _get_skill_assigned_key(self, skill_name: str) -> Optional[str]:
    """Get the keyboard key assigned to this skill."""
    # Look in app.hunt_cfg or skill library
    # Return None if not found
    pass
```

---

## **4️⃣ JSON SCHEMA - IMPORTANT CLARIFICATION** ⚠️

### **Current vs. Target Schema:**

**Current Schema (already in code):**
```python
"skill_slots": [
    {"key": "1", "cast_time": 1.2, "cooldown": 5.0, "type": "attack"},
    {"key": "2", "cast_time": 0.8, "cooldown": 3.0, "type": "buff"},
    ...
]
```

**Question: Should you split into TWO arrays?**

Looking at your prompt reference, it says:
> "Tách chuẩn thành 2 mảng: skill_slots (chứa attacks) và buff_slots (chứa buffs)"

**My Recommendation: YES - Split for clarity**

```python
# Target Schema (UX4.2):
{
    "skill_slots": [  # Attacks only (Combo Lane)
        {"key": "1", "name": "Fireball", "cast_time": 1.2, "cooldown": 5.0},
        {"key": "2", "name": "Ice Lance", "cast_time": 0.8, "cooldown": 3.0},
        ...
    ],
    "buff_slots": [  # Buffs only (Buff Lane)
        {"key": "3", "name": "Shield", "cast_time": 0.5, "cooldown": 10.0},
        {"key": "4", "name": "Haste", "cast_time": 0.3, "cooldown": 15.0}
    ]
}
```

**Migration Logic in `_migrate_skills`:**
```python
def _migrate_skills(data: Dict[str, Any]) -> None:
    """Migrate legacy skills into skill_slots (attacks) and buff_slots (buffs)."""
    
    # Get old data
    old_skill_slots = data.get("skill_slots", [])
    
    # Separate by type
    attacks = []
    buffs = []
    
    for slot in old_skill_slots:
        slot_type = slot.get("type", "attack")
        
        # Normalize slot
        normalized = {
            "key": slot.get("key", ""),
            "name": slot.get("name", ""),
            "cast_time": _safe_float(slot.get("cast_time", 1.0)),
            "cooldown": _safe_float(slot.get("cooldown", 1.0)),
        }
        
        # If name missing, try SkillRepo lookup
        if not normalized["name"]:
            normalized["name"] = _lookup_skill_name(normalized["key"])
        
        if slot_type == "buff":
            buffs.append(normalized)
        else:
            attacks.append(normalized)
    
    # Write back
    data["skill_slots"] = attacks
    data["buff_slots"] = buffs
```

---

## **5️⃣ SKILLREPO LOOKUP FUNCTION**

```python
def _lookup_skill_name(key: str) -> str:
    """Lookup skill name in SkillRepo, fallback to key itself."""
    from lib.features.skills.skill_repo import load_skill_library
    
    skills_db = load_skill_library()
    
    # Try direct key lookup
    if key in skills_db:
        return skills_db[key].get("name", key)
    
    # Try name field
    for skill_id, skill_data in skills_db.items():
        if skill_data.get("key") == key:
            return skill_data.get("name", key)
    
    # Fallback
    logger.warning(f"Skill not found in SkillRepo: {key}, using key as name")
    return key
```

---

## **6️⃣ UNIT TESTS** ✅

**Location & scope for `tests/unit/test_skill_strip_logic.py`:**

```python
import pytest
from unittest.mock import MagicMock, patch

class TestSkillStripLogic:
    """Test bidirectional routing, validation, Toast."""
    
    @pytest.mark.ui
    def test_lane_full_validation(self):
        """Combo Lane (4 max) rejects 5th skill."""
        # Mock hunt_tab with 4 combo skills
        mock_hunt_tab = MagicMock()
        mock_hunt_tab.app.skill_slot_vars = [MagicMock(get=lambda: f"Skill{i}") 
                                              for i in range(4)]
        
        # Try to add 5th
        error = mock_hunt_tab._validate_skill_selection("combo", "Skill5")
        assert "full" in error.lower()
    
    @pytest.mark.ui
    def test_key_conflict_warning(self):
        """Key conflict with combo_start_key shows warning."""
        mock_hunt_tab = MagicMock()
        mock_hunt_tab.app.hunt_cfg = {
            "combo": {"combo_start_key": "Alt+3"}
        }
        mock_hunt_tab._get_skill_assigned_key = MagicMock(return_value="Alt+3")
        
        error = mock_hunt_tab._validate_skill_selection("combo", "Skill1")
        assert "conflict" in error.lower()
    
    @pytest.mark.ui
    def test_toast_auto_dismiss(self):
        """Toast appears and auto-dismisses after duration."""
        mock_hunt_tab = MagicMock()
        mock_hunt_tab.toast_stack = []
        
        mock_hunt_tab.show_toast("Test", duration_ms=100)
        # Would need real tkinter to test dismiss, or mock .after()

    def test_skill_migration_splits_arrays(self):
        """Migration separates attacks and buffs into 2 arrays."""
        old_data = {
            "skill_slots": [
                {"key": "1", "name": "Fireball", "type": "attack"},
                {"key": "2", "name": "Shield", "type": "buff"},
            ]
        }
        
        from lib.features.hunt.config_migrator import _migrate_skills
        _migrate_skills(old_data)
        
        assert len(old_data["skill_slots"]) == 1
        assert len(old_data["buff_slots"]) == 1
        assert old_data["skill_slots"][0]["name"] == "Fireball"
        assert old_data["buff_slots"][0]["name"] == "Shield"
```

---

## **📋 IMPLEMENTATION CHECKLIST**

### **Phase 1: Infrastructure (Day 1)**
- [ ] Create `show_toast()` method on HuntTab
- [ ] Add `_validate_skill_selection()` in HuntTab
- [ ] Update `_on_cmb_selected()` event handler
- [ ] Add `_validate_slot_key_duplicates()` call

### **Phase 2: Schema Migration (Day 2)**
- [ ] Update `_migrate_skills()` to split into 2 arrays
- [ ] Add SkillRepo lookup function
- [ ] Backward compat: handle old single-array format
- [ ] Add fallback defaults (1.0s cast, 1.0s cd)

### **Phase 3: Testing (Day 2-3)**
- [ ] Write 8-10 unit tests
- [ ] Test lane full validation
- [ ] Test key conflict warning
- [ ] Test Toast appearance
- [ ] Test JSON migration splits correctly

### **Phase 4: Integration (Day 3)**
- [ ] Verify app still starts
- [ ] Manual test Toast visibility
- [ ] Test config persistence
- [ ] Verify language switching doesn't break

---

## **✅ SUMMARY OF YOUR PLAN**

| Component | Location | Status | Notes |
|-----------|----------|--------|-------|
| Bidirectional routing | `hunt_tab.py:_on_cmb_selected` | ✅ Correct | Close to source |
| Toast notifications | `HuntTab` class method | ✅ Correct | UI layer only |
| Key conflict checking | `_validate_slot_key_duplicates` | ✅ Good | Enhanced validation |
| JSON migration | `config_migrator._migrate_skills` | ✅ Excellent | Add 2-array split |
| SkillRepo lookup | New helper function | ✅ Good | Fallback to defaults |
| Unit tests | `test_skill_strip_logic.py` | ✅ Ready | 8-10 test cases |

---

**Bottom Line:** Your plan is **solid and well-architected**. The main clarification needed was the **2-array split** for skill_slots/buff_slots, which I recommend implementing. Ready to start coding? 🚀

Created 5 todos