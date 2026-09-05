# Detailed Review: App Status vs UX5.2 Requirements (2026-09-05)

**Status:** 🟡 **UX5.2 CANNOT START YET** (Missing 4 critical components + 2 fixes needed)  
**Recommendation:** Complete UX5.2 prerequisites before implementation

---

## 📊 UX5.2 Implementation Dependency Chain

```
UX5.2 Session (Canvas HP + Recovery) — 25-30 min
  │
  ├─ ✅ UX5.1 Phase 1: Target Card Shell (READY)
  │  ├─ ✅ get_target_monster_info() - 2-tier fallback
  │  ├─ ✅ Target Card Panel UI structure
  │  ├─ ✅ clear_target_card(delay_ms) with race guard
  │  └─ ✅ i18n: status_idle, status_approaching, status_attacking, unknown_mob
  │
  ├─ ⚠️  CB4A Phase 2: Status Badge & Basic HP (PARTIAL - needs fixes)
  │  ├─ ⚠️  target_hp_reader.py (EXISTS but needs SPEC FIX)
  │  │  ├─ ❌ throttle_ms = 150 → MUST CHANGE TO 100
  │  │  ├─ ❌ min_diff = 1.0 → MUST CHANGE TO 0.5
  │  │  ├─ ❌ Logic is OR not AND → MUST FIX TO (elapsed >= 100ms) AND (delta >= 0.5%)
  │  │  ├─ ❌ NO graceful death handler → MUST ADD HP=0% → gray + [Đã Tiêu Diệt]
  │  │  └─ ❌ NO race guard on death → MUST ADD after_cancel() when target changes
  │  ├─ ✅ update_status() method exists in hunt_tab
  │  └─ ✅ update_hp_display() method exists in hunt_tab
  │
  ├─ ✅ CB1: TargetBarDetector.get_hp_percentage() (READY)
  │
  └─ ❌ Window Recovery Service (NOT STARTED)
      ├─ ❌ No async retry logic
      ├─ ❌ No retry lock (shared with UX1)
      ├─ ❌ No Toast notification system
      └─ ❌ No state tracking (retry step count)

---

## ✅ What Exists (Ready)

| Component | Location | Status | Details |
|-----------|----------|--------|---------|
| **UX5.1 Foundation** | `ui/tabs/hunt_tab.py` | ✅ READY | Target Card Panel structure, all i18n keys |
| **Status Badge** | `ui/tabs/hunt_tab.py` L:48-59 | ✅ READY | `update_status()` method implemented |
| **Basic HP Display** | `ui/tabs/hunt_tab.py` L:61-65 | ✅ READY | `update_hp_display(hp_percent)` method |
| **Card Reset** | `ui/tabs/hunt_tab.py` L:68-90 | ✅ READY | `clear_target_card()` with race guard |
| **TargetBarDetector** | `lib/vision/target_bar_detector.py` | ✅ READY | `get_hp_percentage()` method |
| **HP Reader** | `lib/vision/target_hp_reader.py` | ⚠️ PARTIAL | **EXISTS but WRONG SPEC** (see below) |
| **HuntOrchestrator** | `lib/features/hunt/hunt_orchestrator.py` | ✅ READY | Callbacks: `update_target_status`, `update_target_hp` |

---

## ❌ Missing/Broken Components (Blocking UX5.2)

### 1. **Canvas HP Bar** (BLOCKING)
**File:** `ui/tabs/hunt_tab.py` (L:324-325)  
**Current Status:** ❌ Only has Progressbar (`self.hp_progressbar`)  
**UX5.2 Requires:**
```python
# Replace ttk.Progressbar with tk.Canvas:
self.hp_canvas = tk.Canvas(stats_frame, height=24, bg=UI.BG_MUTED, highlightthickness=0)
self.hp_canvas.pack(fill="x", pady=(0, 2))

# Pre-init two Canvas objects:
self.hp_bg = self.hp_canvas.create_rectangle(0, 0, 1, 24, fill="#27272A", outline="#27272A")
self.hp_fill = self.hp_canvas.create_rectangle(0, 0, 0, 24, fill="#00E86D", outline="#00E86D")
self.hp_text = self.hp_canvas.create_text(0, 12, text="", fill="white", anchor="center")

