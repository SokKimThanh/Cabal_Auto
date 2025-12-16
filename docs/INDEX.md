# Cabal Auto Hunt - Documentation Index

**Last Updated**: October 24, 2025 (Sprint 23 Phase 7 Complete)  
**Current Sprint**: Sprint 23 - Advanced Vision Features ✅ Phase 7 COMPLETE

**Note (Round 2 Cleanup, Dec 16, 2025)**: Historical folders were moved under `docs/archive/v2/`.

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
│   ├── HUONG_DAN_NGUOI_MOI.md
│   ├── HUONG_DAN_USER_LEVEL_WIZARD.md
│   ├── OVERLAY_SETUP.md
│   ├── ADVANCED_WINDOW_SETTINGS_GUIDE.md
│   ├── SKILLS_EXPLANATION_SIMPLE.md
│   ├── HOW_TO_USE_TEST_RECOGNITION.md
│   ├── PYTEST_TEMPLATE_CI_CD.md
│   ├── BUTTON_STATE_MANAGEMENT.md
│   ├── BUTTON_STATE_SYSTEM_OVERVIEW.md
│   ├── ACTION_ITEMS_BUTTON_STATE.md
│   ├── MIGRATION_QUICK_MONSTER_EDITOR.md
│   ├── MIGRATION_LIBRARY_MANAGER.md
│   ├── ui-design                      # Icon/button style guide (single-file)
│   └── testing                        # Tests folder reorg summary (single-file)
│
├── testing/                           # 🧪 Testing Process Docs
│   ├── PYTEST_MARKERS_GUIDE.md
│   ├── TEST_STANDARDIZATION_PROGRESS.md
│   └── TEST_VIOLATIONS_CHECKLIST.md
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
├── bugfixes/                          # 🐛 Bug Fixes
│   └── TKINTER_EMPTY_WINDOW_BUG_LESSONS_LEARNED.md
│
├── (moved to archive/v2)              # branches/, sessions/, context/, business/, legacy/, translations/, enhancements/, ux-enhancements/
└── archive/                           # 📦 Archived Documentation
  └── v2/                            # Round 2 archive (branches, sessions, legacy, context, etc.)
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

- [Icon/Button Style Guide](guides/ui-design) - Icon button design rules
- [Icon System Verification](features/ICON_SYSTEM_VERIFICATION.md) - Icon system notes
- [Icon Placement Rules](sprints/sprint21/ICON_PLACEMENT_RULES.md) - Placement conventions

### For UI/Component Development 🆕

- [Button State Management](guides/BUTTON_STATE_MANAGEMENT.md) - Complete API reference
- [System Overview](guides/BUTTON_STATE_SYSTEM_OVERVIEW.md) - Overview (Vietnamese)
- [Action Items](guides/ACTION_ITEMS_BUTTON_STATE.md) - Quick checklist
- [Migration Guides](guides/MIGRATION_QUICK_MONSTER_EDITOR.md) - How to migrate existing code

### For Testers

- [Tests Reorganization Summary](guides/testing) - Test organization
- [Pytest Markers Guide](testing/PYTEST_MARKERS_GUIDE.md) - Markers & how to run subsets
- [Vision Menu Checklist](features/vision/VISION_MENU_CHECKLIST.md) - Vision testing

### Bug Fixes & Troubleshooting 🆕

- [**Quick Fix: Tkinter Empty Window**](QUICK_FIX_TKINTER_EMPTY_WINDOW.md) - Common bug & solution
- [**Detailed: Tkinter Bug Lessons**](bugfixes/TKINTER_EMPTY_WINDOW_BUG_LESSONS_LEARNED.md) - Complete analysis

### Latest Sprint (Sprint 23) ✅ Phase 7 COMPLETE

- **Theme**: Advanced Vision Features - Monster Tracking Integration
- **Duration**: October 24, 2025
- **Status**: ✅ Phase 7 COMPLETE - 13 commits
- **Branch**: feature/S23-vision-advanced
- **Docs**: [sprints/sprint23/](sprints/sprint23/)
- **Progress**: 119 tests passing, 2,142 lines added

### Previous Sprint (Sprint 22) ✅ COMPLETED

- **Theme**: Vision System Core Implementation
- **Duration**: October 18-22, 2025
- **Status**: ✅ COMPLETED - 23 commits
- **Branch**: feature/S22-45-vision-core
- **Docs**: [sprints/sprint22/](sprints/sprint22/)

## 📚 Sprint Documentation

### Sprint 23 - Advanced Vision (Latest) ✅ Phase 7 COMPLETE

**Duration**: October 24, 2025  
**Branch**: `feature/S23-vision-advanced`  
**Status**: ✅ Phase 7 COMPLETE - 13 commits  
**Tests**: 119 passing (108 unit + 11 integration)

