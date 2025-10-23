# Sprint 23 - Vision Advanced Features

**Branch:** `feature/S23-vision-advanced`  
**Start Date:** October 23, 2025  
**Duration:** 2-3 weeks  
**Status:** 🚀 IN PROGRESS  
**Priority:** HIGH - Critical Path

---

## 🎯 Sprint Goal

Complete the Vision System with critical advanced features to enable real-time monster detection and hunting automation.

**Focus Areas:**
- Phase 5: Overlay System
- Phase 7: Monster Tracking Integration  
- Phase 8: Screen Capture System

---

## 📋 Sprint Overview

Building upon Sprint 22's core vision engine, Sprint 23 implements the **critical path features** needed for production use:

1. **Real-time overlay** to visualize detections
2. **Screen capture** for continuous monitoring
3. **Monster tracking** integration with hunt loop

**Dependencies:**
- ✅ Sprint 22 Complete (Vision Engine, Worker Threads, UI)
- ✅ Tests passing (29/30)
- ✅ Documentation complete

---

## 🔥 Critical Path - Phases 5, 7, 8

### Phase 5: Overlay System (Week 1) 🔴 HIGH PRIORITY

**Goal:** Display detection results in real-time on game window

**Features:**
1. **Overlay Toggle** (`Ctrl+Shift+O`)
   - Show/hide overlay
   - Menu item integration
   - Hotkey registration

2. **Detection Box Drawing**
   - Draw bounding boxes on detected monsters
   - Color-coded (green=detected, red=searching)
   - Semi-transparent overlay (alpha blending)
   - Real-time position updates

3. **Preview Canvas Enhancement**
   - Display template preview in Vision Wizard
   - Show detection results
   - PIL.Image integration

**Implementation Tasks:**
- [ ] Create overlay window (transparent, topmost, click-through)
- [ ] Implement detection box drawing
- [ ] Add color coding system
- [ ] Integrate toggle hotkey
- [ ] Update preview canvas with PIL
- [ ] Add real-time position updates (15 FPS)

**Files to Modify:**
- `ui/setup_wizard_vision.py` - Add overlay methods
- `lib/vision/vision_engine.py` - Add overlay data structures
- `app_gui.py` - Integrate overlay hotkey
- `lib/i18n/translations.py` - Add overlay translations

**Testing:**
- [ ] Overlay shows/hides correctly
- [ ] Detection boxes positioned accurately
- [ ] Colors change based on state
- [ ] Performance: 15+ FPS with overlay
- [ ] Hotkey works globally

**Estimated Time:** 3-4 days

---

### Phase 7: Monster Tracking Integration (Week 2) 🔴 HIGH PRIORITY

**Goal:** Integrate vision detection with hunt loop for automated targeting

**Features:**
1. **Start/Stop Tracking**
   - UI buttons in Vision Wizard
   - Start tracking thread
   - Stop and cleanup gracefully

2. **Real-time Monster Detection**
   - Continuous detection loop (100ms interval)
   - Update overlay with current detection
   - Send signals to hunt system

3. **Hunt Loop Integration**
   - Check vision detection in hunt loop
   - Execute skills on detected target
   - Handle lost target scenarios

**Implementation Tasks:**
- [ ] Create tracking control methods
- [ ] Implement detection loop thread
- [ ] Add signal/event system for hunt communication
- [ ] Integrate with `ui/auto_hunt.py` hunt loop
- [ ] Handle target acquisition/loss
- [ ] Add tracking status indicators

**Files to Modify:**
- `ui/setup_wizard_vision.py` - Add tracking controls
- `lib/vision/vision_engine.py` - Add tracking thread
- `ui/auto_hunt.py` - Integrate vision detection
- `app_gui.py` - Add tracking UI elements

**New Files:**
- `lib/vision/tracking_manager.py` - Tracking coordination

**Testing:**
- [ ] Tracking starts/stops cleanly
- [ ] Detection results update correctly
- [ ] Hunt loop receives detection signals
- [ ] Skills execute on detected targets
- [ ] Handles no-detection gracefully

**Estimated Time:** 3-4 days

---

### Phase 8: Screen Capture System (Week 1-2) 🔴 HIGH PRIORITY

**Goal:** Implement efficient screen capture for vision processing

