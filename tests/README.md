# Tests Directory# Tests Directory



Thư mục này chứa tất cả các test scripts, demos và utilities cho dự án Cabal Auto.This directory contains all test scripts and test-related files.



## 📁 Cấu Trúc Thư Mục## Test Files



```### `opencv_test.py`

tests/Performance comparison test between OpenCV and PyAutoGUI template matching.

├── unit/              # Unit tests - Kiểm tra từng component riêng lẻ

├── integration/       # Integration tests - Kiểm tra tích hợp hệ thống**Features:**

├── demos/            # Demo scripts - Minh họa tính năng- Benchmarks OpenCV cv2.matchTemplate() vs PyAutoGUI

├── utils/            # Utility scripts - Công cụ audit/verify- Tests accuracy and performance

├── sprints/          # Sprint-specific tests - Test theo từng sprint- Shows confidence value comparison

│   └── sprint22/     # Sprint 22 tests (Training Mode, etc.)- Provides recommendations

└── README.md         # Tài liệu này

```**Usage:**

```bash

---python tests/opencv_test.py

```

## 🧪 Unit Tests (`unit/`)

### `test_template_matcher_integration.py`

Kiểm tra từng component/tính năng riêng lẻ.Integration test for the unified template_matcher module.



### UI Components**Features:**

- **`test_combobox_data.py`** - ComboBox data loading và hiển thị- Tests template_matcher.locate_template()

- **`test_dialog_save_icons.py`** - Dialog save icons functionality- Verifies OpenCV and PyAutoGUI integration

- **`test_hunt_button_design.py`** - Hunt button UI design- Checks confidence value accuracy

- **`test_topbar_enhancement.py`** - Topbar enhancements- Validates fallback behavior

- **`test_timing_calculator_ui.py`** - Timing calculator UI

**Usage:**

### Data & Paths```bash

- **`test_image_paths.py`** - Image path resolutionpython tests/test_template_matcher_integration.py

- **`test_library_monster_path.py`** - Monster library paths```

- **`test_skill_capture_path.py`** - Skill capture paths

## Running Tests

### Setup Wizard

- **`test_setup_wizard.py`** - Main setup wizard functionality### Run All Tests

- **`test_setup_wizard_button.py`** - Wizard button behaviors```bash

- **`test_setup_wizard_skill_rotation.py`** - Skill rotation in wizard# From project root

- **`test_wizard_first_run_lock.py`** - First run lock mechanismpython tests/opencv_test.py

python tests/test_template_matcher_integration.py

### Features```

- **`test_advanced_monster_dialog.py`** - Advanced monster dialog

- **`test_rotation.py`** - Monster rotation logic### Test Requirements

- **`test_rotation_skills_loading.py`** - Skill rotation loading- Template images in `assets/images/monsters/` or `assets/images/skills/`

- **`test_save_tooltip_dynamic.py`** - Dynamic save tooltips- OpenCV installed (`opencv-python`)

- **`test_language_persistence.py`** - Language setting persistence- PyAutoGUI installed

- PIL/Pillow installed

### Vision/Template Matching

- **`opencv_test.py`** - OpenCV performance testing## Test Coverage



### UsageCurrent test coverage:

```bash- ✅ OpenCV template matching

# Run single unit test- ✅ PyAutoGUI template matching

python tests/unit/test_combobox_data.py- ✅ Template matcher integration

- ✅ Confidence value accuracy

# Run all unit tests (PowerShell)- ⏳ Skills runtime (manual testing via demo scripts)

Get-ChildItem tests/unit/*.py | ForEach-Object { python $_.FullName }- ⏳ Hunt logger (manual testing during hunt)

```- ⏳ Timing calculator (manual testing in GUI)



---## Adding New Tests



## 🔗 Integration Tests (`integration/`)When adding new test files:

1. Name files with `test_` prefix

Kiểm tra tích hợp giữa nhiều components/modules.2. Include docstring explaining test purpose

3. Add usage instructions

### System Integration4. Update this README

- **`test_comprehensive_system.py`** - Comprehensive system integration test5. Consider adding to CI/CD pipeline (future)

- **`test_phase3_comprehensive.py`** - Phase 3 comprehensive testing

- **`test_template_matcher_integration.py`** - Template matcher integration## Test Best Practices



### Features- Keep tests independent

- Kiểm tra UI + Backend + Data flow- Use descriptive names

- Validate end-to-end workflows- Include clear error messages

- Test module interactions- Test both success and failure cases

- Document expected results

### Usage
```bash
# Run comprehensive system test
python tests/integration/test_comprehensive_system.py

# Run template matcher integration
python tests/integration/test_template_matcher_integration.py
```

---

## 🎨 Demo Scripts (`demos/`)

Scripts minh họa tính năng, dùng cho development và testing thủ công.

### Available Demos
- **`demo_dialog_save_icon.py`** - Dialog save icon functionality
- **`demo_global_badge_relocation.py`** - Global badge relocation feature
- **`demo_save_tooltip.py`** - Save tooltip demonstration
- **`demo_template_badge_timing.py`** - Template badge timing
- **`demo_template_save.py`** - Template save functionality
- **`demo_vision_wizard_cleanup.py`** - Vision wizard cleanup
- **`demo_wizard_user_level.py`** - Wizard user level selection

### Usage
```bash
# Run any demo
python tests/demos/demo_dialog_save_icon.py
```

**Note**: Demos may require manual interaction or visual inspection.

---

## 🛠️ Utilities (`utils/`)

Audit, verification, và maintenance scripts.

