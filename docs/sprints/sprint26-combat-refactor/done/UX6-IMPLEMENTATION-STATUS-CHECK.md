# UX6 Implementation Status Check
**Date:** 2026-09-06  
**Focus:** Compare both UX6 documents against current codebase state

---

## 📋 Document Comparison

| Aspect | PROMPT-UX6-v2-improved.md | PROMPT-UX6-window-detection-and-refresh.md |
|--------|--------------------------|---------------------------------------------|
| **Scope** | Practical, focuses on existing code reuse | Comprehensive, includes service layer design |
| **Timeline** | 15-20 minutes (realistic) | 20-25 minutes (with all phases) |
| **Complexity** | LOW - mostly UI wiring | MEDIUM - needs backend services |
| **Implementation** | Immediate (70% backend exists) | Phased (needs ScreenStateAnalyzer) |
| **Risk** | MINIMAL (reuse existing) | LOW (but more tasks) |

---

## 🔍 Setup Wizard Window Detection Analysis

**Question:** Can setup_wizard.py's window detection be reused for UX6?

**Finding:** ❌ **NO** — UX6 already uses a BETTER implementation

### Comparison

| System | Enumeration | Process Filter | Bounds | State Check | Quality |
|--------|-------------|-----------------|--------|------------|---------|
| **Setup Wizard** | Generic WinAPI | ❌ No (all processes) | ❌ No | ❌ No | Basic |
| **AppWindowController** | WinAPI via WindowManager | ✅ Yes (cabal.exe only) | ✅ Yes | ✅ Yes | Superior |

### What This Means

- ✅ UX6 window detection is ALREADY optimal
- ✅ Uses `AppWindowController._list_windows()` (better than setup wizard)
- ✅ Has process validation, bounds data, minimized detection
- ⚠️ Both systems missing: Multi-region title support (Korean, Polish, Chinese)

### Enhancement Opportunity

Add multi-region title matching to **both** systems:
```python
# Current (both places):
titles = ["Cabal", "CABAL", "cabal"]

# Enhanced (add):
titles = ["Cabal", "CABAL", "cabal",  # English
          "카발", "온라인",                # Korean  
          "Cabała", "Online",              # Polish
          "卡巴尔", "在线"]                 # Chinese
```

**See:** [SETUP-WIZARD-TO-UX6-ANALYSIS.md](SETUP-WIZARD-TO-UX6-ANALYSIS.md) for detailed comparison

---

## ✅ Current Implementation Status

### What EXISTS ✅

#### Window Management (COMPLETE)
- ✅ `AppWindowController` class - handles window enumeration & selection
- ✅ `on_hunt_find_windows()` - enumerates windows automatically
- ✅ `on_hunt_refresh_windows()` - manual refresh with retry logic
- ✅ `on_window_combo_selected()` - saves HWND to config
- ✅ `win_combo` combobox - in action_bar_frame (line 757 in app_gui.py)
- ✅ Refresh button - icon_button component (line 791)
- ✅ Window validation service - `WindowSelectionService.validate_selected_cabal_window()`
- ✅ Process filtering - only allows "cabal.exe" processes
- ✅ Window title matching - includes Cabal, CABAL, cabal variants

#### Scan Button
- ✅ `btn_manual_scan` - icon button in action_bar_frame (line 810)
- ✅ `on_scan_clicked()` callback wired to `scan_controller.run_scan(manual=True)`
- ✅ Scan controller exists - `lib/features/hunt/scan_controller.py`

#### AutoScanner (PARTIAL)
- ✅ `AutoScanner.scan_screen()` - captures and analyzes screen
- ✅ Monster detection pipeline - implemented
- ✅ Skill detection - loads from skills.json and matches templates
- ✅ Character class detection stub - `normalize_and_detect_class()` (returns "Unknown")
- ✅ Window detection - `detect_window()`, `_find_cabal_window()`

#### UI Styling
- ✅ UIStyleV2 integrated - all UI colors and spacing consistent
- ✅ Icon library - has `Icons.SCAN_SCREEN` constant
- ✅ Status chips/badges - already implemented in bounds_placeholder frame

---

### What's MISSING ❌

#### Window Detection - UI Level
- ❌ **NOT in HuntTab directly** - window selection lives in action_bar_frame (main app)
- ⚠️ VX6-v2 assumes window combobox should be in HuntTab - **THIS IS WRONG**
- ✅ Actually CORRECT in app_gui.py where it is now

