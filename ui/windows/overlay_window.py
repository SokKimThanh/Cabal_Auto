"""
PyWin32 Overlay Window - True click-through overlay using PyWin32 library
Sprint 23 Phase 5 - PyWin32 Refactor

Features:
- True click-through using WS_EX_TRANSPARENT (PyWin32 native support)
- GDI drawing for detection boxes
- Native Win32 window (no Tkinter ctypes limitations)
- Thread-safe detection updates
- Color-coded states (red/green/blue)
- FPS counter with GDI

Architecture:
- PyWin32 window class registration
- Message loop in background thread
- GDI rendering
- Automatic position tracking

Differences from overlay_window.py (Tkinter + ctypes):
- Uses PyWin32 library (win32gui, win32api) instead of Tkinter + ctypes
- True click-through works reliably
- No canvas widget limitations
- GDI rendering instead of tkinter canvas

Usage:
    overlay = OverlayWindowPyWin32(
        target_rect={'left': 0, 'top': 0, 'width': 800, 'height': 600},
        alpha=0.7,
        fps_limit=15
    )
    overlay.show()
    overlay.update_detections([...])
    overlay.hide()
    overlay.destroy()
"""

import sys
import time
import threading
import queue
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

# Global UI styles
from lib.ui_style import UIStyle as UI

# Win32 imports
if sys.platform == "win32":
    try:
        import win32gui
        import win32con
        import win32api
        import win32ui
    except ImportError as e:
        raise ImportError(
            "PyWin32 library is required for overlay window.\n"
            "Please install it:\n"
            "  pip install pywin32\n"
            "Or if using venv:\n"
            "  venv\\Scripts\\activate\n"
            "  pip install pywin32\n"
            f"\nOriginal error: {e}"
        ) from e
else:
    raise RuntimeError("OverlayWindowPyWin32 only works on Windows!")


# =====================================================================
# Constants - Imported from global UI style
# =====================================================================

# Drawing constants
BORDER_WIDTH = UI.DETECTION_BORDER_WIDTH
TEXT_FONT_HEIGHT = UI.DETECTION_TEXT_FONT_HEIGHT
TEXT_PADDING = UI.DETECTION_TEXT_PADDING
TEXT_CHAR_WIDTH = UI.DETECTION_TEXT_CHAR_WIDTH
FPS_COUNTER_WIDTH = UI.FPS_COUNTER_WIDTH
FPS_COUNTER_HEIGHT = UI.FPS_COUNTER_HEIGHT
FPS_COUNTER_PADDING = UI.FPS_COUNTER_PADDING

# Colors (RGB tuples) - Imported from global UI style
COLOR_BLACK = UI.COLOR_BLACK_RGB
COLOR_WHITE = UI.COLOR_WHITE_RGB
COLOR_RED = UI.COLOR_RED_RGB
COLOR_GREEN = UI.COLOR_GREEN_RGB
COLOR_BLUE = UI.COLOR_BLUE_RGB


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
    
    def to_win32_color(self) -> int:
        """Convert RGB tuple to Win32 COLORREF (0x00BBGGRR)"""
        r, g, b = self.color
        return win32api.RGB(r, g, b)


# =====================================================================
# PyWin32 Overlay Window Class
# =====================================================================

