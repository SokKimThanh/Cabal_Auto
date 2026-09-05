# ✅ IMPROVED PROMPT UX6: Window Detection — Practical Edition

**Status**: Revised based on actual codebase  
**Reality Check**: 70% of backend exists; 30% UI work needed  
**Timeline**: 15-20 minutes (realistic)  
**Sprint**: Sprint 26 (Combat Refactor)

---

## 📋 Feature Overview — What's Actually Needed

The UX6 feature should integrate **existing code** from:
- `WindowManager` (already complete)
- `AutoScanner.scan_screen()` (already complete)
- `AppWindowController` (85% done, needs UI wiring)

Goal: **Move window selection from SetupWizard into main HuntTab + display screen state**

---

## 🎯 Revised Requirements (Based on What Exists)

### **R1: App Startup — Show Window Combobox in HuntTab**

**Current State:**
- ✅ `AppWindowController._list_windows()` works
- ✅ `on_hunt_find_windows()` callback exists
- ❌ But combobox NOT in HuntTab, only in SetupWizard

**What to Do:**
1. In `app_gui.py` **startup** (not setup wizard), call:
   ```python
   self.on_hunt_find_windows()  # Enumerate windows
   ```
2. Add combobox to HuntTab topbar:
   ```
   ┌─────────────────────────────────┐
   │ Game Window: [Cabal Online    ▼] [Refresh] │
   │                                     │
   └─────────────────────────────────────┘
   ```
3. Auto-populate combobox with results

**Time**: 3 minutes (copy existing code, move to HuntTab)

---

### **R2: Refresh Button — Re-enumerate Windows**

**Current State:**
- ✅ `on_hunt_find_windows()` method exists
- ✅ `on_hunt_refresh_windows()` callback exists
- ❌ But button NOT in HuntTab UI

**What to Do:**
1. Add "Refresh" button next to combobox
2. Wire button to: `self.on_hunt_find_windows()`
3. Show spinner during enum (200-300ms)

**Time**: 2 minutes

---

### **R3: Window Selection — Store HWND**

**Current State:**
- ✅ `on_window_combo_selected()` exists
- ✅ Saves to `self.hunt_selected` and config.json
- ❌ But UI not hooked up

**What to Do:**
1. Wire combobox selection to: `self.on_window_combo_selected()`
2. Validate using: `WindowSelectionService.validate_selected_cabal_window()`

**Time**: 1 minute (just wire callback)

---

### **R4: Manual Scan Button — Extract & Display Screen State**

**Current State:**
- ✅ `AutoScanner.scan_screen()` extracts character class, skills, monsters
- ✅ `AutoScanner.run_scan()` saves results to DB
- ❌ But UI doesn't display results

**What to Do:**
1. Add "🔍 Scan" button to HuntTab
2. When clicked:
   ```python
   def on_scan_button_click():
       scanner = AutoScanner(self.vision_engine)
       results = scanner.run_scan()
       # Display results in panel
   ```
3. Create **Screen State Display Panel** showing:
   - Character class (e.g., "Warrior")
   - Skill validity: ✅ Valid (4/6 skills detected)
   - Location: 📍 Thành Phố (Town) or 📍 Khu Vực Quái (Monster Zone)
   - Monster presence: 🎯 Found / ❌ None

**Time**: 5 minutes

---

## 🔧 Implementation Tasks (Realistic)

### **Task 1: Add Window Combobox to HuntTab** (2 min)

**File**: `ui/tabs/hunt_tab.py`

**Location**: Top of tab, right after title

**Code**:
```python
# In HuntTab.__init__ or _build_ui():
window_frame = tk.Frame(self.app.hunt_setup_frame)  # Reuse existing frame
window_frame.pack(fill="x", padx=10, pady=5)

label = tk.Label(window_frame, text="Cửa sổ Game:")
label.pack(side="left", padx=5)

self.window_combo = ttk.Combobox(
    window_frame,
    values=[],
    state="readonly",
    width=40
)
self.window_combo.pack(side="left", padx=5)
self.window_combo.bind("<<ComboboxSelected>>", self.on_window_selected)

refresh_btn = tk.Button(
    window_frame,
    text="🔄 Làm Mới",
    command=self.on_refresh_windows
)
refresh_btn.pack(side="left", padx=5)
```

**Wire to AppWindowController**:
```python
# In app_gui.py.__init__():
self.hunt_tab.on_window_selected = self.window_controller.on_window_combo_selected
self.hunt_tab.on_refresh_windows = self.window_controller.on_hunt_find_windows
```

### **Task 2: Call Enumeration on Startup** (1 min)

**File**: `app_gui.py`

**Location**: In `App.__init__()` after UI is built

**Code**:
```python
# Auto-populate window list on app start
self.after(500, self.window_controller.on_hunt_find_windows)
```

### **Task 3: Add Scan Button & Screen State Panel** (4 min)

**File**: `ui/tabs/hunt_tab.py`

