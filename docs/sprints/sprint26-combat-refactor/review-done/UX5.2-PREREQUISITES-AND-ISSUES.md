# UX5.2 Implementation Prerequisites & Issues Found (2026-09-05)

**Status:** 🔴 **NOT READY** — 4 critical blockers found  
**Recommendation:** Fix all blockers before session starts

---

## 🚨 Critical Issues Blocking UX5.2

### Issue #1: HP Throttling Spec Violation (CRITICAL)

**Location:** `lib/vision/target_hp_reader.py` (Lines 9-10)  
**Current Code:**
```python
self.throttle_ms = 150      # ❌ WRONG
self.min_diff = 1.0          # ❌ WRONG
```

**Problem:**
- UX5.2 spec: 100ms hard limit, NOT 150ms
- UX5.2 spec: 0.5% delta threshold, NOT 1.0%
- Current logic is OR, should be AND

**Impact:** HP updates will exceed 10 FPS ceiling, causing UI stutters

**Required Fix:**
```python
# Change to:
self.throttle_ms = 100
self.min_delta_percent = 0.5

# Fix logic to AND:
# "100ms elapsed" AND "delta >= 0.5%" BOTH required
if time_elapsed >= throttle_ms and delta >= min_delta_percent:
    self.last_drawn_percent = current_percent
    self.last_draw_time = now
```

---

### Issue #2: Missing Canvas HP Bar (BLOCKING)

**Location:** `ui/tabs/hunt_tab.py` (Lines 324-325)  
**Current Code:**
```python
self.hp_progressbar = ttk.Progressbar(stats_frame, ...)  # ❌ WRONG
```

**Problem:**
- UX5.2 requires Canvas, not Progressbar
- No support for segmented step-fill rendering
- Cannot implement graceful death display

**Impact:** Cannot implement any UX5.2 HP features

**Required Changes:**
```python
# Replace Progressbar with:
self.hp_canvas = tk.Canvas(stats_frame, height=24, bg=UI.BG_MUTED, 
                           highlightthickness=0)
self.hp_canvas.pack(fill="x", pady=(0, 2))

# Pre-init Canvas objects:
self.hp_bg = self.hp_canvas.create_rectangle(0, 0, 1, 24, 
                                             fill="#27272A", outline="#27272A")
self.hp_fill = self.hp_canvas.create_rectangle(0, 0, 0, 24, 
                                               fill="#00E86D", outline="#00E86D")
self.hp_text = self.hp_canvas.create_text(0, 12, text="", 
                                         fill="white", anchor="center")
```

---

### Issue #3: No Graceful Death Handler (HIGH PRIORITY)

**Location:** `lib/vision/target_hp_reader.py` (missing) + `ui/tabs/hunt_tab.py` (incomplete)  
**Problem:**
- HP reader doesn't signal death (HP=0%)
- No Canvas gray color on death
- Race guard for rapid re-target is incomplete

**Impact:** Quick kills will cause card inconsistencies or wrong target display

**Required Implementation:**
1. In `target_hp_reader.py`:
   ```python
   # Add death signal:
   if current_percent == 0.0:
       self.last_drawn_percent = 0.0
       return 0.0
   ```

2. In `ui/tabs/hunt_tab.py` update_hp_display():
   ```python
   if hp_percent == 0.0:
       # Gray bar, death text, schedule clear
       self.hp_canvas.itemconfig(self.hp_fill, fill="#52525B")
       self.hp_canvas.itemconfig(self.hp_text, text="[ Đã Tiêu Diệt ]")
       # Cancel any pending clear (race guard)
       if self._pending_clear_id:
           self.after_cancel(self._pending_clear_id)
       # Schedule new clear
       self._pending_clear_id = self.after(200, self.clear_target_card)
   ```

---

### Issue #4: No Window Recovery Service (BLOCKING)

**Location:** `lib/features/hunt/window_selection_service.py` (missing)  
**Problem:**
- Only has validation, NO recovery logic
- No async retry mechanism
- No shared lock with UX1 (Action Bar)
- No Toast notification on failure

**Impact:** Cannot implement recovery button

**Required Implementation:**
- New `WindowRecoveryController` class
- Async 3-step retry (500ms spacing, NO `time.sleep()`)
- Retry lock (singleton pattern or class-level flag)
- Callbacks for progress + failure