class OverlayWindowPyWin32:
    """
    True click-through overlay window using PyWin32 library.
    
    Thread-safe: update_detections() can be called from any thread.
    """
    
    def __init__(
        self,
        target_rect: Optional[Dict[str, int]] = None,
        alpha: float = UI.OVERLAY_BG_ALPHA,  # Default from global style (0.3 = 30%)
        fps_limit: int = 15,
        enable_click_through: bool = True
    ):
        """
        Initialize Win32 overlay window.
        
        Args:
            target_rect: Initial rect {'left', 'top', 'width', 'height'}
            alpha: Transparency level (0.0 = invisible, 1.0 = opaque)
                   Default: 0.3 (30% opacity for black background)
            fps_limit: Maximum FPS for rendering updates
            enable_click_through: Enable click-through (always True for Win32)
        """
        # Validate parameters
        if alpha < 0.0 or alpha > 1.0:
            raise ValueError(f"Alpha must be 0.0-1.0, got {alpha}")
        if fps_limit <= 0:
            raise ValueError(f"FPS limit must be > 0, got {fps_limit}")
        
        self.target_rect = target_rect or {'left': 0, 'top': 0, 'width': 800, 'height': 600}
        self.alpha = alpha
        self.fps_limit = fps_limit
        self.enable_click_through = enable_click_through
        
        # Window state
        self.hwnd = None
        self.visible = False
        self.running = False
        
        # Win32 objects
        self.hInstance = win32api.GetModuleHandle()
        self.className = f"OverlayWindow_{id(self)}"
        
        # Detection data (thread-safe)
        self._detections_queue: queue.Queue[List[DetectionBox]] = queue.Queue(maxsize=2)
        self._current_detections: List[DetectionBox] = []
        self._detections_lock = threading.Lock()
        
        # Message loop thread
        self._message_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Performance tracking
        self._last_render_time = 0.0
        self._frame_interval = 1.0 / fps_limit
        self._fps = 0.0
        
        print(f"[PyWin32Overlay] Initialized (alpha={alpha}, fps={fps_limit})")
    
    def create(self) -> None:
        """Create the Win32 overlay window."""
        if self.hwnd is not None:
            return  # Already created
        
        print("[PyWin32Overlay] Creating window...")
        
        # Window styles for overlay
        ex_style = (
            win32con.WS_EX_LAYERED |      # Transparency support
            win32con.WS_EX_TRANSPARENT |  # Click-through
            win32con.WS_EX_TOPMOST |      # Always on top  
            win32con.WS_EX_NOACTIVATE     # Don't activate on click
        )
        
        style = (
            win32con.WS_POPUP |           # No decorations
            win32con.WS_VISIBLE           # Visible by default
        )
        
        # Create window using simple CreateWindowEx
        # No need to register class - use existing class
        self.hwnd = win32gui.CreateWindowEx(
            ex_style,
            "#32770",  # Dialog class (built-in, no registration needed)
            "Vision Overlay",
            style,
            self.target_rect['left'],
            self.target_rect['top'],
            self.target_rect['width'],
            self.target_rect['height'],
            0,  # No parent
            0,  # No menu
            0,  # No instance
            None
        )
        
        if not self.hwnd:
            raise RuntimeError("Failed to create PyWin32 window!")
        
        print(f"[PyWin32Overlay] Window created: hwnd={self.hwnd}")
        
        # Set transparency (alpha only, no color key)
        alpha_byte = int(self.alpha * 255)
        win32gui.SetLayeredWindowAttributes(
            self.hwnd,
            0,  # No color key
            alpha_byte,
            win32con.LWA_ALPHA  # Alpha blending only
        )
        
        print(f"[PyWin32Overlay] Transparency set: {alpha_byte}/255")
        
        # Hide initially
        win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)
        self.visible = False
        
        print("[PyWin32Overlay] Window created successfully")
    
    def _on_paint_gdi(self) -> None:
        """Handle painting using GDI."""
        if not self.hwnd:
            return
        
        try:
            # Get device context
            dc = win32gui.GetDC(self.hwnd)
            
            # Get window dimensions
            rect = win32gui.GetClientRect(self.hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            
            # Fill background with black first
            black_brush = win32gui.CreateSolidBrush(win32api.RGB(*COLOR_BLACK))
            win32gui.FillRect(dc, (0, 0, width, height), black_brush)  # type: ignore[arg-type]  # PyWin32 stubs: tuple is valid RECT
            win32gui.DeleteObject(black_brush)
            
            # Set background mode to transparent for text
            win32gui.SetBkMode(dc, win32con.TRANSPARENT)
            
            # Get current detections (thread-safe)
            with self._detections_lock:
                detections = self._current_detections.copy()
            
            # Render detection boxes
            self._render_gdi(dc, detections, width, height)
            
            # Release DC
            win32gui.ReleaseDC(self.hwnd, dc)
            
            # Update FPS
            self._update_fps()
            
        except Exception as e:
            print(f"[PyWin32Overlay] Paint error: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_fps(self) -> None:
        """Update FPS calculation."""
        current_time = time.time()
        if self._last_render_time > 0:
            frame_time = current_time - self._last_render_time
            self._fps = 1.0 / frame_time if frame_time > 0 else 0
        self._last_render_time = current_time
    
    def _render_gdi(self, hdc: int, detections: List[DetectionBox], width: int, height: int) -> None:
        """
        Render detection boxes using GDI.
        
        Args:
            hdc: Device context handle
            detections: List of detection boxes to render
            width: Window width
            height: Window height
        """
        try:
            if not self.hwnd:
                return
            
            # Set background mode to transparent
            win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
            
            # Draw each detection box
            for det in detections:
                self._draw_detection_box(hdc, det)
            
            # Draw FPS counter
            self._draw_fps_counter(hdc, width, height)
            
        except Exception as e:
            print(f"[PyWin32Overlay] Render error: {e}")
            import traceback
            traceback.print_exc()
    
    def _draw_detection_box(self, hdc: int, det: DetectionBox) -> None:
        """
        Draw single detection box with label.
        
        Args:
            hdc: Device context handle
            det: Detection box to draw
        """
        # Get box properties
        x, y, w, h = det.x, det.y, det.w, det.h
        color_rgb = det.color
        
        # Convert to Win32 color
        color = win32api.RGB(color_rgb[0], color_rgb[1], color_rgb[2])
        
        # Create pen for rectangle border
        pen = win32gui.CreatePen(win32con.PS_SOLID, BORDER_WIDTH, color)
        old_pen = win32gui.SelectObject(hdc, pen)  # type: ignore[arg-type]  # PyWin32 stubs: PyGdiHANDLE is valid
        
        # Draw rectangle (hollow - no brush)
        old_brush = win32gui.SelectObject(hdc, win32gui.GetStockObject(win32con.NULL_BRUSH))
        win32gui.Rectangle(hdc, x, y, x + w, y + h)
        
        # Restore old brush and pen
        win32gui.SelectObject(hdc, old_brush)
        win32gui.SelectObject(hdc, old_pen)
        win32gui.DeleteObject(pen)
        
        # Draw text label
        if det.label:
            self._draw_text_label(hdc, x, y, h, det.label, det.confidence)
    
    def _draw_text_label(
        self,
        hdc: int,
        x: int,
        y: int,
        box_height: int,
        label: str,
        confidence: float
    ) -> None:
        """
        Draw text label with white background.
        
        Args:
            hdc: Device context handle
            x: Label X position
            y: Box Y position
            box_height: Height of detection box
            label: Text label
            confidence: Confidence score
        """
        text = f"{label} ({confidence:.2f})"
        
        # Set text color to BLACK with WHITE background
        win32gui.SetTextColor(hdc, win32api.RGB(*COLOR_BLACK))
        win32gui.SetBkMode(hdc, win32con.OPAQUE)
        win32gui.SetBkColor(hdc, win32api.RGB(*COLOR_WHITE))
        
        # Calculate text position (above box, or below if not enough space)
        text_y = y - TEXT_FONT_HEIGHT - TEXT_PADDING
        if text_y < 0:
            text_y = y + box_height + TEXT_PADDING // 2
        
        # Calculate text dimensions
        text_width = len(text) * TEXT_CHAR_WIDTH + TEXT_PADDING * 2
        
        # Draw white background for text
        white_brush = win32gui.CreateSolidBrush(win32api.RGB(*COLOR_WHITE))
        bg_rect = (
            x,
            text_y,
            x + text_width,
            text_y + TEXT_FONT_HEIGHT + TEXT_PADDING
        )
        win32gui.FillRect(hdc, bg_rect, white_brush)  # type: ignore[arg-type]  # PyWin32 stubs: tuple is valid RECT
        win32gui.DeleteObject(white_brush)
        
        # Draw text (opaque, not affected by window transparency)
        text_rect = (
            x + TEXT_PADDING,
            text_y + TEXT_PADDING // 2,
            x + text_width,
            text_y + TEXT_FONT_HEIGHT + TEXT_PADDING // 2
        )
        win32gui.DrawText(hdc, text, -1, text_rect, win32con.DT_LEFT)  # type: ignore[arg-type]  # PyWin32 stubs: tuple is valid RECT
    
    def _draw_fps_counter(self, hdc: int, width: int, height: int) -> None:
        """
        Draw FPS counter in top-right corner.
        
        Args:
            hdc: Device context handle
            width: Window width
            height: Window height
        """
        fps_text = f"FPS: {self._fps:.1f}"
        
        # Position in top-right
        fps_x = width - FPS_COUNTER_WIDTH
        fps_y = 10
        
        # Draw white background
        white_brush = win32gui.CreateSolidBrush(win32api.RGB(*COLOR_WHITE))
        fps_rect = (
            fps_x - FPS_COUNTER_PADDING,
            fps_y - TEXT_PADDING // 2,
            fps_x + FPS_COUNTER_WIDTH - FPS_COUNTER_PADDING,
            fps_y + FPS_COUNTER_HEIGHT + TEXT_PADDING // 2
        )
        win32gui.FillRect(hdc, fps_rect, white_brush)  # type: ignore[arg-type]  # PyWin32 stubs: tuple is valid RECT
        win32gui.DeleteObject(white_brush)
        
        # Draw FPS text (black on white)
        win32gui.SetTextColor(hdc, win32api.RGB(*COLOR_BLACK))
        win32gui.SetBkMode(hdc, win32con.OPAQUE)
        win32gui.SetBkColor(hdc, win32api.RGB(*COLOR_WHITE))
        
        text_rect = (
            fps_x,
            fps_y,
            fps_x + FPS_COUNTER_WIDTH - FPS_COUNTER_PADDING,
            fps_y + FPS_COUNTER_HEIGHT
        )
        win32gui.DrawText(hdc, fps_text, -1, text_rect, win32con.DT_LEFT)  # type: ignore[arg-type]  # PyWin32 stubs: tuple is valid RECT
    
    def show(self) -> None:
        """Show the overlay window."""
        if self.hwnd is None:
            raise RuntimeError("Window not created. Call create() first.")
        
        if not self.visible:
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
            win32gui.UpdateWindow(self.hwnd)
            self.visible = True
            
            # Start message loop if not running
            if not self.running:
                self._start_message_loop()
            
            # Force repaint to ensure content is rendered
            win32gui.InvalidateRect(self.hwnd, None, True)
            win32gui.UpdateWindow(self.hwnd)
            
            print("[PyWin32Overlay] Window shown")
    
    def hide(self) -> None:
        """Hide the overlay window."""
        if self.hwnd and self.visible:
            win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)
            self.visible = False
            print("[PyWin32Overlay] Window hidden")
    
    def toggle(self) -> bool:
        """Toggle overlay visibility."""
        if self.visible:
            self.hide()
            return False
        else:
            self.show()
            return True
    
    def update_target_rect(self, rect: Dict[str, int]) -> None:
        """Update target window rect and reposition overlay."""
        old_rect = self.target_rect
        self.target_rect = rect
        
        if self.hwnd:
            # Check if size changed (not just position)
            size_changed = (
                old_rect is None or
                old_rect['width'] != rect['width'] or
                old_rect['height'] != rect['height']
            )
            
            win32gui.SetWindowPos(
                self.hwnd,
                win32con.HWND_TOPMOST,
                rect['left'],
                rect['top'],
                rect['width'],
                rect['height'],
                win32con.SWP_NOACTIVATE
            )
            
            # Force repaint if size changed
            if size_changed:
                win32gui.InvalidateRect(self.hwnd, None, True)
                win32gui.UpdateWindow(self.hwnd)
                print(f"[PyWin32Overlay] Resized to {rect['width']}x{rect['height']}")
    
    def update_detections(self, detections: List[DetectionBox]) -> None:
        """Update detection boxes (thread-safe)."""
        try:
            # Drop old frame if queue full
            if self._detections_queue.full():
                try:
                    self._detections_queue.get_nowait()
                except queue.Empty:
                    pass
            
            self._detections_queue.put_nowait(detections)
            
            # Trigger repaint by calling paint directly
            if self.hwnd and self.visible:
                self._on_paint_gdi()
                
        except queue.Full:
            pass  # Skip frame
    
    def _start_message_loop(self) -> None:
        """Start message loop in background thread."""
        if self.running:
            return
        
        self.running = True
        self._stop_event.clear()
        
        self._message_thread = threading.Thread(
            target=self._message_loop_thread,
            name="Win32OverlayMessageLoop",
            daemon=True
        )
        self._message_thread.start()
        
        print("[PyWin32Overlay] Message loop started")
    
    def _message_loop_thread(self) -> None:
        """Message loop thread - processes detection updates."""
        while not self._stop_event.is_set():
            try:
                # Get latest detections from queue
                try:
                    detections = self._detections_queue.get(timeout=0.1)
                    with self._detections_lock:
                        self._current_detections = detections
                    
                    # Trigger repaint
                    if self.hwnd and self.visible:
                        self._on_paint_gdi()
                        
                except queue.Empty:
                    pass
                
                # FPS limiting
                time.sleep(self._frame_interval)
                
            except Exception as e:
                print(f"[PyWin32Overlay] Message loop error: {e}")
    
    def destroy(self) -> None:
        """Destroy the overlay window."""
        print("[PyWin32Overlay] Destroying window...")
        
        # Stop message loop
        self.running = False
        self._stop_event.set()
        
        if self._message_thread:
            self._message_thread.join(timeout=1.0)
        
        # Destroy window
        if self.hwnd:
            try:
                win32gui.DestroyWindow(self.hwnd)
            except Exception as e:
                print(f"[PyWin32Overlay] Destroy error: {e}")
            self.hwnd = None
        
        self.visible = False
        print("[PyWin32Overlay] Destroyed")
    
    def is_visible(self) -> bool:
        """Check if overlay is currently visible."""
        return self.visible
    
    def set_alpha(self, alpha: float) -> None:
        """Update overlay transparency."""
        if alpha < 0.0 or alpha > 1.0:
            raise ValueError(f"Alpha must be 0.0-1.0, got {alpha}")
        
        self.alpha = alpha
        
        if self.hwnd:
            alpha_byte = int(alpha * 255)
            win32gui.SetLayeredWindowAttributes(
                self.hwnd,
                0,
                alpha_byte,
                win32con.LWA_ALPHA
            )


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
        x: X coordinate
        y: Y coordinate  
        w: Width
        h: Height
        label: Text label
        state: Detection state ('searching', 'detected', 'tracking')
        confidence: Confidence score (0.0-1.0)
        
    Returns:
        DetectionBox instance with appropriate color
    """
    # Color mapping from global UI style
    color_map = {
        'searching': UI.DETECTION_STATE_SEARCHING,
        'detected': UI.DETECTION_STATE_DETECTED,
        'tracking': UI.DETECTION_STATE_TRACKING,
    }
    
    color = color_map.get(state.lower(), UI.DETECTION_STATE_DETECTED)
    
    return DetectionBox(
        x=x, y=y, w=w, h=h,
        label=label,
        color=color,
        confidence=confidence
    )


# =====================================================================
# Demo / Testing
# =====================================================================

if __name__ == "__main__":
    """Demo PyWin32 overlay with sample detections."""
    import keyboard  # For demo hotkey only
    
    print("[Demo] PyWin32 Overlay Demo Starting...")
    print("[Demo] Press Ctrl+Shift+O to toggle overlay ON/OFF")
    print("[Demo] Press Ctrl+C to exit")
    
    # Create overlay with black background (30% opacity)
    overlay = OverlayWindowPyWin32(
        target_rect={'left': 100, 'top': 100, 'width': 800, 'height': 600},
        alpha=0.3,  # 30% opacity for black background
        fps_limit=15
    )
    
    overlay.create()
    overlay.show()
    
    # Demo detections
    demo_detections = [
        create_detection_box(100, 100, 80, 80, "Monster #1", "detected", 0.95),
        create_detection_box(300, 200, 60, 60, "Monster #2", "tracking", 0.88),
        create_detection_box(500, 150, 70, 70, "Searching", "searching", 0.0),
    ]
    
    # Update detections
    overlay.update_detections(demo_detections)
    
    # Register Ctrl+Shift+O hotkey for demo
    def toggle_overlay_demo():
        """Toggle overlay in demo mode."""
        if overlay.visible:
            print("[Demo] Hotkey pressed - HIDING overlay")
            overlay.hide()
        else:
            print("[Demo] Hotkey pressed - SHOWING overlay")
            overlay.show()
    
    keyboard.add_hotkey('ctrl+shift+o', toggle_overlay_demo)
    print("[Demo] Hotkey registered: Ctrl+Shift+O")
    print("[Demo] Overlay active - try clicking through it!")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
            # Re-send detections to trigger repaint
            overlay.update_detections(demo_detections)
    except KeyboardInterrupt:
        print("[Demo] Exiting...")
        keyboard.remove_hotkey('ctrl+shift+o')
        overlay.destroy()
