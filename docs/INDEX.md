# Documentation Index

Tổ chức tài liệu dự án Cabal Auto - Organized October 19, 2025

## 📁 Cấu trúc thư mục / Folder Structure

```
docs/
├── README.md                           # Tổng quan dự án / Project overview
├── INDEX.md                            # File này / This file
├── HUONG_DAN_NGUOI_MOI.md             # Hướng dẫn người mới / Beginner guide
├── HOW_TO_USE_TEST_RECOGNITION.md     # Hướng dẫn test nhận diện / Recognition testing guide
├── PROJECT_REORGANIZATION.md          # Tổng quan tổ chức lại dự án / Project reorganization overview
├── PROJECT_REORGANIZATION_SUMMARY.md  # Tóm tắt tổ chức lại dự án / Project reorganization summary
├── PROJECT_SUMMARY.py                 # Script tạo tóm tắt dự án / Project summary generator
├── SESSION_SUMMARY_2025-10-18.md      # Tóm tắt phiên làm việc / Session summary
├── CONTEXT_UPDATE_SPRINT18_PHASE4.md  # Cập nhật ngữ cảnh Sprint 18 Phase 4 / Context update
│
├── sprints/                            # Tài liệu các Sprint
│   ├── sprint15/
│   │   ├── SPRINT15_COMPLETE.md
│   │   ├── SPRINT15_SUMMARY.txt
│   │   ├── sprint15_demo.py
│   │   └── ...
│   │
│   ├── sprint16/                       # Sprint 16 - UI Redesign
│   │   ├── REDESIGN_PROPOSAL_SPRINT16.md
│   │   ├── SPRINT16_QUICK_REFERENCE.md
│   │   ├── SPRINT16_BUGFIX_WIZARD_AUTOLAUNCH.md
│   │   ├── SPRINT16_BUGFIX_WIZARD_CRASH.md
│   │   ├── SPRINT16_PLANNING_SUMMARY.md
│   │   ├── SPRINT16_TASK1_IMPLEMENTATION.md
│   │   ├── SPRINT16_TASK2_IMPLEMENTATION.md
│   │   ├── SPRINT16_TASK3_IMPLEMENTATION.md
│   │   ├── SPRINT16_TASK4_IMPLEMENTATION.md
│   │   ├── SPRINT16_TASK5_IMPLEMENTATION.md
│   │   └── SPRINT16_UX_WIZARD_IMPROVEMENTS.md
│   │
│   └── sprint18/                       # Sprint 18 - 4-Tab Reorganization
│       ├── SPRINT17_PHASE3_MULTIMOB.md          # Multi-monster support (Phase 3)
│       ├── SPRINT18_PHASE4_TAB_REORGANIZATION.md # 4-tab redesign overview
│       ├── SPRINT18_PHASE4_PROGRESS_1.md        # Progress tracking
│       ├── SPRINT18_PHASE4_TASK2_COMPLETE.md    # Hunt Tab refactor
│       ├── SPRINT18_PHASE4_TASK3_COMPLETE.md    # Setup Tab creation
│       └── WINDOW_SELECTION_UX_ENHANCEMENT.md   # Window selection UX improvement
│
├── bugfixes/                           # Tài liệu sửa lỗi / Bug fix documentation
│   ├── BUGFIX_IMAGE_PREVIEW_SIZE.md
│   ├── BUGFIX_SESSION_SUMMARY.md
│   ├── BUGFIX_SETUP_APPLY_SETTINGS.md
│   ├── BUGFIX_HUNT_START_OPENCV_LOGGER.md
│   ├── BUGFIX_TIMING_RECOMMENDATION_UX.md
│   └── BUGFIX_TIMING_UNHASHABLE_DICT.md
│
├── ux-enhancements/                    # Cải tiến UX / UX improvements
│   ├── UX_ENHANCEMENT_SMART_MONSTER_INPUT.md
│   ├── UX_FIX_PIL_MISSING_ERROR.md
│   └── WIZARD_AUTO_LAUNCH.md
│
└── translations/                       # Tài liệu dịch thuật / Translation documentation
    ├── TRANSLATION_COMPLETION_PIL_FIX.md
    ├── TRANSLATION_QUICK_SUMMARY.md
    ├── PIL_FIX_QUICK_REF.md
    ├── PIL_FIX_SUMMARY.md
    └── CONTEXT_UPDATE_SUMMARY_PIL_FIX.md
```

