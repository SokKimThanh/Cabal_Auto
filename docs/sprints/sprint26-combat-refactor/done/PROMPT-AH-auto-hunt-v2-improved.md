# ✅ IMPROVED PROMPT: Auto Hunt Flow — Practical Edition

**Status**: Revised based on actual codebase  
**Reality Check**: 50% of backend exists; 40% needs to be integrated from CLI  
**Timeline**: 20-25 minutes (realistic)  
**Sprint**: Sprint 26 (Combat Refactor)  
**Key Insight**: Full hunt logic already exists in `auto_hunt.py` (CLI); just need to integrate into `HuntOrchestrator` + wire to GUI buttons

---

## 📋 Feature Overview — What's Actually Happening

The Auto Hunt Flow feature has **two parallel implementations**:

| Path | Status | Location | Problem |
|------|--------|----------|---------|
| **GUI** | 50% done | `HuntOrchestrator` + `ui/tabs/hunt_tab.py` | No Start/Stop buttons, no session tracking |
| **CLI** | 95% done | `ui/windows/auto_hunt.py` | Full hunt loop works but separate process |

**Goal**: Merge CLI hunt logic into GUI-integrated `AutoHuntOrchestrator`

---

## 🎯 Current Issues Preventing Auto Hunt from Working

### Issue 1: No Start/Stop Buttons Wired
- Buttons exist in code but callbacks not implemented
- **Current**: `HuntTab` shows no "Start Auto" / "Stop" buttons
- **Need**: Wire to `HuntOrchestrator.start_hunt()` and `HuntOrchestrator.stop_hunt()`

### Issue 2: CLI Hunt Logic Not in Orchestrator
- **Current**: `auto_hunt.py` has full hunt loop with Z-key sending, dead detection, cleanup
- **Problem**: Runs as separate CLI process (`python ui/windows/auto_hunt.py`)
- **Need**: Extract hunting logic and move to `AutoHuntOrchestrator`

### Issue 3: No Screenshot Cleanup
- **Current**: Screenshots captured but never deleted
- **Need**: Add cleanup after each scan cycle

### Issue 4: No Session Tracking
- **Current**: No tracking of kills, EXP, drops
- **Problem**: Can't show session summary after hunt
- **Need**: Create `HuntSession` class to track stats

### Issue 5: Z-Key Sending Not in Orchestrator
- **Current**: Only in `auto_hunt.py` (CLI)
- **Need**: Add to `HuntOrchestrator.run_hunt_cycle()`

---

## 🔧 Implementation Tasks (Realistic)

### **Task 0: Understand Current Code Paths**

#### What Currently Exists in HuntOrchestrator:
```python
class HuntOrchestrator:
    def start_hunt(self, cfg):
        """Main hunt loop"""
        # Opens worker thread
        # Runs frame capture + detection loop
        # BUT: No explicit "scan cycle" with:
        #   - Z key sending
        #   - Screenshot cleanup
        #   - Session tracking

    def stop_hunt(self):
        """Stop the hunt"""
        # Sets state to IDLE
```

#### What Currently Exists in auto_hunt.py (CLI):
```python
def main():
    """Full hunt loop with all logic"""
    # locate_monster_target() — finds next monster to attack
    # check_dead() — detects if target is dead
    # attack() — sends commands to game
    # session_log — tracks kills
    # Screenshot cleanup — deletes after use
    # Z key sending — for targeting
```

#### What Currently Exists in HuntTab:
```python
class HuntTab:
    # NO Start/Stop buttons wired
    # update_target_card() exists but no automatic updates
    # NO session tracking
```

---

### **Task 1: Create AutoHuntOrchestrator Class** (5 min)

**File**: `lib/features/hunt/auto_hunt_orchestrator.py` (NEW FILE)

**Purpose**: Centralized hunt loop with all logic

