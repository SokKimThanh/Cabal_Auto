# Tests Directory

Thư mục này chứa tất cả các test scripts, demos và utilities cho dự án Cabal Auto.

## 📁 Cấu Trúc Thư Mục

```
tests/
├── unit/                          # ✅ Unit tests (pytest auto-run)
│   └── test_*.py                  # Real pytest unit tests
│
├── integration/                   # ✅ Integration tests (pytest auto-run)
│   └── test_*.py                  # Real pytest integration tests
│
├── manual/                        # 🔧 Manual test scripts (NOT pytest)
│   ├── gui/                       # GUI interactive tests
│   ├── integration/               # Manual integration tests
│   ├── features/                  # Feature testing scripts
│   ├── paths/                     # Path validation scripts
│   └── misc/                      # Other manual tests
│
├── demos/                         # 🎨 Demo scripts (not tests)
│   ├── sprints/                   # Sprint demos
│   └── features/                  # Feature demos
│
├── vision/                        # 👁️ Vision/CV tests
│   ├── opencv_test.py
│   ├── vision_basic_test.py
│   └── vision_perf_test.py
│
├── sprints/                       # 🏃 Sprint-specific tests
│   └── sprint*/
│
├── samples/                       # 📦 Sample data/fixtures
├── utils/                         # 🔧 Test utilities/helpers
└── README.md                      # This file
```

---

## 🧪 Unit Tests (`unit/`)

Automated tests run by pytest in CI/CD. Must follow pytest naming conventions.

### UI Components Tests
- **`test_combobox_data.py`** - ComboBox data loading và hiển thị
- **`test_dialog_save_icons.py`** - Dialog save icons functionality
- **`test_timing_calculator_ui.py`** - Timing calculator UI
- **`test_advanced_monster_dialog.py`** - Advanced monster dialog

### Setup Wizard Tests (Windows-only)
- **`test_setup_wizard.py`** - Main setup wizard functionality
- **`test_setup_wizard_skill_rotation.py`** - Skill rotation in wizard
- **`test_wizard_first_run_lock.py`** - First run lock mechanism
- **`test_language_persistence.py`** - Language setting persistence

### Data & Features Tests
- **`test_rotation_skills_loading.py`** - Skill rotation loading
- **`test_attack_keys_migration.py`** - Attack keys migration

**Run unit tests:**
```bash
pytest tests/unit/ -v
# Skip Windows/GUI tests on Linux
pytest tests/unit/ -v -m "not windows and not gui"
```

---

## 🔗 Integration Tests (`integration/`)

Tests that verify multiple components working together.

- **`test_template_matcher_integration.py`** - Template matcher unified module test

**Run integration tests:**
```bash
pytest tests/integration/ -v
```

---

## 🔧 Manual Tests (`manual/`)

Interactive test scripts that require human interaction. **NOT run by pytest.**

### GUI Tests (`manual/gui/`)
- **`manual_hunt_button_design.py`** - Hunt button UI design verification
- **`manual_setup_wizard_button.py`** - Wizard button behaviors
- **`manual_save_tooltip_dynamic.py`** - Dynamic save tooltips
- **`manual_topbar_enhancement.py`** - Topbar enhancements

### Feature Tests (`manual/features/`)
- **`manual_hunt_skill_flow.py`** - Hunt skill flow testing
- **`manual_key_diagnostics.py`** - Keyboard diagnostics
- **`manual_skill_rotation.py`** - Skill rotation manual testing
- **`manual_skill_rotation_ui.py`** - Skill rotation UI testing

### Path Validation (`manual/paths/`)
- **`manual_image_paths.py`** - Image path resolution
- **`manual_library_monster_path.py`** - Monster library paths
- **`manual_skill_capture_path.py`** - Skill capture paths
- **`manual_tooltip_and_image_refs.py`** - Tooltip image references

### Integration (`manual/integration/`)
- **`manual_comprehensive_system.py`** - Comprehensive system test
- **`manual_phase3_comprehensive.py`** - Phase 3 comprehensive test

### Misc (`manual/misc/`)
- **`manual_migration.py`** - Migration testing
- **`manual_rotation.py`** - Rotation logic
- **`manual_template_matching.py`** - Template matching verification

**Run manual tests:**
```bash
python tests/manual/gui/manual_hunt_button_design.py
```

---

## 👁️ Vision Tests (`vision/`)

Computer vision and template matching tests.

- **`opencv_test.py`** - OpenCV vs PyAutoGUI performance comparison
- **`vision_basic_test.py`** - Basic vision functionality
- **`vision_perf_test.py`** - Vision performance benchmarks
- **`README.md`** - Vision testing documentation

**Run vision tests:**
```bash
python tests/vision/opencv_test.py
python tests/vision/vision_basic_test.py
```

---

## 🎨 Demos (`demos/`)

Demonstration scripts showcasing features. **NOT tests.**

### Feature Demos (`demos/features/`)
- **`demo_dialog_save_icon.py`** - Dialog save icon demo
- **`demo_global_badge_relocation.py`** - Badge relocation demo
- **`demo_save_tooltip.py`** - Save tooltip demo
- **`demo_simple_language.py`** - Language switching demo
- **`demo_template_badge_timing.py`** - Template badge timing
- **`demo_template_save.py`** - Template save demo
- **`demo_vision_wizard_cleanup.py`** - Vision wizard cleanup
- **`demo_wizard_user_level.py`** - Wizard user level demo