# Add resize handler:
self.hp_canvas.bind('<Configure>', self._on_hp_canvas_resize)
```

**Update Logic (Segmented Step-Fill - NO delete("all")):**
```python
def _update_hp_canvas(self, percent: float, current_hp: int, max_hp: int):
    width = self.hp_canvas.winfo_width()
    fill_width = int(width * percent / 100)
    
    # Update fill rectangle only (coords, no delete)
    self.hp_canvas.coords(self.hp_fill, 0, 0, fill_width, 24)
    
    # Color by percent
    if percent > 60:
        color = "#00E86D"  # Green
    elif percent >= 30:
        color = "#FFB800"  # Orange
    else:
        color = "#FF3D3D"  # Red
    self.hp_canvas.itemconfig(self.hp_fill, fill=color, outline=color)
    
    # Update text
    text = f"{current_hp:,} / {max_hp:,} ({percent:.1f}%)"
    self.hp_canvas.coords(self.hp_text, width/2, 12)
    self.hp_canvas.itemconfig(self.hp_text, text=text)
```

**On Death (HP=0%):**
```python
# Canvas turns gray
self.hp_canvas.itemconfig(self.hp_fill, fill="#52525B", outline="#52525B")
self.hp_canvas.itemconfig(self.hp_text, text="[ Đã Tiêu Diệt ]")

# Schedule card clear (200ms delay)
self._pending_clear_id = self.after(200, self.clear_target_card)
```

**Impact:** Cannot implement UX5.2 without Canvas HP bar.

---

### 2. **HP Throttling Spec Violation** (CRITICAL FIX)
**File:** `lib/vision/target_hp_reader.py` (L:1-30)  
**Current Code:**
```python
self.throttle_ms = 150      # ❌ WRONG: Should be 100
self.min_diff = 1.0          # ❌ WRONG: Should be 0.5

def calculate_target_hp_percent(self, frame) -> float:
    now = time.monotonic()
    if (now - self.last_update_time) * 1000 < self.throttle_ms:
        return self.last_hp
    
    current_hp = self.detector.get_hp_percentage(frame)
    self.last_update_time = now
    
    # ❌ LOGIC BUG: OR instead of AND
    if abs(current_hp - self.last_hp) >= self.min_diff or current_hp == 0.0 or current_hp == 100.0:
        self.last_hp = current_hp
    
    return self.last_hp
```

**UX5.2 Spec (EXACT formula):**
- Hard limit: Never render UI faster than 100ms (10 FPS absolute)
- Within 100ms window that has elapsed: **AND** (delta >= 0.5%)
- Must NOT draw before 100ms expires even if delta > 0.5% (no early exit)

**Required Fix:**
```python
class TargetHPReader:
    def __init__(self, target_bar_detector: TargetBarDetector):
        self.detector = target_bar_detector
        self.last_drawn_percent = 100.0    # Track drawn value
        self.last_draw_time = 0.0          # Track last render time
        self.throttle_ms = 100             # ✅ FIX: Was 150
        self.min_delta_percent = 0.5       # ✅ FIX: Was 1.0
    
    def calculate_target_hp_percent(self, frame) -> float:
        now = time.monotonic()
        current_percent = self.detector.get_hp_percentage(frame)
        
        # Check time window (100ms)
        time_elapsed = (now - self.last_draw_time) * 1000
        if time_elapsed < self.throttle_ms:
            return self.last_drawn_percent  # Too soon, return cached
        
        # Time window OK, now check delta (0.5%)
        # ✅ AND logic: both conditions must be true
        delta = abs(current_percent - self.last_drawn_percent)
        if delta >= self.min_delta_percent:
            # Both: time OK AND delta OK → UPDATE
            self.last_drawn_percent = current_percent
            self.last_draw_time = now
        
        return self.last_drawn_percent