#### Screen State Display Panel
- ❌ No "Screen State" panel showing extracted info
- ❌ No character class display (Warrior, Mage, etc.)
- ❌ No skill validity indicator (✅ Valid / ⚠️ Invalid count)
- ❌ No location display (Town vs Monster Zone)
- ❌ No monster presence indicator (👹 Found / 🟢 Ready)

#### ScreenStateAnalyzer Service
- ❌ `lib/features/setup/screen_state_analyzer.py` - doesn't exist
- ❌ `scan_screen_state(hwnd)` method - not implemented
- ❌ Character class extraction - stub only
- ❌ Location detection (town vs zone)
- ❌ Monster presence boolean (is_monster_present)
- ❌ Skill validation against detected class

#### Integration Points
- ⚠️ Scan button wired to `scan_controller.run_scan()` - but no UI display of results
- ❌ No state propagation after scan (IDLE_TOWN, IDLE_ZONE, READY_TO_HUNT)
- ❌ No UI update callback after scan completes

---

## 🔧 PROMPT-UX6-v2-improved.md Analysis

### ✅ Correct Aspects
1. **AutoScanner capabilities** - accurately describes `scan_screen()` method
2. **Window enumeration** - correctly identifies `on_hunt_find_windows()` works
3. **Overall timeline** - 15-20 minutes is realistic for what's missing

### ❌ Incorrect Assumptions
1. **Location**: Suggests adding window combobox to HuntTab
   - **Reality:** Window selection already in action_bar_frame (app-level topbar)
   - **Impact:** Don't need to move/duplicate combobox
   - **Fix:** Skip Task 1, 2 - focus only on Tasks 3, 4

2. **Window enumeration on startup**:
   - **Document says:** "Auto-populate window list on app start"
   - **Reality:** Already happens via `on_hunt_find_windows()` 
   - **Status:** No need to add `self.after(500, ...)` - already wired

3. **Screen state display**:
   - **Document structure:** Assumes separate panel below scan button
   - **Reality:** Could integrate with existing status chips or create new panel
   - **Time impact:** Still need to implement (4-5 min)

### 📊 Task Breakdown (Revised)

| Task | Original | Revised | Status |
|------|----------|---------|--------|
| Task 1: Add window combobox | 2 min | ❌ Skip - exists | Not needed |
| Task 2: Auto-enum on startup | 1 min | ❌ Skip - exists | Not needed |
| Task 3: Add scan button | 4 min | ✅ Button exists, need display panel | 3-4 min |
| Task 4: Enable scan logic | 1 min | ✅ Partially done, need UI update | 1 min |
| **NEW**: Implement ScreenStateAnalyzer | — | ✅ Needed | 5-7 min |
| **Total** | 8 min | 10-12 min | Feasible |

---

## 🔧 PROMPT-UX6-window-detection-and-refresh.md Analysis

### ✅ Comprehensive Aspects
1. **Multi-region window detection** - includes Korean, Polish, Chinese titles
2. **Detailed quality gates** - covers 19 acceptance criteria
3. **Validation matrix** - 12 manual test scenarios
4. **Thread safety** - addresses concurrent enumeration locks

### ⚠️ Partially Implemented
1. **Window enumeration** - works but may need multi-region enhancement
   - Current: Only checks ["Cabal", "CABAL", "cabal"]
   - Missing: Korean ("카발"), Polish ("Cabała"), Chinese ("卡巴尔")
   - **Impact:** Won't find non-English game windows
   - **Fix:** Enhance `_find_cabal_window()` in AutoScanner

2. **Screen state analysis** - completely missing
   - Needs: ScreenStateAnalyzer class (5 methods)
   - Needs: Character class detection logic
   - Needs: Location type detection
   - Needs: Monster presence boolean

3. **i18n integration** - keys exist but not all implemented
   - Missing: setup.character_class_label, setup.skills_found, etc.
   - **Impact:** UI will show English hardcoded strings in Vietnamese mode

### 📊 Implementation Roadmap

