# UI Module - User Interface Components

This directory contains UI-related components for the CABAL Auto Hunt application.

---

## 📁 Directory Structure

```
lib/ui/
├── __init__.py                       # Module initialization
├── README.md                         # This file
├── ui_style.py                       # Global UI styling
├── auto_hunt.py                      # Hunt loop UI
├── setup_wizard.py                   # Initial setup wizard
├── setup_wizard_vision.py            # Vision template setup
├── template_matcher.py               # Template matching UI
├── win_input.py                      # Windows input simulation
├── overlay_window_pywin32.py         # PyWin32 overlay (Sprint 23)
├── window_tracker.py                 # Window position tracking (Sprint 23)
├── detection_converter.py            # Vision → Overlay converter (Sprint 23)
└── overlay_settings.py               # Overlay settings dialog
```

---

## 🆕 Sprint 23 - Overlay System

### New Components

#### 1. **OverlayWindowPyWin32** (`overlay_window_pywin32.py`)
Real-time transparent overlay for vision detection display.

**Features:**
- Semi-transparent, click-through window
- GDI rendering for detection boxes
- FPS-limited updates (configurable)
- Thread-safe detection updates

**Usage:**
```python
from lib.ui.overlay_window_pywin32 import OverlayWindowPyWin32, DetectionBox

overlay = OverlayWindowPyWin32(
    target_rect={'left': 100, 'top': 100, 'width': 800, 'height': 600},
    alpha=0.7,
    fps_limit=15
)
overlay.create()
overlay.show()

# Update with detections
boxes = [DetectionBox(x=100, y=200, w=50, h=60, label="Monster", color=(0,255,0))]
overlay.update_detections(boxes)
```

#### 2. **WindowTracker** (`window_tracker.py`)
High-frequency window position/size tracking for overlay synchronization.

**Features:**
- 60 FPS tracking loop
- Callback system (position/size/state changes)
- Auto hide/show on minimize/restore
- Thread-safe operations

**Usage:**
```python
from lib.ui.window_tracker import WindowTracker

tracker = WindowTracker(
    target_hwnd=game_hwnd,
    poll_rate=60,
    on_position_change=lambda rect: overlay.update_target_rect(rect),
    on_size_change=lambda rect: overlay.update_target_rect(rect)
)
tracker.start()
```

#### 3. **Detection Converter** (`detection_converter.py`)
Utility functions to convert VisionEngine detections to overlay format.

**Functions:**
- `detection_to_box()` - Single detection conversion
- `detections_to_boxes()` - Batch conversion
- `get_state_color()` - State-based color mapping
- `create_empty_search_box()` - Placeholder for no detections

**Usage:**
```python
from lib.ui.detection_converter import detections_to_boxes
from lib.vision.vision_engine import VisionEngine

engine = VisionEngine()
detections = engine.match_templates(frame)
boxes = detections_to_boxes(detections, state="detected")
overlay.update_detections(boxes)
```

---

## 📚 Documentation

### Phase 5 Overlay System
- [PHASE5_OVERLAY_SYSTEM.md](../../docs/sprints/sprint23/PHASE5_OVERLAY_SYSTEM.md) - Technical documentation
- [PHASE5_COMPLETION_SUMMARY.md](../../docs/sprints/sprint23/PHASE5_COMPLETION_SUMMARY.md) - Implementation summary
- [PHASE5_QUICK_REFERENCE.md](../../docs/sprints/sprint23/PHASE5_QUICK_REFERENCE.md) - Quick reference guide

### Demos
- [demo_overlay_vision.py](../../tests/demos/demo_overlay_vision.py) - Vision integration demo

---

## 🎯 Quick Start - Overlay

### 1. Toggle Overlay
```
Press: Ctrl + Shift + O
```

### 2. In Code
```python
# In app_gui.py
def _toggle_overlay(self):
    if not self._overlay_enabled:
        # Create overlay
        overlay = OverlayWindowPyWin32(...)
        overlay.create()
        overlay.show()
        
        # Start tracking
        tracker = WindowTracker(...)
        tracker.start()
    else:
        # Hide and cleanup
        overlay.hide()
        tracker.stop()
```

---

## 🔧 Configuration

Overlay settings stored in `lib/data/hunt_config.json`:

```json
{
  "overlay": {
    "alpha": 0.7,
    "fps_limit": 15,
    "click_through": true
  }
}
```

---

## 🧪 Testing

### Run Overlay Demo
```bash
.\venv\Scripts\python.exe tests\demos\demo_overlay_vision.py
```

### Manual Testing
1. Open CABAL game
2. Run app: `.\venv\Scripts\python.exe app_gui.py`
3. Press `Ctrl+Shift+O`
4. Verify overlay appears and follows window

---

## 📊 Performance

| Component | FPS | CPU | Memory |
|-----------|-----|-----|--------|
| Overlay Rendering | 15 | 1-2% | ~10MB |
| WindowTracker | 60 | 1% | ~5MB |
| Total | - | 2-3% | ~20MB |

---

## 🔗 Dependencies

### PyWin32 (Windows Only)
```bash
pip install pywin32
```

**Used for:**
- Window manipulation (HWND, styles)
- GDI rendering (Device Context, BitBlt)
- Click-through support (WS_EX_TRANSPARENT)

---

## 🚀 Next Steps

Phase 5 complete! Next: **Phase 7 - Monster Tracking Integration**

Integration points ready:
- ✅ Overlay rendering
- ✅ Detection box display
- ✅ Real-time updates
- ✅ Vision data conversion

---

**Last Updated:** October 24, 2025  
**Sprint:** 23 Phase 5 ✅ COMPLETE