```

**Test Cases Needed:**
- Stress test: 2000 updates in 5s → max 50 renders (10 FPS × 5s)
- Delta skip: <0.5% change → no render until cumulative ≥0.5%
- Time cap: Never render faster than 100ms even if delta = 10%

---

### 3. **Graceful Death Reset & Race Guard** (HIGH PRIORITY)
**File:** `lib/vision/target_hp_reader.py` + `ui/tabs/hunt_tab.py`  
**Current Status:** ⚠️ Partial (clear_target_card exists but no death handler)  
**UX5.2 Requires:**

**In HP Reader (`target_hp_reader.py`):**
```python
def calculate_target_hp_percent(self, frame) -> float:
    current_percent = self.detector.get_hp_percentage(frame)
    
    # ... throttle logic ...
    
    # ✅ NEW: Handle death state
    if current_percent == 0.0:
        self.last_drawn_percent = 0.0
        self.last_draw_time = now
        return 0.0  # Signal death to UI
```

**In Target Card UI (`ui/tabs/hunt_tab.py`):**
```python
def update_hp_display(self, hp_percent: float):
    if not hasattr(self, "hp_canvas"):
        return
    
    # ✅ Handle death (0%)
    if hp_percent == 0.0:
        # Gray out bar
        self.hp_canvas.itemconfig(self.hp_fill, fill="#52525B", outline="#52525B")
        self.hp_canvas.itemconfig(self.hp_text, text="[ Đã Tiêu Diệt ]")
        
        # Schedule clear in 200ms
        if hasattr(self, "_pending_clear_id") and self._pending_clear_id:
            try:
                self.after_cancel(self._pending_clear_id)
            except tk.TclError:
                pass
        self._pending_clear_id = self.after(200, self.clear_target_card)
        return
    
    # Normal case (percent > 0)
    # ... render canvas ...

def update_target_card(self, name_or_id: str):
    # ✅ Race guard: cancel pending clear if target changes
    if hasattr(self, "_pending_clear_id") and self._pending_clear_id:
        try:
            self.after_cancel(self._pending_clear_id)
        except tk.TclError:
            pass
        self._pending_clear_id = None
    
    # ... load new target ...
```

**Impact:** Without death handler, kills cause UI inconsistencies.

---

### 4. **Window Recovery Service** (BLOCKING)
**File:** `lib/features/hunt/window_selection_service.py`  
**Current Status:** ❌ Validation only, NO recovery logic  
**UX5.2 Requires:**

**New Async Retry Logic (shared with UX1):**
```python
class WindowRecoveryController:
    """Shared retry logic for window recovery (UX1 + UX5.2)."""
    
    def __init__(self):
        self._retry_in_progress = False  # Lock: only one retry chain at a time
        self._retry_step = 0
        self._retry_max = 3
        self._on_retry_update = None  # Callback: update UI progress
        self._on_retry_failure = None # Callback: show failure Toast
    
    def start_async_recovery(self, hwnd: int, 
                             on_progress: Callable[[int], None] = None,
                             on_failure: Callable[[], None] = None):
        """Start 3-step recovery (500ms spacing, NO time.sleep)."""
        
        if self._retry_in_progress:
            return  # Lock: already retrying, ignore
        
        self._retry_in_progress = True
        self._retry_step = 0
        self._on_retry_update = on_progress
        self._on_retry_failure = on_failure
        self._hwnd = hwnd
        
        # Start step 1 immediately (via after, not blocking)
        self._execute_retry_step()
    
    def _execute_retry_step(self):
        """Execute one retry step, schedule next via after()."""
        self._retry_step += 1
        
        if self._on_retry_update:
            self._on_retry_update(self._retry_step)  # UI: "⏳ Đang thử lại (1/3)..."
        
        # Try to restore window
        wm = WindowManager()
        success = wm.restore(self._hwnd) and wm.set_foreground(self._hwnd)
        
        if success or self._retry_step >= self._retry_max:
            # Success or max retries reached
            self._retry_in_progress = False
            if not success and self._on_retry_failure:
                self._on_retry_failure()  # UI: show Toast
            return
        
        # Schedule next step (500ms delay, NO blocking)
        # This is called from Main Thread via after()
        self.after(500, self._execute_retry_step)
