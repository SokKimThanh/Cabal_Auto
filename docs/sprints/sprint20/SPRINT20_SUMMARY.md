# Sprint 20 - Setup Wizard Vision

**Start Date**: October 19, 2025  
**Status**: 🚧 In Progress  
**Current Phase**: Phase 1 Complete ✅

---

## 🎯 Sprint Goal

Chuẩn bị và triển khai hệ thống **Setup Wizard Vision** hoàn toàn mới để thay thế các công cụ vision cũ (Chọn vùng, Kiểm tra nhận diện, Tự động dò vùng).

---

## 📋 Sprint Phases

### ✅ Phase 1: UI Cleanup (DONE)
**Duration**: 1 day  
**Status**: ✅ Complete

**Objectives**:
- Hide legacy region override section
- Hide 3 old action buttons
- Add "Setup Wizard Vision" button
- Create information dialog

**Deliverables**:
- [x] Legacy components hidden (preserved in code)
- [x] New green wizard button visible
- [x] Hint text explaining upcoming features
- [x] Dialog with detailed information (VI/EN)
- [x] Backward compatibility maintained

**Documentation**:
- `docs/sprints/sprint20/PHASE1_VISION_UI_CLEANUP.md`
- `tests/demo_vision_wizard_cleanup.py`

---

### 🚧 Phase 2: Semi-Transparent Overlay (PLANNED)
**Duration**: 2-3 days  
**Status**: 📝 Planned

**Objectives**:
- Replace opaque black overlay with semi-transparent
- User can see game while selecting region
- Live dimension display while dragging
- Mini preview of selected area

**Features**:
```python
# Semi-transparent overlay
overlay.attributes('-alpha', 0.2)  # 20% opacity

# Live dimension display
dim_label.config(text=f"📏 {width} × {height} px")

# Mini preview
preview_label.configure(image=region_img)
```

**Benefits**:
- ✅ No more "blind" selection
- ✅ Real-time feedback
- ✅ Better UX

---

### 📅 Phase 3: Live Feedback & Validation (PLANNED)
**Duration**: 2-3 days  
**Status**: 📝 Planned

**Objectives**:
- Show what's being selected in real-time
- Validate selection (min/max size)
- Visual guides and snap-to-grid
- Instant preview of detection

**Features**:
```python
# Validation
if width < 50 or height < 50:
    show_warning("Region too small!")

# Snap to grid
if snap_enabled:
    x = round(x / grid_size) * grid_size

# Detection preview
matches = matcher.find(selected_region)
show_preview(matches)
```

---

### 📅 Phase 4: Auto-Numbering & Bounding Boxes (PLANNED)
**Duration**: 2-3 days  
**Status**: 📝 Planned

**Objectives**:
- Automatically number detected objects
- Draw bounding boxes with confidence
- Color coding for different states
- Interactive selection

**Features**:
```python
# Auto-numbering
for i, match in enumerate(matches, 1):
    cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
    cv2.putText(frame, f"#{i}", (x,y-10), ...)
    cv2.putText(frame, f"{confidence:.0%}", (x,y+h+20), ...)

# Color coding
colors = {
    'high': (0, 255, 0),    # Green: >90%
    'medium': (0, 255, 255), # Yellow: 80-90%
    'low': (0, 0, 255)       # Red: <80%
}
```

---

### 📅 Phase 5: Real-time Tracking (PLANNED)
**Duration**: 3-5 days  
**Status**: 📝 Planned

**Objectives**:
- Track monster movement in real-time
- Hybrid tracking (OpenCV + Template Matching)
- Periodic re-verification
- Lost track recovery

**Features**:
```python
# Hybrid tracker
class SmartTracker:
    def __init__(self):
        self.tracker = cv2.TrackerCSRT_create()
        self.frames_since_verify = 0
    
    def track(self, frame):
        # Track with OpenCV
        success, bbox = self.tracker.update(frame)
        self.frames_since_verify += 1
        
        # Re-verify every 10 frames
        if self.frames_since_verify >= 10:
            matches = template_match(frame)
            if matches:
                self.tracker = reinit(matches[0])
                self.frames_since_verify = 0
        
        return bbox if success else None
```