## 📚 Tài liệu chính / Main Documents

### Hướng dẫn sử dụng / User Guides
- **[HUONG_DAN_NGUOI_MOI.md](HUONG_DAN_NGUOI_MOI.md)** - Hướng dẫn người mới bắt đầu
- **[HOW_TO_USE_TEST_RECOGNITION.md](HOW_TO_USE_TEST_RECOGNITION.md)** - Cách test nhận diện template
- **[ADVANCED_WINDOW_SETTINGS_GUIDE.md](ADVANCED_WINDOW_SETTINGS_GUIDE.md)** - Giải thích chi tiết Advanced Window Settings ⭐ **New**
- **[README.md](README.md)** - Tổng quan dự án

### Ngữ cảnh dự án / Project Context
- **[CONTEXT_AUTO_CABAL.md](CONTEXT_AUTO_CABAL.md)** - Tóm tắt ngữ cảnh dự án (cập nhật từ Ngữ cảnh tạo auto cabal.txt)

### Tổng quan dự án / Project Overview
- **[PROJECT_REORGANIZATION.md](PROJECT_REORGANIZATION.md)** - Chi tiết tổ chức lại dự án
- **[PROJECT_REORGANIZATION_SUMMARY.md](PROJECT_REORGANIZATION_SUMMARY.md)** - Tóm tắt tổ chức lại
- **[SESSION_SUMMARY_2025-10-18.md](SESSION_SUMMARY_2025-10-18.md)** - Tóm tắt phiên làm việc gần nhất

## 🚀 Sprint Documentation (Chronological)

### Sprint 21 - System Enhancements & Refinements ✅
**Mục tiêu**: Cải tiến UX dựa trên user feedback - window auto-detection, keyboard shortcuts, prerequisites validation

**Tài liệu**:
- [SPRINT21_SUMMARY.md](SPRINT21_SUMMARY.md) - 📘 COMPLETE SUMMARY
  - ✅ PATCH 1: Codebase Analysis
  - ✅ PATCH 2: Window Auto-Detection cho First Run
  - ✅ PATCH 3: Keyboard Shortcuts Update (Alt+Shift+Z, Z key)
  - ✅ PATCH 4: Combat System Verification (skill rotation)
  - ⚠️ PATCH 5: Target Lock (DEFERRED to Sprint 22)
  - ✅ PATCH 6: Auto Mode Prerequisites Validation
  - ✅ PATCH 7: UI Contrast & Color Consistency
  - ✅ PATCH 8: Documentation & Summary

**Key Changes**:
- 🪟 Auto-detect Cabal window by PID when user skips wizard
- ⌨️ New shortcuts: `Alt+Shift+Z` (toggle hunt), `Z` (target switch)
- ✅ Prerequisites check prevents invalid hunt starts
- 🎨 100% button style consistency

**Tiến độ**: 6/8 patches complete (75%), 1 deferred, 1 documentation

### Sprint 19 - Library Manager (Monster/Skill/Timing)
**Mục tiêu**: Hoàn thiện Library Manager với 3 tab (Quái Vật, Kỹ Năng, Tính Toán Thời Gian), phục vụ cấu hình và tính toán timing áp dụng cho Hunt.

