# Phase 7: Monster Tracking Integration - Detailed Plan

**Sprint:** 23  
**Branch:** `feature/S23-vision-advanced`  
**Date:** October 24, 2025  
**Status:** 🚧 PLANNING  
**Priority:** 🔴 HIGH

---

## 📋 Overview

Phase 7 integrates VisionEngine with the Overlay System to provide real-time monster detection and tracking visualization. This phase replaces simulation data with actual template matching results.

### Objectives

✅ **Real-time Detection Display**
- Replace demo simulation with actual VisionEngine detection
- Display bounding boxes at real monster positions
- Show confidence scores and labels

✅ **Tracking State Management**
- Implement state machine: Searching → Detected → Tracking → Lost
- Color-coded visual feedback for each state
- Handle target acquisition and loss

✅ **Hunt Loop Integration**
- Detection loop runs in background thread
- Signal/event system for hunt communication
- Thread-safe state updates

✅ **Performance Optimization**
- Detection interval: 100ms (10 FPS detection)
- Overlay rendering: 15 FPS
- Minimal CPU overhead

---

## 🎯 Success Criteria

| Metric | Target | Validation |
|--------|--------|------------|
| Detection Latency | < 150ms | From capture to overlay display |
| FPS Impact | < 5% | Game FPS should not drop significantly |
| Memory Overhead | < 50MB | Detection + overlay combined |
| False Positives | < 10% | Template matching accuracy |
| Thread Safety | 100% | No race conditions or deadlocks |

---

## 📦 Implementation Batches

### Batch 1: Detection Loop Foundation
**Priority:** 🔴 CRITICAL  
**Estimated Time:** 2-3 hours  
**Dependencies:** Phase 5 ✅, Phase 8 ✅

#### Task 1.1: Create MonsterDetector Class
**File:** `lib/vision/monster_detector.py` (new)  
**Lines:** ~200

**Requirements:**
- [ ] Class initialization with VisionEngine and ScreenCapture
- [ ] Detection loop thread management (start/stop/pause)
- [ ] Thread-safe state management
- [ ] Signal system for detection events

**Interface:**
```python
class MonsterDetector:
    def __init__(self, vision_engine: VisionEngine, 
                 screen_capture: ScreenCapture):
        """Initialize detector with vision components"""
        
    def start(self, detection_interval: float = 0.1):
        """Start detection loop in background thread"""
        
    def stop(self):
        """Stop detection loop gracefully"""
        
    def pause(self):
        """Pause detection temporarily"""
        
    def resume(self):
        """Resume paused detection"""
        
    def get_latest_detections(self) -> List[Detection]:
        """Thread-safe getter for latest detections"""
        
    # Callback system
    def on_monsters_detected(self, callback: Callable):
        """Register callback for detection events"""
```

**Testing:**
- Unit test: Thread lifecycle (start/stop/pause/resume)
- Unit test: Thread safety (concurrent access)
- Manual test: Run detector alone, check console logs

**Commit Message:**
```
feat(vision): Add MonsterDetector class with thread management

- Background detection loop at configurable interval
- Thread-safe state management with locks
- Signal/callback system for detection events
- Start/stop/pause/resume controls

Part of Sprint 23 Phase 7 Batch 1
```

---

#### Task 1.2: Add Detection State Machine
**File:** `lib/vision/monster_detector.py` (update)  
**Lines:** +100

**Requirements:**
- [ ] Define DetectionState enum (Searching, Detected, Tracking, Lost)
- [ ] Implement state transition logic
- [ ] State duration tracking
- [ ] State change callbacks

**State Machine:**
```
SEARCHING ──detections > 0──> DETECTED
    ↑                             │
    └──────timeout────────────────┘
    
DETECTED ──stable N frames──> TRACKING
    │
    └──detections == 0──> LOST ──timeout──> SEARCHING
```

**Testing:**
- Unit test: State transitions
- Unit test: Timeout handling
- Manual test: Force state changes, verify callbacks

**Commit Message:**
```
feat(vision): Add detection state machine to MonsterDetector

- DetectionState enum: Searching/Detected/Tracking/Lost
- State transition logic with timeout handling
- State change callbacks for UI updates

Part of Sprint 23 Phase 7 Batch 1
```

---

#### Task 1.3: Integrate Screen Capture
**File:** `lib/vision/monster_detector.py` (update)  
**Lines:** +80