---

## 📋 Prerequisite Tasks (Must Complete Before UX5.2)

### Task 1: Fix target_hp_reader.py (5 min)

**File:** `lib/vision/target_hp_reader.py`

1. Change line 9: `throttle_ms = 100`
2. Change line 10: `min_delta_percent = 0.5` (rename from min_diff)
3. Fix logic (lines 12-28):
   ```python
   def calculate_target_hp_percent(self, frame) -> float:
       now = time.monotonic()
       current_percent = self.detector.get_hp_percentage(frame)
       
       # Check time window
       time_elapsed = (now - self.last_draw_time) * 1000
       if time_elapsed < self.throttle_ms:
           return self.last_drawn_percent
       
       # Time OK, check delta
       delta = abs(current_percent - self.last_drawn_percent)
       if delta >= self.min_delta_percent:  # ✅ AND logic
           self.last_drawn_percent = current_percent
           self.last_draw_time = now
       
       # Death signal
       if current_percent == 0.0:
           return 0.0
       
       return self.last_drawn_percent
   ```

4. Test: `pytest tests/unit/vision/test_target_hp_reader.py -v`

---

### Task 2: Add i18n Keys (2 min)

**File:** `lib/i18n/translations.py`

Add to `GLOBAL_TRANSLATIONS`:
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

### Task 3: Implement Window Recovery Service (10 min)

**File:** `lib/features/hunt/window_selection_service.py`

Add new class:
```python
class WindowRecoveryController:
    """Shared retry logic for window recovery (UX1 + UX5.2)."""
    
    _instance = None  # Singleton
    
    def __init__(self):
        self._retry_in_progress = False
        self._retry_step = 0
        self._retry_max = 3
        self._hwnd = None
        self._on_progress = None
        self._on_failure = None
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def start_async_recovery(self, hwnd: int,
                             on_progress=None,
                             on_failure=None):
        """Start 3-step recovery (500ms spacing via self.after)."""
        if self._retry_in_progress:
            return  # Lock: already retrying
        
        self._retry_in_progress = True
        self._retry_step = 0
        self._hwnd = hwnd
        self._on_progress = on_progress
        self._on_failure = on_failure
        
        self._execute_retry_step()
    
    def _execute_retry_step(self):
        """Execute one retry step."""
        self._retry_step += 1
        
        if self._on_progress:
            self._on_progress(self._retry_step)
        
        # Attempt restore
        wm = WindowManager()
        success = wm.restore(self._hwnd) and wm.set_foreground(self._hwnd)
        
        if success or self._retry_step >= self._retry_max:
            self._retry_in_progress = False
            if not success and self._on_failure:
                self._on_failure()
            return
        
        # Schedule next step (500ms, no blocking)
        # IMPORTANT: This must be called from Main Thread context
        # self.after is NOT available here - caller must provide root window
        # See UI implementation for how to pass this
```

---

### Task 4: Replace Progressbar with Canvas (5 min)

**File:** `ui/tabs/hunt_tab.py` (_build_ui method, around line 324)

Replace:
```python
# Remove this:
self.hp_progressbar = ttk.Progressbar(stats_frame, orient="horizontal", 
                                      mode="determinate", maximum=100)
self.hp_progressbar.pack(fill="x", pady=(0, 2))

# With this:
self.hp_canvas = tk.Canvas(stats_frame, height=24, bg=UI.BG_MUTED, 
                           highlightthickness=0)
self.hp_canvas.pack(fill="x", pady=(0, 2))
self.hp_canvas.bind('<Configure>', self._on_hp_canvas_resize)

# Pre-init Canvas objects
self.hp_bg = self.hp_canvas.create_rectangle(0, 0, 1, 24, 
                                             fill="#27272A", outline="#27272A")
self.hp_fill = self.hp_canvas.create_rectangle(0, 0, 0, 24, 
                                               fill="#00E86D", outline="#00E86D")
self.hp_text = self.hp_canvas.create_text(0, 12, text="", 
                                         fill="white", anchor="center")
```

Add handler:
```python
def _on_hp_canvas_resize(self, event):
    """Canvas resize handler for responsive width."""
    width = event.width
    self.hp_canvas.coords(self.hp_bg, 0, 0, width, 24)
```

