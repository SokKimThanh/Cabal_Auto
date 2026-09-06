# UX6: Window Detection & Refresh — Enumerate Game Windows & Manual Screen State Scan

**Phase:** Post-UX5.2 Setup Phase  
**Sprint:** Sprint 26 (Combat Refactor)  
**Timeline:** 20-25 minutes  
**Complexity:** Medium (UI + Service + Screen Scanning Integration)

---

## 📋 **Feature Overview**

**Problem:** When app starts, user cannot easily select which window is the Cabal game. Need manual way to:
1. List all available game windows
2. Refresh the list if game window not yet open
3. Manually select the game window
4. Scan screen to extract current character/skill/monster state

**Solution:** Implement manual window selection with screen state scanning:
1. **Stage 1 - App Startup:** Enumerate game windows → populate combobox
2. **Stage 2 - Refresh Button:** User refreshes list if game not yet detected
3. **Stage 3 - User Selection:** User manually selects the game window from combobox
4. **Stage 4 - Manual Scan Button:** User clicks "Scan" button to extract screen state (character class, skill config, monster presence)

---

## 🎯 **Requirements**

### R1: App Startup — Enumerate & Display Game Windows
- **Trigger:** App launches
- **Action:** 
  1. Enumerate all visible windows on system
  2. Filter for game windows (using criteria below)
  3. Populate combobox with list
- **Output:** Combobox shows list of game windows (or empty if none found)
- **UI State:** Show spinner during enumeration (200-300ms)
- **i18n Keys:**
  - `setup.window_label`: "Cửa sổ Game" / "Game Window"
  - `setup.window_searching`: "⏳ Đang liệt kê cửa sổ..." / "⏳ Enumerating windows..."
  - `setup.window_none`: "(Không tìm thấy)" / "(None found)"

### R2: Refresh Button — Re-enumerate Game Windows
- **Trigger:** User clicks "Refresh" button next to combobox
- **Action:** 
  1. Clear combobox
  2. Re-enumerate all visible windows
  3. Filter for game windows
  4. Repopulate combobox
- **Output:** Updated list in combobox
- **UI State:** Show spinner during enumeration (200-300ms), disable button during scan
- **i18n Keys:**
  - `setup.refresh_btn`: "Làm mới" / "Refresh"

### R3: Game Window Identification — Criteria for Detection

**Primary Criteria (Title Matching):**
- Window title contains one of:
  - "Cabal" (English)
  - "카발" (Korean)
  - "Cabała" (Polish)
  - "卡巴尔" (Chinese)
  - Case-insensitive matching

**Secondary Criteria (Process Validation):**
- Process executable name matches:
  - "Cabal.exe" OR "CabalOnline.exe" OR "Cabal" (exact prefix)
- NOT a launcher/updater process (exclude "CabalLauncher.exe", "CabalUpdater.exe")

**Tertiary Criteria (Window State):**
- Window is visible (not hidden)
- Window class name contains: "DirectXWindowClass" OR "UnityWndClass" OR generic window class
- Exclude minimized windows (unless user previously selected a minimized window)

**Fallback Criteria (Visual Signature) — Optional:**
- Window resolution: typically 800x600 or higher, 16:9 aspect ratio
- Window title format: exactly matches Cabal game window format (not login screen, not menu)

**Exclusion Filters:**
- Exclude system windows (Windows Explorer, Task Manager, etc.)
- Exclude other game windows (League of Legends, Valorant, etc.)
- Exclude Cabal launcher or login screen (user must run actual game client)

**Examples:**
```
✅ Valid Game Windows:
   - "Cabal Online - [Character Name]"
   - "카발 온라인"
   - "Cabal"
   - "카발"

❌ Invalid (Exclude):
   - "CabalLauncher"
   - "Cabal Updater"
   - "C:\\Games\\Cabal\\..." (file path, not game window)
```

### R4: User Selection — Manual Window Selection
- **Trigger:** User selects a window from combobox
- **Action:** 
  1. Store selected window HWND
  2. Save to config.json
  3. Show selected window title in combobox
- **Output:** Selected window is now active game window
- **No automatic state scan** (wait for user to click Scan button)

### R5: Manual Scan Button — Extract Screen State
- **Trigger:** User clicks "Scan" button (after selecting window)
- **Action:**
  1. Scan game window screenshot
  2. Extract character class (Warrior, Mage, Ranger, Assassin)
  3. Extract character level/HP/MP
  4. Validate skill-key bindings against character class
  5. Detect location (Town vs Monster Zone)
  6. Detect monster presence
  7. Update UI with extracted state