**Requirements:**
- [ ] Capture game window region in detection loop
- [ ] Handle capture errors gracefully
- [ ] Skip frame if capture fails
- [ ] Performance logging (capture time)

**Implementation:**
```python
def _detection_loop(self):
    while self._running:
        try:
            # Capture game screen
            frame = self._screen_capture.capture_region(self._target_rect)
            if frame is None:
                continue
            
            # Run detection
            detections = self._vision_engine.match_templates(
                frame, 
                templates=self._monster_templates
            )
            
            # Update state
            self._update_detections(detections)
            
            time.sleep(self._detection_interval)
            
        except Exception as e:
            logging.error(f"Detection loop error: {e}")
```

**Testing:**
- Unit test: Capture error handling
- Manual test: Run with game window, verify captures
- Performance test: Measure capture time

**Commit Message:**
```
feat(vision): Integrate screen capture into detection loop

- Capture game region at configured interval
- Error handling for capture failures
- Performance logging for capture time

Part of Sprint 23 Phase 7 Batch 1
```

---

### Batch 2: Overlay Integration
**Priority:** 🔴 CRITICAL  
**Estimated Time:** 2-3 hours  
**Dependencies:** Batch 1 ✅

#### Task 2.1: Create OverlayController
**File:** `lib/ui/overlay_controller.py` (new)  
**Lines:** ~250

**Requirements:**
- [ ] Bridge between MonsterDetector and PyWin32Overlay
- [ ] Auto-convert Detection → DetectionBox
- [ ] State-based color mapping
- [ ] Update overlay on detection events

**Interface:**
```python
class OverlayController:
    def __init__(self, overlay: PyWin32Overlay, 
                 detector: MonsterDetector):
        """Initialize controller with overlay and detector"""
        
    def start(self):
        """Start listening to detection events"""
        
    def stop(self):
        """Stop listening to detection events"""
        
    def _on_detections_changed(self, detections: List[Detection]):
        """Handle detection updates from detector"""
        boxes = detections_to_boxes(detections, state=self._state)
        self.overlay.update_detections(boxes)
```

**Testing:**
- Unit test: Detection → Box conversion
- Manual test: Run with demo detections, verify boxes appear
- Integration test: Full pipeline (capture → detect → display)

**Commit Message:**
```
feat(ui): Add OverlayController for detection display

- Bridge between MonsterDetector and PyWin32Overlay
- Auto-convert Detection objects to DetectionBox
- State-based color mapping
- Event-driven updates

Part of Sprint 23 Phase 7 Batch 2
```

---

#### Task 2.2: Add FPS and Stats Display
**File:** `lib/ui/overlay_controller.py` (update)  
**Lines:** +100

**Requirements:**
- [ ] Display detection FPS
- [ ] Show number of detections
- [ ] Display current state
- [ ] Performance metrics overlay

**Display Format:**
```
┌─────────────────────────┐
│ Detection: 10 FPS       │
│ Monsters: 3 detected    │
│ State: TRACKING         │
│ Latency: 120ms          │
└─────────────────────────┘
```

**Testing:**
- Manual test: Verify stats update correctly
- Performance test: Stats overhead < 1ms

**Commit Message:**
```
feat(ui): Add detection stats display to overlay

- Show detection FPS and latency
- Display monster count and state
- Minimal performance overhead

Part of Sprint 23 Phase 7 Batch 2
```

---

#### Task 2.3: Handle Window State Changes
**File:** `lib/ui/overlay_controller.py` (update)  
**Lines:** +80

**Requirements:**
- [ ] Pause detection when window minimized
- [ ] Resume detection when window restored
- [ ] Update capture region on window resize
- [ ] Auto-hide overlay on minimize

**Implementation:**
```python
def _on_window_state_changed(self, state: str):
    if state == "minimized":
        self.detector.pause()
        self.overlay.hide()
    elif state == "normal":
        self.overlay.show()
        self.detector.resume()
```

**Testing:**
- Manual test: Minimize/restore window, verify detection pauses/resumes
- Manual test: Resize window, verify capture region updates

**Commit Message:**
```
feat(ui): Handle window state changes in OverlayController

- Pause detection on minimize
- Resume detection on restore
- Update capture region on resize

Part of Sprint 23 Phase 7 Batch 2
```

---

### Batch 3: App Integration
**Priority:** 🟡 HIGH  
**Estimated Time:** 2-3 hours  
**Dependencies:** Batch 2 ✅