**Tài liệu**:
- [SPRINT19_CONTEXT_UPDATE.md](sprints/sprint19/SPRINT19_CONTEXT_UPDATE.md) - Tổng hợp tiến độ Sprint 19 (Tasks 1, 2, 2.5 hoàn tất; hôm nay tiếp tục chỉnh sửa màn hình Quái Vật)
- [SPRINT19_TASK1_COMPLETE.md](sprints/sprint19/SPRINT19_TASK1_COMPLETE.md) - Khung cửa sổ Library Manager
- [SPRINT19_TASK2_COMPLETE.md](sprints/sprint19/SPRINT19_TASK2_COMPLETE.md) - Tab Thư viện Quái Vật (core)
- [SPRINT19_TASK2.5_COMPLETE.md](sprints/sprint19/SPRINT19_TASK2.5_COMPLETE.md) - Hộp thoại Add/Edit Quái Vật
- [SPRINT19_TASK2.5_FINAL_SUMMARY.md](sprints/sprint19/SPRINT19_TASK2.5_FINAL_SUMMARY.md) - Tổng kết Task 2.5
- [SPRINT19_TASK2_COMPLETE.md](sprints/sprint19/SPRINT19_TASK2_COMPLETE.md) - Hoàn tất Tab Quái Vật
- [SPRINT19_TASK2.6_CARD_REDESIGN.md](sprints/sprint19/SPRINT19_TASK2.6_CARD_REDESIGN.md) - Redesign card UI
- [SPRINT19_TASK2.6_REDESIGN.md](sprints/sprint19/SPRINT19_TASK2.6_REDESIGN.md) - Phác thảo redesign
- [SPRINT19_TASK2.6_COMPLETE.md](sprints/sprint19/SPRINT19_TASK2.6_COMPLETE.md) - Hoàn tất redesign UI
- [CODE_REVIEW_TASK2.5.md](sprints/sprint19/CODE_REVIEW_TASK2.5.md) - Code review Task 2.5
- [SESSION_SUMMARY_REVIEW_TESTING.md](sprints/sprint19/SESSION_SUMMARY_REVIEW_TESTING.md) - Tổng hợp review + testing

**Tiến độ**: Đang tiếp tục (hôm nay có chỉnh sửa màn hình Quái Vật để phục vụ tính timing)

### Sprint 18 - 4-Tab UI Reorganization
**Mục tiêu**: Tổ chức lại giao diện thành 4 tab (Hunt, Setup, Stats, Help) để dễ sử dụng hơn

**Tài liệu**:
- [SPRINT18_PHASE4_TAB_REORGANIZATION.md](sprints/sprint18/SPRINT18_PHASE4_TAB_REORGANIZATION.md) - Tổng quan 4-tab redesign
- [SPRINT18_PHASE4_TASK2_COMPLETE.md](sprints/sprint18/SPRINT18_PHASE4_TASK2_COMPLETE.md) - Refactor Hunt Tab
- [SPRINT18_PHASE4_TASK3_COMPLETE.md](sprints/sprint18/SPRINT18_PHASE4_TASK3_COMPLETE.md) - Create Setup Tab
- [WINDOW_SELECTION_UX_ENHANCEMENT.md](sprints/sprint18/WINDOW_SELECTION_UX_ENHANCEMENT.md) - Window selection UX improvement
- [SPRINT17_PHASE3_MULTIMOB.md](sprints/sprint18/SPRINT17_PHASE3_MULTIMOB.md) - Multi-monster support (Phase 3)

**Tiến độ**: 75% complete (6/8 tasks done)

### Sprint 16 - UI Redesign & Wizard
**Mục tiêu**: Redesign giao diện và cải thiện wizard cho người mới

**Tài liệu**:
- [REDESIGN_PROPOSAL_SPRINT16.md](sprints/sprint16/REDESIGN_PROPOSAL_SPRINT16.md) - Đề xuất redesign
- [SPRINT16_QUICK_REFERENCE.md](sprints/sprint16/SPRINT16_QUICK_REFERENCE.md) - Tham khảo nhanh
- [SPRINT16_TASK1-5_IMPLEMENTATION.md](sprints/sprint16/) - 5 tasks implementation
- [SPRINT16_UX_WIZARD_IMPROVEMENTS.md](sprints/sprint16/SPRINT16_UX_WIZARD_IMPROVEMENTS.md) - Cải tiến wizard

**Trạng thái**: ✅ Complete

### Sprint 15 & Earlier
Xem thư mục [sprints/](sprints/) để tìm tài liệu các sprint cũ hơn

## 🐛 Bug Fixes (Sprint 18 Phase 4)

