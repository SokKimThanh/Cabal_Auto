# PROMPT-UX: Auto Hunt Flow (Quy Trình Quét Quái Tự Động)

**Status**: ✅ Draft  
**Timeline**: 15-20 minutes  
**Target Sprint**: Sprint 26 (Combat Refactor)  
**Dependencies**: UX6 (Window Detection + Screen State Analysis), UX5.2 (Display Monster on Auto Screen)

---

## 📋 Feature Overview

Quy trình **Auto Hunt Flow** là vòng lặp tự động quét quái, lấy thông tin, kiểm tra trạng thái (bị đập/chết), và chuyển đến quái tiếp theo. Hiện tại các panel đã có nội dung nhưng chưa có sự kết nối mạch lạc để tự động lặp lại.

### Main Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. User clicks "Start Auto" button                                  │
│    → Set state: HUNTING (active scan loop)                          │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. Scan Cycle (repeat until Stop clicked)                          │
│                                                                      │
│  A. Auto-scan (send Z key, wait 300ms for target to highlight)    │
│  B. Capture screen                                                 │
│  C. Extract monster info (name, HP, type) from screen             │
│  D. Lookup monster in DB → Get monster data (ID, level, rewards)  │
│  E. Display monster on HuntScreen (UX5.2 integration)             │
│  F. Check monster state:                                          │
│     - If HP = 0 (dead): Mark dead → Find next → Continue loop    │
│     - If HP > 0 (alive): Add to hunt history → Attack logic      │
│  G. Clean up: Delete screenshot, clear screen buffer             │
│  H. Wait (configurable interval, e.g., 1-2s per scan cycle)      │
│  I. Loop back to step A                                           │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. User clicks "Stop Auto" button                                   │
│    → Set state: IDLE (cease scanning)                              │
│    → Display final hunt session summary                            │
│    → Offer save session log                                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Requirements

### **R1: Start Auto Button — Initiate Hunt Loop**
- Button in Hunt Control Panel: "🎬 Bắt Đầu Tự Động" (Start Auto)
- On click:
  - Disable button (prevent double-click)
  - Set `HuntOrchestrator.state = HUNTING`
  - Start background scan thread (non-blocking)
  - Show spinner: "⏳ Đang quét..."
  - Enable "⏹️ Dừng" (Stop Auto) button

**i18n Keys**:
- `hunt.auto_start_btn` = "🎬 Bắt Đầu Tự Động"
- `hunt.auto_stop_btn` = "⏹️ Dừng"
- `hunt.scanning_spinner` = "⏳ Đang quét..."

---

### **R2: Scan Cycle — Auto-Detect & Extract Monster Info**

Each cycle (duration: 300-500ms):

#### **Step 2A: Send Z Key (Auto-Target)**
```python
def send_auto_scan_key():
    """Send Z key to force monster highlight in game"""
    # Use win32api or pynput to send Z key to game window
    # Z key = standard targeting key in Cabal
    keyboard.press('z')
    time.sleep(0.1)
    keyboard.release('z')
    time.sleep(0.3)  # Wait for game to register highlight
```

#### **Step 2B-C: Screen Capture & Extract Monster Name**
```python
def extract_monster_info_from_screen(hwnd) -> MonsterScreenData:
    """
    Capture game screen and extract:
    - Monster name (from title bar or nameplate above monster)
    - HP bar status (current/max HP)
    - Monster position on screen
    - Target bar info (if visible)
    
    Returns:
        {
            'name': str,              # e.g., 'Scarlet Scorpion'
            'hp_current': int,        # e.g., 245
            'hp_max': int,            # e.g., 500
            'hp_percent': float,      # 0.0-100.0
            'is_selected': bool,      # True if target bar visible
            'screen_position': (x, y),
            'timestamp': datetime,
            'screenshot': numpy.ndarray  # Raw image for OCR
        }
    """
    screenshot = capture_window(hwnd)
    
    # Step 1: Detect monster nameplate (OCR or template)
    name = ocr_monster_name(screenshot)  # Or use existing CB1 detector
    
    # Step 2: Detect HP bar
    hp_data = detect_hp_bar(screenshot)
    
    # Step 3: Check if target bar visible (means selected)
    is_selected = check_target_bar_visible(screenshot)
    
    return MonsterScreenData(
        name=name,
        hp_current=hp_data['current'],
        hp_max=hp_data['max'],
        hp_percent=(hp_data['current'] / hp_data['max']) * 100,
        is_selected=is_selected,
        screenshot=screenshot,
        timestamp=datetime.now()
    )
```