#### Task 3.1: Add Detector to BotManager
**File:** `lib/system/bot_manager.py` (update)  
**Lines:** +150

**Requirements:**
- [ ] Initialize MonsterDetector in BotManager
- [ ] Start/stop detector with hunt loop
- [ ] Expose detector state to GUI
- [ ] Thread-safe access methods

**Changes:**
```python
class BotManager:
    def __init__(self):
        # ... existing init ...
        self.monster_detector = None
        
    def initialize_detector(self):
        """Initialize monster detector with vision components"""
        self.monster_detector = MonsterDetector(
            vision_engine=self.vision_engine,
            screen_capture=self.screen_capture
        )
        
    def start_hunt(self):
        """Start hunt loop with detection"""
        # ... existing start logic ...
        if self.monster_detector:
            self.monster_detector.start(detection_interval=0.1)
            
    def stop_hunt(self):
        """Stop hunt loop and detection"""
        if self.monster_detector:
            self.monster_detector.stop()
        # ... existing stop logic ...
```

**Testing:**
- Unit test: Detector initialization
- Integration test: Start/stop hunt with detection
- Manual test: Run hunt loop, verify detection works

**Commit Message:**
```
feat(system): Integrate MonsterDetector into BotManager

- Initialize detector with vision components
- Start/stop detector with hunt loop
- Expose detector state to GUI

Part of Sprint 23 Phase 7 Batch 3
```

---

#### Task 3.2: Connect Overlay to Detector
**File:** `app_gui.py` (update)  
**Lines:** +100

**Requirements:**
- [ ] Create OverlayController when overlay enabled
- [ ] Connect controller to detector
- [ ] Handle overlay toggle with detection active
- [ ] Cleanup on app shutdown

**Changes:**
```python
def _toggle_overlay(self):
    # ... existing overlay creation ...
    
    # Create controller if detector available
    if self.bot_manager.monster_detector:
        self._overlay_controller = OverlayController(
            overlay=self._overlay_window,
            detector=self.bot_manager.monster_detector
        )
        self._overlay_controller.start()
```

**Testing:**
- Manual test: Toggle overlay during hunt, verify detections appear
- Manual test: Stop hunt, verify detection stops
- Manual test: Close app, verify cleanup

**Commit Message:**
```
feat(gui): Connect overlay to monster detector

- Create OverlayController when overlay enabled
- Connect controller to MonsterDetector
- Handle cleanup on app shutdown

Part of Sprint 23 Phase 7 Batch 3
```

---

#### Task 3.3: Add Configuration Options
**File:** `config/bot_config.json` (update)  
**Lines:** +20

**Requirements:**
- [ ] Detection interval setting
- [ ] Enable/disable detection
- [ ] Detection confidence threshold
- [ ] Max detections to display

**Config Schema:**
```json
{
  "vision": {
    "detection": {
      "enabled": true,
      "interval_ms": 100,
      "confidence_threshold": 0.7,
      "max_display": 20,
      "state_timeout_ms": 3000
    }
  }
}
```

**Testing:**
- Manual test: Change config values, verify applied
- Unit test: Config validation

**Commit Message:**
```
feat(config): Add monster detection configuration options

- Detection interval and confidence threshold
- Enable/disable detection
- Max detections display limit

Part of Sprint 23 Phase 7 Batch 3
```

---

### Batch 4: Testing & Polish
**Priority:** 🟢 MEDIUM  
**Estimated Time:** 2-3 hours  
**Dependencies:** Batch 3 ✅

#### Task 4.1: Create Integration Tests
**File:** `tests/integration/test_monster_tracking.py` (new)  
**Lines:** ~300

**Test Coverage:**
- [ ] Full pipeline: capture → detect → display
- [ ] State transitions with real detections
- [ ] Window state changes (minimize/restore)
- [ ] Performance under load
- [ ] Error recovery

**Commit Message:**
```
test(integration): Add monster tracking integration tests

- Full detection pipeline tests
- State machine validation
- Performance benchmarks

Part of Sprint 23 Phase 7 Batch 4
```

---

#### Task 4.2: Create Demo Script
**File:** `tests/demos/demo_monster_tracking.py` (new)  
**Lines:** ~200

**Requirements:**
- [ ] Standalone demo with real detection
- [ ] Load monster templates
- [ ] Run detection loop
- [ ] Display results in overlay