- [BUGFIX_IMAGE_PREVIEW_SIZE.md](bugfixes/BUGFIX_IMAGE_PREVIEW_SIZE.md) - Sửa lỗi preview image size
- [BUGFIX_SESSION_SUMMARY.md](bugfixes/BUGFIX_SESSION_SUMMARY.md) - Tóm tắt các bugfix
- [BUGFIX_SETUP_APPLY_SETTINGS.md](bugfixes/BUGFIX_SETUP_APPLY_SETTINGS.md) - Sửa lỗi apply settings (translation access)
- [BUGFIX_HUNT_START_OPENCV_LOGGER.md](bugfixes/BUGFIX_HUNT_START_OPENCV_LOGGER.md) - Sửa lỗi OpenCV missing + logger parameters
- [BUGFIX_TIMING_RECOMMENDATION_UX.md](bugfixes/BUGFIX_TIMING_RECOMMENDATION_UX.md) - Cải tiến UX timing recommendation (skill filtering, visual feedback, z-order)
- [BUGFIX_TIMING_UNHASHABLE_DICT.md](bugfixes/BUGFIX_TIMING_UNHASHABLE_DICT.md) - Sửa lỗi unhashable dict (skill_slots data structure) ⭐ **Latest**

## ✨ UX Enhancements

- [UX_ENHANCEMENT_SMART_MONSTER_INPUT.md](ux-enhancements/UX_ENHANCEMENT_SMART_MONSTER_INPUT.md) - Smart monster input
- [UX_FIX_PIL_MISSING_ERROR.md](ux-enhancements/UX_FIX_PIL_MISSING_ERROR.md) - Fix PIL missing error
- [WIZARD_AUTO_LAUNCH.md](ux-enhancements/WIZARD_AUTO_LAUNCH.md) - Wizard auto-launch

## 🌐 Translations

- [TRANSLATION_COMPLETION_PIL_FIX.md](translations/TRANSLATION_COMPLETION_PIL_FIX.md) - PIL fix translations
- [TRANSLATION_QUICK_SUMMARY.md](translations/TRANSLATION_QUICK_SUMMARY.md) - Tóm tắt translations
- [PIL_FIX_QUICK_REF.md](translations/PIL_FIX_QUICK_REF.md) - PIL fix reference
- [PIL_FIX_SUMMARY.md](translations/PIL_FIX_SUMMARY.md) - PIL fix summary

## 📝 Quy ước đặt tên / Naming Conventions

- **SPRINT{N}_*.md** - Sprint documentation
- **TASK{N}_*.md** - Task implementation details
- **BUGFIX_*.md** - Bug fix documentation
- **UX_*.md** - UX enhancement documentation
- **TRANSLATION_*.md** - Translation documentation
- **PIL_*.md** - PIL/Pillow related documentation

## 🔍 Tìm tài liệu / Finding Documentation

### Theo chức năng / By Feature
- **Multi-monster hunting** → `sprints/sprint18/SPRINT17_PHASE3_MULTIMOB.md`
- **4-tab UI** → `sprints/sprint18/SPRINT18_PHASE4_TAB_REORGANIZATION.md`
- **Setup wizard** → `sprints/sprint16/SPRINT16_UX_WIZARD_IMPROVEMENTS.md`
- **Window selection** → `sprints/sprint18/WINDOW_SELECTION_UX_ENHANCEMENT.md`
- **Smart input** → `ux-enhancements/UX_ENHANCEMENT_SMART_MONSTER_INPUT.md`

### Theo thời gian / By Date
1. **Sprint 15** - Multi-monster foundation
2. **Sprint 16** - UI Redesign & Wizard
3. **Sprint 17 Phase 3** - Multi-monster completion
4. **Sprint 18 Phase 4** - 4-tab reorganization (current)

## 📊 Thống kê / Statistics

- **Tổng số file tài liệu**: ~42 files (+2 new)
- **Sprints hoàn thành**: 3 (Sprint 15, 16, 17)
- **Sprint hiện tại**: Sprint 18 Phase 4 (75% complete)
- **Bug fixes (Sprint 18)**: 5 critical bugs fixed
- **Ngôn ngữ hỗ trợ**: English, Tiếng Việt

---

**Cập nhật lần cuối / Last Updated**: October 19, 2025 (Afternoon)  
**Người tổ chức / Organized By**: AI Assistant
**Latest Changes**: Added Sprint 19 section and links; clarified chronological ordering; noted Monster UI changes today.
