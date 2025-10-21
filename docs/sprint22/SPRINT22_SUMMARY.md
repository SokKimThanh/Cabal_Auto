# Sprint 22 - Advanced Features & Training System

**Start Date**: October 21, 2025  
**Status**: ⏳ IN PROGRESS  
**Theme**: Advanced hunting features, training system, and UI enhancements

---

## 📋 Sprint Overview

**Objective**: Enhance hunting capabilities with training mode, advanced monster management, and improved skill rotation system.

**Key Goals**:
1. Implement Training Mode for skill practice
2. Add special monster types (Training Dummy)
3. Real-time skill performance tracking
4. Enhanced hunt UI for training scenarios
5. Advanced timing and rotation optimization

---

## 🎯 Sprint Patches

### Patch 1: Training Mode (Chế Độ Luyện Kỹ Năng) ⭐
**Status**: ⏳ IN PROGRESS (30% complete)  
**Document**: [SPRINT22_PATCH1_TRAINING_MODE.md](SPRINT22_PATCH1_TRAINING_MODE.md)

**Features**:
- ✅ Training Dummy monster type (`training_mode: true`)
- ✅ Database schema updates (monsters.json)
- ⏳ Training Mode toggle in Hunt Tab
- ⏳ Hunt logic: no target switching in training mode
- ⏳ Real-time skill performance stats display
- ⏳ i18n translations (EN/VI)

**Changes**:
```
Modified Files:
- lib/data/monsters.json (+1 field: training_mode)
- app_gui.py (load/save_monster_library updated)

New Features:
- Training Mode checkbox in Hunt Tab
- Skill statistics tracking
- Performance metrics display
```

**User Benefits**:
- Practice skill rotations safely
- Test timing and cooldowns
- Monitor skill performance
- No need to kill monsters for testing

---

### Patch 2: Advanced Monster Management (PLANNED)
**Status**: 📋 PLANNED  
**Target**: October 22, 2025

**Features**:
- Monster categories (Boss, Elite, Normal, Training)
- Monster difficulty levels
- Custom monster behaviors
- Advanced template matching options

---

### Patch 3: Skill Rotation Optimizer (PLANNED)
**Status**: 📋 PLANNED  
**Target**: October 23, 2025

**Features**:
- Auto-optimize skill rotation based on stats
- DPS calculation and recommendations
- Cooldown conflict detection
- Rotation templates library

---

## 📊 Sprint Progress

### Overall Progress: 10%

| Patch | Feature | Status | Progress |
|-------|---------|--------|----------|
| 1 | Training Mode | ⏳ In Progress | 30% |
| 2 | Advanced Monster Mgmt | 📋 Planned | 0% |
| 3 | Skill Rotation Optimizer | 📋 Planned | 0% |

### Completed Tasks

#### Patch 1
- [x] Add `training_mode` field to monsters.json
- [x] Update `load_monster_library()` function
- [x] Update `save_monster_library()` function
- [x] Set "Coc go~" as training_mode=true
- [x] Create comprehensive documentation

#### Remaining Tasks
- [ ] Add Training Mode checkbox to Hunt Tab UI
- [ ] Implement training mode toggle logic
- [ ] Modify hunt loop for training mode
- [ ] Build skill stats display UI
- [ ] Add i18n translations
- [ ] Test and validate

---

## 🔧 Technical Changes

### Database Schema

#### monsters.json (NEW)
```json
{
  "name": "Monster Name",
  "training_mode": false,  // NEW: marks training dummy
  ...existing fields...
}
```

### Code Modifications

**app_gui.py**:
- `load_monster_library()`: Load training_mode field
- `save_monster_library()`: Save training_mode field

**ui/auto_hunt.py** (PLANNED):
- `hunt_loop()`: Skip target switching if training_mode
- `track_skill_cast()`: Track skill performance stats

### New Features

**Training Mode System**:
- Toggle in Hunt Tab
- Filter monsters to training dummies
- Disable monster rotation
- Show skill performance stats

---

## 📚 Documentation

### New Documents
- [SPRINT22_PATCH1_TRAINING_MODE.md](SPRINT22_PATCH1_TRAINING_MODE.md) - Complete feature spec

### Updated Documents
- README.md - Will add training mode section (pending)
- INDEX.md - Will add Sprint 22 entry (pending)

---

## 🎨 UI/UX Changes