#### **Step 2D: Lookup Monster in Database**
```python
def lookup_monster_in_db(monster_name: str) -> MonsterInfo:
    """
    Query database for monster details
    
    Returns:
        {
            'id': int,
            'name': str,
            'class': str,  # e.g., 'Undead', 'Beast'
            'level': int,
            'exp_reward': int,
            'drop_items': [ItemInfo, ...],
            'spawn_zones': [str, ...],
            'hp': int,
            'is_elite': bool,
            'ai_pattern': str
        }
    """
    from repositories.monster_repository import MonsterRepository
    repo = MonsterRepository()
    return repo.find_by_name(monster_name)
```

#### **Step 2E: Display Monster on HuntScreen (UX5.2)**
```python
def display_monster_on_hunt_screen(monster_info: MonsterInfo, screen_data: MonsterScreenData):
    """
    Update HuntScreen (left panel) with:
    - Monster icon
    - Monster name
    - Monster level
    - HP bar with current/max
    - Drop items
    - Status (Alive/Dead/Changed)
    
    Integration point: Call HuntScreen.update_current_monster()
    """
    hunt_screen.update_current_monster(
        monster_id=monster_info['id'],
        name=monster_info['name'],
        level=monster_info['level'],
        hp_current=screen_data['hp_current'],
        hp_max=screen_data['hp_max'],
        hp_percent=screen_data['hp_percent'],
        is_selected=screen_data['is_selected'],
        drop_items=monster_info['drop_items']
    )
```

#### **Step 2F: Check Monster State (Dead or Alive)**
```python
def check_monster_state(current_scan: MonsterScreenData, previous_scan: Optional[MonsterScreenData]) -> MonsterState:
    """
    Determine if monster is:
    - ALIVE: HP > 0 (continue hunting)
    - DEAD: HP = 0 or changed monster name (transition to next)
    - CHANGED: Same position but different name (already moved)
    
    Returns: {'status': 'ALIVE|DEAD|CHANGED', 'reason': str}
    """
    if current_scan['hp_current'] == 0:
        return {'status': 'DEAD', 'reason': 'HP is zero'}
    
    if previous_scan and current_scan['name'] != previous_scan['name']:
        return {'status': 'CHANGED', 'reason': 'Monster name changed'}
    
    if previous_scan and current_scan['hp_percent'] > 100:
        return {'status': 'CHANGED', 'reason': 'HP exceeded max (new monster)'}
    
    return {'status': 'ALIVE', 'reason': 'Normal state'}
```

#### **Step 2G: Cleanup — Delete Screenshot & Clear Buffer**
```python
def cleanup_scan_data(screenshot_path: str, screen_data: MonsterScreenData):
    """
    Delete temporary scan data to prevent memory/disk bloat
    """
    # Delete screenshot file from disk
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)
    
    # Clear screen buffer from memory
    if screen_data.get('screenshot') is not None:
        del screen_data['screenshot']
    
    # Log cleanup
    logger.info(f"Cleaned up scan data: {screenshot_path}")
```

#### **Step 2H: Wait Before Next Cycle**
```python
def wait_between_scans(interval_sec: float = 1.5):
    """Configurable interval between scan cycles (1-3 seconds)"""
    time.sleep(interval_sec)
```

**i18n Keys**:
- `hunt.cycle_started` = "⏳ Đang quét..."
- `hunt.monster_found` = "Tìm thấy: {name}"
- `hunt.monster_dead` = "☠️ {name} đã chết"
- `hunt.monster_changed` = "🔄 Chuyển sang: {name}"
- `hunt.cleanup_data` = "Dọn dẹp dữ liệu..."

---

### **R3: Stop Auto Button — Cease Hunt Loop**
- Button: "⏹️ Dừng" (Stop Auto) — only enabled during HUNTING state
- On click:
  - Set `HuntOrchestrator.state = IDLE`
  - Stop scan thread gracefully (wait for current cycle to finish)
  - Hide spinner
  - Display hunt session summary (monsters killed, exp gained, items found)
  - Offer save/export session log
  - Enable "Start Auto" button again