#### Phase 7: Monster Tracking Integration ✅ COMPLETE

**Batch 1: Detection Loop Foundation**
- ✅ MonsterDetector class (616 lines, 42 tests)
- ✅ Detection state machine (SEARCHING → DETECTED → TRACKING → LOST)
- ✅ Background detection thread with callbacks
- ✅ Thread-safe state management with RLock

**Batch 2: Overlay Integration**
- ✅ OverlayController class (424 lines, 34 tests)
- ✅ Bridge between detector and overlay
- ✅ Throttled updates and stats tracking
- ✅ State-based box styling

**Batch 3: App Integration**
- ✅ BotManager facade (420 lines, 32 tests)
- ✅ App GUI integration (Phase 7 block)
- ✅ Configuration system (hunt_config.json)
- ✅ Hunt integration hooks

**Batch 4: Testing & Polish**
- ✅ Integration tests (11 tests, 343 lines)
- ✅ Demo script with 3 demonstrations (339 lines)
- ✅ Complete documentation

#### Documentation
- [Phase 7 Plan](sprints/sprint23/PHASE7_MONSTER_TRACKING.md) - Implementation plan
- [Phase 7 Completion](sprints/sprint23/PHASE7_COMPLETION_SUMMARY.md) - Final summary
- [Sprint 23 README](sprints/sprint23/README.md) - Sprint overview

#### Performance Metrics
- **Detection Latency**: ~120ms (target: <150ms) ✅
- **Detection FPS**: 10 FPS ✅
- **Memory Overhead**: ~35MB (target: <50MB) ✅
- **CPU Impact**: ~3% (target: <5%) ✅
- **Test Pass Rate**: 100% (119/119) ✅

#### Statistics
- **13 commits** on feature branch
- **2,142 lines** added (5 new files)
- **119 tests** passing (42+34+32+11)
- **4 batches** completed
- **~9.5 hours** total time

---

### Sprint 22 - Vision System ✅ COMPLETED

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
- [Phase 7: Monster Tracking](sprints/sprint23/PHASE7_MONSTER_TRACKING.md) - Real-time detection
- [Phase 7 Completion](sprints/sprint23/PHASE7_COMPLETION_SUMMARY.md) - Implementation summary

### Global Hotkeys
- [Hotkey Architecture](architecture/GLOBAL_HOTKEY_ARCHITECTURE.md)
- [Hotkey Features](features/hotkeys/README.md)
- [Hotkey Migration](features/hotkeys/GLOBAL_HOTKEY_MIGRATION.md)

### UI Design
- [Icon/Button Style Guide](guides/ui-design)
- [Icon Placement Rules](sprints/sprint21/ICON_PLACEMENT_RULES.md)
- [Icon System Verification](features/ICON_SYSTEM_VERIFICATION.md)

### Testing
- [Test Organization](guides/testing)
- [Pytest Markers](testing/PYTEST_MARKERS_GUIDE.md)
- [Vision Checklist](features/vision/VISION_MENU_CHECKLIST.md)

## 📊 Statistics

### Sprint 23 Metrics (Latest)
- **13 commits** on feature branch
- **2,142 lines** added (5 new files)
- **119 tests** passing (108 unit + 11 integration)
- **4 batches** completed (Detection, Overlay, App, Testing)
- **~9.5 hours** total implementation time
- **Performance**: <150ms latency, 10 FPS detection

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
- **Sprint 23 Phase 7**:
  - MonsterDetector: 616 lines (42 tests)
  - OverlayController: 424 lines (34 tests)
  - BotManager: 420 lines (32 tests)
  - Integration tests: 343 lines (11 tests)
  - Demo script: 339 lines
  - Total: 2,142 lines, 119 tests ✅

- **Sprint 22**:
  - Vision engine: 810 lines
  - Vision Wizard UI: 1,259 lines
  - Worker threads: ~200 lines
  - Tests: 7 test cases
  - Performance: 15 FPS processing rate

## 🔄 Recent Changes (October 24, 2025)

### Sprint 23 Phase 7 Completion ✅
- ✅ MonsterDetector with background detection loop (616 lines, 42 tests)
- ✅ OverlayController for detection visualization (424 lines, 34 tests)
- ✅ BotManager facade for component coordination (420 lines, 32 tests)
- ✅ App integration with configuration system
- ✅ Integration test suite (11 tests passing)
- ✅ Interactive demo script with 3 demonstrations
- ✅ Complete documentation (plan + completion summary)
- ✅ All 119 tests passing (100% pass rate)
- ✅ Performance targets exceeded (~120ms latency, 10 FPS)

### Documentation Reorganization (October 22, 2025) ✅ COMPLETED
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