**Commit Message:**
```
demo: Add monster tracking integration demo

- Demonstrates full detection pipeline
- Uses real monster templates
- Interactive overlay display

Part of Sprint 23 Phase 7 Batch 4
```

---

#### Task 4.3: Update Documentation
**Files:**
- `docs/sprints/sprint23/PHASE7_COMPLETION_SUMMARY.md` (new)
- `lib/vision/README.md` (update)
- `lib/ui/README.md` (update)

**Requirements:**
- [ ] Implementation summary
- [ ] API documentation
- [ ] Usage examples
- [ ] Performance metrics

**Commit Message:**
```
docs: Complete Phase 7 monster tracking documentation

- Implementation summary with metrics
- API reference for new components
- Usage examples and best practices

Part of Sprint 23 Phase 7 Batch 4
```

---

## 📊 Progress Tracking

### Batch Status

| Batch | Tasks | Status | Progress | Est. Time |
|-------|-------|--------|----------|-----------|
| Batch 1: Detection Loop | 3 | 🔲 Not Started | 0/3 | 2-3h |
| Batch 2: Overlay Integration | 3 | 🔲 Not Started | 0/3 | 2-3h |
| Batch 3: App Integration | 3 | 🔲 Not Started | 0/3 | 2-3h |
| Batch 4: Testing & Polish | 3 | 🔲 Not Started | 0/3 | 2-3h |
| **TOTAL** | **12** | **🔲** | **0/12** | **8-12h** |

### Current Focus
🎯 **Batch 1, Task 1.1:** Create MonsterDetector Class

---

## 🚀 Getting Started

### Prerequisites
- ✅ Phase 5 complete (Overlay System)
- ✅ Phase 8 complete (Screen Capture)
- ✅ VisionEngine functional
- ✅ Monster templates available

### Quick Start

```bash
# 1. Start with Batch 1, Task 1.1
# Create lib/vision/monster_detector.py

# 2. Run tests after each task
pytest tests/unit/vision/test_monster_detector.py -v

# 3. Commit after each task completes
git add lib/vision/monster_detector.py
git commit -m "feat(vision): Add MonsterDetector class with thread management"

# 4. Move to next task
```

---

## 📝 Notes

### Design Decisions

1. **Detection Interval: 100ms**
   - Balances responsiveness vs CPU usage
   - 10 FPS detection sufficient for monster tracking
   - Can adjust per user preference

2. **Separate Controller Pattern**
   - Decouples detection logic from overlay rendering
   - Easier to test independently
   - Can swap implementations easily

3. **Thread Safety First**
   - All state access protected by locks
   - Event-driven updates prevent polling
   - Graceful shutdown important

### Potential Issues

1. **Detection Lag:**
   - Solution: Optimize template matching
   - Solution: Reduce detection interval if needed

2. **Memory Leaks:**
   - Solution: Proper cleanup in all stop() methods
   - Solution: Weak references for callbacks

3. **Race Conditions:**
   - Solution: Lock all shared state access
   - Solution: Use thread-safe queues for events

---

## ✅ Completion Checklist

### Batch 1: Detection Loop Foundation
- [ ] Task 1.1: MonsterDetector class created
- [ ] Task 1.2: State machine implemented
- [ ] Task 1.3: Screen capture integrated
- [ ] All tests passing
- [ ] Batch 1 committed

### Batch 2: Overlay Integration
- [ ] Task 2.1: OverlayController created
- [ ] Task 2.2: Stats display added
- [ ] Task 2.3: Window state handling
- [ ] All tests passing
- [ ] Batch 2 committed

### Batch 3: App Integration
- [ ] Task 3.1: Detector in BotManager
- [ ] Task 3.2: Overlay connected
- [ ] Task 3.3: Config options added
- [ ] All tests passing
- [ ] Batch 3 committed

### Batch 4: Testing & Polish
- [ ] Task 4.1: Integration tests
- [ ] Task 4.2: Demo script
- [ ] Task 4.3: Documentation
- [ ] All tests passing
- [ ] Batch 4 committed

### Final Validation
- [ ] Full pipeline working end-to-end
- [ ] Performance targets met
- [ ] No memory leaks
- [ ] Documentation complete
- [ ] Phase 7 COMPLETE ✅

---

**Created by:** GitHub Copilot  
**Date:** October 24, 2025  
**Ready to start:** Batch 1, Task 1.1