**i18n Keys**:
- `hunt.stopped` = "Đã dừng tự động"
- `hunt.session_summary` = "Tóm tắt phiên:"
- `hunt.total_monsters_killed` = "Tổng quái đánh: {count}"
- `hunt.total_exp_gained` = "Tổng EXP: {exp:,}"
- `hunt.items_found` = "Vật phẩm tìm được: {count}"

---

### **R4: Hunt History & Session State**

Maintain per-hunt-session:
```python
class HuntSession:
    session_id: str              # UUID
    start_time: datetime
    end_time: Optional[datetime]
    state: str                   # 'ACTIVE', 'STOPPED', 'PAUSED'
    
    monsters_encountered: List[MonsterEncounter]  # History of each scan
    total_kills: int
    total_exp: int
    total_drops: int
    
    def add_encounter(self, monster: MonsterScreenData):
        """Add scan result to session history"""
        self.monsters_encountered.append(
            MonsterEncounter(
                monster_id=monster.db_id,
                name=monster.name,
                hp_at_encounter=monster.hp_current,
                timestamp=datetime.now()
            )
        )
    
    def to_json(self) -> dict:
        """Export session to JSON for logging"""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_sec': (self.end_time - self.start_time).total_seconds() if self.end_time else 0,
            'total_kills': self.total_kills,
            'total_exp': self.total_exp,
            'total_drops': self.total_drops,
            'monsters': [m.to_dict() for m in self.monsters_encountered]
        }
```

---

### **R5: Error Handling & Graceful Fallback**

If scan fails:
- OCR cannot detect monster name → Show "❓ Không xác định quái" → Continue next cycle
- HP bar not detected → Assume HP unknown → Continue
- Monster not in DB → Log warning → Continue with screen data only
- Screen capture fails → Retry up to 3 times → Stop Auto if persistent

---

## 🔧 Phase 1: Backend Services

### `lib/features/hunt/auto_hunt_orchestrator.py` (NEW)

**Class: AutoHuntOrchestrator**

```python
class AutoHuntOrchestrator:
    """Coordinates auto-hunt scan loop"""
    
    def __init__(self, game_hwnd: int, hunt_screen_ui, hunt_db):
        self.game_hwnd = game_hwnd
        self.hunt_screen_ui = hunt_screen_ui
        self.hunt_db = hunt_db
        self.scan_thread = None
        self.is_scanning = False
        self.current_scan_data = None
        self.session = HuntSession()
        self.lock = threading.Lock()
    
    def start_auto_hunt(self, interval_sec: float = 1.5):
        """Begin auto-hunt loop in background thread"""
        if self.is_scanning:
            return  # Already running
        
        self.is_scanning = True
        self.session = HuntSession()
        self.scan_thread = threading.Thread(
            target=self._scan_loop,
            args=(interval_sec,),
            daemon=False
        )
        self.scan_thread.start()
    
    def _scan_loop(self, interval_sec: float):
        """Main scan loop (runs in background thread)"""
        previous_scan = None
        failed_attempts = 0
        
        while self.is_scanning:
            try:
                # Step 2A: Send Z key
                send_auto_scan_key()
                
                # Step 2B-C: Capture & extract
                screen_data = extract_monster_info_from_screen(self.game_hwnd)
                
                # Step 2D: Lookup in DB
                monster_info = lookup_monster_in_db(screen_data['name'])
                
                # Step 2E: Display on hunt screen (UX5.2)
                self.hunt_screen_ui.update_current_monster(
                    monster_info=monster_info,
                    screen_data=screen_data
                )
                
                # Step 2F: Check state
                state = check_monster_state(screen_data, previous_scan)
                
                if state['status'] == 'DEAD':
                    # Log as kill
                    self.session.add_encounter(screen_data)
                    self.session.total_kills += 1
                    logger.info(f"Monster killed: {screen_data['name']}")
                
                elif state['status'] == 'CHANGED':
                    logger.info(f"Monster changed: {previous_scan['name']} → {screen_data['name']}")
                
                # Step 2G: Cleanup
                cleanup_scan_data(screen_data)
                
                # Update current scan
                previous_scan = screen_data
                self.current_scan_data = screen_data
                failed_attempts = 0
                
            except Exception as e:
                logger.error(f"Scan cycle error: {e}")
                failed_attempts += 1
                if failed_attempts >= 3:
                    logger.critical("Too many failed scans, stopping auto-hunt")
                    self.is_scanning = False
                    break
            
            # Step 2H: Wait
            time.sleep(interval_sec)
        
        # Finalize session
        self.session.end_time = datetime.now()
        logger.info(f"Hunt session ended: {self.session.to_json()}")
    
    def stop_auto_hunt(self):
        """Cease auto-hunt loop"""
        self.is_scanning = False
        if self.scan_thread:
            self.scan_thread.join(timeout=2)
        
        # Return session data for UI display
        return self.session.to_json()
    
    def get_current_state(self) -> dict:
        """Return current hunting state for UI"""
        return {
            'is_hunting': self.is_scanning,
            'current_monster': self.current_scan_data,
            'session_stats': {
                'kills': self.session.total_kills,
                'exp': self.session.total_exp,
                'drops': self.session.total_drops,
                'duration': (datetime.now() - self.session.start_time).total_seconds()
            }
        }
```