- **Output:** Display character class, skill validity, location status
- **UI State:** Show spinner during scan (300-500ms), show results in dedicated panel
- **i18n Keys:**
  - `setup.scan_btn`: "Quét" / "Scan"
  - `setup.scanning`: "⏳ Đang quét màn hình..." / "⏳ Scanning screen..."
  - `setup.character_class_label`: "Class: {class}" / "Class: {class}"
  - `setup.character_level_label`: "Lv. {level}" / "Lv. {level}"
  - `setup.skill_status_valid`: "✅ Tất cả skill hợp lệ" / "✅ All skills valid"
  - `setup.skill_status_invalid`: "⚠️ Có {n} skill không hợp lệ" / "⚠️ {n} skills not valid"
  - `setup.location_town`: "📍 Thành Phố" / "📍 Town"
  - `setup.location_zone`: "📍 Khu Vực Quái Vật" / "📍 Monster Zone"
  - `setup.monster_detected`: "👹 Có Quái Vật" / "👹 Monster Detected"
  - `setup.ready_idle`: "🟢 Sẵn Sàng" / "🟢 Ready"

---

## 💾 **Current Code State**

### Window Detection (Needs to be checked/enhanced)
**File:** [lib/system/window_manager.py](lib/system/window_manager.py)
- Current: `find_window_by_title()`, `restore_window()`, `set_foreground()` exist
- Missing: `enumerate_all_game_windows()` ← NEEDS IMPLEMENTATION
- Missing: Window title pattern matching for multi-region

**File:** [lib/system/process_detector.py](lib/system/process_detector.py)  
- Status: Unknown (check if exists)
- Need: Process name matching (Cabal.exe, CabalLauncher.exe)

### UI Components for Refresh/Search
**File:** [ui/tabs/setup_tab.py](ui/tabs/setup_tab.py) (or similar setup location)
- Current: Likely has window combobox + manual select
- Missing: Refresh button
- Missing: Search button
- Missing: Loading spinner during scan
- Missing: Toast notification system

**File:** [app_gui.py](app_gui.py)
- Location: Check where setup tab is initialized (should be in sidebar "Thiết lập nhanh" / "Setup" section based on DS6)
- Need: Wire up refresh/search buttons to service layer

### Screen State Analysis
**File:** [lib/features/hunt/hunt_orchestrator.py](lib/features/hunt/hunt_orchestrator.py)
- Current: Has `start_hunt_loop()`, `stop_hunt_loop()`
- Missing: `analyze_screen_state()` method to detect character class, skill validity, monster presence
- Integration point: Call after window selection

**File:** [lib/vision/character_detector.py](lib/vision/character_detector.py) (or similar)
- Status: Check if character class detector exists
- Need: Extract class from UI (mage, warrior, ranger, assassin, etc.)
- Pattern: Class icon location, color matching, template matching

**File:** [lib/vision/monster_detector.py](lib/vision/monster_detector.py) (or CB1 existing)
- Current: `TargetBarDetector` exists (CB1)
- Use: Same logic for initial scan

### i18n Integration
**File:** [lib/i18n/translations.py](lib/i18n/translations.py)
- Action: Add 10+ new keys (see R1-R3 sections above)
- Format: Vietnamese/English key pairs as existing pattern

---

## 🔄 **Implementation Plan**

### Phase 1: Backend Services (8 minutes)
1. **WindowDetectionService** (new file: `lib/features/setup/window_detection_service.py`)
   - Method: `enumerate_game_windows() → List[WindowInfo]`
     - Enumerate all visible windows using Windows API (ctypes or pygetwindow)
     - Filter by game window criteria (see R3 above)
     - Return: `[{hwnd, title, process_name, is_visible}, ...]`
     - Return empty list if no game windows found
   - Thread safety: Use `threading.Lock()` to prevent concurrent enumeration