| Phase | Component | Status | Effort |
|-------|-----------|--------|--------|
| Phase 1 | `WindowDetectionService` | ⚠️ Partial | 2 min (enhance) |
| Phase 1 | `ScreenStateAnalyzer` | ❌ Missing | 5-7 min |
| Phase 2 | Window panel (already exists) | ✅ Done | 0 min |
| Phase 2 | Screen state display panel | ❌ Missing | 3-4 min |
| Phase 3 | State propagation | ⚠️ Stub | 2 min |
| i18n | Translation keys | ⚠️ Partial | 2 min |
| Tests | Unit tests | ❌ Missing | 5 min |
| Manual | Validation scenarios | ⏳ Pending | 8 min |

**Total Realistic Effort: 25-35 minutes**

---

## 🎯 Recommended Implementation Order

### Phase 1: Backend Services (10-12 min)

**1.1 Enhance MultiRegion Window Detection** (2 min)
```python
# File: lib/features/hunt/scanner.py
# Enhance _find_cabal_window() to handle:
# - Korean: "카발", "온라인"
# - Polish: "Cabała", "Online"
# - Chinese: "卡巴尔", "在线"
# Current: Only ["Cabal", "CABAL", "cabal"]
```

**1.2 Implement ScreenStateAnalyzer** (7-9 min)
```python
# File: lib/features/setup/screen_state_analyzer.py (NEW)

class ScreenStateAnalyzer:
    def scan_screen_state(hwnd: int) -> Dict:
        """Returns: {
            'character_class': str,  # 'warrior', 'mage', 'ranger', 'assassin'
            'character_level': int,
            'hp_percent': float,
            'mp_percent': float,
            'location': str,  # 'TOWN' or 'ZONE'
            'has_monster': bool,
            'skill_mismatches': List[Dict]
        }"""
        
    def get_character_class_from_screen(screenshot) -> str:
        """Extract class icon or OCR from UI"""
        
    def detect_location_type(screenshot) -> str:
        """Scan for town NPC markers vs zone indicators"""
        
    def detect_monster_presence(screenshot) -> bool:
        """Check if monsters visible in frame"""
        
    def validate_skill_keys(character_class, skill_config) -> ValidationResult:
        """Compare required_class vs detected_class"""
```

### Phase 2: UI Components (5-6 min)

**2.1 Create Screen State Display Panel** (3-4 min)
```python
# File: ui/panels/screen_state_panel.py (NEW)
# or integrate into hunt_tab.py

Panel shows:
- Character class (icon + name)
- Level + HP%/MP%
- Location (Town/Zone badge)
- Monster presence (Found/Not Found)
- Skill validity (Valid/Invalid count)
- Last scan time
```

**2.2 Wire Scan Button to Display** (1-2 min)
```python
# File: app_gui.py, in on_scan_clicked()

def on_scan_clicked():
    if hasattr(self, "scan_controller"):
        results = self.scan_controller.run_scan(manual=True)
        # Update screen_state_panel with results
        if hasattr(self, "screen_state_panel"):
            self.screen_state_panel.update_from_scan(results)
```

### Phase 3: Integration & i18n (3-4 min)

**3.1 Add i18n Keys** (2 min)
```python
# Missing keys:
setup.character_class_label = "Lớp Nhân Vật:"
setup.skills_found = "✅ {count} kỹ năng phát hiện được"
setup.skills_invalid = "⚠️ Có {n} skill không hợp lệ"
setup.location_town = "📍 Thành Phố"
setup.location_zone = "📍 Khu Vực Quái Vật"
setup.monster_found = "👹 Có Quái Vật"
setup.monster_not_found = "🟢 Sẵn Sàng"
```

**3.2 State Propagation** (1-2 min)
```python
# After scan, update HuntOrchestrator state
# IDLE_TOWN -> don't trigger hunt
# IDLE_ZONE -> ready for hunt
# SCANNING -> UI locked during scan
```

### Phase 4: Testing & Validation (5-8 min)

- Write 4 unit tests (window multi-region, state extraction, validation, location)
- Manual validation (6-8 key scenarios from matrix)

---

## 📊 Current UI Structure (app_gui.py)

