"""
Window Manager - Sprint 23 Phase 8
Window detection and manipulation utilities

Features:
- Find windows by title/class
- Get window position and size
- Set window focus/foreground
- Window state tracking (minimized, maximized, etc.)
- Multi-monitor support

Usage:
    wm = WindowManager()
    hwnd = wm.find_window("Cabal")
    if hwnd:
        rect = wm.get_window_rect(hwnd)
        wm.set_foreground(hwnd)
"""

import win32gui
import win32con
import win32api
import win32process
import psutil
from ctypes import windll, c_int, byref, c_void_p
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class WindowInfo:
    """Complete window information"""
    hwnd: int
    title: str
    class_name: str
    pid: int
    process_name: str
    rect: Dict[str, int]  # left, top, right, bottom, width, height
    is_visible: bool
    is_enabled: bool
    is_minimized: bool
    is_maximized: bool
    is_foreground: bool
    
    def __str__(self) -> str:
        return (
            f"Window('{self.title}' - {self.process_name}, "
            f"{self.rect['width']}x{self.rect['height']}, "
            f"visible={self.is_visible}, minimized={self.is_minimized})"
        )


class WindowManager:
    """
    Windows window management utilities
    
    Provides high-level API for window operations needed by
    screen capture and overlay systems.
    """
    
    def __init__(self):
        """Initialize window manager"""
        self._cached_windows = {}
        self._cache_timeout = 2.0  # seconds
        logger.info("WindowManager initialized")
    
    def find_window(
        self,
        title_contains: Optional[str] = None,
        class_name: Optional[str] = None,
        process_name: Optional[str] = None,
        visible_only: bool = True
    ) -> Optional[int]:
        """
        Find window by various criteria
        
        Args:
            title_contains: Substring in window title
            class_name: Window class name (exact match)
            process_name: Process name (e.g., "cabal.exe")
            visible_only: Only return visible windows
            
        Returns:
            Window handle (HWND) or None if not found
        """
        windows = self.list_windows(
            title_contains=title_contains,
            class_name=class_name,
            process_name=process_name,
            visible_only=visible_only
        )
        
        if windows:
            return windows[0].hwnd
        return None
    
    def find_all_windows(
        self,
        title_contains: Optional[str] = None,
        class_name: Optional[str] = None,
        process_name: Optional[str] = None,
        visible_only: bool = True
    ) -> List[int]:
        """
        Find all windows matching criteria
        
        Args:
            Same as find_window()
            
        Returns:
            List of window handles (HWND)
        """
        windows = self.list_windows(
            title_contains=title_contains,
            class_name=class_name,
            process_name=process_name,
            visible_only=visible_only
        )
        return [w.hwnd for w in windows]
    
    def list_windows(
        self,
        title_contains: Optional[str] = None,
        class_name: Optional[str] = None,
        process_name: Optional[str] = None,
        visible_only: bool = True
    ) -> List[WindowInfo]:
        """
        List all windows with detailed info
        
        Args:
            title_contains: Filter by title substring
            class_name: Filter by class name
            process_name: Filter by process name
            visible_only: Only return visible windows
            
        Returns:
            List of WindowInfo objects
        """
        results = []
        
        def callback(hwnd, _):
            try:
                # Basic visibility check
                if visible_only and not win32gui.IsWindowVisible(hwnd):
                    return True
                
                # Get window info
                info = self.get_window_info(hwnd)
                if not info:
                    return True
                
                # Apply filters
                if title_contains and title_contains.lower() not in info.title.lower():
                    return True
                
                if class_name and class_name != info.class_name:
                    return True
                
                if process_name and process_name.lower() not in info.process_name.lower():
                    return True
                
                results.append(info)
            
            except Exception as e:
                logger.debug(f"Error processing window {hwnd}: {e}")
            
            return True
        
        try:
            win32gui.EnumWindows(callback, None)
        except Exception as e:
            logger.error(f"EnumWindows failed: {e}")
        
        logger.debug(f"Found {len(results)} windows")
        return results
    
    def get_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        """
        Get complete information about a window
        
        Args:
            hwnd: Window handle
            
        Returns:
            WindowInfo object or None if invalid
        """
        try:
            if not win32gui.IsWindow(hwnd):
                return None
            
            # Basic info
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            
            # Process info
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except:
                process_name = "Unknown"
            
            # Rect
            rect = self.get_window_rect(hwnd)
            
            # State
            is_visible = win32gui.IsWindowVisible(hwnd)
            is_enabled = win32gui.IsWindowEnabled(hwnd)
            is_minimized = win32gui.IsIconic(hwnd)
            is_maximized = win32gui.IsZoomed(hwnd)
            is_foreground = (win32gui.GetForegroundWindow() == hwnd)
            
            return WindowInfo(
                hwnd=hwnd,
                title=title,
                class_name=class_name,
                pid=pid,
                process_name=process_name,
                rect=rect,
                is_visible=is_visible,
                is_enabled=is_enabled,
                is_minimized=is_minimized,
                is_maximized=is_maximized,
                is_foreground=is_foreground
            )
        
        except Exception as e:
            logger.debug(f"get_window_info failed for {hwnd}: {e}")
            return None
    
    def get_window_rect(self, hwnd: int) -> Dict[str, int]:
        """
        Get window rectangle
        
        Args:
            hwnd: Window handle
            
        Returns:
            Dict with left, top, right, bottom, width, height
        """
        try:
            rect = win32gui.GetWindowRect(hwnd)
            return {
                'left': rect[0],
                'top': rect[1],
                'right': rect[2],
                'bottom': rect[3],
                'width': rect[2] - rect[0],
                'height': rect[3] - rect[1]
            }
        except Exception as e:
            logger.error(f"get_window_rect failed for {hwnd}: {e}")
            return {
                'left': 0, 'top': 0, 'right': 0, 'bottom': 0,
                'width': 0, 'height': 0
            }
    
    def get_client_rect(self, hwnd: int) -> Dict[str, int]:
        """
        Get window client area (excluding title bar/borders)
        
        Args:
            hwnd: Window handle
            
        Returns:
            Dict with left, top, right, bottom, width, height
        """
        try:
            rect = win32gui.GetClientRect(hwnd)
            # GetClientRect returns relative coords, convert to screen
            pt = win32gui.ClientToScreen(hwnd, (0, 0))
            return {
                'left': pt[0],
                'top': pt[1],
                'right': pt[0] + rect[2],
                'bottom': pt[1] + rect[3],
                'width': rect[2],
                'height': rect[3]
            }
        except Exception as e:
            logger.error(f"get_client_rect failed for {hwnd}: {e}")
            return {
                'left': 0, 'top': 0, 'right': 0, 'bottom': 0,
                'width': 0, 'height': 0
            }
    
    def set_foreground(self, hwnd: int) -> bool:
        """
        Bring window to foreground
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if successful
        """
        try:
            # Restore if minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # Set foreground
            win32gui.SetForegroundWindow(hwnd)
            return True
        
        except Exception as e:
            logger.error(f"set_foreground failed for {hwnd}: {e}")
            return False
    
    def minimize(self, hwnd: int) -> bool:
        """Minimize window"""
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True
        except Exception as e:
            logger.error(f"minimize failed: {e}")
            return False
    
    def maximize(self, hwnd: int) -> bool:
        """Maximize window"""
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        except Exception as e:
            logger.error(f"maximize failed: {e}")
            return False
    
    def restore(self, hwnd: int) -> bool:
        """Restore window from minimized/maximized"""
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            return True
        except Exception as e:
            logger.error(f"restore failed: {e}")
            return False
    
    def is_window_valid(self, hwnd: int) -> bool:
        """Check if window handle is still valid"""
        try:
            return win32gui.IsWindow(hwnd)
        except:
            return False
    
    def wait_for_window(
        self,
        title_contains: str,
        timeout: float = 10.0,
        check_interval: float = 0.5
    ) -> Optional[int]:
        """
        Wait for window to appear
        
        Args:
            title_contains: Window title substring
            timeout: Max wait time in seconds
            check_interval: Check interval in seconds
            
        Returns:
            Window handle or None if timeout
        """
        import time
        start_time = time.time()
        
        logger.info(f"Waiting for window '{title_contains}' (timeout={timeout}s)")
        
        while time.time() - start_time < timeout:
            hwnd = self.find_window(title_contains=title_contains)
            if hwnd:
                logger.info(f"Found window: {hwnd}")
                return hwnd
            time.sleep(check_interval)
        
        logger.warning(f"Window '{title_contains}' not found after {timeout}s")
        return None
    
    def get_monitor_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all monitors
        
        Returns:
            List of monitor info dicts
        """
        monitors = []
        
        def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            try:
                info = win32api.GetMonitorInfo(hMonitor)
                monitors.append({
                    'handle': hMonitor,
                    'rect': {
                        'left': lprcMonitor[0],
                        'top': lprcMonitor[1],
                        'right': lprcMonitor[2],
                        'bottom': lprcMonitor[3],
                        'width': lprcMonitor[2] - lprcMonitor[0],
                        'height': lprcMonitor[3] - lprcMonitor[1]
                    },
                    'work_area': info.get('Work', lprcMonitor),
                    'is_primary': info.get('Flags', 0) & win32con.MONITORINFOF_PRIMARY
                })
            except Exception as e:
                logger.debug(f"Error getting monitor info: {e}")
            return True
        
        try:
            win32api.EnumDisplayMonitors(None, None, callback, 0)
        except Exception as e:
            logger.error(f"EnumDisplayMonitors failed: {e}")
        
        return monitors
    
    def get_window_monitor(self, hwnd: int) -> Optional[Dict[str, Any]]:
        """
        Get monitor that contains most of the window
        
        Args:
            hwnd: Window handle
            
        Returns:
            Monitor info dict or None
        """
        try:
            hMonitor = win32api.MonitorFromWindow(
                hwnd,
                win32con.MONITOR_DEFAULTTONEAREST
            )
            
            monitors = self.get_monitor_info()
            for monitor in monitors:
                if monitor['handle'] == hMonitor:
                    return monitor
        
        except Exception as e:
            logger.error(f"get_window_monitor failed: {e}")
        
        return None


# =====================================================================
# Convenience Functions
# =====================================================================

def find_cabal_window() -> Optional[int]:
    """
    Find Cabal game window
    
    Returns:
        Window handle or None
    """
    wm = WindowManager()
    
    # Try common Cabal window titles
    titles = ["Cabal", "CABAL", "CABAL Online"]
    
    for title in titles:
        hwnd = wm.find_window(title_contains=title)
        if hwnd:
            return hwnd
    
    return None


def get_cabal_rect() -> Optional[Dict[str, int]]:
    """
    Get Cabal window rectangle
    
    Returns:
        Rect dict or None
    """
    hwnd = find_cabal_window()
    if hwnd:
        wm = WindowManager()
        return wm.get_window_rect(hwnd)
    return None


if __name__ == "__main__":
    # Demo: List all windows
    logging.basicConfig(level=logging.INFO)
    
    wm = WindowManager()
    
    print("=== All Visible Windows ===")
    windows = wm.list_windows(visible_only=True)
    for w in windows[:10]:  # Show first 10
        print(f"  {w}")
    print(f"Total: {len(windows)} windows\n")
    
    print("=== Looking for Cabal ===")
    cabal_hwnd = find_cabal_window()
    if cabal_hwnd:
        info = wm.get_window_info(cabal_hwnd)
        print(f"Found: {info}")
        
        # Get monitor info
        monitor = wm.get_window_monitor(cabal_hwnd)
        if monitor:
            print(f"Monitor: {monitor['rect']}")
    else:
        print("Cabal window not found")
    
    print("\n=== Monitor Info ===")
    monitors = wm.get_monitor_info()
    for i, mon in enumerate(monitors):
        print(f"Monitor {i}: {mon['rect']} (primary={mon['is_primary']})")
