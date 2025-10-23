"""
Window Tracker - Real-time window state monitoring for overlay sync
Sprint 23 Phase 5 Enhancement

Features:
- Track window position, size, state (minimized/maximized/normal)
- Detect window visibility changes
- High-frequency polling (60 FPS) for smooth tracking
- Callback system for state changes
- Thread-safe operation

Usage:
    tracker = WindowTracker(
        target_hwnd=game_hwnd,
        on_position_change=lambda rect: overlay.update_position(rect),
        on_size_change=lambda rect: overlay.update_size(rect),
        on_visibility_change=lambda visible: overlay.set_visible(visible),
        on_state_change=lambda state: handle_state(state)
    )
    tracker.start()
    # ... later
    tracker.stop()
"""

import threading
import time
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import win32gui
    import win32con
except ImportError:
    raise ImportError("pywin32 required for WindowTracker")


class WindowState(Enum):
    """Window state enumeration"""
    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    HIDDEN = "hidden"


@dataclass
class WindowSnapshot:
    """Snapshot of window state at a point in time"""
    hwnd: int
    rect: Dict[str, int]  # {left, top, right, bottom, width, height}
    state: WindowState
    is_visible: bool
    is_foreground: bool
    timestamp: float
    
    def __eq__(self, other) -> bool:
        """Compare snapshots (ignore timestamp)"""
        if not isinstance(other, WindowSnapshot):
            return False
        return (
            self.hwnd == other.hwnd and
            self.rect == other.rect and
            self.state == other.state and
            self.is_visible == other.is_visible and
            self.is_foreground == other.is_foreground
        )