**Features:**
1. **Screen Capture Module**
   - Windows API (win32gui/win32ui) or MSS
   - Capture specific region (ROI)
   - Optimized for 15 FPS
   - Memory efficient

2. **Cabal Window Detection**
   - Auto-detect Cabal window
   - Get window position & size
   - Handle window movement
   - Handle minimize/maximize

3. **Frame Queue Management**
   - Capture → Queue → Process pipeline
   - Handle queue overflow (skip frames)
   - Memory management
   - Thread-safe operations

**Implementation Tasks:**
- [ ] Create screen_capture.py module
- [ ] Implement window detection
- [ ] Add capture methods (full/region)
- [ ] Integrate with worker thread
- [ ] Add frame queue management
- [ ] Optimize for performance (15+ FPS)
- [ ] Handle edge cases (window moved, minimized)

**Files to Create:**
- `lib/system/screen_capture.py` - Screen capture module
- `lib/system/window_manager.py` - Window detection/management

**Files to Modify:**
- `lib/vision/vision_engine.py` - Integrate screen capture
- Worker thread - Use captured frames

**Testing:**
- [ ] Captures at 15+ FPS
- [ ] Handles window movement
- [ ] Queue doesn't overflow
- [ ] Memory usage stable
- [ ] Works with minimized window

**Estimated Time:** 2-3 days

---

## 📊 Sprint Timeline

### Week 1: Foundation (Phase 5 + Phase 8 Start)
**Days 1-2:** Phase 5 - Overlay System
- Overlay window creation
- Detection box drawing
- Color coding

**Days 3-4:** Phase 5 Completion
- Preview canvas enhancement
- Hotkey integration
- Testing

**Day 5:** Phase 8 Start - Screen Capture
- Create screen_capture.py
- Window detection

### Week 2: Integration (Phase 8 + Phase 7)
**Days 1-2:** Phase 8 Completion
- Frame queue management
- Performance optimization
- Integration with worker thread

**Days 3-4:** Phase 7 - Monster Tracking
- Tracking control methods
- Detection loop thread
- Hunt loop integration

**Day 5:** Testing & Polish
- Integration testing
- Bug fixes
- Performance tuning

### Week 3: Testing & Documentation (Optional)
**Days 1-2:** Comprehensive Testing
- End-to-end testing
- Edge case handling
- Performance validation

**Days 3-4:** Documentation
- Update architecture docs
- Add user guides
- Code documentation

**Day 5:** Sprint Review
- Demo preparation
- Sprint retrospective
- Plan Sprint 24

---

## 🎯 Success Criteria

### Phase 5: Overlay System ✅
- [ ] Overlay shows detection boxes in real-time
- [ ] Toggle works with `Ctrl+Shift+O`
- [ ] Color-coded boxes (green/red)
- [ ] Performance: 15+ FPS with overlay active
- [ ] Preview canvas shows templates

### Phase 7: Monster Tracking ✅
- [ ] Tracking starts/stops via UI
- [ ] Detection updates every 100ms
- [ ] Hunt loop uses vision detection
- [ ] Skills execute on detected monsters
- [ ] Handles target loss gracefully

### Phase 8: Screen Capture ✅
- [ ] Captures screen at 15+ FPS
- [ ] Auto-detects Cabal window
- [ ] Handles window movement
- [ ] Queue management prevents overflow
- [ ] Memory usage remains stable

---

## 📚 Documentation Plan

### Documents to Create:
- [ ] `SPRINT23_PLAN.md` (this file)
- [ ] `PHASE5_OVERLAY_SYSTEM.md`
- [ ] `PHASE7_MONSTER_TRACKING.md`
- [ ] `PHASE8_SCREEN_CAPTURE.md`
- [ ] `INTEGRATION_GUIDE.md`

### Documents to Update:
- [ ] `docs/sprints/sprint22/VISION_WIZARD_FRAMEWORK.md` - Mark TODOs as done
- [ ] `docs/INDEX.md` - Add Sprint 23 entry
- [ ] `PROJECT_STRUCTURE.md` - Update with new modules
- [ ] `README.md` - Update features list

---

## 🧪 Testing Strategy

### Unit Tests
- [ ] Overlay window creation/destruction
- [ ] Detection box drawing accuracy
- [ ] Screen capture performance
- [ ] Window detection reliability
- [ ] Tracking thread start/stop

