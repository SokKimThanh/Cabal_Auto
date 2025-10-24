# Phase 8: Screen Capture System

## Overview

Phase 8 implements a high-performance screen capture system for capturing game windows in real-time. The system is designed to achieve 15+ FPS capture rate using Windows GDI APIs and provides thread-safe frame access through a producer-consumer architecture.

## Architecture

### Components

1. **ScreenCapture** (`lib/system/screen_capture.py`)
   - Main capture class with multi-threaded frame acquisition
   - BitBlt-based capture using Windows GDI
   - Frame queue management with automatic frame dropping
   - Real-time statistics tracking

2. **WindowManager** (`lib/system/window_manager.py`)
   - Window detection and enumeration
   - Window manipulation (focus, resize, minimize)
   - Monitor information retrieval
   - Process information integration

### Threading Model

```
┌─────────────────────────────────────────────────────────────┐
│                     Main Thread                              │
│  - Creates ScreenCapture instance                            │
│  - Calls start_capture()                                     │
│  - Calls get_frame() to retrieve frames                      │
│  - Calls get_stats() for performance metrics                 │
│  - Calls stop_capture() to cleanup                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ spawns
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Capture Thread (Producer)                   │
│  - Runs in background (_capture_loop)                        │
│  - Captures frames at target FPS (default 15)                │
│  - Puts frames into queue (queue_size=5)                     │
│  - Drops old frames if queue full                            │
│  - Updates statistics every second                           │
│  - Cleans up GDI resources on exit                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ queue.Queue
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Frame Queue (Consumer)                     │
│  - Thread-safe queue with maxsize=5                          │
│  - Main thread retrieves frames via get_frame()              │
│  - Non-blocking get with timeout                             │
│  - Automatic frame dropping on overflow                      │
└─────────────────────────────────────────────────────────────┘
```

## API Documentation

### ScreenCapture Class

#### Constructor

```python
ScreenCapture(
    hwnd: int,
    queue_size: int = 5,
    target_fps: int = 15
)
```

**Parameters:**
- `hwnd`: Window handle to capture from
- `queue_size`: Maximum number of frames in queue (default: 5)
- `target_fps`: Target frames per second (default: 15)

**Raises:**
- `ImportError`: If not running on Windows platform
- `RuntimeError`: If window handle is invalid or GDI setup fails

#### Methods

##### `start_capture() -> None`

Starts the capture thread.

**Raises:**
- `RuntimeError`: If capture is already running or GDI setup fails

**Example:**
```python
capture = ScreenCapture(hwnd)
capture.start_capture()
```

##### `stop_capture() -> None`

Stops the capture thread and cleans up resources.

**Thread-safe:** Can be called from any thread

**Example:**
```python
capture.stop_capture()
```

##### `get_frame(timeout: float = 0.1) -> Optional[np.ndarray]`

Retrieves the latest frame from the queue.

**Parameters:**
- `timeout`: Maximum time to wait for a frame in seconds (default: 0.1)

**Returns:**
- `np.ndarray`: BGR image array if available
- `None`: If no frame available within timeout

**Example:**
```python
frame = capture.get_frame(timeout=0.5)
if frame is not None:
    # Process frame
    cv2.imshow("Game Window", frame)
```

##### `get_stats() -> CaptureStats`

Returns current capture statistics.

**Returns:**
- `CaptureStats`: Dataclass with performance metrics

**Example:**
```python
stats = capture.get_stats()
print(f"FPS: {stats.fps:.2f}")
print(f"Frames captured: {stats.frames_captured}")
print(f"Frames dropped: {stats.frames_dropped}")
```

#### Properties

##### `is_capturing -> bool`

Returns whether capture thread is currently running.

**Example:**
```python
if capture.is_capturing:
    print("Capture is active")
```

### CaptureStats Dataclass

```python
@dataclass
class CaptureStats:
    fps: float              # Current frames per second
    frames_captured: int    # Total frames captured since start
    frames_dropped: int     # Total frames dropped (queue full)
    queue_size: int        # Current number of frames in queue
    last_update: float     # Timestamp of last statistics update
```

### WindowManager Class

#### Static Methods

##### `find_window(title: Optional[str] = None, class_name: Optional[str] = None) -> Optional[int]`