```
┌─────────────────────────────────────────────────────────┐
│ action_bar_frame (Zone A)                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ [Window Combo ▼] [🔄] [🔍]  [Status Chips]  [Start] [🌐] [Apply] │
│                                                         │
│ Column layout:                                          │
│ - Col 0: win_combo (380px, weight=2)                   │
│ - Col 1: refresh_btn (44px)                            │
│ - Col 2: scan_btn (44px)                               │
│ - Col 3: bounds_placeholder (260px) ← Add screen_state here? │
│ - Col 4: start_stop_btn (160px)                        │
│ - Col 5: language_combo (80px)                         │
│ - Col 6: global_apply_btn (160px)                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Option A:** Add screen_state info to col 3 (bounds_placeholder)  
**Option B:** Add full panel below action_bar_frame  
**Recommendation:** Option A (reuse existing space, cleaner)

---

## 🚀 Recommended Implementation Path

### **Approach: Hybrid (Practical)**

Combine best of both documents:
- Use **v2-improved** for immediate wins (minimal changes)
- Use **original** for comprehensive spec (backend services, tests)
- Focus on **ScreenStateAnalyzer** which is the biggest gap

### Implementation Timeline

```
Step 1: Enhance MultiRegion Detection      (2 min)   ← Quick win
Step 2: Implement ScreenStateAnalyzer      (7 min)   ← Core missing piece
Step 3: Create Screen State Display Panel  (4 min)   ← UI for results
Step 4: Wire Scan Button to Display        (2 min)   ← Integration
Step 5: Add i18n Keys                      (2 min)   ← Localization
Step 6: Write Tests                        (5 min)   ← Quality
Step 7: Manual Validation                  (5 min)   ← Verification
─────────────────────────────────────────────────────
TOTAL: 27-30 minutes
```

### What NOT to Do (Avoid Rework)

- ❌ Don't move window combobox from action_bar_frame to HuntTab
- ❌ Don't re-implement window enumeration (already works)
- ❌ Don't create separate refresh button (already exists)
- ❌ Don't duplicate on_hunt_find_windows() logic

### What to Focus On

- ✅ Implement `ScreenStateAnalyzer` service (biggest gap)
- ✅ Create screen state display panel (UI for results)
- ✅ Enhance window title matching (multi-region support)
- ✅ Add missing i18n keys
- ✅ Wire scan button to display results

---

## 📝 Decision Matrix

| Requirement | v2-improved | original | Recommended |
|-------------|-------------|----------|-------------|
| **Window Enum** | Exists | Exists | Use existing ✅ |
| **Refresh Button** | Exists | Exists | Use existing ✅ |
| **Scan Button** | Exists | Exists | Use existing ✅ |
| **State Display** | Needs impl | Comprehensive spec | Use spec, keep practical |
| **ScreenStateAnalyzer** | Not mentioned | Detailed spec | Use detailed spec |
| **Testing** | Not mentioned | 4 unit tests | Follow spec |
| **Validation Matrix** | Not mentioned | 12 scenarios | Validation only |

---

## ✅ Verification Checklist

After implementation, verify:

- [ ] Window combobox populates on app startup (≤300ms)
- [ ] Refresh button re-enumerates without duplicate entries
- [ ] Scan button calls `scan_controller.run_scan(manual=True)`
- [ ] Screen state panel displays after scan completes
- [ ] Character class extracted and shown (Warrior/Mage/Ranger/Assassin)
- [ ] Skill validity shown (✅ count or ⚠️ mismatch list)
- [ ] Location shown (📍 Town or 📍 Zone)
- [ ] Monster presence shown (👹 Found or 🟢 Ready)
- [ ] All i18n strings localized (vi/en both visible)
- [ ] No main thread blocking during scan (UI responsive)
- [ ] All 4 unit tests pass
- [ ] Manual validation matrix: 6/6+ scenarios pass

---

## 📚 Reference Files

- **Current Implementation:**
  - `app_gui.py` (line 757-850) - action_bar_frame layout
  - `ui/controllers/app_window_controller.py` - window management
  - `lib/features/hunt/scanner.py` - AutoScanner class
  - `lib/features/hunt/scan_controller.py` - scan orchestration

- **To Create:**
  - `lib/features/setup/screen_state_analyzer.py` (NEW)
  - `ui/panels/screen_state_panel.py` (NEW, or extend hunt_tab)

- **To Enhance:**
  - `lib/features/hunt/scanner.py` - multi-region window detection
  - `lib/i18n/translations.py` - add missing keys

---

**Status:** ✅ Analysis Complete  
**Recommended Action:** Follow hybrid approach (practical v2 + comprehensive backend)  
**Estimated Total Effort:** 25-35 minutes  
**Risk Level:** LOW (most code exists, filling gaps only)
