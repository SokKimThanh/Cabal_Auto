# Cabal Auto Hunt - Documentation Index

**Last Updated**: October 22, 2025 (Sprint 22 Phase 2B Complete)  
**Current Sprint**: Sprint 22 - Vision System Core Implementation ✅ COMPLETED

## 📁 New Documentation Structure

```
docs/
├── README.md                          # Main documentation entry
├── INDEX.md                           # This file - Complete index
│
├── architecture/                      # 🏛️ System Architecture
│   ├── README.md
│   ├── GLOBAL_HOTKEY_ARCHITECTURE.md
│   ├── GLOBAL_HOTKEYS_EXTENDED_ARCHITECTURE.md
│   ├── WORKER_THREAD_ARCHITECTURE.md
│   └── SINGLE_INSTANCE_LOCK.md
│
├── features/                          # ⭐ Features Documentation
│   ├── hotkeys/
│   │   ├── README.md
│   │   ├── GLOBAL_HOTKEY_MIGRATION.md
│   │   └── HOTKEY_F8_TOGGLE.md
│   ├── vision/                        # Vision System (Sprint 22)
│   │   ├── README.md
│   │   ├── VISION_WIZARD_FRAMEWORK.md
│   │   ├── QUICK_START_VISION_WIZARD.md
│   │   ├── VISION_MENU_INTEGRATION.md
│   │   └── VISION_MENU_CHECKLIST.md
│   ├── first-run/
│   │   └── FEATURE_FIRST_RUN_LOCK.md
│   └── templates/
│       └── FEATURE_TEMPLATE_LOCK_HOLD_TO_SAVE.md
│
├── guides/                            # 📖 User Guides
│   ├── ui-design/
│   │   ├── ICON_BUTTON_STYLE_GUIDE.md
│   │   ├── BUTTON_STYLE_CONSISTENCY.md
│   │   └── FEATURE_ICON_RECOLORING.md
│   └── testing/
│       └── TESTS_REORGANIZATION_SUMMARY.md
│
├── sprints/                           # 🚀 Sprint Documentation
│   ├── sprint21/                      # Sprint 21 (UI/UX Icons)
│   └── sprint22/                      # Sprint 22 (Vision System)
│       ├── README.md
│       ├── SPRINT22_SUMMARY.md
│       ├── phases/
│       │   ├── PHASE1_COMPLETE_SUMMARY.md
│       │   ├── PHASE1B_SUMMARY.md
│       │   └── COMPLETION_REPORT.md
│       ├── patches/
│       │   ├── SPRINT22_PATCH1_TRAINING_MODE.md
│       │   ├── SPRINT22_PATCH2_TRAINING_UI.md
│       │   └── SPRINT22_PATCH2_QUICK_SUMMARY.md
│       ├── implementation/
│       │   ├── IMPLEMENTATION_GUIDE.md
│       │   ├── IMPLEMENTATION_STATUS.md
│       │   └── SETUP_WIZARD_MENU_AND_LAYOUT.md
│       ├── updates/
│       │   └── ICON_UPDATES_ACCEPT_LOCKED.md
│       ├── examples/
│       │   ├── VISION_WIZARD_INTEGRATION_EXAMPLES.py
│       │   └── VISION_MENU_PATCHES.py
│       └── templates/
│           └── pr_template_vision.md
│
├── maintenance/                       # 🔧 Maintenance
│   └── LOG_FILES_MANAGEMENT_SUMMARY.md
│
├── enhancements/                      # ✨ Enhancements (Legacy)
├── bugfixes/                          # 🐛 Bug Fixes (Legacy)
├── context/                           # 📝 Context Documentation
├── translations/                      # 🌐 Translations
├── ux-enhancements/                   # 💫 UX Enhancements
└── archive/                           # 📦 Archived Documentation
```

## 🎯 Quick Navigation

### For Developers

#### Architecture
- [Global Hotkeys](architecture/GLOBAL_HOTKEY_ARCHITECTURE.md) - Hotkey system architecture
- [Worker Threads](architecture/WORKER_THREAD_ARCHITECTURE.md) - Non-blocking CV processing
- [Single Instance Lock](architecture/SINGLE_INSTANCE_LOCK.md) - Prevent multiple instances

#### Features
- [Vision System](features/vision/README.md) - Vision System documentation
- [Global Hotkeys](features/hotkeys/README.md) - Hotkey features
- [First Run Lock](features/first-run/FEATURE_FIRST_RUN_LOCK.md) - First-time setup

#### Implementation Guides
- [Vision Quick Start](features/vision/QUICK_START_VISION_WIZARD.md) - Get started with Vision
- [Sprint 22 Guide](sprints/sprint22/implementation/IMPLEMENTATION_GUIDE.md) - Implementation guide