2. **ScreenStateAnalyzer** (new file: `lib/features/setup/screen_state_analyzer.py`)
   - Method: `scan_screen_state(hwnd) → ScreenState`
     - Capture screenshot of game window
     - Extract character class UI element (icon, text, color)
     - Extract character level/HP/MP from status bar
     - Validate skill-key bindings: compare assigned skills vs detected class
     - Detect location (Town vs Monster Zone) via UI indicators
     - Detect monster presence via existing CB1 template matching
     - Return: `{class, level, hp_percent, mp_percent, location, has_monster, skill_mismatches}`
   - Method: `get_character_class_from_screen(screenshot) → str`
     - Template matching or OCR for class detection
     - Return: one of ["warrior", "mage", "ranger", "assassin"] or "unknown"
   - Method: `validate_skill_keys(character_class, skill_config) → ValidationResult`
     - Compare each skill's `required_class` with detected `character_class`
     - Return: `{is_valid, mismatches: [{skill_name, detected_class, required_class}]}`
   - Method: `detect_location_type(screenshot) → LocationType`
     - Scan for town UI elements (NPC icon, shops)
     - Return: "TOWN" or "ZONE"
   - Method: `detect_monster_presence(screenshot) → bool`
     - Use existing CB1 `TargetBarDetector` logic
     - Return: True if monster health bar detected

### Phase 2: UI Components (9 minutes)
1. **Setup Tab — Window Selection Panel** (`ui/tabs/setup_tab.py` or new)
   - Label: "Cửa sổ Game" / "Game Window"
   - Combobox: Display list of enumerated game windows
     - Show window title for each entry
     - Allow user to select manually
     - On selection: Store HWND to config.json
   - "Refresh" button next to combobox
     - Icon: 🔄 or ↻
     - Tooltip: "Làm mới danh sách" / "Refresh list"
     - On click: Re-enumerate and repopulate combobox
     - Show loading spinner during enumeration (200-300ms)
   - Loading spinner (animated overlay during enumerate)
   - Disable Refresh button during enumeration (prevent double-click)

2. **Setup Tab — Screen Scan Panel** (new section below window selection)
   - Label: "Quét Thông Tin Màn Hình" / "Screen State Analysis"
   - "Scan" button
     - Icon: 🔍 or 📊
     - Tooltip: "Quét cập nhật thông tin" / "Scan and update screen state"
     - Enabled only after window selected
     - On click: Call `ScreenStateAnalyzer.scan_screen_state(hwnd)`
     - Show loading spinner during scan (300-500ms)
     - Disable button during scan
   - Results panel (display after scan completes):
     - Character class: "⚔️ Warrior, Lv. 50"
     - HP/MP status: "HP: 800/1000, MP: 300/500"
     - Location: "📍 Thành Phố" or "📍 Khu Vực Quái Vật"
     - Monster status: "👹 Có Quái Vật" or "🟢 Sẵn Sàng"
     - Skill validity:
       - ✅ "Tất cả skill hợp lệ" (if all valid)
       - ⚠️ "Có {n} skill không hợp lệ" (if mismatches)
       - If mismatches, show collapsible list with details

### Phase 3: Integration & State Flow (3 minutes)
1. **App Startup Flow:**
   ```
   app_gui.py.__init__()
       ↓
   on_app_startup()
       ↓
   WindowDetectionService.enumerate_game_windows()
       ↓
   Populate combobox with list
       ↓
   Load stored HWND from config.json (if exists)
       ↓ [Stored HWND found & still valid]
       Auto-select in combobox
       ↓ [Not found or invalid]
       Show empty combobox (wait for user to refresh/select)
   ```

2. **User Selection Flow (when user selects window in combobox):**
   ```
   on_window_combobox_select(hwnd)
       ↓
   Store HWND to config.json
       ↓
   Enable "Scan" button
       ↓ [Manual]
       Wait for user to click "Scan" button
   ```

3. **Refresh Button Flow:**
   ```
   on_refresh_button_click()
       ↓
   Show loading spinner
       ↓
   self.after(50, enumerate_windows_async)
       ↓
   WindowDetectionService.enumerate_game_windows()
       ↓
   Clear combobox
       ↓
   Repopulate with new list
       ↓
   Auto-select previous window if still in list
       ↓
   Hide loading spinner
   ```

4. **Manual Scan Button Flow:**
   ```
   on_scan_button_click()
       ↓
   Check if window selected (if not, disable button)
       ↓
   Show loading spinner
       ↓
   self.after(50, scan_screen_async)
       ↓
   ScreenStateAnalyzer.scan_screen_state(hwnd)
       ↓
   Extract: character_class, level, hp, mp, location, has_monster, skill_mismatches
       ↓
   Update UI: Display character class, location, monster status, skill validity
       ↓
   Hide loading spinner
       ↓ [Location = TOWN]
       HuntOrchestrator.set_state(IDLE_TOWN)
       ↓ [Location = ZONE & has_monster]
       HuntOrchestrator.start_hunt_scan()  # Use existing CB1 logic
       ↓ [Location = ZONE & no_monster]
       HuntOrchestrator.set_state(IDLE_ZONE)
   ```