**Code**:
```python
"""
Auto Hunt Orchestrator — Main hunt loop with session tracking
Integrates:
  - HuntOrchestrator base logic
  - auto_hunt.py hunt cycle logic
  - Screenshot cleanup
  - Session tracking (kills, EXP, drops)
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Any
from enum import Enum
from threading import Thread, Event
from queue import Queue
import os

logger = logging.getLogger(__name__)

class HuntState(Enum):
    IDLE = "idle"
    HUNTING = "hunting"
    PAUSED = "paused"
    ERROR = "error"

@dataclass
class HuntSessionStats:
    """Track hunt session statistics"""
    start_time: float = field(default_factory=time.time)
    monsters_killed: int = 0
    exp_gained: int = 0
    drops_collected: list = field(default_factory=list)
    duration_seconds: float = 0
    
    def calculate_duration(self):
        self.duration_seconds = time.time() - self.start_time
        return self.duration_seconds

class AutoHuntOrchestrator:
    """
    Centralized hunt loop that:
    1. Sends Z key to highlight next target
    2. Captures screen
    3. Extracts monster name/HP
    4. Looks up in DB
    5. Displays on HuntScreen
    6. Checks if monster is dead
    7. Tracks session stats
    8. Cleans up screenshots
    9. Waits and loops
    """
    
    def __init__(
        self,
        hwnd: int,
        vision_engine,
        monster_repo,
        window_manager,
        screen_capture,
        logger,
        **callbacks
    ):
        """
        Parameters:
        - hwnd: Game window handle
        - vision_engine: For monster detection
        - monster_repo: For DB lookups
        - window_manager: For window validation
        - screen_capture: For frame capture
        - logger: For logging
        - callbacks: {
            'schedule_ui_task': fn,  # For thread-safe UI updates
            'update_target_hp': fn,
            'update_target_name': fn,
            'update_status': fn,
            'log_event': fn,
        }
        """
        self.hwnd = hwnd
        self.vision_engine = vision_engine
        self.monster_repo = monster_repo
        self.window_manager = window_manager
        self.screen_capture = screen_capture
        self.logger = logger
        self.callbacks = callbacks
        
        self.state = HuntState.IDLE
        self.current_target: Optional[Dict[str, Any]] = None
        self.session_stats = HuntSessionStats()
        self.stop_event = Event()
        self.hunt_thread: Optional[Thread] = None
        
        # Paths for cleanup
        self.screenshot_dir = "tmp/hunt_screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def _schedule_ui_task(self, fn: Callable):
        """Thread-safe UI update"""
        if 'schedule_ui_task' in self.callbacks:
            self.callbacks['schedule_ui_task'](fn)
        else:
            fn()
    
    def _send_z_key(self):
        """
        Send Z key to game window to highlight next target
        
        Z is the standard "target nearest" key in Cabal
        """
        try:
            import pyautogui
            pyautogui.press('z')
            time.sleep(0.1)
            pyautogui.release('z')
            time.sleep(0.3)  # Wait for game to register
            self.logger.info("Z key sent successfully")
        except Exception as e:
            self.logger.error(f"Failed to send Z key: {e}")
    
    def _capture_and_extract(self) -> Optional[Dict[str, Any]]:
        """
        Capture screen and extract monster info
        
        Returns:
            {
                'name': str,
                'hp_current': int,
                'hp_max': int,
                'hp_percent': float,
                'is_alive': bool,
            }
        """
        try:
            # Capture screenshot
            frame = self.screen_capture.get_frame()
            if frame is None:
                self.logger.warning("Failed to capture frame")
                return None
            
            # Detect monsters in frame using vision engine
            detections = self.vision_engine.detect_monster_pipeline(frame)
            if not detections:
                self.logger.info("No monsters detected in frame")
                return None
            
            # Get highest-priority detection (first target)
            target = detections[0]
            
            # Calculate HP percent
            hp_percent = (target.get('hp_current', 0) / max(1, target.get('hp_max', 1))) * 100
            
            monster_info = {
                'name': target.get('name', 'Unknown'),
                'hp_current': target.get('hp_current', 0),
                'hp_max': target.get('hp_max', 1),
                'hp_percent': min(100, max(0, hp_percent)),
                'is_alive': hp_percent > 0,
            }
            
            self.logger.info(f"Extracted: {monster_info['name']} ({monster_info['hp_percent']:.0f}%)")
            return monster_info
            
        except Exception as e:
            self.logger.error(f"Failed to extract monster info: {e}")
            return None
    
    def _lookup_monster_db(self, monster_name: str) -> Optional[Dict[str, Any]]:
        """
        Lookup monster in database
        
        Returns:
            {
                'id': int,
                'name': str,
                'level': int,
                'hp': int,
                'defense': int,
                'exp_reward': int,
                'drop_items': list,
            }
        """
        try:
            monster = self.monster_repo.get_target_monster_info(monster_name)
            if monster:
                self.logger.info(f"Found in DB: {monster['name']} (Level {monster['level']})")
            return monster
        except Exception as e:
            self.logger.error(f"Failed to lookup monster: {e}")
            return None
    
    def _check_if_dead(self, monster_info: Dict[str, Any]) -> bool:
        """
        Check if current target is dead
        
        Dead = HP <= 0 or monster not visible
        """
        if not monster_info:
            self.logger.info("No monster info available")
            return True
        
        is_dead = monster_info['hp_percent'] <= 0
        status = "💀 Dead" if is_dead else "🎯 Alive"
        self.logger.info(f"Target status: {status} ({monster_info['hp_percent']:.0f}%)")
        return is_dead
    
    def _cleanup_screenshot(self, filename: str = None):
        """
        Delete screenshot after processing
        
        This prevents disk space bloat during long hunts
        """
        try:
            if filename and os.path.exists(filename):
                os.remove(filename)
                self.logger.debug(f"Deleted screenshot: {filename}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup screenshot: {e}")
    
    def _display_on_hunt_screen(self, monster_db: Dict[str, Any]):
        """
        Update HuntTab to display current target
        
        Calls UI callbacks to update target card
        """
        def update_ui():
            if 'update_target_name' in self.callbacks:
                self.callbacks['update_target_name'](monster_db['name'])
            if 'update_target_hp' in self.callbacks:
                self.callbacks['update_target_hp'](
                    monster_db['hp_percent'],
                    monster_db['hp_current'],
                    monster_db['hp_max']
                )
        
        self._schedule_ui_task(update_ui)
    
    def _run_hunt_cycle(self):
        """
        Run one complete hunt cycle:
        
        1. Send Z key (highlight target)
        2. Capture screen + extract monster info
        3. Lookup in DB
        4. Display on HuntScreen
        5. Check if dead
        6. Cleanup screenshot
        7. Wait
        """
        while not self.stop_event.is_set() and self.state == HuntState.HUNTING:
            try:
                self.logger.info("--- Hunt Cycle Start ---")
                
                # Step 1: Send Z key
                self.logger.info("Step 1: Sending Z key to target...")
                self._send_z_key()
                
                # Step 2-3: Capture & extract
                self.logger.info("Step 2-3: Capturing and extracting monster info...")
                monster_info = self._capture_and_extract()
                if not monster_info:
                    self.logger.warning("No monster found, continuing...")
                    time.sleep(2)
                    continue
                
                # Step 4: Lookup in DB
                self.logger.info("Step 4: Looking up monster in database...")
                monster_db = self._lookup_monster_db(monster_info['name'])
                if not monster_db:
                    self.logger.warning(f"Monster '{monster_info['name']}' not found in DB")
                    monster_db = {'name': monster_info['name'], 'hp_percent': monster_info['hp_percent']}
                
                # Merge screen data into DB data
                monster_db.update({
                    'hp_current': monster_info['hp_current'],
                    'hp_max': monster_info['hp_max'],
                    'hp_percent': monster_info['hp_percent'],
                    'is_alive': monster_info['is_alive'],
                })
                self.current_target = monster_db
                
                # Step 5: Display on HuntScreen
                self.logger.info("Step 5: Displaying on HuntScreen...")
                self._display_on_hunt_screen(monster_db)
                
                # Step 6: Check if dead
                self.logger.info("Step 6: Checking if monster is dead...")
                if self._check_if_dead(monster_db):
                    self.session_stats.monsters_killed += 1
                    self.logger.info(f"Monster killed! Total kills: {self.session_stats.monsters_killed}")
                    # TODO: Add to drops_collected from monster_db['drop_items']
                else:
                    self.logger.info("Monster alive, continuing hunt...")
                
                # Step 7: Cleanup
                self.logger.info("Step 7: Cleaning up...")
                self._cleanup_screenshot()
                
                # Step 8: Wait
                wait_time = 1.5  # Configurable from hunt_cfg
                self.logger.info(f"Step 8: Waiting {wait_time}s before next cycle...")
                
                # Use small waits to allow stop_event interruption
                for _ in range(int(wait_time * 10)):
                    if self.stop_event.is_set():
                        break
                    time.sleep(0.1)
                
                self.logger.info("--- Hunt Cycle End ---\n")
                
            except Exception as e:
                self.logger.error(f"Error in hunt cycle: {e}", exc_info=True)
                self.state = HuntState.ERROR
                self._schedule_ui_task(lambda: self._update_status(f"Error: {str(e)}"))
                time.sleep(2)
    
    def _update_status(self, status_text: str):
        """Update status in UI"""
        if 'update_status' in self.callbacks:
            self.callbacks['update_status'](status_text)
    
    def start_hunt(self, hunt_cfg: Dict[str, Any]):
        """
        Start automatic hunting
        
        Parameters:
        - hunt_cfg: Hunt configuration from hunt_config.json
        """
        if self.state == HuntState.HUNTING:
            self.logger.warning("Hunt already running")
            return
        
        self.state = HuntState.HUNTING
        self.stop_event.clear()
        self.session_stats = HuntSessionStats()
        
        self._update_status("⏳ Đang quét...")
        self.logger.info("=== AUTO HUNT STARTED ===")
        
        # Run hunt loop in background thread
        self.hunt_thread = Thread(target=self._run_hunt_cycle, daemon=True)
        self.hunt_thread.start()
    
    def stop_hunt(self):
        """
        Stop automatic hunting
        """
        if self.state != HuntState.HUNTING:
            self.logger.warning("Hunt not running")
            return
        
        self.logger.info("=== AUTO HUNT STOPPED ===")
        self.stop_event.set()
        
        # Calculate final stats
        self.session_stats.calculate_duration()
        
        self._update_status(f"🏁 Kết Thúc: {self.session_stats.monsters_killed} quái, {self.session_stats.duration_seconds:.0f}s")
        
        self.state = HuntState.IDLE
        
        # Wait for thread to finish
        if self.hunt_thread:
            self.hunt_thread.join(timeout=5)
        
        return self.session_stats
    
    def get_session_stats(self) -> HuntSessionStats:
        """Get current session statistics"""
        return self.session_stats
```