class WindowTracker:
    """
    Real-time window state tracker with callback system.
    
    Monitors a target window and triggers callbacks when:
    - Position changes (move)
    - Size changes (resize)
    - Visibility changes (show/hide)
    - State changes (normal/minimized/maximized)
    """
    
    def __init__(
        self,
        target_hwnd: int,
        poll_rate: int = 60,  # FPS
        on_position_change: Optional[Callable[[Dict[str, int]], None]] = None,
        on_size_change: Optional[Callable[[Dict[str, int]], None]] = None,
        on_visibility_change: Optional[Callable[[bool], None]] = None,
        on_state_change: Optional[Callable[[WindowState], None]] = None,
        on_any_change: Optional[Callable[[WindowSnapshot], None]] = None,
    ):
        """
        Initialize window tracker.
        
        Args:
            target_hwnd: Window handle to track
            poll_rate: Polling frequency in Hz (default 60 FPS)
            on_position_change: Callback(rect) when window moves
            on_size_change: Callback(rect) when window resizes
            on_visibility_change: Callback(visible) when show/hide
            on_state_change: Callback(state) when minimize/maximize/restore
            on_any_change: Callback(snapshot) on any change
        """
        self.target_hwnd = target_hwnd
        self.poll_rate = poll_rate
        self.poll_interval = 1.0 / poll_rate
        
        # Callbacks
        self.on_position_change = on_position_change
        self.on_size_change = on_size_change
        self.on_visibility_change = on_visibility_change
        self.on_state_change = on_state_change
        self.on_any_change = on_any_change
        
        # State
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_snapshot: Optional[WindowSnapshot] = None
        
        print(f"[WindowTracker] Initialized for HWND:{target_hwnd} @ {poll_rate} FPS")
    
    def start(self) -> None:
        """Start tracking window."""
        if self._running:
            print("[WindowTracker] Already running")
            return
        
        self._running = True
        self._stop_event.clear()
        
        self._thread = threading.Thread(
            target=self._tracking_loop,
            name="WindowTracker",
            daemon=True
        )
        self._thread.start()
        
        print(f"[WindowTracker] Started tracking HWND:{self.target_hwnd}")
    
    def stop(self) -> None:
        """Stop tracking window."""
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        
        self._thread = None
        print("[WindowTracker] Stopped")
    
    def get_current_snapshot(self) -> Optional[WindowSnapshot]:
        """Get current window snapshot (thread-safe)."""
        try:
            return self._capture_snapshot()
        except Exception as e:
            print(f"[WindowTracker] Error capturing snapshot: {e}")
            return None
    
    def _capture_snapshot(self) -> WindowSnapshot:
        """Capture current window state."""
        # Get window rect
        try:
            rect_tuple = win32gui.GetWindowRect(self.target_hwnd)
            left, top, right, bottom = rect_tuple
            rect = {
                'left': left,
                'top': top,
                'right': right,
                'bottom': bottom,
                'width': right - left,
                'height': bottom - top
            }
        except Exception:
            # Window may be destroyed
            raise RuntimeError(f"Cannot get rect for HWND:{self.target_hwnd}")
        
        # Get window state
        state = self._get_window_state()
        
        # Check visibility
        is_visible = win32gui.IsWindowVisible(self.target_hwnd) != 0
        
        # Check if foreground
        foreground_hwnd = win32gui.GetForegroundWindow()
        is_foreground = (foreground_hwnd == self.target_hwnd)
        
        return WindowSnapshot(
            hwnd=self.target_hwnd,
            rect=rect,
            state=state,
            is_visible=is_visible,
            is_foreground=is_foreground,
            timestamp=time.time()
        )
    
    def _get_window_state(self) -> WindowState:
        """Determine current window state."""
        try:
            # Check minimized
            if win32gui.IsIconic(self.target_hwnd):
                return WindowState.MINIMIZED
            
            # Check maximized
            if win32gui.IsZoomed(self.target_hwnd):
                return WindowState.MAXIMIZED
            
            # Check visible
            if not win32gui.IsWindowVisible(self.target_hwnd):
                return WindowState.HIDDEN
            
            return WindowState.NORMAL
            
        except Exception:
            return WindowState.HIDDEN
    
    def _tracking_loop(self) -> None:
        """Main tracking loop (runs in background thread)."""
        print(f"[WindowTracker] Tracking loop started @ {self.poll_rate} FPS")
        print(f"[WindowTracker] Callbacks registered: pos={self.on_position_change is not None}, size={self.on_size_change is not None}, vis={self.on_visibility_change is not None}, state={self.on_state_change is not None}")
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while not self._stop_event.is_set():
                loop_start = time.time()
                
                try:
                    # Capture current state
                    snapshot = self._capture_snapshot()
                    
                    # Compare with last snapshot
                    if self._last_snapshot is None:
                        # First snapshot - trigger all callbacks
                        print(f"[WindowTracker] First snapshot captured, triggering initial callbacks...")
                        self._trigger_all_callbacks(snapshot, is_initial=True)
                    else:
                        # Detect changes and trigger appropriate callbacks
                        self._detect_and_trigger_changes(self._last_snapshot, snapshot)
                    
                    # Update last snapshot
                    self._last_snapshot = snapshot
                    frame_count += 1
                    
                    # Log heartbeat every 60 frames (1 second at 60 FPS)
                    if frame_count % 60 == 0:
                        print(f"[WindowTracker] ❤️ Heartbeat: frame #{frame_count}, tracking HWND:{self.target_hwnd}")
                    
                    # Log stats every 5 seconds
                    if frame_count % (self.poll_rate * 5) == 0:
                        elapsed = time.time() - start_time
                        actual_fps = frame_count / elapsed
                        print(f"[WindowTracker] Stats: {frame_count} frames, {actual_fps:.1f} FPS avg")
                    
                except RuntimeError as e:
                    # Window destroyed or invalid
                    print(f"[WindowTracker] Target window lost: {e}")
                    break
                    
                except Exception as e:
                    print(f"[WindowTracker] Loop error: {e}")
                
                # Sleep to maintain poll rate
                elapsed = time.time() - loop_start
                sleep_time = max(0, self.poll_interval - elapsed)
                self._stop_event.wait(timeout=sleep_time)
                
        except Exception as e:
            print(f"[WindowTracker] Fatal error in tracking loop: {e}")
            import traceback
            traceback.print_exc()
        
        print("[WindowTracker] Tracking loop ended")
    
    def _detect_and_trigger_changes(
        self,
        old: WindowSnapshot,
        new: WindowSnapshot
    ) -> None:
        """Detect changes between snapshots and trigger callbacks."""
        # Position change
        if (old.rect['left'] != new.rect['left'] or 
            old.rect['top'] != new.rect['top']):
            try:
                print(f"[WindowTracker] 🔄 Position CHANGE detected: ({old.rect['left']},{old.rect['top']}) → ({new.rect['left']},{new.rect['top']})")
                if self.on_position_change:
                    self.on_position_change(new.rect)
                    print(f"[WindowTracker] ✅ Position callback executed")
            except Exception as e:
                print(f"[WindowTracker] ❌ Error in on_position_change: {e}")
                import traceback
                traceback.print_exc()
        
        # Size change
        if (old.rect['width'] != new.rect['width'] or 
            old.rect['height'] != new.rect['height']):
            try:
                print(f"[WindowTracker] 📏 Size CHANGE detected: {old.rect['width']}x{old.rect['height']} → {new.rect['width']}x{new.rect['height']}")
                if self.on_size_change:
                    self.on_size_change(new.rect)
                    print(f"[WindowTracker] ✅ Size callback executed")
            except Exception as e:
                print(f"[WindowTracker] ❌ Error in on_size_change: {e}")
                import traceback
                traceback.print_exc()
        
        # Visibility change
        if old.is_visible != new.is_visible:
            try:
                print(f"[WindowTracker] 👁️ Visibility CHANGE detected: {old.is_visible} → {new.is_visible}")
                if self.on_visibility_change:
                    self.on_visibility_change(new.is_visible)
                    print(f"[WindowTracker] ✅ Visibility callback executed")
            except Exception as e:
                print(f"[WindowTracker] ❌ Error in on_visibility_change: {e}")
                import traceback
                traceback.print_exc()
        
        # State change
        if old.state != new.state:
            try:
                print(f"[WindowTracker] 🔄 State CHANGE detected: {old.state.value} → {new.state.value}")
                if self.on_state_change:
                    self.on_state_change(new.state)
                    print(f"[WindowTracker] ✅ State callback executed")
            except Exception as e:
                print(f"[WindowTracker] ❌ Error in on_state_change: {e}")
                import traceback
                traceback.print_exc()
        
        # Any change
        if old != new:
            try:
                if self.on_any_change:
                    self.on_any_change(new)
            except Exception as e:
                print(f"[WindowTracker] ❌ Error in on_any_change: {e}")
                import traceback
                traceback.print_exc()
    
    def _trigger_all_callbacks(
        self,
        snapshot: WindowSnapshot,
        is_initial: bool = False
    ) -> None:
        """Trigger all callbacks with initial snapshot."""
        prefix = "[Initial] " if is_initial else ""
        
        try:
            if self.on_position_change:
                print(f"{prefix}[WindowTracker] Calling on_position_change...")
                self.on_position_change(snapshot.rect)
                print(f"{prefix}[WindowTracker] ✅ Position callback done: ({snapshot.rect['left']},{snapshot.rect['top']})")
        except Exception as e:
            print(f"{prefix}[WindowTracker] ❌ Error in on_position_change: {e}")
            import traceback
            traceback.print_exc()
        
        try:
            if self.on_size_change:
                print(f"{prefix}[WindowTracker] Calling on_size_change...")
                self.on_size_change(snapshot.rect)
                print(f"{prefix}[WindowTracker] ✅ Size callback done: {snapshot.rect['width']}x{snapshot.rect['height']}")
        except Exception as e:
            print(f"{prefix}[WindowTracker] ❌ Error in on_size_change: {e}")
            import traceback
            traceback.print_exc()
        
        try:
            if self.on_visibility_change:
                print(f"{prefix}[WindowTracker] Calling on_visibility_change...")
                self.on_visibility_change(snapshot.is_visible)
                print(f"{prefix}[WindowTracker] ✅ Visibility callback done: {snapshot.is_visible}")
        except Exception as e:
            print(f"{prefix}[WindowTracker] ❌ Error in on_visibility_change: {e}")
            import traceback
            traceback.print_exc()
        
        try:
            if self.on_state_change:
                print(f"{prefix}[WindowTracker] Calling on_state_change...")
                self.on_state_change(snapshot.state)
                print(f"{prefix}[WindowTracker] ✅ State callback done: {snapshot.state.value}")
        except Exception as e:
            print(f"{prefix}[WindowTracker] ❌ Error in on_state_change: {e}")
            import traceback
            traceback.print_exc()
        
        try:
            if self.on_any_change:
                self.on_any_change(snapshot)
        except Exception as e:
            print(f"{prefix}[WindowTracker] ❌ Error in on_any_change: {e}")
            import traceback
            traceback.print_exc()
    
    def is_running(self) -> bool:
        """Check if tracker is running."""
        return self._running
    
    def __enter__(self):
        """Context manager support."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.stop()
