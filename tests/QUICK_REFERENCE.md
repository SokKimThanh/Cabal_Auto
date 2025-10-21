# Quick Reference - Tests Folder

**Quick navigation and common commands for the organized tests folder.**

---

## 📁 Folder Structure Quick View

```
tests/
├── unit/           # 18 files - Component tests
├── integration/    # 3 files - System tests  
├── demos/          # 7 files - Visual demos
├── utils/          # 2 files - Audit tools
└── sprints/
    └── sprint22/   # 1 file - Training mode
```

---

## ⚡ Quick Commands

### Run Specific Test Category

```powershell
# Unit tests
python -m pytest tests/unit/

# Integration tests  
python -m pytest tests/integration/

# Sprint 22 tests
python tests/sprints/sprint22/test_training_mode.py
```

### Run All Tests

```powershell
# PowerShell - Run everything
Get-ChildItem tests -Recurse -Filter "test_*.py" | ForEach-Object { python $_.FullName }
```

### Run Specific Test

```bash
# Example: Test setup wizard
python tests/unit/test_setup_wizard.py

# Example: Test training mode
python tests/sprints/sprint22/test_training_mode.py
```

---

## 🎯 Find Test By Feature

| Feature | Test Location |
|---------|---------------|
| **Setup Wizard** | `unit/test_setup_wizard*.py` |
| **Monster Rotation** | `unit/test_rotation*.py` |
| **Template Matching** | `unit/opencv_test.py`, `integration/test_template_matcher*.py` |
| **Training Mode** | `sprints/sprint22/test_training_mode.py` |
| **UI Components** | `unit/test_*_ui.py` |
| **Path Resolution** | `unit/test_*_path.py` |

---

## 🚀 Common Workflows

### Adding New Unit Test

```bash
# 1. Create test file in unit/
# tests/unit/test_my_feature.py

# 2. Run the test
python tests/unit/test_my_feature.py

# 3. Update README if needed
```

### Adding New Sprint Test

```bash
# 1. Create sprint folder (if doesn't exist)
mkdir tests/sprints/sprint23

# 2. Create test file
# tests/sprints/sprint23/test_new_feature.py

# 3. Run the test
python tests/sprints/sprint23/test_new_feature.py
```

### Running Demo for Visual Check

```bash
# Pick any demo from demos/
python tests/demos/demo_save_tooltip.py
```

---

## 📚 Full Documentation

For complete documentation, see [README.md](README.md)

For reorganization details, see `/docs/TESTS_REORGANIZATION_SUMMARY.md`

---

**Last Updated**: October 21, 2025