```

**In UI Target Card (`ui/tabs/hunt_tab.py`):**
```python
def _on_recovery_button_clicked(self):
    """Handler for window recovery button."""
    if not hasattr(self.app, "hunt_selected"):
        return
    
    selected = self.app.hunt_selected.get()
    if not selected or not isinstance(selected, dict):
        return
    
    hwnd = selected.get("hwnd")
    if not hwnd:
        return
    
    # Get recovery controller (singleton)
    recovery_controller = WindowRecoveryController.instance()
    
    # Start recovery
    recovery_controller.start_async_recovery(
        hwnd=hwnd,
        on_progress=lambda step: self._update_recovery_ui(step),
        on_failure=lambda: self._show_recovery_failed()
    )

def _update_recovery_ui(self, step: int):
    """Update UI during retry (not blocking)."""
    text = f"⏳ Đang thử lại ({step}/3)..."
    if hasattr(self, "recovery_status_label"):
        self.recovery_status_label.config(text=text)

def _show_recovery_failed(self):
    """Show failure message."""
    # Change label to red
    if hasattr(self, "recovery_status_label"):
        self.recovery_status_label.config(
            text="❌ Không thể khôi phục",
            fg=UIStyle.STATE_ERROR
        )
    
    # Show Toast
    if hasattr(self.app, "show_toast"):
        self.app.show_toast(
            self.app._t("target_card.recovery_failed"),
            style="error"
        )
```

**Impact:** Cannot implement recovery button without this logic.

---

## 🔴 Missing i18n Keys (UX5.2)

**File:** `lib/i18n/translations.py`  
**Current Keys:**
- ✅ `target_card.level`, `target_card.max_hp`, `target_card.defense`
- ✅ `target_card.status_idle`, `target_card.status_approaching`, `target_card.status_attacking`
- ✅ `target_card.unknown_mob`

**NEW Keys Required for UX5.2:**
```python
"target_card.target_dead": {
    "vi": "[ Đã Tiêu Diệt ]",
    "en": "[ Defeated ]"
},
"target_card.recovery_btn": {
    "vi": "Khôi Phục Cửa Sổ Game",
    "en": "Restore Game Window"
},
"target_card.recovery_retry": {
    "vi": "⏳ Đang thử lại ({step}/3)...",
    "en": "⏳ Retrying ({step}/3)..."
},
"target_card.recovery_failed": {
    "vi": "Không thể khôi phục game. Vui lòng mở lại game bằng tay.",
    "en": "Cannot restore game. Please reopen game manually."
}
```

---

## � Prerequisite Checklist Before Starting UX5.2

### Part 1: Fix target_hp_reader.py (5 min)

- [ ] **Change throttle_ms**: `150` → `100`
- [ ] **Change min_diff**: `1.0` → `0.5`
- [ ] **Fix logic to AND**: 
  ```python
  if time_elapsed >= throttle_ms and delta >= min_delta:
      self.last_drawn_percent = current_percent
      self.last_draw_time = now
  ```
- [ ] **Add death handler**: `if current_percent == 0.0: return 0.0`
- [ ] **Test:** `pytest tests/unit/vision/test_target_hp_reader.py -v`

### Part 2: Add Missing i18n Keys (2 min)

- [ ] Add 4 new keys to `lib/i18n/translations.py`:
  - `target_card.target_dead`
  - `target_card.recovery_btn`
  - `target_card.recovery_retry`
  - `target_card.recovery_failed`

### Part 3: Implement Window Recovery Service (10 min)

- [ ] Create `WindowRecoveryController` class in `window_selection_service.py`
- [ ] Implement `start_async_recovery(hwnd, on_progress, on_failure)`
- [ ] Implement `_execute_retry_step()` with `self.after()` (NO `time.sleep()`)
- [ ] Add retry lock (`_retry_in_progress` flag)
- [ ] Test with mock `WindowManager`

### Part 4: Ready UI for Canvas (5 min)

- [ ] Replace Progressbar with Canvas in `_build_ui()`:
  ```python
  # Remove: self.hp_progressbar = ttk.Progressbar(...)
  # Add:
  self.hp_canvas = tk.Canvas(stats_frame, height=24, ...)
  self.hp_bg = self.hp_canvas.create_rectangle(...)
  self.hp_fill = self.hp_canvas.create_rectangle(...)
  self.hp_text = self.hp_canvas.create_text(...)
  ```
- [ ] Add `_on_hp_canvas_resize()` handler

### Part 5: Wire Callbacks (3 min)

- [ ] In HuntOrchestrator, pass recovery callback to Target Card
- [ ] Verify callbacks: `update_target_hp`, `update_target_status` are wired

---

## 🎯 Implementation Order (Recommended)

**Phase 1 - Foundation (15 min):**
1. Fix target_hp_reader.py throttle + logic ✅ (5 min)
2. Add i18n keys ✅ (2 min)
3. Ready Canvas structure ✅ (5 min)
4. Wire callbacks ✅ (3 min)

**Phase 2 - UX5.2 Implementation (25-30 min):**
1. Implement Canvas rendering with step-fill
2. Implement graceful death handler + race guard
3. Implement window recovery service + retry logic
4. Full integration testing

**Total Timeline:** 40-45 min end-to-end

---

## ✅ Testing Requirements

### Unit Tests Needed

**`tests/unit/test_target_hp_reader.py`:**
- [ ] Test throttle cap at 100ms
- [ ] Test delta threshold (0.5%)
- [ ] Test AND logic (both time + delta required)
- [ ] Test death signal (0% returns 0.0)

**`tests/unit/test_target_hp_recovery.py`:**
- [ ] Stress test: 2000 updates/5s → max 50 renders
- [ ] Delta skip: <0.5% → no render
- [ ] Death reset: HP=0% → gray bar + [Đã Tiêu Diệt]
- [ ] Race guard: target change during 200ms → after_cancel
- [ ] Retry lock: two recovery starts → only one chain runs
- [ ] 3-step async: no `time.sleep()`, uses `self.after()`

### Integration Tests

- [ ] Canvas scales with window resize
- [ ] Colors update correctly (>60%, 30-60%, <30%)
- [ ] DPI support: 100%, 125%, 150%, 175%, 200%
- [ ] i18n switching: vi ↔ en updates all labels

---

## 🚨 Critical Requirements (MUST NOT VIOLATE)

### From UX5.2 Prompt

1. **Throttling Math:**
   - ✅ Hard limit: 100ms per render (10 FPS)
   - ✅ AND condition: `time_elapsed >= 100ms` **AND** `delta >= 0.5%`
   - ❌ No early exit, no exceptions to 100ms rule

2. **Death Handler:**
   - ✅ Canvas gray (`#52525B`)
   - ✅ Text: `[Đã Tiêu Diệt]`
   - ✅ Schedule clear: `self.after(200, clear_target_card)`
   - ✅ Race guard: `after_cancel()` when target changes

