"""
Overlay Window - Transparent, topmost, click-through window for vision detection display
Sprint 23 Phase 5

Features:
- Transparent background with alpha blending
- Always on top (topmost)
- Click-through (WS_EX_TRANSPARENT)
- Real-time detection box rendering
- Color-coded states (red=searching, green=detected, blue=tracking)
- FPS-limited updates (default 15 FPS)
- Syncs position with target game window

Architecture:
- Win32 API for transparent, click-through window
- Canvas-based rendering using tkinter
- Thread-safe update queue
- Automatic position tracking

Usage:
    overlay = OverlayWindow(
        target_hwnd=game_window_hwnd,
        target_rect={'left': 0, 'top': 0, 'width': 800, 'height': 600},
        alpha=0.7,
        fps_limit=15
    )
    overlay.show()
    overlay.update_detections([...])
    overlay.hide()
    overlay.destroy()
"""

import tkinter as tk
import sys
import time
import threading
import queue
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

# Windows-specific imports for click-through and transparency
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
    
    # Win32 constants
    GWL_EXSTYLE = -20
    GWL_WNDPROC = -4
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_NOACTIVATE = 0x08000000  # Window doesn't activate when clicked
    WS_EX_TOPMOST = 0x00000008
    LWA_ALPHA = 0x00000002
    
    # SetWindowPos flags
    SWP_FRAMECHANGED = 0x0020
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOZORDER = 0x0004
    SWP_SHOWWINDOW = 0x0040
    
    # SetWindowLong result
    HWND_TOPMOST = -1
    
    # Window messages for WndProc
    WM_NCHITTEST = 0x0084
    HTTRANSPARENT = -1
    
    # Define WndProc callback type
    WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_long)
else:
    # Stub for non-Windows platforms
    GWL_EXSTYLE = None
    GWL_WNDPROC = None
    WS_EX_LAYERED = None
    WS_EX_TRANSPARENT = None
    WS_EX_NOACTIVATE = None
    WS_EX_TOPMOST = None
    LWA_ALPHA = None
    SWP_FRAMECHANGED = None
    SWP_NOMOVE = None
    SWP_NOSIZE = None
    SWP_NOZORDER = None
    SWP_SHOWWINDOW = None
    HWND_TOPMOST = None
    WM_NCHITTEST = None
    HTTRANSPARENT = None
    WNDPROC = None


# =====================================================================
# Data Classes
# =====================================================================

@dataclass
class DetectionBox:
    """Single detection box for rendering"""
    x: int
    y: int
    w: int
    h: int
    label: str
    color: Tuple[int, int, int]  # RGB tuple
    confidence: float = 0.0
    
    def to_tkinter_color(self) -> str:
        """Convert RGB tuple to tkinter color string"""
        return f"#{self.color[0]:02x}{self.color[1]:02x}{self.color[2]:02x}"


# =====================================================================
# Overlay Window Class
# =====================================================================