### Integration Tests
- [ ] Overlay + Vision engine
- [ ] Screen capture + Worker thread
- [ ] Tracking + Hunt loop
- [ ] End-to-end vision system

### Performance Tests
- [ ] FPS with overlay active
- [ ] Memory usage over time
- [ ] CPU usage optimization
- [ ] Queue overflow handling

### Manual Tests
- [ ] Visual verification of overlay
- [ ] Hunt automation with vision
- [ ] Window movement scenarios
- [ ] Edge cases (minimized, multi-monitor)

---

## 🐛 Known Risks & Mitigation

### Risk 1: Performance Degradation
**Impact:** FPS drops below 15  
**Mitigation:**
- Optimize screen capture (use MSS or win32)
- Reduce overlay drawing complexity
- Profile and optimize bottlenecks

### Risk 2: Window Detection Issues
**Impact:** Can't detect Cabal window  
**Mitigation:**
- Implement multiple detection methods
- Add manual window selection fallback
- Handle multi-monitor setups

### Risk 3: Integration Complexity
**Impact:** Hunt loop integration breaks existing functionality  
**Mitigation:**
- Keep vision system optional (toggle)
- Comprehensive regression testing
- Feature flags for gradual rollout

---

## 📈 Metrics & KPIs

### Performance Metrics
- **FPS Target:** ≥15 FPS (screen capture + detection + overlay)
- **Memory:** <200MB additional (compared to baseline)
- **CPU:** <10% on modern i5/i7
- **Latency:** <100ms detection-to-action

### Quality Metrics
- **Test Coverage:** >80% for new code
- **Bug Density:** <5 bugs per 1000 LOC
- **Documentation:** 100% public APIs documented

### User Metrics
- **Setup Time:** <5 minutes to configure vision
- **Success Rate:** >90% monster detection accuracy
- **User Satisfaction:** Positive feedback from testing

---

## 🔄 Sprint Backlog

### High Priority (Must Have)
- [x] Planning document created
- [ ] Phase 5: Overlay System
- [ ] Phase 7: Monster Tracking
- [ ] Phase 8: Screen Capture
- [ ] Integration testing
- [ ] Documentation updates

### Medium Priority (Should Have)
- [ ] Performance optimization
- [ ] Error handling improvements
- [ ] User configuration UI
- [ ] Logging system

### Low Priority (Nice to Have)
- [ ] Multi-monitor support
- [ ] Recording mode (save captures)
- [ ] Debug visualization tools

---

## 🚀 Getting Started

### Prerequisites
```bash
# Ensure Sprint 22 is complete
git checkout main
git pull origin main

# Create Sprint 23 branch
git checkout -b feature/S23-vision-advanced
```

### Development Setup
1. Review Sprint 22 implementation
2. Read this planning document
3. Set up development environment
4. Start with Phase 8 (Screen Capture) - foundation for others

### First Task: Screen Capture Module
```bash
# Create module
touch lib/system/screen_capture.py
touch lib/system/window_manager.py

# Start implementation
# See PHASE8_SCREEN_CAPTURE.md for details
```

---

## 📞 Support & Resources

### Documentation
- **Sprint 22:** `docs/sprints/sprint22/`
- **Vision Engine:** `lib/vision/vision_engine.py`
- **Worker Thread:** `docs/sprints/sprint22/WORKER_THREAD_ARCHITECTURE.md`

### External Resources
- MSS (Screen Capture): https://python-mss.readthedocs.io/
- Win32 API: https://pypi.org/project/pywin32/
- Tkinter Overlay: https://docs.python.org/3/library/tkinter.html

---

## ✅ Definition of Done

**Sprint 23 is complete when:**
1. ✅ All Phase 5, 7, 8 features implemented
2. ✅ Tests passing (unit + integration)
3. ✅ Performance meets KPIs (≥15 FPS)
4. ✅ Documentation updated
5. ✅ Code reviewed and merged to main
6. ✅ Demo prepared for stakeholders

---

**Created:** October 23, 2025  
**Author:** GitHub Copilot  
**Status:** 🚀 Ready to Start  
**Next Sprint:** Sprint 24 (Phase 6, 9-11 - Polish Features)