**Time**: 5 min

---

### **Task 2: Add Start/Stop Buttons to HuntTab** (3 min)

**File**: `ui/tabs/hunt_tab.py`

**Location**: Add to hunt control panel

**Code**:
```python
# Create hunt control buttons frame
hunt_control_frame = tk.Frame(self.app.hunt_setup_frame)
hunt_control_frame.pack(fill="x", padx=10, pady=10)

# Start Auto button
self.start_auto_btn = tk.Button(
    hunt_control_frame,
    text="🎬 Bắt Đầu Tự Động",
    command=self.on_start_auto,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 11, "bold"),
    width=20
)
self.start_auto_btn.pack(side="left", padx=5)

# Stop Auto button
self.stop_auto_btn = tk.Button(
    hunt_control_frame,
    text="⏹️ Dừng",
    command=self.on_stop_auto,
    bg="#f44336",
    fg="white",
    font=("Arial", 11, "bold"),
    width=20,
    state="disabled"  # Disabled until hunt starts
)
self.stop_auto_btn.pack(side="left", padx=5)

# Status label
self.hunt_status_label = tk.Label(
    hunt_control_frame,
    text="Sẵn sàng",
    fg="#666",
    font=("Arial", 9)
)
self.hunt_status_label.pack(side="left", padx=10)

def on_start_auto():
    """Start automatic hunt"""
    if not hasattr(self.app, 'auto_hunt_orchestrator'):
        messagebox.showerror("Lỗi", "AutoHuntOrchestrator not initialized")
        return
    
    # Disable start button, enable stop button
    self.start_auto_btn.config(state="disabled")
    self.stop_auto_btn.config(state="normal")
    self.hunt_status_label.config(text="⏳ Đang quét...", fg="#ff9800")
    
    # Start hunt
    hunt_cfg = self.app.hunt_cfg or {}
    self.app.auto_hunt_orchestrator.start_hunt(hunt_cfg)

def on_stop_auto():
    """Stop automatic hunt"""
    if not hasattr(self.app, 'auto_hunt_orchestrator'):
        return
    
    # Stop hunt and get stats
    stats = self.app.auto_hunt_orchestrator.stop_hunt()
    
    # Disable stop button, enable start button
    self.stop_auto_btn.config(state="disabled")
    self.start_auto_btn.config(state="normal")
    
    # Show summary
    summary = f"Kết Thúc Hunt\n\n" \
              f"Quái Giết: {stats.monsters_killed}\n" \
              f"Thời Gian: {stats.duration_seconds:.0f}s\n" \
              f"Drops: {len(stats.drops_collected)} items"
    
    self.hunt_status_label.config(text="Sẵn sàng", fg="#666")
    messagebox.showinfo("Hunt Summary", summary)

self.on_start_auto = on_start_auto
self.on_stop_auto = on_stop_auto
```