Finds a window by title or class name.

**Parameters:**
- `title`: Window title (partial match, case-insensitive)
- `class_name`: Window class name (exact match)

**Returns:**
- `int`: Window handle if found
- `None`: If no matching window found

**Example:**
```python
hwnd = WindowManager.find_window(title="Cabal")
if hwnd:
    capture = ScreenCapture(hwnd)
```

##### `get_all_windows(include_invisible: bool = False) -> List[WindowInfo]`

Returns list of all windows.

**Parameters:**
- `include_invisible`: Include hidden/invisible windows (default: False)

**Returns:**
- `List[WindowInfo]`: List of window information

**Example:**
```python
windows = WindowManager.get_all_windows()
for win in windows:
    print(f"{win.title} - {win.hwnd}")
```

##### `get_window_info(hwnd: int) -> Optional[WindowInfo]`

Gets detailed information about a window.

**Parameters:**
- `hwnd`: Window handle

**Returns:**
- `WindowInfo`: Window details if valid
- `None`: If window handle is invalid

**Example:**
```python
info = WindowManager.get_window_info(hwnd)
if info:
    print(f"Title: {info.title}")
    print(f"Size: {info.width}x{info.height}")
    print(f"Process: {info.process_name}")
```

##### `set_foreground(hwnd: int) -> bool`

Brings window to foreground and sets focus.

**Parameters:**
- `hwnd`: Window handle

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
if WindowManager.set_foreground(hwnd):
    print("Window focused successfully")
```

##### `get_window_rect(hwnd: int) -> Optional[Dict[str, int]]`

Gets window rectangle coordinates.

**Parameters:**
- `hwnd`: Window handle

**Returns:**
- `Dict[str, int]`: Dictionary with keys: x, y, width, height
- `None`: If window handle is invalid

**Example:**
```python
rect = WindowManager.get_window_rect(hwnd)
if rect:
    print(f"Position: ({rect['x']}, {rect['y']})")
    print(f"Size: {rect['width']}x{rect['height']}")
```

### WindowInfo Dataclass

```python
@dataclass
class WindowInfo:
    hwnd: int                    # Window handle
    title: str                   # Window title
    class_name: str             # Window class name
    is_visible: bool            # Whether window is visible
    is_enabled: bool            # Whether window is enabled
    is_minimized: bool          # Whether window is minimized
    is_maximized: bool          # Whether window is maximized
    x: int                      # X coordinate
    y: int                      # Y coordinate
    width: int                  # Window width
    height: int                 # Window height
    process_id: int             # Process ID
    process_name: Optional[str] # Process name (if psutil available)
```

## Usage Examples

### Basic Capture

```python
from lib.system.screen_capture import ScreenCapture
from lib.system.window_manager import WindowManager
import cv2

# Find game window
hwnd = WindowManager.find_window(title="Cabal")
if not hwnd:
    print("Game window not found!")
    exit(1)

# Create capture instance
capture = ScreenCapture(hwnd, target_fps=30)

# Start capturing
capture.start_capture()

try:
    while True:
        # Get latest frame
        frame = capture.get_frame(timeout=0.1)
        if frame is not None:
            # Display frame
            cv2.imshow("Game Capture", frame)
            
            # Show statistics
            stats = capture.get_stats()
            print(f"FPS: {stats.fps:.2f}, Dropped: {stats.frames_dropped}")
        
        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Cleanup
    capture.stop_capture()
    cv2.destroyAllWindows()
```

### Window Detection and Focus

```python
from lib.system.window_manager import WindowManager

# List all game windows
all_windows = WindowManager.get_all_windows()
game_windows = [w for w in all_windows if "Cabal" in w.title]

print(f"Found {len(game_windows)} game windows:")
for win in game_windows:
    print(f"  - {win.title} ({win.process_name})")
    print(f"    Position: ({win.x}, {win.y})")
    print(f"    Size: {win.width}x{win.height}")
    print(f"    Minimized: {win.is_minimized}, Maximized: {win.is_maximized}")

# Focus first game window
if game_windows:
    hwnd = game_windows[0].hwnd
    if WindowManager.set_foreground(hwnd):
        print("Window focused successfully")