---

### `lib/features/hunt/monster_screen_analyzer.py` (NEW or EXTEND)

**Methods**:
```python
def send_auto_scan_key() -> None:
    """Send Z key to game window"""
    # Implementation using pynput or win32api

def extract_monster_info_from_screen(hwnd: int) -> MonsterScreenData:
    """Capture screen, OCR monster name, detect HP bar"""
    # Implementation

def detect_hp_bar(screenshot) -> dict:
    """Extract current/max HP from health bar"""
    # Implementation

def check_target_bar_visible(screenshot) -> bool:
    """Detect if target selection bar is visible"""
    # Implementation using CB1 TargetBarDetector

def check_monster_state(current: MonsterScreenData, previous: Optional[MonsterScreenData]) -> dict:
    """Determine monster status (ALIVE/DEAD/CHANGED)"""
    # Implementation

def cleanup_scan_data(screen_data: MonsterScreenData) -> None:
    """Delete screenshot file and clear memory buffer"""
    # Implementation
```

---

## 🎨 Phase 2: UI Components

### `ui/tabs/hunt_tab.py` (MODIFY)

Add Hunt Control Panel section:

```python
class HuntControlPanel(ttk.Frame):
    """Control panel for auto-hunt: Start/Stop buttons, status display"""
    
    def __init__(self, parent, hunt_orchestrator_callback):
        super().__init__(parent)
        
        # Buttons row
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side='top', fill='x', padx=10, pady=5)
        
        # Start Auto button
        self.start_auto_btn = ttk.Button(
            btn_frame,
            text=_("hunt.auto_start_btn"),
            command=self.on_start_auto,
            state='normal'
        )
        self.start_auto_btn.pack(side='left', padx=5)
        
        # Stop button (disabled until auto starts)
        self.stop_auto_btn = ttk.Button(
            btn_frame,
            text=_("hunt.auto_stop_btn"),
            command=self.on_stop_auto,
            state='disabled'
        )
        self.stop_auto_btn.pack(side='left', padx=5)
        
        # Status spinner
        self.spinner_label = ttk.Label(
            btn_frame,
            text="",
            foreground="green"
        )
        self.spinner_label.pack(side='left', padx=10)
        
        # Stats display
        stats_frame = ttk.LabelFrame(self, text=_("hunt.session_summary"))
        stats_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.kills_label = ttk.Label(stats_frame, text="Tổng quái đánh: 0")
        self.kills_label.pack(anchor='w', padx=10, pady=5)
        
        self.exp_label = ttk.Label(stats_frame, text="Tổng EXP: 0")
        self.exp_label.pack(anchor='w', padx=10, pady=5)
        
        self.drops_label = ttk.Label(stats_frame, text="Vật phẩm: 0")
        self.drops_label.pack(anchor='w', padx=10, pady=5)
        
        self.duration_label = ttk.Label(stats_frame, text="Thời gian: 0s")
        self.duration_label.pack(anchor='w', padx=10, pady=5)
    
    def on_start_auto(self):
        """Handle Start Auto button click"""
        self.start_auto_btn.config(state='disabled')
        self.stop_auto_btn.config(state='normal')
        self.spinner_label.config(text="⏳ Đang quét...")
        
        # Trigger orchestrator
        self.orchestrator_callback.start_auto_hunt()
        
        # Update stats every 1 second
        self.update_stats()
    
    def on_stop_auto(self):
        """Handle Stop Auto button click"""
        self.start_auto_btn.config(state='normal')
        self.stop_auto_btn.config(state='disabled')
        self.spinner_label.config(text="")
        
        # Trigger orchestrator
        session = self.orchestrator_callback.stop_auto_hunt()
        
        # Display final stats
        self.show_session_summary(session)
    
    def update_stats(self):
        """Update stats display from orchestrator"""
        if not self.orchestrator_callback.is_scanning:
            return
        
        state = self.orchestrator_callback.get_current_state()
        stats = state['session_stats']
        
        self.kills_label.config(text=f"Tổng quái đánh: {stats['kills']}")
        self.exp_label.config(text=f"Tổng EXP: {stats['exp']:,}")
        self.drops_label.config(text=f"Vật phẩm: {stats['drops']}")
        self.duration_label.config(text=f"Thời gian: {int(stats['duration'])}s")
        
        # Schedule next update
        self.after(1000, self.update_stats)
    
    def show_session_summary(self, session: dict):
        """Display hunt session summary after stop"""
        summary = f"""
        Phiên Quét Tự Động
        ──────────────────
        Quái đánh: {session['total_kills']}
        EXP nhận: {session['total_exp']:,}
        Vật phẩm: {session['total_drops']}
        Thời gian: {int(session['duration_sec'])}s
        """
        messagebox.showinfo(_("hunt.stopped"), summary)
```