---

### Task 5: Update Methods in hunt_tab.py (3 min)

**Update `update_hp_display(hp_percent: float)`:**

Replace:
```python
def update_hp_display(self, hp_percent: float):
    if not hasattr(self, "hp_progressbar"):
        return
    self.hp_progressbar.config(value=hp_percent)
    if hasattr(self, "hp_percent_label"):
        self.hp_percent_label.config(text=f"{hp_percent:.1f}%")
```

With:
```python
def update_hp_display(self, hp_percent: float, current_hp: int = 0, 
                      max_hp: int = 10000):
    """Update Canvas HP bar with color and text."""
    if not hasattr(self, "hp_canvas"):
        return
    
    # Death case
    if hp_percent == 0.0:
        self.hp_canvas.itemconfig(self.hp_fill, fill="#52525B", outline="#52525B")
        self.hp_canvas.itemconfig(self.hp_text, text="[ Đã Tiêu Diệt ]")
        # Schedule clear (already handled in update_target_card)
        return
    
    # Normal rendering
    width = self.hp_canvas.winfo_width()
    if width < 2:
        width = 200  # Default if not rendered yet
    
    fill_width = int(width * hp_percent / 100)
    
    # Update bar position
    self.hp_canvas.coords(self.hp_fill, 0, 0, fill_width, 24)
    
    # Color by percent
    if hp_percent > 60:
        color = "#00E86D"  # Green
    elif hp_percent >= 30:
        color = "#FFB800"  # Orange
    else:
        color = "#FF3D3D"  # Red
    
    self.hp_canvas.itemconfig(self.hp_fill, fill=color, outline=color)
    
    # Update text
    text = f"{current_hp:,} / {max_hp:,} ({hp_percent:.1f}%)"
    self.hp_canvas.coords(self.hp_text, width/2, 12)
    self.hp_canvas.itemconfig(self.hp_text, text=text)
    
    # Update label for compatibility
    if hasattr(self, "hp_percent_label"):
        self.hp_percent_label.config(text=f"{hp_percent:.1f}%")
```

---

## ✅ Validation Checklist

Before starting UX5.2, verify:

- [ ] `target_hp_reader.py` throttle = 100ms, delta = 0.5%
- [ ] `target_hp_reader.py` logic uses AND (time AND delta)
- [ ] `ui/tabs/hunt_tab.py` has Canvas HP bar (not Progressbar)
- [ ] Canvas has pre-init objects: hp_bg, hp_fill, hp_text
- [ ] `i18n/translations.py` has all 4 new keys (target_dead, recovery_*)
- [ ] `window_selection_service.py` has WindowRecoveryController class
- [ ] All unit tests pass: `pytest tests/unit/ -v`

---

## 🎯 Effort & Timeline

| Task | Time | Blocker |
|------|------|---------|
| Fix throttle logic | 5 min | YES |
| Add i18n keys | 2 min | YES |
| Window recovery service | 10 min | YES |
| Replace Progressbar with Canvas | 5 min | YES |
| Update methods | 3 min | YES |
| Testing | 5 min | GATE |
| **TOTAL** | **30 min** | **→ Then start UX5.2** |

---

## ⚠️ Critical Reminders (From UX5.2 Prompt)

1. **Throttling is AND logic:**
   - NOT: "render if time OK OR delta large"
   - YES: "render if (time OK) AND (delta OK)"
   - NO EXCEPTIONS to 100ms rule

2. **Death Handler Race Guard:**
   - Must call `after_cancel()` before updating card for new target
   - Prevents accidental deletion of new target's card

3. **Retry Must Be Async:**
   - NO `time.sleep()` on Main Thread
   - Use `self.after(500, next_step)` between retries
   - Run from UI context (hunt_tab has `self.after`)

4. **HP Reader Must NOT Rewrite Logic:**
   - Only wrap `TargetBarDetector.get_hp_percentage()` (CB1)
   - Add throttle + smoothing, NOT new pixel-reading algorithm
   - Maintain CB1 as single source of truth

---

**Date:** 2026-09-05  
**Status:** Ready for prerequisites to be completed  
**Next:** Complete all 5 prerequisite tasks, then start UX5.2 session
