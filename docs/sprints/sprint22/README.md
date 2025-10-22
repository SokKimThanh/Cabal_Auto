# Sprint 22 - Vision System Wizard & Advanced Features

Welcome to Sprint 22 documentation! 🎯

## 📚 Documentation Files

### Main Documents
- **[VISION_WIZARD_FRAMEWORK.md](VISION_WIZARD_FRAMEWORK.md)** - Vision Wizard framework and setup guide (NEW)
- **[SPRINT22_SUMMARY.md](SPRINT22_SUMMARY.md)** - Complete sprint overview and progress tracking
- **[SPRINT22_PATCH1_TRAINING_MODE.md](SPRINT22_PATCH1_TRAINING_MODE.md)** - Training Mode feature specification
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Quick implementation guide for developers

## 🎯 Sprint Goal

Enhance hunting capabilities with:
1. **Training Mode** - Practice skills on training dummies
2. **Advanced Monster Management** - Monster categories and behaviors
3. **Skill Rotation Optimizer** - Auto-optimize rotations based on stats

## 📊 Current Status

**Sprint Progress**: 10% (Patch 1 in progress)

- ✅ **Patch 1**: Training Mode (30% complete)
- 📋 **Patch 2**: Advanced Monster Management (Planned)
- 📋 **Patch 3**: Skill Rotation Optimizer (Planned)

## 🚀 Quick Start

### For Users
1. Read [SPRINT22_PATCH1_TRAINING_MODE.md](SPRINT22_PATCH1_TRAINING_MODE.md) for feature overview
2. Check "Usage Guide" section for setup instructions
3. Follow step-by-step to enable training mode

### For Developers
1. Review [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for implementation steps
2. Complete remaining tasks (UI, hunt logic, translations)
3. Test thoroughly before commit

## 📋 Patch 1: Training Mode

### What's Completed (30%)
- ✅ Database schema (`training_mode` field)
- ✅ Load/save functions updated
- ✅ "Coc go~" configured as training dummy
- ✅ Complete documentation

### What's Remaining (70%)
- ⏳ Training Mode UI in Hunt Tab
- ⏳ Training mode toggle logic
- ⏳ Hunt loop modifications
- ⏳ Skill stats display
- ⏳ i18n translations (EN/VI)

### Implementation Time
**Estimated**: 2-3 hours for full implementation

## 🔧 Technical Overview

### Database Changes
```json
{
  "name": "Coc go~",
  "training_mode": true,  // NEW: marks training dummy
  ...
}
```

### Code Changes
- `app_gui.py`: +200 lines (UI + logic)
- `ui/auto_hunt.py`: ~50 lines modified
- `lib/i18n/*.json`: +20 translations

## 📖 Key Concepts

### Training Mode
- **Purpose**: Practice skill rotations without killing monsters
- **Target**: Training Dummy (HP vô hạn)
- **Features**: Real-time skill stats, no target switching

### Training Dummy
- Special monster type with `training_mode: true`
- Doesn't die when attacked
- Used for skill practice and testing

### Skill Performance Stats
- Cast count
- Last cast time
- Cooldown remaining
- Success rate (%)

## 🎨 UI Preview

```
┌─────────────────────────────────────────┐
│ 🎯 Training Mode                        │
├─────────────────────────────────────────┤
│ ☑ Enable Training Mode (Practice Skills│
│                                         │
│ Practice skill rotation on training    │
│ dummy without target switching.         │
│                                         │
│ ┌─ Skill Performance Statistics ──────┐│
│ │ Skill       Casts  Last  Cool  %%   ││
│ │ ──────────  ─────  ────  ────  ───  ││
│ │ Power Slash  12    2.3s  Ready 100  ││
│ │ Fire Ball     8    3.1s  1.2s   88  ││
│ └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

## 🧪 Testing

### Manual Test Scenarios
1. Enable training mode → verify UI changes
2. Start hunt → verify no target switching
3. Monitor stats → verify accuracy
4. Disable training mode → verify restoration

### Unit Tests (TODO)
- Training mode toggle
- Monster filtering
- Skill stats tracking
- UI state management

## 📞 Support

### Getting Help
1. Read feature documentation
2. Check implementation guide
3. Review code examples
4. Test step-by-step

### Resources
- **Main Docs**: [docs/INDEX.md](../INDEX.md)
- **User Guide**: [docs/guides/HUONG_DAN_NGUOI_MOI.md](../guides/HUONG_DAN_NGUOI_MOI.md)
- **Sprint 21**: [docs/sprint21/](../sprint21/)

## 🔄 Version History

**October 21, 2025**:
- Created Sprint 22 folder
- Added Patch 1 documentation (Training Mode)
- Database schema updated
- Implementation guide created

---

**Sprint**: Sprint 22 - Advanced Features  
**Status**: ⏳ IN PROGRESS (10%)  
**Last Updated**: October 21, 2025
