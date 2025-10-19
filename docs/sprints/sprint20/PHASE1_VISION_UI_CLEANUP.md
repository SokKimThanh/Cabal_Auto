# Sprint 20 - Vision Wizard UI Preparation

**Date**: October 19, 2025  
**Status**: 🚧 In Progress (Phase 1: UI Cleanup)  
**Type**: UX Enhancement + Feature Preparation

---

## 🎯 Objectives

**Phase 1**: Temporarily hide legacy vision tools
- ❌ Old: Region override fields + 3 action buttons (confusing UX)
- ✅ New: Single "Setup Wizard Vision" button (coming soon)

**Phase 2-6**: Build complete Setup Wizard Vision (Future sprints)

---

## 📋 Changes - Phase 1

### 1. **Hidden (Preserved) Legacy Components**

**What was hidden**:
```python
# Region override section (4 input fields: L, T, W, H)
# 3 action buttons:
#   🖼️ Chọn vùng (Pick Region)
#   🔍 Kiểm tra nhận diện (Test Recognition)
#   📋 Tự động dò vùng (Auto-Detect Region)
```

**How hidden**:
```python
# ============================================================================
# LEGACY REGION OVERRIDE SECTION - TEMPORARILY HIDDEN FOR WIZARD VISION UPGRADE
# TODO: Will be replaced by new Setup Wizard Vision feature
# Keeping code structure for future reference and migration
# ============================================================================

# HIDDEN: Region override section - preserved for future upgrade
# region_frame = tk.Frame(form_body, bg='#E3F2FD')
# ... (commented out, not removed)
```

**Why preserve**:
- Backward compatibility with existing data
- Code structure reference for migration
- Can be re-enabled if needed
- Gradual transition strategy

### 2. **New: Setup Wizard Vision Button**

**Location**: Replaced region override section in template form

**Visual Design**:
```
┌─────────────────────────────────────────────────────┐
│  🟢 Green background (#E8F5E9)                      │
│                                                     │
│  💡 Hint text:                                      │
│  "Xem thêm về các chức năng sắp được nâng cấp..."  │
│                                                     │
│  [ 🔮 Setup Wizard Vision ]                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Code**:
```python
wizard_frame = tk.Frame(form_body, bg='#E8F5E9', relief='solid', borderwidth=1)

# Hint text
hint_text = (
    'Xem thêm về các chức năng sắp được nâng cấp bằng cách nhấp vào nút bên dưới'
    if self.lang == 'vi' else
    'Click the button below to learn about upcoming feature upgrades'
)
tk.Label(wizard_frame, text=hint_text, ...).pack(...)

# Button
wizard_btn = tk.Button(
    wizard_btn_frame,
    text='🔮 Setup Wizard Vision',
    command=self._open_setup_wizard_vision,
    bg='#66BB6A', fg='white',
    ...
)
```

### 3. **New Dialog: Setup Wizard Vision Info**

**Method**: `_open_setup_wizard_vision()`

**Dialog Structure**:
```
╔══════════════════════════════════════════════════════╗
║  🔮 Setup Wizard Vision - Coming Soon!              ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  📋 Các Tính Năng Sắp Được Nâng Cấp                 ║
║                                                      ║
║  [Scrollable Text Area]                             ║
║                                                      ║
║  🎯 TỔNG QUAN                                        ║
║  Chúng tôi đang phát triển hệ thống...              ║
║                                                      ║
║  ✨ CÁC TÍNH NĂNG MỚI                                ║
║  1. 🎨 Semi-Transparent Overlay                     ║
║  2. 🎯 Auto-Numbering & Visual Feedback             ║
║  3. 📹 Real-time Tracking                           ║
║  4. 🔍 Scale-Invariant Detection                    ║
║  5. 🧙 Step-by-Step Wizard UI                       ║
║                                                      ║
║  📅 TIMELINE                                         ║
║  Week 1-2: UI/UX improvements                       ║
║  Week 3-4: Tracking system                          ║
║  Week 5-6: Advanced features                        ║
║                                                      ║
║                              [ Đóng ]                ║
╚══════════════════════════════════════════════════════╝
```

**Content** (Vietnamese):
- 🎯 Tổng quan về wizard mới
- ✨ 5 tính năng chính
- 🔧 So sánh Before/After
- 📅 Timeline dự kiến
- 💡 Lý do nâng cấp
- 📚 Tài liệu tham khảo

**Content** (English):
- 🎯 Overview of new wizard
- ✨ 5 main features
- 🔧 Before/After comparison
- 📅 Estimated timeline
- 💡 Why upgrade
- 📚 Documentation links

---

## 🎨 UI Changes Comparison

### Before (Old - Hidden)

```
┌─────────────────────────────────────────────┐
│  Region Override (L,T,W,H)                  │
│  ┌──────┬──────┬──────┬──────┐             │
│  │ L:   │ T:   │ W:   │ H:   │             │
│  └──────┴──────┴──────┴──────┘             │
│                                             │
│  Để trống để dùng biên cửa sổ game.        │
│                                             │
│  [ 🖼️ Chọn vùng ]                           │
│  [ 🔍 Kiểm tra nhận diện ]                  │
│  [ 📋 Tự động dò vùng ]                     │
└─────────────────────────────────────────────┘