**Time**: 3 min

---

### **Task 3: Wire AutoHuntOrchestrator to HuntTab** (2 min)

**File**: `app_gui.py`

**Location**: In `App.__init__()` after UI init

**Code**:
```python
# Initialize AutoHuntOrchestrator
from lib.features.hunt.auto_hunt_orchestrator import AutoHuntOrchestrator

# Create orchestrator with callbacks
self.auto_hunt_orchestrator = AutoHuntOrchestrator(
    hwnd=self.hunt_selected.get('hwnd', 0),
    vision_engine=self.vision_engine,
    monster_repo=self.monster_repo,
    window_manager=self.window_manager,
    screen_capture=self.screen_capture,
    logger=logger,
    schedule_ui_task=lambda fn: self.after(0, fn),
    update_target_hp=self.hunt_tab.update_hp_display,
    update_target_name=self.hunt_tab.update_target_card,
    update_status=self.hunt_tab.update_status,
)

# Wire button callbacks
self.hunt_tab.on_start_auto = lambda: self.hunt_tab.on_start_auto()
self.hunt_tab.on_stop_auto = lambda: self.hunt_tab.on_stop_auto()
```

**Time**: 2 min

---

### **Task 4: Add i18n Keys** (1 min)

**File**: `lib/i18n/translations.json` or equivalent

