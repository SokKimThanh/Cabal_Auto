# Vision Wizard - Menu and Layout Documentation

**Sprint 22 - Vision System Implementation**  
**Status**: Phase 2 Complete (Core Engine + UI Hooks)  
**Last Updated**: 2025-01-XX

---

## Table of Contents

1. [Overview](#overview)
2. [Phase 1 Summary](#phase-1-summary)
3. [Phase 2 Summary](#phase-2-summary)
4. [API Reference](#api-reference)
5. [Configuration Files](#configuration-files)
6. [Manual Test Checklist](#manual-test-checklist)
7. [Code Examples](#code-examples)

---

## Overview

Vision Wizard là hệ thống quản lý template và tracking cho game automation, được triển khai qua 2 phases:

- **Phase 1A**: Vision Wizard UI framework (`ui/setup_wizard_vision.py`)
- **Phase 1B**: Menu integration (`app_gui.py` - Vision menu + global hotkeys)
- **Phase 2**: Core vision engine + UI hooks (`lib/vision/vision_engine.py`)

**Key Features**:
- Multi-template, multi-scale detection
- Non-Maximum Suppression (NMS)
- Hybrid tracking (CV tracker + periodic template re-verification)
- Template manager với config persistence (JSON)
- Region selection (ROI)
- Strict separation: UI code không import cv2

---

## Phase 1 Summary

### Phase 1A: Vision Wizard Framework

**File**: `ui/setup_wizard_vision.py` (915 lines)

**Class**: `VisionWizard(tk.Toplevel)`
- Singleton pattern: chỉ mở 1 instance duy nhất
- Topmost mode: luôn hiển thị trên game window
- 5 panels: Header, Top (search mode/threshold), Middle (template tree), Bottom (buttons), Preview (canvas)

**UI Components**:
- Search mode combo: 3 modes (position, fullscreen, region)
- Threshold entry: 0.0 - 1.0 validation
- Template Treeview: 3 columns (name, path, threshold)
- Buttons: Add, Remove, Save Threshold, Test Recognition, Close
- Preview Canvas: 860x150 placeholder cho overlay

**Keyboard Shortcuts**:
- `Escape`: Close wizard
- `Ctrl+S`: Save threshold
- `Ctrl+T`: Test recognition
- `Delete`: Remove selected template

**Translations**: Hỗ trợ en + vi (12 keys trong `lib/i18n/translations.py`)

**Documentation**:
- `docs/sprint22/VISION_WIZARD_FRAMEWORK.md`
- `docs/sprint22/VISION_WIZARD_INTEGRATION_EXAMPLES.py`
- `docs/sprint22/QUICK_START_VISION_WIZARD.md`
- `docs/sprint22/PHASE1_COMPLETE_SUMMARY.md`

### Phase 1B: Menu Integration

**File**: `app_gui.py` (+156 lines)

**Vision Menu** (5 items):
1. **Open Vision Wizard** (`Ctrl+Shift+V`): Mở VisionWizard singleton
2. **Scan Region** (`Ctrl+Alt+S`): Placeholder cho Phase 3
3. **Add Template** (`Ctrl+T`): Quick add template file dialog
4. **Manage Templates** (`Ctrl+Shift+T`): Alias to open wizard
5. **Toggle Overlay** (`Ctrl+Shift+O`): Placeholder cho Phase 5

**Callback Methods**:
- `_open_vision_wizard()`: Creates/shows VisionWizard instance
- `_scan_region()`: Placeholder
- `_add_template()`: File dialog for quick template add
- `_manage_templates()`: Alias to `_open_vision_wizard()`
- `_toggle_overlay()`: Placeholder
- `_on_vision_wizard_closed()`: Cleanup callback

**Global Hotkeys**: Tích hợp vào `keyboard` library hotkey_map

**Translations**: 6 keys added (en + vi) in `lib/i18n/translations.py`

**Documentation**:
- `docs/sprint22/VISION_MENU_INTEGRATION.md`
- `docs/sprint22/VISION_MENU_INTEGRATION_CHECKLIST.md`
- `docs/sprint22/PHASE1B_COMPLETE_SUMMARY.md`

---

## Phase 2 Summary

### Goals

1. ✅ Tách logic OpenCV vào module riêng `lib/vision/vision_engine.py`
2. ✅ Triển khai detection (multi-template, multi-scale) + NMS
3. ✅ Triển khai hybrid tracking (tracker + periodic re-verify)
4. ✅ Template manager với config persistence
5. ✅ Region selection với save/load config
6. ✅ Wire UI hooks để VisionWizard gọi engine API
7. ✅ Tạo tests cơ bản
8. ⏳ Documentation update (this file)
9. ⏳ PR template and submission

### Deliverables

| # | Deliverable | Status | Files | Commit |
|---|-------------|--------|-------|--------|
| 1 | Core Engine | ✅ | `lib/vision/vision_engine.py` (810 lines) | `7be151f` |
| 2 | Config Files | ✅ | `lib/data/vision_templates.json`, `vision_region.json` | `fe1781c` |
| 3 | Basic Tests | ✅ | `tests/vision_basic_test.py` (339 lines), `tests/vision_test_README.md` | `3f1da9f` |
| 4 | UI Hooks | ✅ | `ui/setup_wizard_vision.py` (+304/-62) | `e16aec1` |
| 5 | Documentation | 🚧 | `docs/sprint22/SETUP_WIZARD_MENU_AND_LAYOUT.md` | Current |
| 6 | PR Template | ⏳ | `docs/sprint22/pr_template_vision.md` | Pending |

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     app_gui.py (Main App)                    │
│  - Vision Menu (5 items)                                     │
│  - Global hotkeys (Ctrl+Shift+V, etc.)                       │
│  - Callbacks: _open_vision_wizard(), _scan_region(), etc.    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ calls create_or_show_vision_wizard()
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          ui/setup_wizard_vision.py (VisionWizard)            │
│  - UI Layout: 5 panels (header, top, middle, bottom, preview│
│  - Template Treeview, Threshold Entry, Search Mode Combo     │
│  - Methods: load_templates(), add_template(), etc.           │
│  - NO cv2 imports (strict separation)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ calls get_vision_engine()
                         ▼
┌─────────────────────────────────────────────────────────────┐
│       lib/vision/vision_engine.py (VisionEngine)             │
│  - Singleton pattern: get_vision_engine()                    │
│  - Template loading: load_templates(path_list)               │
│  - Detection: match_templates(frame, roi, templates, scales) │
│  - NMS: nms(detections, iou_threshold)                       │
│  - Tracking: start_track(), update_tracks(), stop_all_tracks │
│  - Config persistence: _save_templates_config(), etc.        │
│  - All cv2 operations here                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ reads/writes
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              lib/data/*.json (Config Files)                  │
│  - vision_templates.json: Template metadata (id, path, etc.) │
│  - vision_region.json: Region definitions (x, y, w, h)       │
└─────────────────────────────────────────────────────────────┘
```

### Key Classes

#### VisionEngine (lib/vision/vision_engine.py)

**Singleton Access**:
```python
from lib.vision.vision_engine import get_vision_engine

engine = get_vision_engine()
```

**Dataclasses**:
- `Template`: Image data (cv2 Mat), thumbnail, path, threshold
- `Detection`: Template ID, bounding box, confidence score
- `TrackedObject`: Tracker instance, template, last position, frame count

**Main Methods**: See [API Reference](#api-reference)

#### VisionWizard (ui/setup_wizard_vision.py)

**Singleton Access**:
```python
from ui.setup_wizard_vision import create_or_show_vision_wizard

wizard = create_or_show_vision_wizard(parent_widget)
```

**Key Attributes**:
- `self.templates`: List[Dict] - Template metadata from JSON
- `self.vision_engine`: VisionEngine instance
- `self.template_tree`: Treeview widget
- `self.preview_canvas`: Canvas for overlay (Phase 3+)

**Main Methods**:
- `load_templates()`: Load from JSON + wire to engine
- `add_template()`: File dialog + save to JSON + reload engine
- `remove_template()`: Remove from list + save + reload engine
- `save_threshold()`: Update template threshold + save to JSON
- `test_recognition()`: Call engine.match_templates() with synthetic frame
- `save_region(name, x, y, w, h)`: Persist ROI to vision_region.json
- `load_region(name)`: Load ROI from vision_region.json
- `start_detection_loop()`: Placeholder (Phase 3)
- `stop_detection_loop()`: Call engine.stop_all_tracks()

---

## API Reference

### VisionEngine APIs

#### Template Management

**`load_templates(path_list: List[str]) -> int`**
- Load template images từ file paths
- Returns: Số templates loaded thành công
- Example:
  ```python
  engine = get_vision_engine()
  count = engine.load_templates([
      'assets/images/monsters/hp_bar.png',
      'assets/images/skills/skill_1.png'
  ])
  print(f"Loaded {count} templates")
  ```

**`get_template_by_id(template_id: str) -> Optional[Template]`**
- Get template object by ID
- Returns: Template dataclass hoặc None
- Example:
  ```python
  template = engine.get_template_by_id('monster_hp_bar')
  if template:
      print(f"Threshold: {template.threshold}")
  ```

#### Detection

**`match_templates(frame, roi, templates, scales, max_results) -> List[Detection]`**
- Detect templates trong frame với multi-scale matching
- Args:
  - `frame` (np.ndarray): Input image (grayscale hoặc BGR)
  - `roi` (Optional[Tuple[int, int, int, int]]): Region of interest (x, y, w, h)
  - `templates` (Optional[List[Template]]): Templates to match (None = all loaded)
  - `scales` (List[float]): Scale factors (default: [0.8, 1.0, 1.2])
  - `max_results` (int): Max detections per template
- Returns: List[Detection] với NMS applied
- Example:
  ```python
  import cv2
  frame = cv2.imread('screenshot.png', cv2.IMREAD_GRAYSCALE)
  
  detections = engine.match_templates(
      frame=frame,
      roi=(100, 100, 500, 400),  # ROI: x=100, y=100, w=500, h=400
      templates=None,  # Use all loaded templates
      scales=[0.8, 1.0, 1.2],
      max_results=5
  )
  
  for det in detections:
      print(f"Found {det.template_id} at ({det.x}, {det.y}) with score {det.score:.2f}")
  ```

**`nms(detections: List[Detection], iou_threshold: float = 0.3) -> List[Detection]`**
- Non-Maximum Suppression để loại bỏ duplicate detections
- Args:
  - `detections`: List of detections (cùng template)
  - `iou_threshold`: IoU threshold (default 0.3)
- Returns: Filtered detections
- Example:
  ```python
  # NMS already applied in match_templates()
  # Manual NMS:
  filtered = engine.nms(detections, iou_threshold=0.5)
  ```

#### Tracking

**`start_track(frame: np.ndarray, detection: Detection, tracker_type: str = 'CSRT') -> bool`**
- Bắt đầu tracking object từ detection
- Args:
  - `frame`: Current frame
  - `detection`: Detection object to track
  - `tracker_type`: 'CSRT' (chính xác) hoặc 'KCF' (nhanh)
- Returns: True if success
- Example:
  ```python
  import cv2
  frame = cv2.imread('screenshot.png')
  
  detections = engine.match_templates(frame, ...)
  if detections:
      success = engine.start_track(frame, detections[0], tracker_type='CSRT')
      print(f"Tracking started: {success}")
  ```

**`update_tracks(frame: np.ndarray, reverify_interval: int = 30) -> List[Tuple[str, int, int, int, int]]`**
- Update tất cả active trackers
- Periodic re-verification với template matching (mỗi `reverify_interval` frames)
- Args:
  - `frame`: Current frame
  - `reverify_interval`: Frames between re-verification (default 30)
- Returns: List[(tracker_id, x, y, w, h)] - active trackers
- Example:
  ```python
  # Trong detection loop
  while True:
      frame = capture_screen()
      
      # Update tracks
      active_tracks = engine.update_tracks(frame, reverify_interval=30)
      
      # Draw overlay
      for track_id, x, y, w, h in active_tracks:
          cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
  ```

**`reverify_track(frame: np.ndarray, tracker: TrackedObject, template: Template) -> bool`**
- Re-verify tracker position với template matching
- Internal method, called by `update_tracks()`
- Returns: True if re-verification success

**`stop_track(tracker_id: str) -> None`**
- Stop một tracker cụ thể
- Example:
  ```python
  engine.stop_track('track_001')
  ```

**`stop_all_tracks() -> None`**
- Stop tất cả trackers
- Example:
  ```python
  engine.stop_all_tracks()
  ```

**`get_active_tracks() -> List[TrackedObject]`**
- Get danh sách tất cả active trackers
- Returns: List[TrackedObject]

#### Configuration

**`_save_templates_config() -> None`**
- Save templates metadata to `lib/data/vision_templates.json`
- Internal method, called automatically

**`_load_templates_config() -> None`**
- Load templates metadata từ JSON
- Called in `__init__()`

---

### VisionWizard APIs

#### Template Management

**`load_templates() -> None`**
- Load templates từ `lib/data/vision_templates.json`
- Wire to engine: `engine.load_templates(paths)`
- Update UI: Refresh template tree
- Example:
  ```python
  wizard = create_or_show_vision_wizard(root)
  wizard.load_templates()
  ```

**`add_template() -> None`**
- File dialog để chọn template image
- Add to `self.templates` list
- Save to JSON: `_save_templates_config()`
- Reload engine: `engine.load_templates(paths)`
- UI: Show success message + refresh tree

**`remove_template() -> None`**
- Xóa template đang chọn trong tree
- Save to JSON + reload engine
- Confirmation dialog trước khi xóa

**`save_threshold() -> None`**
- Update threshold cho template đang chọn
- Persist to JSON
- Validation: 0.0 - 1.0

#### Testing

**`test_recognition() -> None`**
- Call `engine.match_templates()` với synthetic test frame
- Show results: templates loaded, detections found, threshold
- TODO Phase 3: Real screen capture + overlay display

#### Region Management

**`save_region(region_name: str, x: int, y: int, width: int, height: int) -> None`**
- Persist ROI to `lib/data/vision_region.json`
- Example:
  ```python
  wizard.save_region('monster_area', 100, 100, 500, 400)
  ```

**`load_region(region_name: str = "default") -> Optional[Tuple[int, int, int, int]]`**
- Load ROI từ JSON
- Returns: (x, y, width, height) hoặc None
- Example:
  ```python
  roi = wizard.load_region('monster_area')
  if roi:
      x, y, w, h = roi
  ```

#### Detection Loop (Phase 3+)

**`start_detection_loop() -> None`**
- Placeholder: Phase 3 sẽ implement
- TODO: Screen capture loop + real-time detection + overlay

**`stop_detection_loop() -> None`**
- Stop detection loop
- Call `engine.stop_all_tracks()`

---

## Configuration Files

### vision_templates.json

**Location**: `lib/data/vision_templates.json`

**Structure**: Array of template objects

**Fields**:
- `id` (str): Unique identifier (lowercase, underscore-separated)
- `name` (str): Display name
- `path` (str): Relative path to template image
- `threshold` (float): Detection threshold (0.0 - 1.0)
- `scales` (List[float]): Scale factors for multi-scale matching
- `enabled` (bool): Enable/disable template

**Example**:
```json
[
  {
    "id": "monster_hp_bar",
    "name": "Monster_HP_Bar",
    "path": "assets/images/monsters/hp_bar.png",
    "threshold": 0.8,
    "scales": [0.8, 1.0, 1.2],
    "enabled": true
  },
  {
    "id": "skill_icon_1",
    "name": "Skill_Icon_1",
    "path": "assets/images/skills/skill_1.png",
    "threshold": 0.75,
    "scales": [1.0],
    "enabled": true
  }
]
```

**Usage**:
- VisionWizard reads this file in `load_templates()`
- UI saves to this file via `_save_templates_config()`
- Engine does NOT read this file (UI passes paths to engine)

### vision_region.json

**Location**: `lib/data/vision_region.json`

**Structure**:
- `default_region`: Default ROI
- `regions`: Dict of named regions

**Fields** (per region):
- `x` (int): Top-left X coordinate
- `y` (int): Top-left Y coordinate
- `width` (int): Region width
- `height` (int): Region height

**Example**:
```json
{
  "default_region": {
    "x": 0,
    "y": 0,
    "width": 1920,
    "height": 1080
  },
  "regions": {
    "monster_area": {
      "x": 100,
      "y": 100,
      "width": 500,
      "height": 400
    },
    "skill_bar": {
      "x": 800,
      "y": 900,
      "width": 300,
      "height": 100
    }
  }
}
```

**Usage**:
- VisionWizard saves via `save_region()`
- VisionWizard loads via `load_region()`
- User can select region in UI (Phase 3+)

---

## Manual Test Checklist

### Phase 1A: Vision Wizard Framework

- [ ] Open wizard: `python -m ui.setup_wizard_vision`
- [ ] Verify UI layout: 5 panels visible
- [ ] Test keyboard shortcuts:
  - [ ] `Escape`: Close wizard
  - [ ] `Ctrl+S`: Save threshold (warning if no selection)
  - [ ] `Ctrl+T`: Test recognition (placeholder message)
  - [ ] `Delete`: Remove template (warning if no selection)
- [ ] Test translations: Switch language (en/vi) in main app
- [ ] Test singleton: Open wizard twice → same instance lifted

### Phase 1B: Menu Integration

- [ ] Open main app: `python app_gui.py`
- [ ] Verify Vision menu: 5 items visible
- [ ] Test global hotkeys:
  - [ ] `Ctrl+Shift+V`: Open Vision Wizard
  - [ ] `Ctrl+Alt+S`: Scan Region (placeholder)
  - [ ] `Ctrl+T`: Add Template (file dialog)
  - [ ] `Ctrl+Shift+T`: Manage Templates (open wizard)
  - [ ] `Ctrl+Shift+O`: Toggle Overlay (placeholder)
- [ ] Test menu callbacks:
  - [ ] Click "Open Vision Wizard" → Wizard opens
  - [ ] Click "Add Template" → File dialog opens
- [ ] Verify translations: Vision menu items in en/vi

### Phase 2: Core Engine + UI Hooks

#### Engine Tests (Automated)

- [ ] Run automated tests: `python tests/vision_basic_test.py`
  - [ ] Test 1: Engine initialization
  - [ ] Test 2: Template loading
  - [ ] Test 3: Template detection
  - [ ] Test 4: NMS
  - [ ] Test 5: Tracking
  - [ ] Test 6: Config persistence
- [ ] All tests pass ✅

#### UI Hooks Tests (Manual)

**Setup**:
1. Open Vision Wizard: `Ctrl+Shift+V`
2. Prepare test template images in `assets/images/`

**Test load_templates()**:
- [ ] Edit `lib/data/vision_templates.json` với valid paths
- [ ] Close + reopen wizard
- [ ] Verify templates loaded in tree
- [ ] Console: "Vision engine loaded X templates"

**Test add_template()**:
- [ ] Click "Add Template" button
- [ ] Select valid image file
- [ ] Verify:
  - [ ] Template added to tree
  - [ ] `vision_templates.json` updated
  - [ ] Console: "Vision engine loaded X templates" (X = total)
  - [ ] Success message shown

**Test remove_template()**:
- [ ] Select template in tree
- [ ] Click "Remove" button
- [ ] Confirm dialog → Yes
- [ ] Verify:
  - [ ] Template removed from tree
  - [ ] `vision_templates.json` updated
  - [ ] Console: "Vision engine loaded X templates" (X = total - 1)
  - [ ] Success message shown

**Test save_threshold()**:
- [ ] Select template in tree
- [ ] Change threshold in entry (e.g., 0.85)
- [ ] Click "Save Threshold" button
- [ ] Verify:
  - [ ] Threshold updated in tree
  - [ ] `vision_templates.json` updated (threshold = 0.85)
  - [ ] Success message shown
- [ ] Test validation:
  - [ ] Enter invalid value (e.g., 1.5)
  - [ ] Click "Save Threshold"
  - [ ] Error message: "Ngưỡng không hợp lệ"

**Test test_recognition()**:
- [ ] Ensure templates loaded
- [ ] Click "Test Recognition" button
- [ ] Verify:
  - [ ] Info dialog shows:
    - Templates loaded: X
    - Detections found: Y (có thể = 0 với synthetic frame)
    - Threshold: Z
    - Note: Using synthetic test frame
  - [ ] No errors

**Test region save/load** (via Python console):
```python
from ui.setup_wizard_vision import create_or_show_vision_wizard
import tkinter as tk

root = tk.Tk()
wizard = create_or_show_vision_wizard(root)

# Save region
wizard.save_region('test_region', 100, 200, 300, 400)
# Verify: lib/data/vision_region.json created/updated

# Load region
roi = wizard.load_region('test_region')
assert roi == (100, 200, 300, 400), "Region mismatch"
print("✅ Region save/load OK")
```

**Test detection loop placeholders**:
- [ ] Call `wizard.start_detection_loop()` via console
- [ ] Verify: Placeholder message shown
- [ ] Call `wizard.stop_detection_loop()` via console
- [ ] Console: "All tracks stopped"

#### Error Handling

- [ ] Test with missing OpenCV:
  - Uninstall OpenCV: `pip uninstall opencv-python`
  - Open wizard
  - Click "Test Recognition"
  - Verify: Error message "NumPy/OpenCV not installed"
  - Reinstall: `pip install opencv-python`

- [ ] Test with missing vision_engine:
  - Rename `lib/vision/vision_engine.py` temporarily
  - Open wizard
  - Click "Test Recognition"
  - Verify: Warning "Vision engine not initialized"
  - Restore file

- [ ] Test with missing templates:
  - Clear `vision_templates.json` (set to `[]`)
  - Open wizard
  - Click "Test Recognition"
  - Verify: Warning "No templates loaded"

### Regression Tests

- [ ] Main app still opens: `python app_gui.py`
- [ ] Existing features unaffected:
  - [ ] Auto Hunt works
  - [ ] Skills rotation works
  - [ ] Hotkeys work (F8, F9, etc.)
- [ ] No import errors in console
- [ ] No type errors (ignore warnings)

---

## Code Examples

### Example 1: Open Vision Wizard from Main App

```python
# In app_gui.py (already implemented)

from ui.setup_wizard_vision import create_or_show_vision_wizard

class App(tk.Tk):
    def _open_vision_wizard(self):
        """Callback for Vision menu / Ctrl+Shift+V"""
        wizard = create_or_show_vision_wizard(
            parent=self,
            on_close=self._on_vision_wizard_closed
        )
        wizard.lift()
        wizard.focus_force()
    
    def _on_vision_wizard_closed(self):
        """Cleanup when wizard closed"""
        print("Vision wizard closed")
```

### Example 2: Load Templates and Detect

```python
from lib.vision.vision_engine import get_vision_engine
import cv2

# Get engine instance
engine = get_vision_engine()

# Load templates
count = engine.load_templates([
    'assets/images/monsters/hp_bar.png',
    'assets/images/skills/skill_1.png'
])
print(f"Loaded {count} templates")

# Capture screen (example)
frame = cv2.imread('screenshot.png', cv2.IMREAD_GRAYSCALE)

# Detect templates
detections = engine.match_templates(
    frame=frame,
    roi=None,  # Full frame
    templates=None,  # All loaded templates
    scales=[0.8, 1.0, 1.2],
    max_results=10
)

# Print results
for det in detections:
    print(f"Template: {det.template_id}")
    print(f"Position: ({det.x}, {det.y})")
    print(f"Size: {det.width}x{det.height}")
    print(f"Score: {det.score:.2f}")
    print("---")
```

### Example 3: Start Tracking Detected Objects

```python
from lib.vision.vision_engine import get_vision_engine
import cv2

engine = get_vision_engine()

# Load templates
engine.load_templates(['assets/images/monsters/hp_bar.png'])

# Capture initial frame
frame = cv2.imread('screenshot.png')

# Detect
detections = engine.match_templates(frame, roi=None)

if detections:
    # Start tracking first detection
    success = engine.start_track(frame, detections[0], tracker_type='CSRT')
    print(f"Tracking started: {success}")
    
    # In game loop:
    while True:
        new_frame = cv2.imread('new_screenshot.png')
        
        # Update tracks (re-verify every 30 frames)
        active_tracks = engine.update_tracks(new_frame, reverify_interval=30)
        
        # Draw overlay
        for track_id, x, y, w, h in active_tracks:
            cv2.rectangle(new_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        cv2.imshow('Tracking', new_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Stop tracking
    engine.stop_all_tracks()
```

### Example 4: Save and Load Regions

```python
from ui.setup_wizard_vision import create_or_show_vision_wizard
import tkinter as tk

root = tk.Tk()
wizard = create_or_show_vision_wizard(root)

# Save multiple regions
wizard.save_region('monster_area', 100, 100, 500, 400)
wizard.save_region('skill_bar', 800, 900, 300, 100)
wizard.save_region('minimap', 1600, 50, 300, 300)

# Load and use region
monster_roi = wizard.load_region('monster_area')
if monster_roi:
    x, y, w, h = monster_roi
    
    # Use in detection
    from lib.vision.vision_engine import get_vision_engine
    import cv2
    
    engine = get_vision_engine()
    frame = cv2.imread('screenshot.png', cv2.IMREAD_GRAYSCALE)
    
    detections = engine.match_templates(
        frame=frame,
        roi=(x, y, w, h),  # Only search in monster_area
        templates=None,
        scales=[1.0]
    )
    
    print(f"Found {len(detections)} monsters in region")
```

### Example 5: Use Vision Engine in Custom Script

```python
# scripts/custom_detection.py

from lib.vision.vision_engine import get_vision_engine
import cv2
import time

def main():
    # Initialize engine
    engine = get_vision_engine()
    
    # Load templates from config
    # (Or manually specify paths)
    templates = [
        'assets/images/monsters/monster1.png',
        'assets/images/monsters/monster2.png'
    ]
    engine.load_templates(templates)
    
    print(f"Loaded {len(engine.templates)} templates")
    
    # Detection loop
    try:
        while True:
            # Capture screen (use your capture method)
            # For demo: load static image
            frame = cv2.imread('game_screenshot.png')
            if frame is None:
                print("No screenshot found")
                break
            
            # Detect
            detections = engine.match_templates(
                frame=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                roi=None,
                templates=None,  # Use all
                scales=[0.8, 1.0, 1.2]
            )
            
            print(f"Found {len(detections)} objects")
            
            # Draw overlay
            for det in detections:
                cv2.rectangle(
                    frame,
                    (det.x, det.y),
                    (det.x + det.width, det.y + det.height),
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    frame,
                    f"{det.template_id} ({det.score:.2f})",
                    (det.x, det.y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1
                )
            
            # Display
            cv2.imshow('Detection', frame)
            if cv2.waitKey(1000) & 0xFF == ord('q'):
                break
    
    finally:
        cv2.destroyAllWindows()
        engine.stop_all_tracks()

if __name__ == '__main__':
    main()
```

---

## Next Steps

### Phase 3: Real Screen Capture + Overlay

1. **Screen capture integration**:
   - Add capture method in `lib/vision/vision_engine.py` (using MSS or PIL)
   - Update `test_recognition()` để dùng real capture thay vì synthetic frame

2. **Real-time overlay**:
   - Update `preview_canvas` để hiển thị frame + detections
   - Add draw methods: `_draw_detections()`, `_draw_tracks()`

3. **Detection loop**:
   - Implement `start_detection_loop()`: periodic screen capture + detection
   - Threading để không block UI
   - FPS control (target: 10-30 FPS)

4. **Region selection UI**:
   - Add button "Select Region" → open overlay window
   - User clicks and drags to define ROI
   - Save region to JSON

### Phase 4: Advanced Tracking

1. **Tracker loss handling**:
   - Re-detect if tracker lost
   - Auto-switch tracker types (CSRT → KCF nếu slow)

2. **Multi-object tracking**:
   - Track multiple objects simultaneously
   - Color-coded overlay per object

3. **Tracking metrics**:
   - Display FPS, track count, detection count
   - Log tracking events

### Phase 5: Integration with Auto Hunt

1. **Monster detection**:
   - Use vision engine để detect monsters
   - Replace existing pixel-based detection

2. **Skill cooldown detection**:
   - Detect skill icons availability
   - Optimize skill rotation timing

3. **HP bar detection**:
   - Detect player/monster HP bars
   - Auto-potion logic

---

## References

- **Phase 1A Docs**: `docs/sprint22/VISION_WIZARD_FRAMEWORK.md`
- **Phase 1B Docs**: `docs/sprint22/VISION_MENU_INTEGRATION.md`
- **Engine Implementation**: `lib/vision/vision_engine.py`
- **UI Implementation**: `ui/setup_wizard_vision.py`
- **Tests**: `tests/vision_basic_test.py`, `tests/vision_test_README.md`
- **Config Examples**: `lib/data/vision_templates.json`, `lib/data/vision_region.json`

---

**End of Documentation**