---

## 🧪 **Validation Tests**

### Unit Tests: `tests/unit/test_window_detection.py`

**Test 1: Enumerate Windows — Filter by Title & Process**
```python
def test_enumerate_windows_filters_by_criteria():
    """Verify only valid Cabal game windows are returned"""
    service = WindowDetectionService()
    windows = service.enumerate_game_windows()
    for w in windows:
        assert ('Cabal' in w.title or '카발' in w.title or 'Cabała' in w.title)
        assert ('Cabal.exe' in w.process_name or 'CabalOnline.exe' in w.process_name)
        assert w.is_visible
    # Pass if 0 windows (no Cabal running) or N>0 valid windows
```

**Test 2: Scan Screen State — Extract Character Class**
```python
def test_scan_screen_state_extracts_character_class():
    """Verify character class is correctly extracted from screen"""
    analyzer = ScreenStateAnalyzer()
    hwnd = get_test_window_hwnd()  # Mock or use test VM
    state = analyzer.scan_screen_state(hwnd)
    assert state.character_class in ['warrior', 'mage', 'ranger', 'assassin', 'unknown']
    assert state.level > 0
    assert state.hp_percent >= 0 and state.hp_percent <= 100
```

**Test 3: Skill Validation — Detect Class Mismatch**
```python
def test_validate_skill_keys_detects_mismatch():
    """Verify skill-class mismatch is detected"""
    analyzer = ScreenStateAnalyzer()
    skill_config = {
        'Q': {'skill': 'Fireball', 'required_class': 'mage'},  # Mismatch
        'W': {'skill': 'Slash', 'required_class': 'warrior'}    # Match
    }
    result = analyzer.validate_skill_keys('warrior', skill_config)
    assert len(result.mismatches) == 1
    assert result.mismatches[0].skill_name == 'Fireball'
```

**Test 4: Location Detection — Town vs Zone**
```python
def test_detect_location_type_distinguishes_town_vs_zone():
    """Verify town vs zone detection"""
    analyzer = ScreenStateAnalyzer()
    screenshot = get_test_screenshot()  # Mock screenshot
    location = analyzer.detect_location_type(screenshot)
    assert location in ['TOWN', 'ZONE']
```

### Integration Tests: `tests/integration/test_window_detection_flow.py`

**Test 5: Full Flow — Enumerate → Select → Scan**
```python
def test_full_window_detection_and_scan_flow():
    """Verify complete flow: enumerate → select → scan → state"""
    app = App()
    
    # Step 1: App startup should enumerate
    time.sleep(0.3)
    windows_count = len(app.window_combobox['values'])
    assert windows_count >= 0  # OK if 0 (no Cabal running)
    
    # Step 2: Click refresh
    app.refresh_btn.invoke()
    time.sleep(0.3)
    windows_count_after = len(app.window_combobox['values'])
    assert windows_count_after >= 0
    
    # Step 3: If windows available, select one
    if windows_count_after > 0:
        app.window_combobox.current(0)
        assert app.scan_btn.cget('state') == 'normal'  # Should enable scan
        
        # Step 4: Click scan
        app.scan_btn.invoke()
        time.sleep(0.5)
        
        # Verify results displayed
        assert app.character_class_label.cget('text') != ''
        assert app.location_label.cget('text') != ''
```

### Manual Validation Matrix

