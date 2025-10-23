# Test Violations Fix Checklist

## 🎯 Priority 1: Tests Causing CI Failures

### ✅ FIXED
- [x] `tests/vision/vision_basic_test.py` - Missing fixtures (5 errors in CI)
  - Added pytest fixtures: engine, samples_dir, template_path, frame_path, frame, detections
  - Removed return statements
  - Converted to proper pytest tests

## 🔧 Priority 2: Tests Returning Values (11 files)

### Files to Fix:
- [ ] `tests/sprints/sprint22/test_training_mode.py` (5 test functions)
  - test_database_schema() - returns True/False
  - test_skill_stats_class() - returns True/False
  - test_i18n_translations() - returns True/False
  - test_hunt_config_schema() - returns True/False
  - test_file_structure() - returns True/False
  
- [ ] `tests/unit/test_advanced_monster_dialog.py` (5 test functions)
  - Returns list[] instead of using asserts
  
- [ ] `tests/unit/test_setup_wizard.py`
  - test_data_paths() - returns True

## 📌 Priority 3: Missing Markers (5 files)

### Files Needing GUI Markers:
- [ ] `tests/unit/test_language_persistence.py`
- [ ] `tests/unit/test_rotation_skills_loading.py`  
- [ ] `tests/unit/test_setup_wizard.py`
- [ ] `tests/unit/test_setup_wizard_skill_rotation.py`
- [ ] `tests/unit/test_wizard_first_run_lock.py`

**Fix Pattern:**
```python
import pytest
pytestmark = [pytest.mark.gui, pytest.mark.windows]

if sys.platform != "win32":
    pytest.skip("Requires Windows GUI", allow_module_level=True)
```

## 🔍 Priority 4: Missing Pytest Import (6 files)

### Files Missing pytest:
- [ ] `tests/unit/test_advanced_monster_dialog.py`
- [ ] `tests/unit/test_attack_keys_migration.py`
- [ ] `tests/unit/test_combobox_data.py`
- [ ] `tests/unit/test_rotation_skills_loading.py`
- [ ] `tests/unit/test_timing_calculator_ui.py`
- [ ] `tests/sprints/sprint22/test_training_mode.py`

**Fix:** Add `import pytest` at the top

## ⚠️ Priority 5: Missing Assertions (13 test functions)

### Tests With No Assertions:
- [ ] test_combobox_data.py::test_data_loading
- [ ] test_dialog_save_icons.py::test_monster_dialog_icon (manual - OK)
- [ ] test_dialog_save_icons.py::test_skill_dialog_icon (manual - OK)
- [ ] test_language_persistence.py::test_language_persistence
- [ ] test_language_persistence.py::test_user_level_persistence
- [ ] test_rotation_skills_loading.py::test_rotation_tab_from_wizard
- [ ] test_rotation_skills_loading.py::test_rotation_tab_from_app
- [ ] test_setup_wizard_skill_rotation.py::test_setup_wizard
- [ ] test_timing_calculator_ui.py::test_ui_integration
- [ ] test_wizard_first_run_lock.py (4 test scenarios)

**Fix:** Add appropriate assert statements

## 🛡️ Priority 6: Unprotected GUI Import (1 file)

- [ ] `tests/unit/test_rotation_skills_loading.py` - Line 13
  - Module-level tkinter import without platform skip

## 📊 Statistics

- Total Violations: 36
- Fixed: 5 (vision_basic_test.py)
- Remaining: 31
- Files Affected: 11

## 🎯 Next Actions

1. Commit vision_basic_test.py fixes ✅
2. Fix test_training_mode.py (convert return True/False to assert)
3. Add pytest import to 6 files
4. Add GUI markers to 5 files
5. Add assertions to 13 test functions
6. Add platform skip to test_rotation_skills_loading.py

## 📝 Notes

- Manual GUI tests in test_dialog_save_icons.py are correctly marked with @pytest.mark.manual
- test_advanced_monster_dialog.py needs special attention (returns lists for reporting)
- All changes should follow PYTEST_TEMPLATE_CI_CD.md guidelines
