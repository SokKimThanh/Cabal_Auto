# Project File Organization Guidelines

**Date**: October 19, 2025  
**Status**: Active Guidelines

---

## 📁 Directory Structure Standards

### Core Principle
**"Place test files in `tests/` directory"**

All test, demo, and audit scripts must be organized in the `tests/` directory, not in project root.

---

## 📂 Standard Directory Layout

```
E:\Cabal_Auto\
├── app_gui.py                  # Main application entry point
├── README.md                   # Project documentation
│
├── assets/                     # Static assets (images, icons)
│   └── images/
│       ├── icons/              # UI icons (.png, .ico)
│       ├── monsters/           # Monster templates
│       └── skills/             # Skill icons
│
├── data/                       # ❌ DEPRECATED - Use lib/data/
│
├── lib/                        # Core library modules
│   ├── data/                   # ✅ Configuration files (JSON)
│   │   ├── config.json
│   │   ├── hunt_config.json
│   │   ├── monsters.json
│   │   └── skills.json
│   ├── features/               # Feature modules
│   ├── i18n/                   # Internationalization
│   ├── system/                 # System utilities
│   ├── ui/                     # UI components
│   └── vision/                 # Computer vision modules
│
├── docs/                       # Documentation files
│   ├── bugfixes/               # Bug fix documentation
│   ├── sprints/                # Sprint summaries
│   ├── translations/           # Translation guides
│   └── ux-enhancements/        # UX improvement docs
│
├── scripts/                    # Utility scripts
│   ├── main.py
│   ├── main_skills.py
│   └── main_safe.py
│
├── tests/                      # ✅ ALL TEST FILES GO HERE
│   ├── test_*.py               # Unit/integration tests
│   ├── demo_*.py               # Demo/example scripts
│   └── audit_*.py              # Audit/verification scripts
│
├── ui/                         # UI modules (screens)
│   ├── auto_hunt.py
│   └── setup_wizard.py
│
├── tmp/                        # Temporary files
└── logs/                       # Log files
```

---

## 🎯 File Naming Conventions

### Test Files

**Pattern**: `test_<feature>.py`

**Examples**:
```
✅ tests/test_comprehensive_system.py
✅ tests/test_save_tooltip_dynamic.py
✅ tests/test_skill_capture_path.py
✅ tests/test_library_monster_path.py
✅ tests/test_image_paths.py
✅ tests/test_setup_wizard.py
✅ tests/test_rotation.py
✅ tests/test_phase3_comprehensive.py
✅ tests/test_advanced_monster_dialog.py
✅ tests/test_template_matcher_integration.py
```

**Don't**:
```
❌ test_something.py           # Root level
❌ root/test_*.py               # Wrong location
```

### Demo Files

**Pattern**: `demo_<feature>.py`

**Examples**:
```
✅ tests/demo_save_tooltip.py
✅ tests/demo_icon_loader.py      # Future
✅ tests/demo_skill_rotation.py   # Future
```

**Purpose**: Interactive demonstrations of features

### Audit Files

**Pattern**: `audit_<scope>.py`

**Examples**:
```
✅ tests/audit_data_paths.py
✅ tests/audit_icon_coverage.py   # Future
✅ tests/audit_i18n_keys.py       # Future
```

**Purpose**: Automated verification scripts

---

## 📋 Current Test Inventory

### Unit Tests (10 files)

| File | Purpose |
|------|---------|
| `test_comprehensive_system.py` | Full system integration test |
| `test_save_tooltip_dynamic.py` | Dynamic tooltip state test |
| `test_skill_capture_path.py` | Skill image capture path verification |
| `test_library_monster_path.py` | Library Manager monster path test |
| `test_image_paths.py` | Image path consolidation test |
| `test_setup_wizard.py` | Setup wizard data loading test |
| `test_rotation.py` | Skill rotation logic test |
| `test_phase3_comprehensive.py` | Phase 3 comprehensive test |
| `test_advanced_monster_dialog.py` | Advanced monster dialog test |
| `test_template_matcher_integration.py` | Template matcher integration test |

### Demo Scripts (1 file)

| File | Purpose |
|------|---------|
| `demo_save_tooltip.py` | Interactive save button tooltip demo |

### Audit Scripts (1 file)

| File | Purpose |
|------|---------|
| `audit_data_paths.py` | Data path consistency checker |

**Total**: 12 files in `tests/` directory

---

## ✅ Best Practices

### When Creating New Test Files

1. **Always create in `tests/` directory**
   ```python
   # ✅ CORRECT
   tests/test_new_feature.py
   
   # ❌ WRONG
   test_new_feature.py
   ```

2. **Use descriptive names**
   ```python
   # ✅ GOOD
   tests/test_icon_helper_fallback.py
   
   # ❌ BAD
   tests/test1.py
   tests/temp_test.py
   ```

3. **Add docstring header**
   ```python
   """Test icon helper fallback mechanism.
   
   This test verifies that icon_helper correctly falls back to:
   1. PNG when ICO unavailable
   2. Emoji when both unavailable
   """
   ```

4. **Include imports from project root**
   ```python
   import sys
   from pathlib import Path
   
   # Add project root to path
   sys.path.insert(0, str(Path(__file__).parent.parent))
   
   # Now import from lib/
   from lib.ui.icon_helper import IconHelper
   ```