### Sprint Demos (`demos/sprints/`)
- **`sprint13_demo.py`** - Sprint 13 features
- **`sprint14_demo.py`** - Sprint 14 features
- **`sprint15_demo.py`** - Sprint 15 features

**Run demos:**
```bash
python tests/demos/features/demo_save_tooltip.py
```

---

## 🏃 Sprint Tests (`sprints/`)

Tests organized by sprint iterations.

### Sprint 22 - Training Mode
- **`test_training_mode.py`** - Training mode functionality

---

## 🔧 Test Utilities (`utils/`)

Helper scripts for testing and auditing.

- **`audit_data_paths.py`** - Audit data file paths
- **`verify_wizard_changes.py`** - Verify wizard changes


**Run utilities:**
```bash
python tests/utils/audit_data_paths.py
python tests/utils/verify_wizard_changes.py
```

---

## 🚀 Running Tests

### Run All Pytest Tests
```bash
# Run all automated tests
pytest tests/ -v

# Skip Windows/GUI tests (for Linux CI)
pytest tests/ -v -m "not windows and not gui"

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/ --cov=lib --cov=ui --cov-report=term-missing
```

### Run Manual Tests
```bash
# GUI tests (Windows only)
python tests/manual/gui/manual_hunt_button_design.py

# Feature tests
python tests/manual/features/manual_hunt_skill_flow.py

# Path validation
python tests/manual/paths/manual_image_paths.py
```

### Run Vision Tests
```bash
python tests/vision/opencv_test.py
python tests/vision/vision_basic_test.py
```

### Run Demos
```bash
python tests/demos/features/demo_save_tooltip.py
python tests/demos/sprints/sprint13_demo.py
```

---

## 📝 Test Coverage

Current test coverage:
- ✅ OpenCV template matching
- ✅ PyAutoGUI template matching
- ✅ Template matcher integration
- ✅ Confidence value accuracy
- ✅ UI component functionality
- ✅ Setup wizard workflows
- ✅ Data loading and validation
- ⏳ Skills runtime (manual testing via demo scripts)
- ⏳ Hunt logger (manual testing during hunt)
- ⏳ Timing calculator (manual testing in GUI)

---

## ➕ Adding New Tests

When adding new test files:

### For Pytest Tests (unit/integration/)
1. **Name**: Start with `test_` prefix (e.g., `test_new_feature.py`)
2. **Markers**: Add appropriate markers (`@pytest.mark.windows`, `@pytest.mark.gui`)
3. **Platform checks**: Add skip conditions if Windows/GUI specific
4. **Docstrings**: Document what the test validates
5. **Assertions**: Use clear assertion messages

**Template:**
```python
import pytest
import sys

pytestmark = [pytest.mark.unit]  # or pytest.mark.integration

if sys.platform != "win32":  # if Windows-only
    pytest.skip("Requires Windows", allow_module_level=True)

def test_feature_name():
    """Test description."""
    result = your_function()
    assert result is not None, "Expected non-None result"
```

### For Manual Tests (manual/)
1. **Name**: Start with `manual_` prefix
2. **Location**: Choose appropriate subdirectory (gui/features/paths/misc)
3. **Documentation**: Add usage instructions at top
4. **No pytest**: These should NOT be collected by pytest

### For Demos (demos/)
1. **Name**: Start with `demo_` prefix
2. **Purpose**: Demonstrate feature, not test it
3. **Interactive**: Can include user interaction

**Update this README** with new test descriptions!

---

## 🎯 Test Best Practices

### General
- ✅ Keep tests independent (no shared state)
- ✅ Use descriptive test names (`test_should_load_config_when_file_exists`)
- ✅ Include clear error messages in assertions
- ✅ Test both success and failure cases
- ✅ Clean up resources (files, windows) in teardown

### Platform Compatibility
- ✅ Mark Windows-only tests: `@pytest.mark.windows`
- ✅ Mark GUI tests: `@pytest.mark.gui`
- ✅ Skip appropriately: `pytest.skip("reason", allow_module_level=True)`
- ✅ Handle optional imports gracefully

### CI/CD Considerations
- ✅ Tests should pass on headless Linux
- ✅ Use relative paths from project root
- ✅ Don't hardcode absolute paths
- ✅ Handle missing DISPLAY gracefully
- ✅ No module-level code that crashes on import

---

## 📚 Documentation

- **`PYTEST_TEMPLATE_CI_CD.md`** - Template for writing pytest tests
- **`QUICK_REFERENCE.md`** - Quick reference guide
- **`vision/README.md`** - Vision testing documentation

---

## 🔧 CI/CD Integration

Tests are run automatically in GitHub Actions:

```yaml
# .github/workflows/python-app.yml
- name: Test with pytest
  run: |
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    export DISPLAY=:99
    pytest -v --tb=short --strict-markers -m "not windows and not gui"
```

**Markers used in CI:**
- Skip `@pytest.mark.windows` tests on Linux
- Skip `@pytest.mark.gui` tests (no real display)
- Run `@pytest.mark.unit` and `@pytest.mark.integration`

---

## 📞 Support

For test-related questions:
1. Check `PYTEST_TEMPLATE_CI_CD.md` for templates
2. Review existing tests for examples
3. See `QUICK_REFERENCE.md` for common patterns
4. Contact development team

---

**Last Updated**: 2025-10-23  
**Maintainer**: Development Team
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