---

### 📅 Phase 6: Scale-Invariant Detection (PLANNED)
**Duration**: 3-5 days  
**Status**: 📝 Planned

**Objectives**:
- Handle camera zoom in/out
- Multi-scale template matching
- Feature-based matching (SIFT/ORB)
- Auto-calibration

**Features**:
```python
# Multi-scale matching
def find_with_zoom(screen, template):
    scales = [0.5, 0.75, 1.0, 1.25, 1.5]
    best_matches = []
    
    for scale in scales:
        resized = cv2.resize(template, None, fx=scale, fy=scale)
        matches = match_template(screen, resized)
        best_matches.extend(matches)
    
    return remove_duplicates(best_matches)

# Feature-based (robust)
detector = cv2.SIFT_create()
kp1, des1 = detector.detectAndCompute(template, None)
kp2, des2 = detector.detectAndCompute(screen, None)
matches = bf_matcher.knnMatch(des1, des2, k=2)
```

---

## 📊 Progress Tracker

### Overall Sprint Progress

```
Phase 1: UI Cleanup               ████████████████████ 100% ✅
Phase 2: Overlay                  ░░░░░░░░░░░░░░░░░░░░   0% 📝
Phase 3: Feedback                 ░░░░░░░░░░░░░░░░░░░░   0% 📝
Phase 4: Auto-Number              ░░░░░░░░░░░░░░░░░░░░   0% 📝
Phase 5: Tracking                 ░░░░░░░░░░░░░░░░░░░░   0% 📝
Phase 6: Scale-Invariant          ░░░░░░░░░░░░░░░░░░░░   0% 📝

Total Sprint:                     ███░░░░░░░░░░░░░░░░░  17% 🚧
```

### Timeline

| Phase | Start | End | Duration | Status |
|-------|-------|-----|----------|--------|
| 1 | Oct 19 | Oct 19 | 1 day | ✅ Done |
| 2 | Oct 20 | Oct 22 | 2-3 days | 📝 Planned |
| 3 | Oct 23 | Oct 25 | 2-3 days | 📝 Planned |
| 4 | Oct 26 | Oct 28 | 2-3 days | 📝 Planned |
| 5 | Oct 29 | Nov 2 | 3-5 days | 📝 Planned |
| 6 | Nov 3 | Nov 7 | 3-5 days | 📝 Planned |

**Estimated Completion**: November 7, 2025

---

## 🎨 Before & After

### Before (Phase 0 - Old System)

```
┌─────────────────────────────────────────────┐
│  Region Override (L,T,W,H)                  │
│  [ L:    ] [ T:    ] [ W:    ] [ H:    ]    │
│                                             │
│  [ 🖼️ Chọn vùng ]                           │
│  [ 🔍 Kiểm tra nhận diện ]                  │
│  [ 📋 Tự động dò vùng ]                     │
└─────────────────────────────────────────────┘

Problems:
❌ 3 confusing buttons
❌ No explanation
❌ Blind overlay (black)
❌ No visual feedback
❌ No tracking
❌ No zoom handling
```

### After Phase 1 (Current)

```
┌─────────────────────────────────────────────┐
│  💡 Xem thêm về các chức năng sắp được      │
│     nâng cấp...                             │
│                                             │
│  [ 🔮 Setup Wizard Vision ]                 │
└─────────────────────────────────────────────┘

Improvements:
✅ 1 clear button
✅ Explains what's coming
✅ Clean UI
✅ Backward compatible
```

### After Phase 6 (Target - November 2025)

```
┌─────────────────────────────────────────────┐
│  🧙 Setup Wizard Vision                     │
│                                             │
│  Step 1/4: Select Game Window               │
│  [Preview of game]                          │
│                                             │
│  Step 2/4: Draw Hunting Area                │
│  [Semi-transparent overlay with live dims]  │
│                                             │
│  Step 3/4: Test Detection                   │
│  [Auto-numbered boxes: #1, #2, #3...]      │
│                                             │
│  Step 4/4: Live Tracking                    │
│  [Real-time tracking with zoom handling]    │
│                                             │
│  [ ← Back ]  [ Next → ]  [ ✅ Finish ]      │
└─────────────────────────────────────────────┘

Features:
✅ Semi-transparent overlay
✅ Live feedback
✅ Auto-numbering
✅ Real-time tracking
✅ Zoom handling
✅ Step-by-step wizard
```