### When Creating Demo Files

1. **Make them interactive**
   - Show visual feedback
   - Allow user interaction
   - Display results clearly

2. **Keep them simple**
   - Focus on one feature
   - Clear instructions
   - Easy to understand

3. **Example structure**:
   ```python
   """Demo: Feature Name
   
   This demo shows how [feature] works interactively.
   
   Usage:
       python tests/demo_feature.py
   """
   
   # Setup
   # Demo code
   # Interactive UI
   # Run loop
   ```

### When Creating Audit Files

1. **Make them comprehensive**
   - Check all relevant files
   - Report detailed findings
   - Suggest fixes

2. **Use clear output**
   - ✅ Success markers
   - ❌ Error markers
   - ⚠️  Warning markers
   - Summary section

3. **Example structure**:
   ```python
   """Audit: Scope Description
   
   This audit checks [what] across [where].
   
   Reports:
   - What's correct
   - What needs fixing
   - Recommendations
   """
   
   # Scan files
   # Analyze patterns
   # Report findings
   # Summarize
   ```

---

## 🚫 Common Mistakes to Avoid

### ❌ Wrong Locations

```
# DON'T put tests in root
E:\Cabal_Auto\test_something.py

# DON'T put tests in lib/
E:\Cabal_Auto\lib\test_something.py

# DON'T put tests in scripts/
E:\Cabal_Auto\scripts\test_something.py
```

### ✅ Correct Locations

```
# DO put tests in tests/
E:\Cabal_Auto\tests\test_something.py

# DO organize by category if needed
E:\Cabal_Auto\tests\unit\test_icon_helper.py
E:\Cabal_Auto\tests\integration\test_full_workflow.py
```

---

## 📝 Migration Checklist

If you find test files in wrong locations:

- [ ] Identify misplaced files
- [ ] Move to `tests/` directory
- [ ] Update import paths if needed
- [ ] Update documentation references
- [ ] Test execution still works
- [ ] Update .gitignore if needed
- [ ] Commit changes

---

## 🔍 Quick Check Commands

### Find all test files
```powershell
Get-ChildItem -Path . -Filter "test_*.py" -Recurse | Select-Object FullName
```

### Find tests in wrong location (root)
```powershell
Get-ChildItem -Path . -Filter "test_*.py" -File | Select-Object Name
# Should return empty if all correct
```

### List all files in tests/
```powershell
Get-ChildItem -Path tests\ -Filter "*.py" | Select-Object Name
```

### Count test files
```powershell
(Get-ChildItem -Path tests\ -Filter "*.py").Count
```

---

## 📊 Directory Health Metrics

### Current Status (October 19, 2025)

| Metric | Value | Status |
|--------|-------|--------|
| Test files in `tests/` | 12 | ✅ 100% |
| Test files in root | 0 | ✅ Perfect |
| Test files in other dirs | 0 | ✅ Perfect |
| Demo files in `tests/` | 1 | ✅ 100% |
| Audit files in `tests/` | 1 | ✅ 100% |

**Health Score**: 🟢 100% - All test files properly organized

---

## 🎓 Training Examples

### Example 1: Creating a New Test

```python
# File: tests/test_tooltip_performance.py
"""Test tooltip display performance.

Measures tooltip response time and memory usage.
"""
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.ui.tooltip import attach_i18n_tooltip

def test_tooltip_response_time():
    """Test tooltip appears within 500ms."""
    # Test implementation
    pass

if __name__ == '__main__':
    test_tooltip_response_time()
```

### Example 2: Creating a Demo

```python
# File: tests/demo_icon_themes.py
"""Demo: Icon theme switching.

Shows how to switch between light/dark icon themes.
"""
import sys
from pathlib import Path
import tkinter as tk

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.ui.icon_helper import IconHelper

class ThemeDemo:
    def __init__(self):
        # Demo implementation
        pass
    
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    demo = ThemeDemo()
    demo.run()
```

### Example 3: Creating an Audit

```python
# File: tests/audit_import_consistency.py
"""Audit: Import statement consistency.

Checks that all imports use consistent style.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def audit_imports():
    """Check import consistency across project."""
    # Audit implementation
    pass

if __name__ == '__main__':
    audit_imports()
```

---

## 📚 Related Documentation

- `tests/README.md` - Test suite documentation
- `docs/PROJECT_REORGANIZATION.md` - Project structure changes
- `.gitignore` - Ignored files/directories

---

## 🔄 Maintenance

### Review Schedule

- **Weekly**: Check for misplaced test files
- **Monthly**: Review test coverage
- **Quarterly**: Update this guideline

### Continuous Integration

```yaml
# .github/workflows/test.yml (example)
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          cd tests
          python -m pytest
```

---

## ✅ Checklist for Code Review

When reviewing PRs:

- [ ] All test files in `tests/` directory?
- [ ] No test files in project root?
- [ ] Test file names follow convention?
- [ ] Imports from project root work?
- [ ] Documentation updated if needed?
- [ ] Tests actually run and pass?

---

**Remember**: 
🎯 **"Tests go in `tests/`"** - Simple rule, no exceptions!

Keep the project clean and organized for better maintainability.