**Code**:
```python
# Add scan button to hunt setup frame
scan_frame = tk.Frame(self.app.hunt_setup_frame)
scan_frame.pack(fill="x", padx=10, pady=5)

self.scan_btn = tk.Button(
    scan_frame,
    text="🔍 Quét Màn Hình",
    command=self.on_scan_screen,
    state="disabled"  # Only enable when window selected
)
self.scan_btn.pack(side="left", padx=5)

# Screen state display panel
self.screen_state_frame = tk.LabelFrame(
    self.app.hunt_setup_frame,
    text="📊 Trạng Thái Màn Hình",
    padx=10,
    pady=8
)
self.screen_state_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Character class display
self.class_label = tk.Label(self.screen_state_frame, text="Lớp Nhân Vật: —")
self.class_label.pack(anchor="w", pady=3)

# Skill validity display
self.skill_label = tk.Label(self.screen_state_frame, text="Kỹ Năng: —")
self.skill_label.pack(anchor="w", pady=3)

# Location display
self.location_label = tk.Label(self.screen_state_frame, text="Vị Trí: —")
self.location_label.pack(anchor="w", pady=3)

# Monster presence display
self.monster_label = tk.Label(self.screen_state_frame, text="Quái Vật: —")
self.monster_label.pack(anchor="w", pady=3)

def on_scan_screen():
    """Scan screen and display state"""
    from lib.features.hunt.scanner import AutoScanner
    
    if not hasattr(self.app, 'vision_engine') or not self.app.vision_engine:
        messagebox.showerror("Lỗi", "Vision engine not available")
        return
    
    # Show spinner
    self.scan_btn.config(state="disabled", text="⏳ Đang quét...")
    self.app.update()
    
    try:
        scanner = AutoScanner(self.app.vision_engine)
        results = scanner.run_scan()
        
        # Display results
        self.class_label.config(text=f"Lớp Nhân Vật: {results.get('class', 'Unknown')}")
        
        skills = results.get('skills', [])
        valid_count = len(skills)
        self.skill_label.config(text=f"Kỹ Năng: ✅ {valid_count} kỹ năng phát hiện được")
        
        # Location (assume from config)
        window_bounds = self.app.hunt_cfg.get('window_bounds', {})
        location = "📍 Chưa xác định"
        if 'zone_name' in window_bounds:
            location = f"📍 {window_bounds['zone_name']}"
        self.location_label.config(text=f"Vị Trí: {location}")
        
        monsters = results.get('monsters', [])
        monster_text = f"🎯 {len(monsters)} quái phát hiện" if monsters else "❌ Không phát hiện quái"
        self.monster_label.config(text=f"Quái Vật: {monster_text}")
        
    except Exception as e:
        messagebox.showerror("Lỗi Quét", str(e))
    finally:
        self.scan_btn.config(state="normal", text="🔍 Quét Màn Hình")

self.on_scan_screen = on_scan_screen
```

### **Task 4: Enable Scan Button on Window Select** (1 min)

**File**: `ui/tabs/hunt_tab.py`

**Code**:
```python
def on_window_selected():
    """Called when user selects a window"""
    # Enable scan button
    self.scan_btn.config(state="normal")
    # Clear previous state
    self.class_label.config(text="Lớp Nhân Vật: —")
    self.skill_label.config(text="Kỹ Năng: —")
    self.location_label.config(text="Vị Trí: —")
    self.monster_label.config(text="Quái Vật: —")

self.on_window_selected = on_window_selected
```

---

## 📊 Implementation Checklist

- [ ] Task 1: Add window combobox to HuntTab (2 min)
- [ ] Task 2: Auto-enumerate on startup (1 min)
- [ ] Task 3: Add scan button & screen state panel (4 min)
- [ ] Task 4: Enable scan button logic (1 min)
- [ ] Test: Window enumeration on startup
- [ ] Test: Refresh button re-enumerates
- [ ] Test: Window selection saves to config
- [ ] Test: Scan button displays character class, skills, location
- [ ] Add i18n keys (1 min)

**Total**: ~12 minutes

---

## 🎨 UI Layout (Desired)

```
┌────────────────────────────────────────────────┐
│ Hunt Setup                                     │
├────────────────────────────────────────────────┤
│                                                │
│ Cửa sổ Game: [Cabal Online - Warrior    ▼] [🔄 Làm Mới]
│                                                │
│ [🔍 Quét Màn Hình]                            │
│                                                │
│ ┌────────────────────────────────────────────┐ │
│ │ 📊 Trạng Thái Màn Hình                     │ │
│ ├────────────────────────────────────────────┤ │
│ │ Lớp Nhân Vật: Warrior                      │ │
│ │ Kỹ Năng: ✅ 4 kỹ năng phát hiện được       │ │
│ │ Vị Trí: 📍 Thành Phố                       │ │
│ │ Quái Vật: 🎯 3 quái phát hiện              │ │
│ └────────────────────────────────────────────┘ │
│                                                │
└────────────────────────────────────────────────┘
```

---

## 📌 i18n Keys Needed

```python
{
    "setup.window_label": "Cửa sổ Game",
    "setup.refresh_btn": "🔄 Làm Mới",
    "setup.scan_btn": "🔍 Quét Màn Hình",
    "setup.scanning": "⏳ Đang quét...",
    "setup.screen_state": "📊 Trạng Thái Màn Hình",
    "setup.character_class": "Lớp Nhân Vật:",
    "setup.skills": "Kỹ Năng:",
    "setup.skills_found": "✅ {count} kỹ năng phát hiện được",
    "setup.location": "Vị Trí:",
    "setup.monster": "Quái Vật:",
    "setup.monster_found": "🎯 {count} quái phát hiện",
    "setup.monster_not_found": "❌ Không phát hiện quái",
    "setup.scanning_failed": "Lỗi Quét",
}
```

---

**Status**: ✅ READY FOR IMPLEMENTATION  
**Complexity**: LOW (just UI wiring + display)  
**Risk**: MINIMAL (all backend exists)