### `ui/panels/hunt_screen.py` (MODIFY)

Update to display current monster from auto-hunt:

```python
class HuntScreen(ttk.Frame):
    """Left panel showing current target monster info during hunt"""
    
    def update_current_monster(self, monster_info: dict, screen_data: dict):
        """Called by AutoHuntOrchestrator during each scan cycle"""
        self.monster_name_label.config(
            text=f"🎯 {monster_info['name']} (Lv. {monster_info['level']})"
        )
        
        self.monster_hp_label.config(
            text=f"HP: {screen_data['hp_current']}/{screen_data['hp_max']} ({screen_data['hp_percent']:.1f}%)"
        )
        
        # Update HP bar canvas
        self.draw_hp_bar(
            current=screen_data['hp_current'],
            max_hp=screen_data['hp_max']
        )
        
        # Display drops
        drops_text = ", ".join([item['name'] for item in monster_info.get('drop_items', [])])
        self.drops_label.config(text=f"Drop: {drops_text}")
```

---

## 🧪 Phase 3: Integration & Wiring

### `app_gui.py` (MODIFY)

Wire up auto-hunt flows:

```python
class App(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        # Initialize orchestrator
        self.auto_hunt_orchestrator = AutoHuntOrchestrator(
            game_hwnd=self.get_selected_window_hwnd(),
            hunt_screen_ui=self.hunt_screen,  # Reference to HuntScreen panel
            hunt_db=self.db_service
        )
        
        # Wire hunt control panel to orchestrator
        self.hunt_control_panel.orchestrator_callback = self.auto_hunt_orchestrator
        
        # Monitor orchestrator state changes
        self.monitor_hunt_state()
    
    def get_selected_window_hwnd(self) -> int:
        """Get currently selected game window handle"""
        return self.selected_hwnd  # From setup tab combo selection
    
    def monitor_hunt_state(self):
        """Periodically check hunt state and update UI"""
        if self.auto_hunt_orchestrator.is_scanning:
            # Update hunt screen with current monster
            current = self.auto_hunt_orchestrator.current_scan_data
            if current:
                self.hunt_screen.update_current_monster(current)
        
        self.after(500, self.monitor_hunt_state)
```

---

## 🧪 Validation Tests

### Unit Tests: `tests/unit/test_auto_hunt_flow.py`