### For Designers

- [Icon Button Style Guide](guides/ui-design/ICON_BUTTON_STYLE_GUIDE.md) - Icon design rules
- [Button Consistency](guides/ui-design/BUTTON_STYLE_CONSISTENCY.md) - Button styling
- [Icon Recoloring](guides/ui-design/FEATURE_ICON_RECOLORING.md) - Icon color system

### For Testers

- [Testing Guide](guides/testing/TESTS_REORGANIZATION_SUMMARY.md) - Test organization
- [Vision Menu Checklist](features/vision/VISION_MENU_CHECKLIST.md) - Vision testing

### Latest Sprint (Sprint 22) ✅ COMPLETED

- **Theme**: Vision System Core Implementation
- **Duration**: October 18-22, 2025
- **Status**: ✅ COMPLETED - 23 commits
- **Branch**: feature/S22-45-vision-core
- **Docs**: [sprints/sprint22/](sprints/sprint22/)

## 📚 Sprint Documentation

### Sprint 22 - Vision System (Latest) ✅ COMPLETED

**Duration**: October 18-22, 2025  
**Branch**: `feature/S22-45-vision-core`  
**Status**: ✅ COMPLETED - 23 commits

#### Key Deliverables

**Phase 1: Core Engine**
- ✅ Vision engine implementation (810 lines)
- ✅ Template matching & NMS
- ✅ Multi-template support
- ✅ Config management

**Phase 2: Worker Threads**
- ✅ Worker thread architecture
- ✅ Queue-based communication (15 FPS)
- ✅ Performance tests (7 test cases)
- ✅ Architecture documentation (302 lines)

**Phase 3: UI Integration**
- ✅ Vision Wizard UI (1,259 lines)
- ✅ Singleton pattern
- ✅ Template management
- ✅ i18n support (vi/en)

**Phase 4: Menu & Hotkeys**
- ✅ Vision menu integration
- ✅ Global hotkeys (Ctrl+Shift+V)
- ✅ Setup tab configuration
- ✅ Tooltips with lang_provider

**Patches**
- ✅ Training mode support
- ✅ Training UI enhancements
- ✅ Type hint fixes
- ✅ Menu display fixes

#### Documentation
- [Sprint 22 README](sprints/sprint22/README.md) - Overview
- [Completion Report](sprints/sprint22/phases/COMPLETION_REPORT.md) - Final report
- [Vision System](features/vision/README.md) - Feature docs
- [Worker Threads](architecture/WORKER_THREAD_ARCHITECTURE.md) - Architecture

#### Statistics
- **23 commits** on feature branch
- **3,349 lines** added (core code)
- **4 phases** completed
- **2 patches** applied
- **7 test cases** implemented

### Sprint 21 - UI/UX Enhancement ✅ COMPLETED

**Duration**: October 15-17, 2025  
**Status**: ✅ COMPLETED

#### Key Deliverables
- ✅ Icon system enhancement
- ✅ Button style consistency
- ✅ Setup wizard icons
- ✅ Global button design

#### Documentation
- [Sprint 21 Summary](sprint21/SPRINT21_SUMMARY.md)
- [Icon Placement Rules](sprint21/ICON_PLACEMENT_RULES.md)

Historical sprint documentation:

#### **Sprint 16**: Setup Wizard Implementation
- UI Redesign
- 5-step wizard
- First-run experience
- **Docs**: [sprints/sprint16/](sprints/sprint16/)

#### **Sprint 18**: 4-Tab Reorganization
- Hunt, Setup, Stats, Help tabs
- UI layout redesign
- **Docs**: [sprints/sprint18/](sprints/sprint18/)

#### **Sprint 19**: Library Manager
- Monster library
- Skill library
- Timing calculator
- **Docs**: [sprints/sprint19/](sprints/sprint19/)

#### **Sprint 20**: System Improvements
- Performance optimization
- Code refactoring
- **Docs**: [sprints/sprint20/](sprints/sprint20/)

#### **Sprint 13-15**: Early Development
- Core features
- Initial UI
- **Docs**: [sprints/](sprints/)

---

### 8. Core Architecture Documentation (Root `docs/`)

**Technical architecture and system design**:

- **[SINGLE_INSTANCE_LOCK.md](SINGLE_INSTANCE_LOCK.md)** - Single instance enforcement (Windows mutex + Unix file lock)
- **[GLOBAL_HOTKEY_ARCHITECTURE.md](GLOBAL_HOTKEY_ARCHITECTURE.md)** - Hotkey system architecture analysis ⌨️ **NEW**
- **[GLOBAL_HOTKEY_MIGRATION.md](GLOBAL_HOTKEY_MIGRATION.md)** - F8 → Ctrl+Shift+R/E migration guide ⌨️ **NEW**
- **[HOTKEY_F8_TOGGLE.md](HOTKEY_F8_TOGGLE.md)** - ⚠️ **DEPRECATED** - Old F9→F8 migration (superseded)

