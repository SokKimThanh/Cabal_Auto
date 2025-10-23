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
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    LWA_ALPHA = 0x00000002
else:
    # Stub for non-Windows platforms
    GWL_EXSTYLE = None
    WS_EX_LAYERED = None
    WS_EX_TRANSPARENT = None
    LWA_ALPHA = None


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
        enable_click_through: bool = True
    ):
        """
        Initialize overlay window.
        
        Args:
            target_hwnd: Handle of target window to track (optional)
            target_rect: Initial rect {'left', 'top', 'width', 'height'}
            alpha: Transparency level (0.0 = invisible, 1.0 = opaque)
            fps_limit: Maximum FPS for rendering updates
            enable_click_through: Enable click-through (Win32 only)
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
        
        # State
        self.window: Optional[tk.Toplevel] = None
        self.canvas: Optional[tk.Canvas] = None
        self.visible = False
        self.running = False
        
        # Detection data (thread-safe)
        self._detections_queue: queue.Queue[List[DetectionBox]] = queue.Queue(maxsize=2)
        self._current_detections: List[DetectionBox] = []
        self._detections_lock = threading.Lock()
        
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
            borderwidth=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Apply click-through on Windows
        if self.enable_click_through:
            self._apply_click_through()
        
        # Start hidden
        self.window.withdraw()
        
    def _apply_click_through(self) -> None:
        """Apply Win32 transparent window style for click-through."""
        if not sys.platform == "win32":
            return
        
        if self.window is None:
            return
        
        try:
            # Get window handle
            hwnd = self.window.winfo_id()
            
            # Get current extended style
            user32 = ctypes.windll.user32
            current_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            
            # Add transparent and layered flags
            new_style = current_style | WS_EX_LAYERED | WS_EX_TRANSPARENT
            
            # Apply new style
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
            
            # Set layered window attributes
            # Convert alpha to 0-255 range
            alpha_byte = int(self.alpha * 255)
            user32.SetLayeredWindowAttributes(hwnd, 0, alpha_byte, LWA_ALPHA)
            
        except Exception as e:
            print(f"[Overlay] Failed to apply click-through: {e}")
    
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
                
                # Background for text
                self.canvas.create_rectangle(
                    det.x,
                    det.y - 20,
                    det.x + len(label_text) * 7 + 4,
                    det.y - 2,
                    fill=color_str,
                    outline="",
                    tags="label_bg"
                )
                
                # Text
                self.canvas.create_text(
                    det.x + 2,
                    det.y - 10,
                    text=label_text,
                    anchor="w",
                    fill="white",
                    font=("Arial", 9, "bold"),
                    tags="label"
                )
                
            except Exception as e:
                print(f"[Overlay] Render box error: {e}")
    
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
    
    # Create root window
    root = tk.Tk()
    root.title("Overlay Demo Control")
    root.geometry("300x200")
    
    # Create overlay
    overlay = OverlayWindow(
        target_rect={'left': 100, 'top': 100, 'width': 800, 'height': 600},
        alpha=0.7,
        fps_limit=15
    )
    overlay.create(parent=root)
    
    # Demo detections
    demo_detections = [
        create_detection_box(100, 100, 80, 80, "Monster #1", "detected", 0.95),
        create_detection_box(300, 200, 60, 60, "Monster #2", "tracking", 0.88),
        create_detection_box(500, 150, 70, 70, "Searching", "searching", 0.0),
    ]
    
    # Control buttons
    def toggle_overlay():
        state = overlay.toggle()
        toggle_btn.config(text="Hide Overlay" if state else "Show Overlay")
    
    def update_demo():
        overlay.update_detections(demo_detections)
    
    toggle_btn = tk.Button(root, text="Show Overlay", command=toggle_overlay, width=20)
    toggle_btn.pack(pady=10)
    
    update_btn = tk.Button(root, text="Update Detections", command=update_demo, width=20)
    update_btn.pack(pady=10)
    
    quit_btn = tk.Button(root, text="Quit", command=lambda: [overlay.destroy(), root.destroy()], width=20)
    quit_btn.pack(pady=10)
    
    # Info label
    info = tk.Label(root, text="Click 'Show Overlay' to test\nTransparent, click-through overlay", justify="left")
    info.pack(pady=10)
    
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