**Code**:
```json
{
    "hunt.auto_start_btn": "🎬 Bắt Đầu Tự Động",
    "hunt.auto_stop_btn": "⏹️ Dừng",
    "hunt.scanning": "⏳ Đang quét...",
    "hunt.ready": "Sẵn sàng",
    "hunt.session_summary": "Kết Thúc Hunt",
    "hunt.monsters_killed": "Quái Giết:",
    "hunt.time_elapsed": "Thời Gian:",
    "hunt.drops_collected": "Drops:",
}
```

**Time**: 1 min

---

### **Task 5: Add Session Summary Dialog** (2 min)

**File**: `ui/tabs/hunt_tab.py`

**Code**:
```python
def show_hunt_summary(stats: HuntSessionStats):
    """Display hunt summary after stop"""
    summary_text = (
        f"┌─────────────────────────┐\n"
        f"│   Kết Thúc Hunt Session │\n"
        f"├─────────────────────────┤\n"
        f"│ Quái Giết: {stats.monsters_killed:>8}    │\n"
        f"│ EXP Nhận: {stats.exp_gained:>9}    │\n"
        f"│ Thời Gian: {stats.duration_seconds:>7}s    │\n"
        f"│ Items: {len(stats.drops_collected):>13}    │\n"
        f"└─────────────────────────┘"
    )
    
    messagebox.showinfo("Hunt Summary", summary_text)

self.show_hunt_summary = show_hunt_summary
```