---

### 9. Context (`context/`)

System context and architecture documentation:
- **CONTEXT_MAIN.txt** - Main system context

---

### 9. Archive (`archive/`) - 17+ files

Deprecated or superseded documentation:

**Categories**:
- Old summaries: `SUMMARY_*.md`
- Migration guides: `MIGRATION_*.md`
- Project reorganization: `PROJECT_*.md`
- Historical sessions: `SESSION_*.md`
- Implementation checklists: `IMPLEMENTATION_*.md`
- Update logs: `UPDATE_*.md`

---

## 🔍 Finding Documentation

### By Topic

**Setup & Configuration**:
- Setup Wizard: [sprints/sprint16/](sprints/sprint16/)
- Window Settings: [guides/ADVANCED_WINDOW_SETTINGS_GUIDE.md](guides/ADVANCED_WINDOW_SETTINGS_GUIDE.md)
- First Run: [features/FEATURE_FIRST_RUN_LOCK.md](features/FEATURE_FIRST_RUN_LOCK.md)

**UI/UX & Icons**:
- Icon System: [sprint21/ICON_PLACEMENT_RULES.md](sprint21/ICON_PLACEMENT_RULES.md) ⭐
- Icon Coverage: [sprint21/ICON_STATUS_REPORT.md](sprint21/ICON_STATUS_REPORT.md)
- Button Design: [sprint21/SPRINT21_PATCH13_GLOBAL_BUTTON_DESIGN.md](sprint21/SPRINT21_PATCH13_GLOBAL_BUTTON_DESIGN.md)
- Dialog Icons: [enhancements/ENHANCEMENT_DIALOG_SAVE_ICONS.md](enhancements/ENHANCEMENT_DIALOG_SAVE_ICONS.md)

**Skills & Combat**:
- Training Mode: [sprint22/SPRINT22_PATCH1_TRAINING_MODE.md](sprint22/SPRINT22_PATCH1_TRAINING_MODE.md) ⭐
- Implementation Guide: [sprint22/IMPLEMENTATION_GUIDE.md](sprint22/IMPLEMENTATION_GUIDE.md)
- Skills Guide: [guides/SKILLS_EXPLANATION_SIMPLE.md](guides/SKILLS_EXPLANATION_SIMPLE.md)
- Rotation Tab: [bugfixes/BUGFIX_ROTATION_TAB_NO_SKILLS.md](bugfixes/BUGFIX_ROTATION_TAB_NO_SKILLS.md)

**Testing**:
- Template Testing: [guides/HOW_TO_USE_TEST_RECOGNITION.md](guides/HOW_TO_USE_TEST_RECOGNITION.md)
- Tests Organization: [TESTS_REORGANIZATION_SUMMARY.md](TESTS_REORGANIZATION_SUMMARY.md) ✨ **NEW**

**Internationalization**:
- Language Persistence: [bugfixes/BUGFIX_LANGUAGE_PERSISTENCE.md](bugfixes/BUGFIX_LANGUAGE_PERSISTENCE.md)
- Vietnamese Guide: [guides/HUONG_DAN_NGUOI_MOI.md](guides/HUONG_DAN_NGUOI_MOI.md) 🇻🇳

### By Sprint

- **Sprint 13-15**: [sprints/SPRINT15_COMPLETE.md](sprints/SPRINT15_COMPLETE.md)
- **Sprint 16**: [sprints/sprint16/](sprints/sprint16/) - Setup Wizard
- **Sprint 18**: [sprints/sprint18/](sprints/sprint18/) - 4-Tab UI
- **Sprint 19**: [sprints/sprint19/](sprints/sprint19/) - Library Manager
- **Sprint 20**: [sprints/sprint20/](sprints/sprint20/) - Performance
- **Sprint 21**: [sprint21/](sprint21/) - UI/UX Icons ✅ COMPLETE
- **Sprint 22**: [sprint22/](sprint22/) - Training Mode ⭐ **CURRENT**

---

## 📝 Documentation Standards

### File Naming Convention
- Features: `FEATURE_*.md`
- Enhancements: `ENHANCEMENT_*.md`
- Bugfixes: `BUGFIX_*.md`
- Guides: `HOW_TO_*.md` or `HUONG_DAN_*.md` (Vietnamese)
- Sprints: `SPRINT##_*.md`
- Icons: `ICON_*.md`
- Summaries: `SUMMARY_*.md` (archived)