| Scenario | User Action | Expected Behavior | Acceptance Criteria |
|----------|-------------|-------------------|---------------------|
| **S1: App Startup** | Launch app | Enumerate game windows, populate combobox | ✅ Combobox shows windows or "(None found)" |
| **S2: No Cabal Running** | Launch app (no Cabal) | Combobox empty or shows non-Cabal windows filtered out | ✅ Combobox empty, Scan button disabled |
| **S3: Cabal Running** | Launch app (Cabal open) | Combobox shows Cabal window automatically | ✅ Combobox auto-selects window, Scan button enabled |
| **S4: Refresh Button** | Click Refresh | Re-enumerate windows, update combobox within 300ms | ✅ Spinner shows, list updates, <300ms |
| **S5: Manual Selection** | User selects window from combo | Store HWND to config.json, enable Scan button | ✅ Selection saved, Scan button enabled |
| **S6: Scan — Character Detected** | Click Scan with game open | Extract character class, level, HP | ✅ "⚔️ Warrior, Lv. 50" displays |
| **S7: Scan — Skill Valid** | Scan with all skills matching class | Show "✅ Tất cả skill hợp lệ" | ✅ Skill validity indicator shows valid |
| **S8: Scan — Skill Invalid** | Scan with mismatched skills | Show "⚠️ Có N skill không hợp lệ" + list | ✅ Warning shows, collapsible list appears |
| **S9: Scan — Location Town** | Scan while in town (NPC visible) | Show "📍 Thành Phố", skip monster detection | ✅ Location label = Town, no background scan |
| **S10: Scan — Location Zone + Monster** | Scan in zone with monster | Show "📍 Khu Vực Quái Vật" + "👹 Có Quái Vật", trigger hunt scan | ✅ Location = Zone, monster indicator, hunt state updates |
| **S11: Scan — Location Zone, No Monster** | Scan in zone, no monster | Show "📍 Khu Vực Quái Vật" + "🟢 Sẵn Sàng" | ✅ Location = Zone, ready indicator |
| **S12: i18n Validation** | Toggle language (vi/en) | All UI strings update correctly | ✅ Vi/En both visible, no hard-coded text |

---

## 📁 **Code Structure**

```
lib/features/setup/
    ├── window_detection_service.py     (NEW) — Window enumeration & search
    ├── screen_state_analyzer.py        (NEW) — Character class, skill validation, location detection
    └── __init__.py

ui/tabs/
    └── setup_tab.py                    (MODIFY) — Add refresh/search buttons, state display

lib/system/
    └── window_manager.py               (ENHANCE) — Add enumerate_all_game_windows()

lib/i18n/
    └── translations.py                 (MODIFY) — Add 10+ new i18n keys

app_gui.py                              (MODIFY) — Wire up refresh/search, auto-detect on startup

tests/unit/
    └── test_window_detection.py        (NEW) — 6 unit tests

tests/integration/
    └── test_window_detection_flow.py   (NEW) — 1 full integration test
```

---

## ⏱️ **Timeline Breakdown**

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 1 | Implement `WindowDetectionService.enumerate_game_windows()` | 3 min | ⏳ Pending |
| 1 | Implement `ScreenStateAnalyzer.scan_screen_state()` + helpers | 5 min | ⏳ Pending |
| 2 | Add Window Selection panel (combobox + Refresh button) | 4 min | ⏳ Pending |
| 2 | Add Screen Scan panel (Scan button + results display) | 4 min | ⏳ Pending |
| 2 | Add loading spinners for both operations | 2 min | ⏳ Pending |
| 3 | Wire up state flow in `app_gui.py` (startup, combobox select, scan) | 3 min | ⏳ Pending |
| 3 | Integrate `HuntOrchestrator` state propagation (IDLE_TOWN/ZONE/SCANNING) | 2 min | ⏳ Pending |
| i18n | Add 15+ new translation keys | 2 min | ⏳ Pending |
| Tests | Write 4 unit tests (enumerate, scan, validation, location) | 4 min | ⏳ Pending |
| Manual | Validation matrix (12 scenarios × 2-3 resolutions) | 8 min | ⏳ Pending |
| **TOTAL** | | **20-25 min** | ⏳ Pending |

---

## ✅ **Quality Gate Criteria**

**Gate: Window Detection & Screen State Analysis Ready**