class OverlayWindow:
    """
    Transparent, topmost, click-through overlay window for vision detection.
    
    Thread-safe: update_detections() can be called from any thread.
    """
    
    def __init__(
        self,
        target_hwnd: Optional[int] = None,
        target_rect: Optional[Dict[str, int]] = None,
        alpha: float = 0.7,
        fps_limit: int = 15,
        enable_click_through: bool = True,
        trail_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize overlay window.
        
        Args:
            target_hwnd: Handle of target window to track (optional)
            target_rect: Initial rect {'left', 'top', 'width', 'height'}
            alpha: Transparency level (0.0 = invisible, 1.0 = opaque)
            fps_limit: Maximum FPS for rendering updates
            enable_click_through: Enable click-through (Win32 only)
            trail_config: Trail configuration {'enabled': bool, 'length': int, 'fade': bool}
        """
        # Validate parameters
        if alpha < 0.0 or alpha > 1.0:
            raise ValueError(f"Alpha must be 0.0-1.0, got {alpha}")
        if fps_limit <= 0:
            raise ValueError(f"FPS limit must be > 0, got {fps_limit}")
        
        self.target_hwnd = target_hwnd
        self.target_rect = target_rect or {'left': 0, 'top': 0, 'width': 800, 'height': 600}
        self.alpha = alpha
        self.fps_limit = fps_limit
        self.enable_click_through = enable_click_through and sys.platform == "win32"
        
        # Trail configuration
        default_trail = {'enabled': False, 'length': 5, 'fade': True}
        self.trail_config = {**default_trail, **(trail_config or {})}
        
        # State
        self.window: Optional[tk.Toplevel] = None
        self.canvas: Optional[tk.Canvas] = None
        self.visible = False
        self.running = False
        
        # Win32 WndProc subclassing
        self._old_wndproc = None
        self._new_wndproc = None
        
        # Detection data (thread-safe)
        self._detections_queue: queue.Queue[List[DetectionBox]] = queue.Queue(maxsize=2)
        self._current_detections: List[DetectionBox] = []
        self._detections_lock = threading.Lock()
        
        # Trail history: dict[label] -> List[DetectionBox]
        self._trail_history: Dict[str, List[DetectionBox]] = {}
        self._trail_lock = threading.Lock()
        
        # Update thread
        self._update_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Performance tracking
        self._last_render_time = 0.0
        self._frame_interval = 1.0 / fps_limit
        
    def create(self, parent: Optional[tk.Tk] = None) -> None:
        """
        Create the overlay window.
        
        Args:
            parent: Parent tkinter window (optional, creates new Tk if None)
        """
        if self.window is not None:
            return  # Already created
        
        # Create toplevel window
        if parent is not None:
            self.window = tk.Toplevel(parent)
        else:
            # Create independent root if no parent
            root = tk.Tk()
            root.withdraw()  # Hide root window
            self.window = tk.Toplevel(root)
        
        # Configure window
        self.window.title("Vision Overlay")
        self.window.overrideredirect(True)  # Remove window decorations
        self.window.attributes('-topmost', True)  # Always on top
        
        # Set transparency
        try:
            self.window.attributes('-alpha', self.alpha)
        except tk.TclError:
            pass  # Some systems may not support alpha
        
        # Set initial geometry
        self._update_geometry()
        
        # Create canvas for rendering
        self.canvas = tk.Canvas(
            self.window,
            bg='black',
            highlightthickness=0,
            borderwidth=0,
            takefocus=0  # Don't accept keyboard focus
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Configure canvas to ensure white text renders properly
        self.canvas.config(insertbackground='white')
        
        # CRITICAL: Disable ALL canvas mouse events for click-through
        # This is the key to make tkinter click-through work!
        if self.enable_click_through:
            self._disable_canvas_events()
        
        # Apply click-through on Windows
        if self.enable_click_through:
            self._apply_click_through()
        
        # Start hidden
        self.window.withdraw()
    
    def _wndproc_hook(self, hwnd, msg, wparam, lparam):
        """Custom WndProc to handle WM_NCHITTEST for click-through."""
        # If click-through enabled and hit test message, return transparent
        if msg == WM_NCHITTEST and self.enable_click_through:
            return HTTRANSPARENT
        
        # Call original WndProc
        if self._old_wndproc:
            return ctypes.windll.user32.CallWindowProcW(
                self._old_wndproc, hwnd, msg, wparam, lparam
            )
        return 0
    
    def _disable_canvas_events(self):
        """Disable all mouse and keyboard events on canvas for true click-through."""
        if not self.canvas:
            return
        
        print("[Overlay] Disabling ALL canvas events for click-through...")
        
        # Disable all mouse events
        mouse_events = [
            "<Button-1>", "<Button-2>", "<Button-3>",
            "<ButtonPress>", "<ButtonRelease>",
            "<Double-Button-1>", "<Triple-Button-1>",
            "<B1-Motion>", "<B2-Motion>", "<B3-Motion>",
            "<Motion>", "<Enter>", "<Leave>",
            "<MouseWheel>", "<Button-4>", "<Button-5>"
        ]
        
        for event in mouse_events:
            try:
                # Bind to lambda that returns "break" to stop propagation
                self.canvas.bind(event, lambda e: "break", add=False)
            except:
                pass
        
        # Disable keyboard events
        keyboard_events = [
            "<Key>", "<KeyPress>", "<KeyRelease>",
            "<FocusIn>", "<FocusOut>"
        ]
        
        for event in keyboard_events:
            try:
                self.canvas.bind(event, lambda e: "break", add=False)
            except:
                pass
        
        # Set canvas to not accept any interaction
        try:
            self.canvas.configure(state='disabled')
            print("[Overlay] ✅ Canvas set to 'disabled' state")
        except:
            pass
        
        print("[Overlay] ✅ All canvas events disabled")
    
    def _enable_canvas_events(self):
        """Re-enable canvas events when click-through disabled."""
        if not self.canvas:
            return
        
        print("[Overlay] Re-enabling canvas events...")
        
        # Unbind all events
        for event in self.canvas.bind():
            try:
                self.canvas.unbind(event)
            except:
                pass
        
        # Re-enable canvas
        try:
            self.canvas.configure(state='normal')
            print("[Overlay] ✅ Canvas set to 'normal' state")
        except:
            pass
        
        print("[Overlay] ✅ Canvas events re-enabled")
        
    def _apply_click_through(self) -> None:
        """Apply Win32 transparent window style for click-through."""
        if not sys.platform == "win32":
            return
        
        if self.window is None:
            return
        
        try:
            # Ensure window is updated before getting handle
            self.window.update_idletasks()
            
            # Get window handle
            hwnd = self.window.winfo_id()
            
            # Get current extended style
            user32 = ctypes.windll.user32
            current_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            
            print(f"[Overlay] Current style BEFORE change: {hex(current_style)}")
            
            # Toggle transparent flag based on enable_click_through
            if self.enable_click_through:
                # Add transparent, layered, and noactivate flags for true click-through
                new_style = current_style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE
                print(f"[Overlay] Enabling click-through")
            else:
                # Remove transparent and noactivate flags, keep layered for alpha
                new_style = (current_style | WS_EX_LAYERED) & ~WS_EX_TRANSPARENT & ~WS_EX_NOACTIVATE
                print(f"[Overlay] Disabling click-through")
            
            print(f"[Overlay] Target new style: {hex(new_style)}")
            
            # Apply new style
            result = user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
            print(f"[Overlay] SetWindowLongW result (old style): {hex(result) if result else 'ERROR'}")
            
            # Verify style was applied
            verified_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            print(f"[Overlay] Verified style AFTER change: {hex(verified_style)}")
            
            if verified_style != new_style:
                print(f"[Overlay] ⚠️ WARNING: Style mismatch! Expected {hex(new_style)}, got {hex(verified_style)}")
            else:
                print(f"[Overlay] ✅ Style applied successfully")
            
            # Set layered window attributes (MUST be called after style change)
            # Convert alpha to 0-255 range
            alpha_byte = int(self.alpha * 255)
            lwa_result = user32.SetLayeredWindowAttributes(hwnd, 0, alpha_byte, LWA_ALPHA)
            print(f"[Overlay] SetLayeredWindowAttributes result: {lwa_result} (alpha: {alpha_byte})")
            
            # Force window to update and redraw with SWP_FRAMECHANGED
            swp_result = user32.SetWindowPos(
                hwnd, 
                HWND_TOPMOST,  # Keep topmost
                0, 0, 0, 0,
                SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER
            )
            print(f"[Overlay] SetWindowPos result: {swp_result}")
            
            # Force redraw
            user32.UpdateWindow(hwnd)
            print(f"[Overlay] UpdateWindow called")
            
            # Final verification
            final_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            print(f"[Overlay] Final verified style: {hex(final_style)}")
            
            # Check specific flags
            has_layered = bool(final_style & WS_EX_LAYERED)
            has_transparent = bool(final_style & WS_EX_TRANSPARENT)
            has_noactivate = bool(final_style & WS_EX_NOACTIVATE)
            
            print(f"[Overlay] Flags check:")
            print(f"  - WS_EX_LAYERED: {has_layered}")
            print(f"  - WS_EX_TRANSPARENT: {has_transparent}")
            print(f"  - WS_EX_NOACTIVATE: {has_noactivate}")
            
            if self.enable_click_through:
                if has_transparent and has_noactivate:
                    print(f"[Overlay] ✅ Click-through ENABLED successfully")
                else:
                    print(f"[Overlay] ❌ Click-through flags NOT set correctly!")
            else:
                if not has_transparent and not has_noactivate:
                    print(f"[Overlay] ✅ Click-through DISABLED successfully")
                else:
                    print(f"[Overlay] ❌ Click-through flags still present!")
            
        except Exception as e:
            import traceback
            print(f"[Overlay] ❌ Failed to apply click-through: {e}")
            traceback.print_exc()
    
    def _subclass_wndproc(self, hwnd):
        """Subclass window procedure to return HTTRANSPARENT on WM_NCHITTEST."""
        if not sys.platform == "win32":
            return
        
        try:
            # Create new WndProc callback (must keep reference!)
            self._new_wndproc = WNDPROC(self._wndproc_hook)
            
            # Subclass the window
            user32 = ctypes.windll.user32
            self._old_wndproc = user32.SetWindowLongW(hwnd, GWL_WNDPROC, self._new_wndproc)
            
            print(f"[Overlay] ✅ WndProc subclassed (old: {self._old_wndproc})")
            print(f"[Overlay] → Will return HTTRANSPARENT on WM_NCHITTEST")
            
        except Exception as e:
            print(f"[Overlay] ⚠️ Failed to subclass WndProc: {e}")
    
    def _unsubclass_wndproc(self, hwnd):
        """Restore original window procedure."""
        if not sys.platform == "win32" or not self._old_wndproc:
            return
        
        try:
            user32 = ctypes.windll.user32
            user32.SetWindowLongW(hwnd, GWL_WNDPROC, self._old_wndproc)
            print(f"[Overlay] ✅ WndProc restored to original")
            self._old_wndproc = None
            self._new_wndproc = None
        except Exception as e:
            print(f"[Overlay] ⚠️ Failed to restore WndProc: {e}")
    
    def _update_geometry(self) -> None:
        """Update window geometry based on target rect."""
        if self.window is None:
            return
        
        left = self.target_rect.get('left', 0)
        top = self.target_rect.get('top', 0)
        width = self.target_rect.get('width', 800)
        height = self.target_rect.get('height', 600)
        
        # Ensure positive dimensions
        width = max(1, width)
        height = max(1, height)
        
        geometry_str = f"{width}x{height}+{left}+{top}"
        self.window.geometry(geometry_str)
    
    def show(self) -> None:
        """Show the overlay window."""
        if self.window is None:
            raise RuntimeError("Window not created. Call create() first.")
        
        if not self.visible:
            self.window.deiconify()
            self.visible = True
            
            # Start update thread if not running
            if not self.running:
                self._start_update_thread()
    
    def hide(self) -> None:
        """Hide the overlay window."""
        if self.window is not None and self.visible:
            self.window.withdraw()
            self.visible = False
    
    def toggle(self) -> bool:
        """
        Toggle overlay visibility.
        
        Returns:
            New visibility state (True=visible, False=hidden)
        """
        if self.visible:
            self.hide()
            return False
        else:
            self.show()
            return True
    
    def update_target_rect(self, rect: Dict[str, int]) -> None:
        """
        Update target window rect and reposition overlay.
        
        Args:
            rect: New rect {'left', 'top', 'width', 'height'}
        """
        self.target_rect = rect
        self._update_geometry()
    
    def update_detections(self, detections: List[DetectionBox]) -> None:
        """
        Update detection boxes (thread-safe).
        
        Args:
            detections: List of DetectionBox instances
        """
        # Drop old frame if queue full (skip frames to maintain real-time)
        try:
            if self._detections_queue.full():
                try:
                    self._detections_queue.get_nowait()
                except queue.Empty:
                    pass
            
            self._detections_queue.put_nowait(detections)
        except queue.Full:
            pass  # Skip frame if queue still full
    
    def _start_update_thread(self) -> None:
        """Start the rendering update thread."""
        if self.running:
            return
        
        self.running = True
        self._stop_event.clear()
        
        self._update_thread = threading.Thread(
            target=self._update_loop,
            name="OverlayUpdateThread",
            daemon=True
        )
        self._update_thread.start()
    
    def _stop_update_thread(self) -> None:
        """Stop the rendering update thread."""
        if not self.running:
            return
        
        self.running = False
        self._stop_event.set()
        
        if self._update_thread is not None:
            self._update_thread.join(timeout=1.0)
            self._update_thread = None
    
    def _update_loop(self) -> None:
        """Main update loop (runs in background thread)."""
        while not self._stop_event.is_set():
            try:
                # FPS limiting
                current_time = time.time()
                elapsed = current_time - self._last_render_time
                
                if elapsed < self._frame_interval:
                    # Sleep remainder of frame time
                    sleep_time = self._frame_interval - elapsed
                    self._stop_event.wait(timeout=sleep_time)
                    continue
                
                # Get latest detections from queue (non-blocking)
                try:
                    detections = self._detections_queue.get_nowait()
                    with self._detections_lock:
                        self._current_detections = detections
                except queue.Empty:
                    # No new data, use current detections
                    pass
                
                # Schedule render in main thread (thread-safe)
                # Only schedule if window still exists
                if self.window is not None and self.visible:
                    try:
                        # Use after_idle instead of after(0) - more reliable
                        self.window.after_idle(self._render)
                    except (tk.TclError, RuntimeError):
                        # Window destroyed, stop loop
                        break
                
                self._last_render_time = current_time
                
            except Exception as e:
                print(f"[Overlay] Update loop error: {e}")
                # Don't spam errors - wait a bit before retrying
                self._stop_event.wait(timeout=0.1)
    
    def _render(self) -> None:
        """Render detection boxes to canvas (called from main thread)."""
        if self.canvas is None:
            return
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Get current detections (thread-safe)
        with self._detections_lock:
            detections = self._current_detections.copy()
        
        # Update trail history if enabled
        if self.trail_config.get('enabled', False):
            self._update_trail_history(detections)
        
        # Draw trails first (behind current detections)
        if self.trail_config.get('enabled', False):
            self._render_trails()
        
        # Draw each detection box
        for det in detections:
            try:
                # Draw rectangle
                color_str = det.to_tkinter_color()
                self.canvas.create_rectangle(
                    det.x,
                    det.y,
                    det.x + det.w,
                    det.y + det.h,
                    outline=color_str,
                    width=2,
                    tags="detection"
                )
                
                # Draw label with confidence
                label_text = f"{det.label}"
                if det.confidence > 0.0:
                    label_text += f" {det.confidence:.2f}"
                
                # Background for text (black with high opacity for better readability)
                self.canvas.create_rectangle(
                    det.x,
                    det.y - 22,
                    det.x + len(label_text) * 7 + 8,
                    det.y - 2,
                    fill="black",
                    outline=color_str,
                    width=1,
                    tags="label_bg"
                )
                
                # Text (white on black for maximum contrast)
                self.canvas.create_text(
                    det.x + 4,
                    det.y - 12,
                    text=label_text,
                    anchor="w",
                    fill="#FFFFFF",  # Explicit white hex color
                    font=("Arial", 10, "bold"),
                    tags="label"
                )
                
            except Exception as e:
                print(f"[Overlay] Render box error: {e}")
        
        # Render FPS counter (always on top)
        self._render_fps_counter()
    
    def _render_fps_counter(self) -> None:
        """Render FPS counter on overlay."""
        if self.canvas is None:
            return
        
        # Calculate FPS from last render time
        current_time = time.time()
        if self._last_render_time > 0:
            frame_time = current_time - self._last_render_time
            fps = 1.0 / frame_time if frame_time > 0 else 0
            
            # FPS background for better visibility (render FIRST)
            self.canvas.create_rectangle(
                10, 10,
                120, 40,
                fill="black",
                outline="#FFFF00",
                width=2,
                tags="fps_bg"
            )
            
            # Display FPS text (render AFTER background)
            self.canvas.create_text(
                15, 15,
                text=f"FPS: {fps:.1f}",
                anchor="nw",
                fill="#FFFF00",  # Bright yellow
                font=("Arial", 14, "bold"),
                tags="fps"
            )
    
    def _update_trail_history(self, detections: List[DetectionBox]) -> None:
        """Update trail history with current detections."""
        with self._trail_lock:
            trail_length = self.trail_config.get('length', 5)
            
            # Update history for each detection
            for det in detections:
                label = det.label
                
                # Initialize history list if needed
                if label not in self._trail_history:
                    self._trail_history[label] = []
                
                # Add current position to history
                self._trail_history[label].append(det)
                
                # Trim to max length
                if len(self._trail_history[label]) > trail_length:
                    self._trail_history[label] = self._trail_history[label][-trail_length:]
            
            # Clean up old labels (not in current detections)
            current_labels = {det.label for det in detections}
            old_labels = set(self._trail_history.keys()) - current_labels
            for label in old_labels:
                del self._trail_history[label]
    
    def _render_trails(self) -> None:
        """Render detection trails (historical positions)."""
        if self.canvas is None:
            return
        
        with self._trail_lock:
            fade_enabled = self.trail_config.get('fade', True)
            
            for label, history in self._trail_history.items():
                if len(history) < 2:
                    continue  # Need at least 2 points for trail
                
                # Render trail from oldest to newest (excluding current)
                for i, det in enumerate(history[:-1]):  # Exclude last (current) detection
                    try:
                        # Calculate opacity based on position in history
                        if fade_enabled:
                            # Fade older positions more
                            opacity_factor = (i + 1) / len(history)  # 0.0 to 1.0
                            opacity = int(opacity_factor * 150)  # Max 150 opacity for trails
                        else:
                            opacity = 100
                        
                        # Create faded color
                        r, g, b = det.color
                        # Blend with background (assuming black/dark background)
                        faded_r = min(255, int(r * (opacity / 255)))
                        faded_g = min(255, int(g * (opacity / 255)))
                        faded_b = min(255, int(b * (opacity / 255)))
                        faded_color = f"#{faded_r:02x}{faded_g:02x}{faded_b:02x}"
                        
                        # Draw faded box
                        self.canvas.create_rectangle(
                            det.x,
                            det.y,
                            det.x + det.w,
                            det.y + det.h,
                            outline=faded_color,
                            width=1,
                            tags="trail"
                        )
                        
                    except Exception as e:
                        print(f"[Overlay] Trail render error: {e}")
    
    def destroy(self) -> None:
        """Destroy the overlay window and cleanup resources."""
        # Stop update thread
        self._stop_update_thread()
        
        # Destroy window
        if self.window is not None:
            try:
                self.window.destroy()
            except Exception:
                pass
            self.window = None
            self.canvas = None
        
        self.visible = False
    
    def is_visible(self) -> bool:
        """Check if overlay is currently visible."""
        return self.visible
    
    def set_alpha(self, alpha: float) -> None:
        """
        Update overlay transparency.
        
        Args:
            alpha: New alpha value (0.0-1.0)
        """
        if alpha < 0.0 or alpha > 1.0:
            raise ValueError(f"Alpha must be 0.0-1.0, got {alpha}")
        
        self.alpha = alpha
        
        if self.window is not None:
            try:
                self.window.attributes('-alpha', alpha)
            except tk.TclError:
                pass
            
            # Update Win32 alpha if click-through enabled
            if self.enable_click_through:
                self._apply_click_through()


# =====================================================================
# Helper Functions
# =====================================================================

def create_detection_box(
    x: int,
    y: int,
    w: int,
    h: int,
    label: str,
    state: str = "detected",
    confidence: float = 0.0
) -> DetectionBox:
    """
    Create a DetectionBox with automatic color based on state.
    
    Args:
        x, y, w, h: Bounding box coordinates
        label: Label text (e.g., monster name)
        state: Detection state - 'searching', 'detected', or 'tracking'
        confidence: Confidence score (0.0-1.0)
    
    Returns:
        DetectionBox instance with appropriate color
    """
    # Color mapping
    color_map = {
        'searching': (255, 0, 0),    # Red
        'detected': (0, 255, 0),     # Green
        'tracking': (0, 0, 255),     # Blue
    }
    
    color = color_map.get(state.lower(), (0, 255, 0))  # Default green
    
    return DetectionBox(
        x=x,
        y=y,
        w=w,
        h=h,
        label=label,
        color=color,
        confidence=confidence
    )


# =====================================================================
# Demo / Testing
# =====================================================================

if __name__ == "__main__":
    """Demo overlay window with sample detections."""
    
    # Create root window (positioned to NOT overlap with overlay)
    root = tk.Tk()
    root.title("Overlay Demo Control")
    root.geometry("300x300+950+100")  # Position control to the right of overlay
    
    # Create overlay (left side of screen)
    overlay = OverlayWindow(
        target_rect={'left': 100, 'top': 100, 'width': 800, 'height': 600},
        alpha=0.7,
        fps_limit=15,
        enable_click_through=False  # Disable click-through for demo so you can interact
    )
    overlay.create(parent=root)
    
    # Demo detections
    demo_detections = [
        create_detection_box(100, 100, 80, 80, "Monster #1", "detected", 0.95),
        create_detection_box(300, 200, 60, 60, "Monster #2", "tracking", 0.88),
        create_detection_box(500, 150, 70, 70, "Searching", "searching", 0.0),
    ]
    
    # FPS tracking and auto-update
    frame_times = []
    auto_update_running = False
    
    def auto_update_detections():
        """Continuously update detections to measure real FPS."""
        if overlay.visible and auto_update_running:
            overlay.update_detections(demo_detections)
            root.after(10, auto_update_detections)  # Update every 10ms for smooth FPS
    
    # Control buttons
    def toggle_overlay():
        global auto_update_running
        state = overlay.toggle()
        toggle_btn.config(text="Hide Overlay" if state else "Show Overlay")
        if state:
            auto_update_running = True
            auto_update_detections()  # Start auto-update for real FPS measurement
        else:
            auto_update_running = False
    
    def update_demo():
        overlay.update_detections(demo_detections)
        print(f"[Demo] Updated detections manually")
    
    toggle_btn = tk.Button(root, text="Show Overlay", command=toggle_overlay, width=25)
    toggle_btn.pack(pady=5)
    
    update_btn = tk.Button(root, text="Update Detections", command=update_demo, width=25)
    update_btn.pack(pady=5)
    
    # Click-through toggle
    click_through_var = tk.BooleanVar(value=False)
    def toggle_click_through():
        overlay.enable_click_through = click_through_var.get()
        if overlay.window:
            overlay.window.update()  # Force window update first
            overlay._apply_click_through()
            overlay.window.update_idletasks()
        status = "ON ⚠️ (can't click overlay)" if click_through_var.get() else "OFF ✅ (can click overlay)"
        print(f"[Demo] Click-through: {status}")
        click_status_label.config(text=f"Click-through: {status}")
    
    click_through_check = tk.Checkbutton(
        root, 
        text="Enable Click-through",
        variable=click_through_var,
        command=toggle_click_through,
        width=25
    )
    click_through_check.pack(pady=5)
    
    # Click-through status
    click_status_label = tk.Label(
        root,
        text="Click-through: OFF ✅",
        font=("Arial", 9),
        fg="green"
    )
    click_status_label.pack(pady=2)
    
    quit_btn = tk.Button(root, text="Quit", command=lambda: [overlay.destroy(), root.destroy()], width=25)
    quit_btn.pack(pady=5)
    
    # Info label
    info = tk.Label(
        root, 
        text="1. Click 'Show Overlay'\n"
             "   → Auto-updates at 15 FPS\n"
             "2. Watch overlay (left side)\n"
             "3. Toggle click-through to test\n"
             "4. Red text now readable!",
        justify="left",
        font=("Arial", 9)
    )
    info.pack(pady=10)
    
    # FPS info label
    fps_info = tk.Label(
        root,
        text="FPS Target: 15\n(rendering updates automatically)",
        justify="left",
        font=("Arial", 8),
        fg="blue"
    )
    fps_info.pack(pady=5)
    
    # Cleanup on close
    def on_close():
        overlay.destroy()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    
    print("[Demo] Overlay window demo started")
    print("[Demo] - Click 'Show Overlay' to display")
    print("[Demo] - Overlay is transparent and click-through")
    print("[Demo] - Use 'Update Detections' to refresh boxes")
    
    root.mainloop()