### Hunt Tab
**New Section**: Training Mode
- Checkbox: "🎯 Enable Training Mode (Practice Skills)"
- Description text
- Skill Performance Statistics table
- Visual indicators (badges, colors)

**Changes**:
- Monster list filters when training mode ON
- Monster rotation disabled in training mode
- Skill stats frame shows/hides dynamically

---

## 🧪 Testing Strategy

### Unit Tests
- Training mode toggle functionality
- Monster filtering logic
- Skill stats tracking accuracy
- UI state management

### Integration Tests
- Hunt loop with training mode
- Skill execution with stats
- UI updates during hunt
- Mode switching (training ↔ normal)

### Manual Tests
- End-to-end training workflow
- Skill rotation testing
- Performance monitoring
- Edge cases (no training dummy, etc.)

---

## 📈 Performance Metrics

### Before Sprint 22
- Hunt modes: Normal only
- Training: Not supported
- Skill stats: None
- Monster types: Generic

### After Patch 1 (Target)
- Hunt modes: Normal + Training
- Training: Supported with stats
- Skill stats: Real-time tracking
- Monster types: Normal + Training Dummy

---

## 🐛 Known Issues

### Patch 1
- Skill stats update may lag (async needed)
- Training dummy template matching needs tuning
- UI layout needs responsive design testing

---

## 🔮 Future Enhancements

### Phase 2 (Post-Sprint 22)
- Advanced stats: DPS, combos, optimization
- Training profiles: Save/load sessions
- Visual feedback: Animations, progress bars
- Export stats to CSV/JSON

### Phase 3
- AI-powered rotation suggestions
- Historical performance analysis
- Multi-dummy training support
- Training mode presets

---

## 📞 Support & Resources

### Documentation
- **Patch 1**: [SPRINT22_PATCH1_TRAINING_MODE.md](SPRINT22_PATCH1_TRAINING_MODE.md)
- **User Guide**: [docs/guides/HUONG_DAN_NGUOI_MOI.md](../guides/HUONG_DAN_NGUOI_MOI.md)
- **README**: [README.md](../../README.md)

### Getting Help
1. Check patch documentation
2. Review implementation checklist
3. Test training mode toggle
4. Monitor skill stats display

---

## 📊 Sprint Statistics

**Sprint 22 Overview**:
- **Total Patches**: 3 (planned)
- **Completed**: 0
- **In Progress**: 1 (Patch 1 - 30%)
- **Planned**: 2

**Code Changes** (Patch 1):
- Files modified: 2
- Lines added: ~200 (estimated)
- New fields: 1 (training_mode)
- New UI components: 3 (checkbox, stats table, indicators)

**Documentation**:
- New docs: 2 (this + patch 1)
- Pages: ~50 (patch 1 doc)
- Code examples: 15+
- Screenshots: TBD

---

## ✅ Patch 1 Completion Criteria

**Definition of Done**:
- [x] Database schema updated
- [x] Load/save functions support training_mode
- [ ] Training Mode UI implemented
- [ ] Hunt logic modified for training mode
- [ ] Skill stats display working
- [ ] i18n translations added
- [ ] Tested with "Coc go~" monster
- [ ] Documentation complete
- [ ] User guide updated

**Acceptance Criteria**:
1. User can enable/disable training mode via checkbox
2. Training mode only shows training dummies
3. Hunt doesn't switch targets in training mode
4. Skill stats update in real-time
5. UI shows clear visual indicators
6. Works in both EN and VI languages

---

## 🎯 Next Steps

### Immediate (This Week)
1. Complete Training Mode UI (Patch 1 Task 2, 3)
2. Modify hunt logic (Patch 1 Task 4)
3. Build skill stats display (Patch 1 Task 5)
4. Add translations (Patch 1 Task 6)
5. Test thoroughly

### Short-term (Next Week)
1. Complete Patch 1
2. Plan Patch 2 (Advanced Monster Management)
3. User testing and feedback
4. Bug fixes and refinements

### Long-term (This Month)
1. Complete Sprint 22 (all 3 patches)
2. Update README.md and INDEX.md
3. Create video tutorials
4. Plan Sprint 23

---

**Maintained by**: Cabal Auto Hunt Development Team  
**Sprint**: Sprint 22  
**Status**: ⏳ IN PROGRESS (10% complete)  
**Last Updated**: October 21, 2025