```python
def test_send_auto_scan_key_sends_z():
    """Verify Z key is sent to game window"""
    # Mock keyboard
    # Assert Z key sent
    pass

def test_extract_monster_info_from_screen():
    """Verify screen capture and monster name extraction"""
    screenshot = load_test_screenshot()
    data = extract_monster_info_from_screen(screenshot)
    assert data['name'] == expected_name
    assert data['hp_current'] > 0
    pass

def test_check_monster_state_detects_dead():
    """Verify dead monster is detected when HP = 0"""
    current = {'hp_current': 0, 'name': 'Scorpion'}
    previous = {'hp_current': 100, 'name': 'Scorpion'}
    state = check_monster_state(current, previous)
    assert state['status'] == 'DEAD'
    pass

def test_check_monster_state_detects_changed():
    """Verify monster change detection"""
    current = {'hp_current': 100, 'name': 'Skeleton'}
    previous = {'hp_current': 100, 'name': 'Scorpion'}
    state = check_monster_state(current, previous)
    assert state['status'] == 'CHANGED'
    pass

def test_hunt_session_accumulates_kills():
    """Verify session tracks kills correctly"""
    session = HuntSession()
    session.add_encounter(MonsterScreenData(name='Scorpion'))
    session.total_kills += 1
    assert session.total_kills == 1
    pass
```

### Integration Test: `tests/integration/test_auto_hunt_full_cycle.py`

```python
def test_full_auto_hunt_cycle():
    """Verify complete scan cycle: send key → capture → extract → lookup → display"""
    app = App()
    
    # Step 1: Click Start Auto
    app.hunt_control_panel.on_start_auto()
    time.sleep(0.1)
    
    # Step 2: Wait for one cycle (1.5s default + 0.5s buffer)
    time.sleep(2)
    
    # Step 3: Verify monster displayed
    assert app.hunt_screen.monster_name_label.cget('text') != ''
    
    # Step 4: Click Stop Auto
    app.hunt_control_panel.on_stop_auto()
    
    # Step 5: Verify session summary shown
    # (Mocked messagebox assertion)
    pass
```

---

## ✅ Manual Validation Matrix

| Scenario | User Action | Expected Behavior | Acceptance Criteria |
|----------|-------------|-------------------|---------------------|
| **S1: Start Auto** | Click "🎬 Bắt Đầu Tự Động" | Spinner shows, Start button disabled, Stop enabled | ✅ UI updates, scan begins |
| **S2: Scan Cycle** | Auto scans (Z key + screen capture) | Extract monster name, lookup DB, display on hunt screen | ✅ Monster name shows, HP bar updates |
| **S3: Monster Alive** | Monster HP > 0 in scan | Status = ALIVE, continue scanning | ✅ Scan continues, no state change |
| **S4: Monster Dead** | Monster HP = 0 in scan | Status = DEAD, log kill, continue to next monster | ✅ Kill count increments, session updated |
| **S5: Monster Changed** | Monster name changes between scans | Status = CHANGED, note transition in log | ✅ New monster displayed, transition logged |
| **S6: Stop Auto** | Click "⏹️ Dừng" | Stop scan loop, show session summary | ✅ Spinner hidden, stats displayed, buttons swap |
| **S7: Session Summary** | After Stop | Show kills, EXP, drops, duration | ✅ All stats correct, export option shown |
| **S8: Cleanup** | After each scan | Screenshot deleted, memory cleared | ✅ Disk space freed, no memory leak |
| **S9: Error Fallback** | Monster name not detected | Show "❓ Không xác định quái", continue | ✅ No crash, scan continues |
| **S10: Performance** | 10 consecutive scans | Avg cycle time ≤ 1.5s, no UI freeze | ✅ Smooth operation, no lag |
| **S11: Pause & Resume** | Click Stop then Start | New session created, history preserved | ✅ Session ID unique, old data saved |
| **S12: i18n** | Toggle language (vi/en) | All UI strings update | ✅ Both languages visible |

---