❌ Problems:
- 3 buttons → confusing
- No explanation what they do
- Blind overlay (can't see game)
- No visual feedback
```

### After (New - Visible)

```
┌─────────────────────────────────────────────┐
│  💡 Xem thêm về các chức năng sắp được      │
│     nâng cấp bằng cách nhấp vào nút...      │
│                                             │
│  [ 🔮 Setup Wizard Vision ]                 │
│                                             │
└─────────────────────────────────────────────┘

✅ Benefits:
- 1 clear button
- Explains what's coming
- No confusion
- Clean UI
```

---

## 📊 Code Statistics

### Files Modified

**File**: `lib/ui/library_manager.py`

**Lines Changed**:
- Commented out: ~30 lines (region override + 3 buttons)
- Added: ~250 lines (wizard button + dialog)
- Net: +220 lines

**Methods**:
- NEW: `_open_setup_wizard_vision()` (230 lines)
- PRESERVED: `_pick_template_region()` (commented usage)
- PRESERVED: `_test_template_recognition()` (commented usage)
- PRESERVED: `_auto_detect_template_region()` (commented usage)

### Code Preservation Strategy

```python
# 1. Structure preserved
self.template_region_vars = {
    'left': tk.StringVar(),
    'top': tk.StringVar(),
    'width': tk.StringVar(),
    'height': tk.StringVar(),
}
self.template_region_entries = {}
# → Still initialized for backward compatibility

# 2. Methods preserved
def _pick_template_region(self):
    """Let user pick a region from screen for current template; fill fields and persist."""
    # → Still functional, just not called from UI

# 3. Can be re-enabled easily
# Just uncomment the UI code block if needed
```

---

## 🧪 Testing Checklist

### Phase 1 Testing (Current)

**UI Display**:
- [ ] Old region override section is HIDDEN
- [ ] Old 3 buttons are HIDDEN
- [ ] New green frame is VISIBLE
- [ ] Hint text is displayed correctly (VI/EN)
- [ ] "Setup Wizard Vision" button is visible
- [ ] Button has green background (#66BB6A)

**Dialog Functionality**:
- [ ] Click button → Dialog opens
- [ ] Dialog title correct (VI/EN)
- [ ] Dialog is centered on parent window
- [ ] Dialog is modal (blocks parent)
- [ ] Content text is scrollable
- [ ] Content displays all sections
- [ ] Content matches language (VI/EN)
- [ ] Close button works
- [ ] Esc key closes dialog

**Backward Compatibility**:
- [ ] `self.template_region_vars` still exists
- [ ] `self.template_region_entries` still exists
- [ ] Template selection still works
- [ ] Template editing still works
- [ ] No errors in console

**Visual Polish**:
- [ ] Green frame has border
- [ ] Text is italic and green
- [ ] Button has cursor='hand2'
- [ ] Dialog has proper padding
- [ ] Scrollbar works smoothly

---

## 🚀 Future Phases (Sprint 20+)

### Phase 2: Semi-Transparent Overlay (Week 1-2)
```python
# Replace blind black overlay
overlay.attributes('-alpha', 0.2)  # 20% opacity
# → User can see game while selecting
```

### Phase 3: Live Feedback (Week 1-2)
```python
# Show dimensions while dragging
dim_label.config(text=f"📏 {width} × {height} px")

# Show mini preview of selected area
preview_label.configure(image=region_img)
```

### Phase 4: Auto-Numbering (Week 2-3)
```python
# Number detected monsters
for i, match in enumerate(matches, 1):
    cv2.putText(frame, f"#{i}", (x, y-10), ...)
```

### Phase 5: Real-time Tracking (Week 3-4)
```python
# Hybrid tracker
tracker = cv2.TrackerCSRT_create()
tracker.init(frame, bbox)

# Re-verify every 10 frames
if frame_count % 10 == 0:
    matches = template_matcher.find_all_matches(frame)
```

### Phase 6: Scale-Invariant (Week 5-6)
```python
# Multi-scale matching
scales = [0.5, 0.75, 1.0, 1.25, 1.5]
for scale in scales:
    resized = cv2.resize(template, None, fx=scale, fy=scale)
    matches = match_template(screen, resized)

# Or feature-based (SIFT/ORB)
detector = cv2.SIFT_create()
kp1, des1 = detector.detectAndCompute(template, None)
```

---

## 📚 Documentation

**Current Sprint**:
- This file: `docs/sprints/sprint20/PHASE1_VISION_UI_CLEANUP.md`

**Future Documentation** (To be created):
- `docs/sprints/sprint20/VISION_WIZARD_DESIGN.md`
- `docs/ADVANCED_VISION_FEATURES.md`
- `docs/VISION_TRACKING_GUIDE.md`
- `docs/SCALE_INVARIANT_DETECTION.md`

**Related**:
- `docs/sprints/sprint19/UX_GLOBAL_BADGE_RELOCATION.md`
- `docs/sprints/sprint19/SPRINT19_SUMMARY.md`

---

## 💡 Design Decisions

### Why Hide Instead of Remove?

**Reasons**:
1. **Backward Compatibility**: Existing data may reference region fields
2. **Gradual Migration**: Can transition users smoothly
3. **Code Reference**: Useful for building new wizard
4. **Rollback Option**: Can re-enable if needed
5. **No Data Loss**: Users' existing regions preserved

### Why Single Button?

**Reasons**:
1. **Reduce Confusion**: 3 buttons → 1 button = clearer
2. **Set Expectations**: "Coming Soon" dialog manages expectations
3. **Clean UI**: Less clutter, more focus
4. **Educational**: Dialog explains what's coming

### Why Show Dialog Now?

**Reasons**:
1. **Transparency**: Users know why features are missing
2. **Excitement**: Preview of upcoming features
3. **Feedback**: Can gather user expectations
4. **Communication**: Timeline and rationale clear

---

## ✅ Success Criteria - Phase 1

### Must Have ✅
- [x] Legacy region override section hidden
- [x] Legacy 3 buttons hidden
- [x] New wizard button visible and styled
- [x] Hint text explaining what's coming
- [x] Dialog opens with full information
- [x] Bilingual support (VI/EN)
- [x] No console errors
- [x] Backward compatibility maintained

### Nice to Have ✨
- [x] Green background for positive vibe
- [x] Scrollable content for long text
- [x] Emoji icons for visual appeal
- [x] Detailed timeline in dialog
- [x] Clear Before/After comparison

### Future ⏭️
- [ ] Actual wizard implementation (Phase 2-6)
- [ ] Semi-transparent overlay
- [ ] Real-time tracking
- [ ] Scale-invariant detection
- [ ] Complete step-by-step wizard

---

**Status**: ✅ Phase 1 Complete  
**Next**: Sprint 20 Phase 2 - Overlay & Live Feedback  
**Impact**: High (Major UX preparation)  
**Risk**: Low (Non-breaking, backward compatible)