| Criterion | Pass | Fail |
|-----------|------|------|
| **Functionality** | Startup enumerates windows (≤300ms) | Takes >300ms or crashes |
| **Functionality** | Refresh button re-enumerates and updates combobox (≤300ms) | Takes >300ms or shows duplicate entries |
| **Functionality** | Window select stores HWND and enables Scan button | HWND not persisted or Scan disabled |
| **Functionality** | Scan button captures and analyzes screen within 500ms | Takes >500ms or throws exception |
| **Display** | Character class, level, HP extracted and shown | Missing UI labels or incorrect extraction |
| **Display** | Skill validity shown (✅ or ⚠️ with count) | Always shows valid or missing indicator |
| **Display** | Location shown ("📍 Thành Phố" or "📍 Khu Vực Quái Vật") | Always shows one or both missing |
| **Display** | Monster detected indicator shown when in zone | Monster presence not indicated |
| **State** | After scan, HuntOrchestrator.state = IDLE_TOWN/IDLE_ZONE | State not updated or wrong value |
| **i18n** | All strings configurable in i18n keys (vi/en) | Hard-coded strings found |
| **Threading** | Main thread not blocked during enum/scan (no freezing) | UI freezes during operations |
| **UX** | Loading spinner shows during scan (clear visual feedback) | No spinner or instant (looks broken) |
| **UX** | Character class, skill validity, location displayed after scan | Missing fields or incorrect values |
| **Logging** | Each step logged (enum, find, analyze, validate) with timestamp | Silent failures or no trace |
| **Thread Safety** | No concurrent window enumeration (lock prevents double-enum) | Race condition in enum |
| **Integration** | Hunt state propagates (IDLE_TOWN, IDLE_ZONE, SCANNING) | State not updated or incorrect |
| **i18n** | All UI strings use translation keys (vi/en both visible) | Hard-coded strings or missing languages |
| **Tests** | All 6 unit tests pass, 1 integration test passes | Any test fails or assertion errors |
| **Manual** | Validation matrix: 7/7 scenarios pass | Any scenario fails or regression |

**Gate Pass Condition:** ✅ All criteria **Pass**  
**Gate Fail Condition:** ❌ Any criterion **Fail** → Iterate (fix + re-test)

---

## 🔗 **Dependencies & Context**

### External Libraries
- `ctypes` (Windows API) — For `enumerate_game_windows()`
- `pygetwindow` or `win32gui` — Window enumeration helper
- Existing: `opencv2`, `PIL` — For screen state analysis

### Architecture Constraints
- **No Main Thread blocking:** Use `self.after()` for all UI/service calls
- **No `time.sleep()`:** All delays via `self.after(ms, fn)`
- **Callback Pattern:** Service → UI via `schedule_ui_task` callback
- **Thread Safety:** Lock on shared resources (window enum, screen capture)

### Related Features
- **UX5.2:** HP throttling + recovery (already implemented)
- **CB1:** `TargetBarDetector.get_hp_percentage()` (reuse for location scan)
- **DS6:** Layout refactor (window setup in correct sidebar position)

---

## 📝 **Implementation Notes**

1. **Window Title Matching:**
   - Korean: "카발" (Cabal in Korean)
   - Chinese: "卡巴尔" (if supported)
   - English: "Cabal", "Cabal Online"
   - Polish: "Cabała"
   - Case-insensitive matching

2. **Character Class Detection:**
   - Option A (Recommended): Use existing skill hotkey config → infer from assigned skills
     - If Q/W/E are mage-only spells → Mage
     - Fallback: Scan UI element for class icon
   - Option B: Template matching for class icon location
   - Option C: OCR on class name label (if visible)

3. **Location State Detection:**
   - **Town Indicator:** Look for NPC names (vendor, skill trainer) or known town layout
   - **Monster Zone:** Absence of town NPCs + monster health bar present (use existing CB1 detector)
   - **Fallback:** Assume zone (conservative, less spam)

4. **Skill Validation Data:**
   - Source: Extract from `skill_config.json` + skill database (existing)
   - Each skill has `required_class` field
   - Build validation matrix on app startup (cache for fast lookup)

5. **Performance Optimization:**
   - Cache `enumerate_game_windows()` result for 5 seconds (prevent spam)
   - Cache `analyze_character_state()` result for 10 seconds (character class rarely changes)
   - Use background thread for screen capture (non-blocking UI)

---

## 🎯 **Success Metrics**

After implementation, measure:
- **User doesn't need manual refresh:** On-startup auto-detect success rate >90%
- **Search latency:** Find game window in <2 seconds (including screen analysis)
- **False positives:** No non-game windows selected as game window
- **Skill warnings:** All skill-class mismatches detected and warned
- **Location accuracy:** Town vs zone detection >95% (manual validation)
- **No Main Thread stalls:** All operations complete without visible UI freeze

---

## 🚀 **Next Phase (UX7)**

After UX6 complete:
- **UX7: Hotkey Rebind & Skill Assignment** — Allow user to reassign skills to hotkeys in UI with live validation
- **UX8: Hunt Profile Save/Load** — Save character config + skill setup as reusable profile
- **UX9: Multi-Character Support** — Store & switch between multiple character profiles

---

**Prompt Version:** 1.0  
**Last Updated:** 2026-09-05  
**Status:** Ready for Implementation  
**Approval:** Pending