## ⏱️ Timeline Breakdown

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 1 | Implement `AutoHuntOrchestrator._scan_loop()` | 5 min | ⏳ Pending |
| 1 | Implement `MonsterScreenAnalyzer` (send key, capture, OCR, HP detect) | 5 min | ⏳ Pending |
| 1 | Implement `check_monster_state()` & `cleanup_scan_data()` | 3 min | ⏳ Pending |
| 2 | Add Hunt Control Panel (buttons, spinner, stats display) | 4 min | ⏳ Pending |
| 2 | Update HuntScreen to display current monster | 2 min | ⏳ Pending |
| 3 | Wire up `app_gui.py` (initialize orchestrator, monitor state) | 2 min | ⏳ Pending |
| 3 | Integrate with HuntOrchestrator state machine | 2 min | ⏳ Pending |
| i18n | Add 12+ new translation keys | 2 min | ⏳ Pending |
| Tests | Write 4 unit tests | 3 min | ⏳ Pending |
| Tests | Write 1 integration test | 2 min | ⏳ Pending |
| Manual | Validation matrix (12 scenarios) | 8 min | ⏳ Pending |
| **TOTAL** | | **15-20 min** | ⏳ Pending |

---

## 🛡️ Quality Gate Criteria

| Criterion | Pass | Fail |
|-----------|------|------|
| **Functionality** | Start Auto initiates scan loop within 200ms | Takes >200ms or doesn't start |
| **Functionality** | Each scan cycle completes within 1.5s | Takes >2s (indicates bottleneck) |
| **Functionality** | Monster name extracted correctly from 10/10 test screenshots | <8/10 success rate |
| **Functionality** | HP bar detection accurate ±5% | <95% accuracy |
| **Functionality** | Monster state detection (ALIVE/DEAD/CHANGED) correct | False positives in state |
| **Display** | Current monster displayed on HuntScreen during scan | Monster info missing or outdated |
| **Display** | Stats updated in real-time (kills, EXP, drops) | Stats frozen or delayed >1s |
| **State** | HuntOrchestrator.state = HUNTING when auto active | Wrong state value |
| **Cleanup** | Screenshot files deleted after scan | Files accumulate on disk |
| **Memory** | No memory leak after 100 consecutive scans | RAM usage exceeds 500MB |
| **Threading** | Main thread not blocked during scan (UI responsive) | UI freezes or jank during scan |
| **Error Handling** | Failed OCR → continue scanning (not crash) | Exception propagates, auto stops |
| **i18n** | All UI text uses translation keys (vi/en both work) | Hard-coded strings found |
| **Session** | Hunt session JSON valid and complete | Missing fields or malformed JSON |

---

## 📁 Code Structure

```
lib/features/hunt/
    ├── auto_hunt_orchestrator.py       (NEW) — Main loop coordinator
    ├── monster_screen_analyzer.py      (NEW) — Screen capture & analysis
    ├── hunt_session.py                 (NEW) — Session tracking
    └── __init__.py

ui/tabs/
    └── hunt_tab.py                     (MODIFY) — Add HuntControlPanel

ui/panels/
    └── hunt_screen.py                  (MODIFY) — Update monster display

lib/i18n/
    └── translations.py                 (MODIFY) — Add 12+ keys

app_gui.py                              (MODIFY) — Wire orchestrator

tests/unit/
    └── test_auto_hunt_flow.py          (NEW) — 4 unit tests

tests/integration/
    └── test_auto_hunt_full_cycle.py    (NEW) — 1 integration test
```

---

## 📌 i18n Keys Required

```python
{
    "hunt.auto_start_btn": "🎬 Bắt Đầu Tự Động",
    "hunt.auto_stop_btn": "⏹️ Dừng",
    "hunt.scanning_spinner": "⏳ Đang quét...",
    "hunt.cycle_started": "⏳ Đang quét...",
    "hunt.monster_found": "Tìm thấy: {name}",
    "hunt.monster_dead": "☠️ {name} đã chết",
    "hunt.monster_changed": "🔄 Chuyển sang: {name}",
    "hunt.cleanup_data": "Dọn dẹp dữ liệu...",
    "hunt.stopped": "Đã dừng tự động",
    "hunt.session_summary": "Tóm tắt phiên:",
    "hunt.total_monsters_killed": "Tổng quái đánh: {count}",
    "hunt.total_exp_gained": "Tổng EXP: {exp:,}",
    "hunt.items_found": "Vật phẩm tìm được: {count}",
    "hunt.unknown_monster": "❓ Không xác định quái",
    "hunt.monster_unchanged": "Chưa đổi",
}
```

---

**Created**: 2026-09-05  
**Sprint**: Sprint 26 (Combat Refactor)  
**Status**: Ready for Implementation