### Available Utilities
- **`audit_data_paths.py`** - Audit all data file paths in project
- **`verify_wizard_changes.py`** - Verify wizard implementation changes

### Usage
```bash
# Audit data paths
python tests/utils/audit_data_paths.py

# Verify wizard changes
python tests/utils/verify_wizard_changes.py
```

---

## 🚀 Sprint-Specific Tests (`sprints/`)

Tests được tổ chức theo từng sprint development.

### Sprint 22 (`sprints/sprint22/`)
- **`test_training_mode.py`** - Training Mode comprehensive test suite
  - Database schema validation
  - SkillStats class functionality
  - i18n translations
  - Hunt config schema
  - File structure validation

### Usage
```bash
# Run Sprint 22 tests
python tests/sprints/sprint22/test_training_mode.py
```

**Future Sprints**: Mỗi sprint mới sẽ có folder riêng trong `sprints/`.

---

## 📋 Test Categories

### By Type
| Category | Location | Purpose |
|----------|----------|---------|
| **Unit Tests** | `unit/` | Test individual components |
| **Integration Tests** | `integration/` | Test component interactions |
| **Demos** | `demos/` | Visual/manual testing |
| **Utilities** | `utils/` | Maintenance/verification |
| **Sprint Tests** | `sprints/` | Sprint-specific features |

### By Feature
| Feature | Test Files |
|---------|-----------|
| **Setup Wizard** | `unit/test_setup_wizard*.py`, `demos/demo_wizard*.py` |
| **Monster Management** | `unit/test_advanced_monster_dialog.py`, `unit/test_rotation*.py` |
| **Template Matching** | `unit/opencv_test.py`, `integration/test_template_matcher*.py` |
| **UI Components** | `unit/test_*_ui.py`, `demos/demo_*.py` |
| **Training Mode** | `sprints/sprint22/test_training_mode.py` |

---

## 🔧 Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install opencv-python pyautogui pillow pytest
```

### Run All Tests
```powershell
# PowerShell - Run all tests in all categories
Get-ChildItem tests -Recurse -Filter "test_*.py" | ForEach-Object { python $_.FullName }
```

### Run Specific Category
```bash
# Unit tests only
python -m pytest tests/unit/

# Integration tests only
python -m pytest tests/integration/

# Sprint 22 tests only
python tests/sprints/sprint22/test_training_mode.py
```

### Run Single Test
```bash
# Run specific test file
python tests/unit/test_combobox_data.py
```

---

## 📊 Test Coverage

### Current Coverage
- **Unit Tests**: 18 files
- **Integration Tests**: 3 files
- **Demos**: 7 files
- **Utilities**: 2 files
- **Sprint Tests**: 1 file (Sprint 22)

### Quality Metrics
- **Total Test Files**: 31+
- **Test Categories**: 5
- **Sprint Coverage**: Sprint 22 (100%)

---

## 🎯 Best Practices

### Writing New Tests

1. **Choose Correct Category**:
   - Component in isolation → `unit/`
   - Multiple components → `integration/`
   - Visual demo → `demos/`
   - Sprint feature → `sprints/sprintXX/`

2. **Naming Convention**:
   - Tests: `test_<feature_name>.py`
   - Demos: `demo_<feature_name>.py`
   - Utils: `<verb>_<noun>.py` (e.g., `audit_paths.py`)

3. **File Structure**:
   ```python
   # Header with description
   # Test functions with clear names
   # Main block for direct execution
   if __name__ == '__main__':
       run_tests()
   ```

4. **Documentation**:
   - Add docstring explaining test purpose
   - Document required setup/prerequisites
   - Include usage examples

### Adding New Sprint Tests

```bash
# Create new sprint folder
mkdir tests/sprints/sprint23

# Add test file
# tests/sprints/sprint23/test_new_feature.py
```

---

## 🐛 Debugging Tests

### Common Issues

1. **Import Errors**:
   ```bash
   # Run from project root
   cd e:\Cabal_Auto
   python tests/unit/test_name.py
   ```

2. **Path Issues**:
   - Tests assume execution from project root
   - Use absolute paths or `os.path` for file references

3. **Missing Assets**:
   - Ensure `assets/images/` contains required templates
   - Check `lib/data/` for required JSON files

---

## 📝 Changelog

### 2025-10-21 - Major Reorganization
- ✅ Created organized folder structure (5 categories)
- ✅ Moved 31+ test files to appropriate folders
- ✅ Added comprehensive README documentation
- ✅ Established naming conventions
- ✅ Created sprint-specific test structure

### Previous
- Mixed organization in single `tests/` folder
- Basic README with limited coverage

---

## 🔮 Future Enhancements

### Planned Improvements
- [ ] Add `pytest` configuration file
- [ ] Implement automated test runner script
- [ ] Add code coverage reporting
- [ ] Create CI/CD test pipeline
- [ ] Add performance benchmarking suite
- [ ] Expand integration test coverage

### Sprint 23 Planning
- [ ] Create `sprints/sprint23/` folder
- [ ] Add tests for upcoming features
- [ ] Maintain 100% sprint coverage

---

## 📚 Additional Resources

### Documentation
- Main project docs: `/docs/`
- Sprint 22 docs: `/docs/sprint22/`
- Project README: `/README.md`

### Related Folders
- Source code: `/lib/`
- UI components: `/ui/`
- Application: `/app_gui.py`

---

**Last Updated**: October 21, 2025  
**Maintained By**: Development Team  
**Project**: Cabal Auto v2.0