---

## 📚 Documentation

### Phase 1
- **Detail**: `docs/sprints/sprint20/PHASE1_VISION_UI_CLEANUP.md`
- **Test**: `tests/demo_vision_wizard_cleanup.py`

### Future Phases (To be created)
- `docs/sprints/sprint20/PHASE2_OVERLAY.md`
- `docs/sprints/sprint20/PHASE3_FEEDBACK.md`
- `docs/sprints/sprint20/PHASE4_AUTO_NUMBER.md`
- `docs/sprints/sprint20/PHASE5_TRACKING.md`
- `docs/sprints/sprint20/PHASE6_SCALE_INVARIANT.md`

### Technical Guides
- `docs/VISION_WIZARD_DESIGN.md` (Architecture)
- `docs/ADVANCED_VISION_FEATURES.md` (Features)
- `docs/VISION_TRACKING_GUIDE.md` (Tracking)
- `docs/SCALE_INVARIANT_DETECTION.md` (Zoom)

---

## 🔧 Technical Stack

### Libraries
- **OpenCV 4.x**: Computer vision, tracking, feature detection
- **Pillow (PIL)**: Image processing, thumbnails
- **NumPy**: Array operations, transformations
- **Tkinter**: GUI framework

### OpenCV Features Used
- Template Matching: `cv2.matchTemplate()`
- Trackers: `cv2.TrackerCSRT_create()`, `TrackerKCF`
- Feature Detection: `cv2.SIFT_create()`, `cv2.ORB_create()`
- Homography: `cv2.findHomography()`
- Drawing: `cv2.rectangle()`, `cv2.putText()`

---

## ✅ Success Criteria

### Phase 1 (Current) ✅
- [x] Legacy components hidden
- [x] New button visible
- [x] Dialog functional
- [x] Backward compatible
- [x] No errors

### Overall Sprint (Target)
- [ ] All 6 phases complete
- [ ] Wizard fully functional
- [ ] Detection accuracy >85%
- [ ] Tracking FPS >10
- [ ] Zoom handling working
- [ ] User-friendly UX
- [ ] Comprehensive docs
- [ ] All tests passing

---

## 🎓 Lessons Learned (So Far)

### Phase 1 Insights
1. **Preserve, Don't Remove**: Commenting out code better than deleting for backward compatibility
2. **Clear Communication**: Dialog explaining "why" reduces user confusion
3. **Visual Cues**: Green color + hint text sets positive expectations
4. **Bilingual Support**: Essential for Vietnamese users

### Challenges Ahead
1. **Semi-transparent overlay**: Need to handle Tkinter alpha on Windows
2. **Real-time tracking**: Balance between accuracy and performance
3. **Scale-invariant**: Multi-scale vs feature-based trade-offs
4. **UX complexity**: Making wizard simple despite advanced features

---

## 🚀 Next Steps

### Immediate (Next Session)
1. Start Phase 2: Semi-transparent overlay implementation
2. Research Tkinter alpha transparency options
3. Design overlay UI mockups
4. Test overlay performance

### Short-term (This Week)
1. Complete Phase 2-3 (Overlay + Feedback)
2. Begin Phase 4 (Auto-numbering)
3. Create technical documentation
4. User testing feedback

### Long-term (Next 2 Weeks)
1. Complete Phase 5-6 (Tracking + Zoom)
2. Integration testing
3. Performance optimization
4. User guide creation
5. Release wizard v1.0

---

**Status**: ✅ Phase 1 Complete, Ready for Phase 2  
**Overall Progress**: 17% (1/6 phases done)  
**Next Milestone**: Semi-Transparent Overlay (Phase 2)