### Document Structure
Each document should include:
1. **Title** and version/date
2. **Purpose/Overview** - What this document covers
3. **Technical Details** - Implementation specifics
4. **Code Examples** - Working code snippets
5. **Testing/Validation** - How to verify
6. **Related Documents** - Cross-references

### Icon Documentation Standards (New)
For icon-related documents:
1. **Visual Examples** - Screenshots or diagrams
2. **Code Templates** - Copy-paste ready examples
3. **DO/DON'T Patterns** - Clear anti-patterns
4. **Coverage Analysis** - What's implemented vs missing

---

## 🔄 Recent Changes (October 21, 2025)

### Sprint 22 - Training Mode (Patch 1)
**Status**: ⏳ IN PROGRESS (30% complete)

**Completed**:
- ✅ Database schema: Added `training_mode` field to monsters.json
- ✅ Updated load/save monster library functions
- ✅ Configured "Coc go~" as training dummy (infinite HP)
- ✅ Created comprehensive documentation (4 files)
- ✅ Implementation guide for developers

**In Progress**:
- ⏳ Hunt Tab: Add Training Mode checkbox toggle
- ⏳ Hunt logic: Skip target switching in training mode
- ⏳ UI: Build skill performance stats display
- ⏳ i18n: Add EN/VI translations
- ⏳ Testing: Manual verification

**New Files**:
```
docs/sprint22/
├── SPRINT22_PATCH1_TRAINING_MODE.md  (700 lines)
├── IMPLEMENTATION_GUIDE.md            (350 lines)
├── SPRINT22_SUMMARY.md                (400 lines)
└── README.md                          (200 lines)
```

---

### Documentation Reorganization (Patch 16)
**Status**: ✅ COMPLETE

**Changes**:
- ✅ Created 5 categorical folders
- ✅ Moved 30+ files to appropriate locations
- ✅ Updated INDEX.md structure (this file)
- ✅ Archived old summaries
- ✅ README.md updated to v2.0

**New Structure**:
```
docs/
├── features/      (2 files)
├── enhancements/  (4 files)
├── guides/        (5 files)
├── sprint21/      (8 files) ✅
├── sprint22/      (4 files) ⭐
├── bugfixes/      (16 files)
├── archive/       (17+ files)
└── sprints/       (existing)
```

### Sprint 21 Documentation (Patches 10-16)
- ✨ **ICON_PLACEMENT_RULES.md** - Comprehensive icon design guide
- ✨ **ICON_STATUS_REPORT.md** - Icon coverage analysis
- ✨ Sprint 21 patches consolidated in `sprint21/`
- ✨ 8 patch documents + summary

---

## 📊 Statistics

- **Total Files**: 40+ markdown files
- **Categories**: 8 folders (features, enhancements, guides, sprint21, sprint22, bugfixes, archive, sprints)
- **Sprints Completed**: 21 (Sprint 1-21, 100%)
- **Current Sprint**: Sprint 22 (Training Mode - 31% complete)
- **Languages**: English, Tiếng Việt 🇻🇳
- **Icon Coverage**: 39 buttons, 28 with .ico files (72%)
- **Test Files**: 31+ organized in 5 categories (unit, integration, demos, utils, sprints)

---

## 🎯 TODO

### High Priority
- [ ] Update README.md with new structure
- [ ] Create visual diagrams for icon rules
- [ ] Add Sprint 21 Patch 16 to summary

### Medium Priority
- [ ] Consolidate bugfix summaries
- [ ] Add more code examples to guides
- [ ] Create icon design templates

### Low Priority
- [ ] Update sprint documentation templates
- [ ] Archive very old session summaries
- [ ] Consider consolidating sprint folders

---

## 📞 Support

### For Questions
1. **New Users**: Check [guides/HUONG_DAN_NGUOI_MOI.md](guides/HUONG_DAN_NGUOI_MOI.md) 🇻🇳
2. **Developers**: Review [sprint21/ICON_PLACEMENT_RULES.md](sprint21/ICON_PLACEMENT_RULES.md)
3. **Bug Reports**: Search [bugfixes/](bugfixes/) first
4. **Historical Context**: Check [archive/](archive/)

### Documentation Navigation
- **Main Entry**: [README.md](README.md)
- **This Index**: [INDEX.md](INDEX.md) (you are here)
- **Latest Sprint**: [sprint21/SPRINT21_SUMMARY.md](sprint21/SPRINT21_SUMMARY.md)

---

**Maintained by**: Cabal Auto Hunt Development Team  
**Next Review**: Sprint 22  
**Documentation Version**: 2.0 (Reorganized October 21, 2025)