```

### Performance Monitoring

```python
from lib.system.screen_capture import ScreenCapture
from lib.system.window_manager import WindowManager
import time

hwnd = WindowManager.find_window(title="Cabal")
capture = ScreenCapture(hwnd, target_fps=30, queue_size=10)

capture.start_capture()

# Monitor performance for 10 seconds
start_time = time.time()
while time.time() - start_time < 10:
    frame = capture.get_frame()
    
    # Get statistics every second
    stats = capture.get_stats()
    if int(time.time()) % 1 == 0:
        print(f"FPS: {stats.fps:.2f}")
        print(f"Total captured: {stats.frames_captured}")
        print(f"Total dropped: {stats.frames_dropped}")
        print(f"Queue size: {stats.queue_size}")
        print(f"Drop rate: {stats.frames_dropped / max(stats.frames_captured, 1) * 100:.1f}%")
        print("-" * 40)
    
    time.sleep(0.01)

capture.stop_capture()
```

### Multi-Monitor Support

```python
from lib.system.window_manager import WindowManager

# Get all monitors
monitors = WindowManager.get_monitors()
print(f"Found {len(monitors)} monitors:")

for i, monitor in enumerate(monitors):
    print(f"Monitor {i}:")
    print(f"  Primary: {monitor['is_primary']}")
    print(f"  Position: ({monitor['x']}, {monitor['y']})")
    print(f"  Size: {monitor['width']}x{monitor['height']}")
    print(f"  Work area: {monitor['work_x']}, {monitor['work_y']}, "
          f"{monitor['work_width']}, {monitor['work_height']}")
```

## Performance Considerations

### Target FPS

- **Default: 15 FPS** - Balanced performance for most games
- **30 FPS** - Smooth capture for fast-paced games (higher CPU usage)
- **60 FPS** - High-performance capture (very high CPU usage)

### Queue Size

- **Default: 5 frames** - ~333ms buffer at 15 FPS
- **Smaller queues (2-3)** - Lower latency but more frame drops
- **Larger queues (10+)** - Higher latency but smoother under load

### Frame Dropping

Frames are automatically dropped when:
1. Queue is full (consumer too slow)
2. No space available for new frame

Monitor `frames_dropped` in statistics to detect performance issues.

### CPU Usage

Typical CPU usage per capture instance:
- **15 FPS**: 1-2% CPU (single core)
- **30 FPS**: 2-4% CPU (single core)
- **60 FPS**: 4-8% CPU (single core)

### Memory Usage

- **Per frame**: ~2-8 MB (depends on window size)
- **Total memory**: queue_size × frame_size
- **Example**: 1920x1080 window with queue_size=5 ≈ 30 MB

## Platform Requirements

### Windows Only

Both modules require Windows platform:
- Uses Windows GDI APIs (BitBlt, CreateCompatibleDC)
- Uses win32 APIs (EnumWindows, GetWindowText)
- Will raise `ImportError` on non-Windows platforms

### Dependencies

```
opencv-python>=4.12.0
numpy>=2.3.4
pywin32>=311
psutil>=7.1.1  # Optional, for process name detection
```

### Python Version

- **Minimum**: Python 3.8
- **Tested**: Python 3.14.0
- **Recommended**: Python 3.10+

## Error Handling

### Common Errors

#### ImportError: "Screen capture is only supported on Windows"

**Cause**: Running on non-Windows platform

**Solution**: This module only works on Windows. Use platform checks before importing.

#### RuntimeError: "Invalid window handle"

**Cause**: Window doesn't exist or was closed

**Solution**: Verify window exists with `WindowManager.find_window()` before creating capture.

#### RuntimeError: "Failed to create device context"

**Cause**: GDI resource exhaustion or invalid window

**Solution**: 
1. Ensure window is valid and visible
2. Check if too many capture instances are running
3. Restart application to free GDI resources

#### No frames received (get_frame returns None)

**Cause**: Window is minimized, hidden, or capture thread crashed

**Solution**:
1. Check `is_capturing` property
2. Verify window is visible with `WindowManager.get_window_info()`
3. Check capture thread for exceptions

### Exception Handling Example

```python
from lib.system.screen_capture import ScreenCapture
from lib.system.window_manager import WindowManager