**Time**: 2 min

---

## 📊 Implementation Checklist

- [ ] Task 0: Understand current code paths (0 min, read above)
- [ ] Task 1: Create AutoHuntOrchestrator class (5 min)
- [ ] Task 2: Add Start/Stop buttons to HuntTab (3 min)
- [ ] Task 3: Wire orchestrator to HuntTab (2 min)
- [ ] Task 4: Add i18n keys (1 min)
- [ ] Task 5: Add session summary dialog (2 min)
- [ ] Test: Click Start Auto → hunt loop runs
- [ ] Test: Z key sent each cycle
- [ ] Test: Monster detection working
- [ ] Test: DB lookup working
- [ ] Test: Monster displayed on screen
- [ ] Test: Click Stop Auto → hunt stops + summary shown
- [ ] Test: Session stats correct

**Total**: ~15 minutes

---

## 🎨 UI Layout (Desired)

```
┌────────────────────────────────────────────────────────────────┐
│ Hunt Control                                                   │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│ [🎬 Bắt Đầu Tự Động]  [⏹️ Dừng (disabled)]  Status: Sẵn sàng  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
│                                                                 │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ Target Card                                                │ │
│ ├────────────────────────────────────────────────────────────┤ │
│ │ [Image]                                                     │ │
│ │ Scarlet Scorpion (Lv. 45)                                   │ │
│ │ HP: 245/500 (49%) [━━━━━━━━━━━━━━─────────────]           │ │
│ │ Defense: 120 | Type: Scorpion                              │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

[After Stop Click]
┌─────────────────────────┐
│   Kết Thúc Hunt Session │
├─────────────────────────┤
│ Quái Giết:       5      │
│ EXP Nhận:    15500      │
│ Thời Gian:     120s     │
│ Items:          3       │
└─────────────────────────┘
```

---

## 🔗 Integration Points

**What gets wired together:**

```
HuntTab (UI)
  ├─ [Start Auto Button] → on_start_auto()
  │                          ↓
  │                  AutoHuntOrchestrator.start_hunt()
  │                  ├─ Thread: _run_hunt_cycle()
  │                  │  ├─ _send_z_key()
  │                  │  ├─ _capture_and_extract()
  │                  │  ├─ _lookup_monster_db()
  │                  │  ├─ _display_on_hunt_screen()
  │                  │  │  └─ [Callback] HuntTab.update_target_card()
  │                  │  ├─ _check_if_dead()
  │                  │  ├─ _cleanup_screenshot()
  │                  │  └─ [Wait 1.5s]
  │                  │
  │  ├─ [Stop Auto Button] → on_stop_auto()
  │                          ↓
  │              AutoHuntOrchestrator.stop_hunt()
  │              ├─ stop_event.set()
  │              ├─ Wait for thread
  │              ├─ Calculate stats
  │              └─ Return HuntSessionStats
  │                  ↓
  │          [Show Session Summary Dialog]
```

---

## 🎯 Key Improvements Over Current

| Aspect | Old (CLI-only) | New (GUI-integrated) |
|--------|-----------------|----------------------|
| **UI** | No UI buttons | Start/Stop buttons |
| **Threading** | Separate process | Background thread + callbacks |
| **Session Tracking** | Logging only | HuntSessionStats object |
| **Cleanup** | Manual | Automatic per cycle |
| **Z-Key Sending** | Yes | Yes |
| **Dead Detection** | Yes | Yes |
| **DB Lookup** | Yes | Yes |
| **HP Display** | No | Yes (real-time) |
| **Summary** | None | Dialog after stop |

---

**Status**: ✅ READY FOR IMPLEMENTATION  
**Complexity**: MEDIUM (new class + UI wiring)  
**Risk**: LOW (all logic already exists in CLI, just moving/integrating)  
**Backward Compat**: ✅ Old CLI still works separately