3. **Recovery Retry:**
   - ✅ 3 steps, 500ms spacing
   - ✅ NO `time.sleep()` (must use `self.after()`)
   - ✅ Retry lock: prevent concurrent retries
   - ✅ Toast on failure

4. **HP Reader:**
   - ✅ **NO** rewrite of pixel-reading logic
   - ✅ Must call `TargetBarDetector.get_hp_percentage()` (CB1)
   - ✅ Only wrap for throttle + smooth

---

## 📊 Current Status Summary

| Task | Status | Effort | Blocker |
|------|--------|--------|---------|
| Fix target_hp_reader throttle | 🔴 TODO | 5 min | YES |
| Add i18n keys | 🔴 TODO | 2 min | YES |
| Window recovery service | 🔴 TODO | 10 min | YES |
| Canvas HP bar | 🔴 TODO | 20 min | YES |
| Death handler + race guard | 🔴 TODO | 5 min | YES |
| Integration + testing | 🔴 TODO | 10 min | GATE |

**Total Effort:** 40-45 minutes  
**Can Start UX5.2:** After completing all "FIX" tasks above

---

## Next Steps

**Immediately:**
1. ✅ **DO NOT** start UX5.2 implementation yet
2. ✅ **FIX FIRST:** target_hp_reader.py (throttle + logic)
3. ✅ **ADD:** i18n keys for recovery
4. ✅ **PREPARE:** Canvas structure + callbacks

**Then:**
5. ✅ Start UX5.2 full implementation (25-30 min)
6. ✅ Run all tests, validate gate criteria
7. ✅ Commit with PASSED status
