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

## 🔍 Search by Topic

### Vision System
- [Vision README](features/vision/README.md) - Complete vision docs
- [Vision Wizard Framework](features/vision/VISION_WIZARD_FRAMEWORK.md)
- [Vision Quick Start](features/vision/QUICK_START_VISION_WIZARD.md)
- [Worker Thread Architecture](architecture/WORKER_THREAD_ARCHITECTURE.md)

### Global Hotkeys
- [Hotkey Architecture](architecture/GLOBAL_HOTKEY_ARCHITECTURE.md)
- [Hotkey Features](features/hotkeys/README.md)
- [Hotkey Migration](features/hotkeys/GLOBAL_HOTKEY_MIGRATION.md)

### UI Design
- [Icon Style Guide](guides/ui-design/ICON_BUTTON_STYLE_GUIDE.md)
- [Button Consistency](guides/ui-design/BUTTON_STYLE_CONSISTENCY.md)
- [Icon Recoloring](guides/ui-design/FEATURE_ICON_RECOLORING.md)

### Testing
- [Test Organization](guides/testing/TESTS_REORGANIZATION_SUMMARY.md)
- [Vision Checklist](features/vision/VISION_MENU_CHECKLIST.md)

## 📊 Statistics

### Sprint 22 Metrics
- **23 commits** on feature branch
- **3,349 lines** added (core code)
- **302 lines** documentation (architecture)
- **7 test cases** implemented
- **4 phases** completed
- **2 patches** applied

### Documentation Metrics
- **Architecture docs**: 4 files
- **Feature docs**: 9 files (vision, hotkeys, first-run, templates)
- **Sprint docs**: 20+ files (organized by phase/patch/implementation)
- **Guide docs**: 4 files
- **Total reorganization**: 40+ files moved/renamed

### Code Coverage
- Vision engine: 810 lines
- Vision Wizard UI: 1,259 lines
- Worker threads: ~200 lines
- Tests: 7 test cases
- Performance: 15 FPS processing rate

## 🔄 Recent Changes (October 22, 2025)

### Documentation Reorganization ✅ COMPLETED
- ✅ Created `architecture/` directory (4 docs)
- ✅ Created `features/` subdirectories (hotkeys, vision, first-run, templates)
- ✅ Created `guides/` subdirectories (ui-design, testing)
- ✅ Reorganized `sprints/sprint22/` (phases, patches, implementation, updates, examples, templates)
- ✅ Created 4 comprehensive README.md files
- ✅ Updated INDEX.md with new structure

### Sprint 22 Completion ✅
- ✅ Vision System core implemented (23 commits)
- ✅ All 4 phases completed (1, 1B, 2, 2B)
- ✅ Type hints fixed (threshold_frame, UIStyle, i18n)
- ✅ Menu integration working (Vision menu displays correctly)
- ✅ Hotkeys configured (Ctrl+Shift+V for Vision Wizard)
- ✅ Documentation complete (40+ files organized)

## 📞 Support

For questions or issues:
1. Check relevant documentation in this index
2. Review sprint summaries for context
3. Check bugfixes/ for known issues
4. Refer to architecture/ for system design

---

**Note**: This documentation structure was completely reorganized on October 22, 2025 for better maintainability and navigation.

**Maintained by**: Cabal Auto Hunt Development Team  
**Documentation Version**: 3.0 (Reorganized October 22, 2025)