try:
    # Find window
    hwnd = WindowManager.find_window(title="Cabal")
    if not hwnd:
        raise ValueError("Game window not found")
    
    # Check window state
    info = WindowManager.get_window_info(hwnd)
    if info and info.is_minimized:
        print("Warning: Window is minimized, restoring...")
        WindowManager.restore_window(hwnd)
    
    # Create capture
    capture = ScreenCapture(hwnd)
    capture.start_capture()
    
    # Capture loop
    while capture.is_capturing:
        frame = capture.get_frame(timeout=0.5)
        if frame is None:
            print("Warning: No frame received")
            continue
        
        # Process frame
        # ...
        
except ImportError as e:
    print(f"Platform error: {e}")
except RuntimeError as e:
    print(f"Capture error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    if 'capture' in locals():
        capture.stop_capture()
```

## Testing

### Test Files

1. `tests/sprints/sprint23/test_screen_capture.py` (490 lines)
   - Unit tests for ScreenCapture class
   - Performance tests (15+ FPS validation)
   - Edge case testing (null handles, thread safety)

2. `tests/sprints/sprint23/test_window_manager.py` (550 lines)
   - Unit tests for WindowManager class
   - Window detection and manipulation tests
   - Monitor information tests

3. `tests/sprints/sprint23/test_phase8_simple.py` (170 lines)
   - Integration tests without mocking
   - Import validation
   - Class instantiation tests

### Running Tests

```powershell
# All Phase 8 tests
pytest tests/sprints/sprint23/ -v

# Only unit tests
pytest tests/sprints/sprint23/ -v -m unit

# Only Windows-specific tests
pytest tests/sprints/sprint23/ -v -m windows

# With coverage
pytest tests/sprints/sprint23/ --cov=lib.system --cov-report=html
```

### Test Markers

- `@pytest.mark.windows`: Requires Windows platform
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.slow`: Tests that take >1 second
- `@pytest.mark.performance`: Performance validation tests

## Integration Guide

### Vision Engine Integration

See Task 3 implementation for full integration with `lib/vision/vision_engine.py`:

```python
from lib.system.screen_capture import ScreenCapture
from lib.system.window_manager import WindowManager

class VisionEngine:
    def __init__(self):
        self.capture = None
        self.hwnd = None
    
    def start(self, window_title: str):
        # Find and focus window
        self.hwnd = WindowManager.find_window(title=window_title)
        if not self.hwnd:
            raise ValueError(f"Window not found: {window_title}")
        
        WindowManager.set_foreground(self.hwnd)
        
        # Start capture
        self.capture = ScreenCapture(self.hwnd, target_fps=15)
        self.capture.start_capture()
    
    def process_frame(self):
        if not self.capture:
            return None
        
        frame = self.capture.get_frame(timeout=0.1)
        if frame is None:
            return None
        
        # Process frame with vision algorithms
        # ...
        
        return frame
    
    def stop(self):
        if self.capture:
            self.capture.stop_capture()
            self.capture = None
```

## Future Enhancements

### Potential Improvements

1. **Hardware Acceleration**
   - Use Desktop Duplication API for better performance
   - GPU-accelerated frame processing

2. **Recording Support**
   - Save frames to video file
   - Configurable compression settings

3. **Region Capture**
   - Capture specific window regions
   - Multiple capture regions per window

4. **Performance Tuning**
   - Adaptive FPS based on CPU usage
   - Dynamic queue size adjustment

5. **Cross-Platform Support**
   - X11 capture for Linux
   - Quartz capture for macOS

## Changelog

### Phase 8 (2025-10-23)

- ✅ Initial implementation
- ✅ ScreenCapture class with multi-threading
- ✅ WindowManager class with window detection
- ✅ Comprehensive test suite (1,200+ lines)
- ✅ Platform checks and error handling
- ✅ Type safety improvements
- ✅ Null pointer protection
- ✅ Documentation complete

## References

- [Windows GDI BitBlt Documentation](https://docs.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-bitblt)
- [Python threading Documentation](https://docs.python.org/3/library/threading.html)
- [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- Sprint 23 Phase Plan: `docs/sprints/sprint23/SPRINT23_PLAN.md`

---

**Author**: Sprint 23 Team  
**Date**: October 23, 2025  
**Version**: 1.0.0
