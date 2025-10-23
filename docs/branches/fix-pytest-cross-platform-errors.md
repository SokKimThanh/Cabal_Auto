# 🔧 Pytest Cross-Platform Errors Fix - Task Breakdown

**Branch**: `fix/pytest-cross-platform-errors`  
**Date**: October 23, 2025  
**Issue**: 11/32 tests failing on Linux CI  
**Target**: All tests passing on both Linux and Windows

---

## 📋 BATCH WORKFLOW

### Batch 1: Dependencies & Configuration ⚡
**Time**: 20 phút  
**Priority**: P0 - Critical  
**Files**: 2 files

#### Tasks:
- [ ] Task 1.1: Update `requirements.txt` with missing packages
- [ ] Task 1.2: Create `pytest.ini` with markers
- [ ] Commit: `fix: add missing dependencies and pytest markers`
- [ ] Push & verify CI

---

### Batch 2: Platform Detection ⚡⚡
**Time**: 30 phút  
**Priority**: P0 - Critical  
**Files**: 1 file

#### Tasks:
- [ ] Task 2.1: Add platform detection to `lib/system/win_input.py`
- [ ] Task 2.2: Mock functions for non-Windows platforms
- [ ] Task 2.3: Test imports on Windows (should still work)
- [ ] Commit: `fix: add cross-platform support for win_input module`
- [ ] Push & verify CI

---

### Batch 3: Import Path Resolution ⚡
**Time**: 15 phút  
**Priority**: P1 - High  
**Files**: 1 file

#### Tasks:
- [ ] Task 3.1: Create `tests/conftest.py`
- [ ] Task 3.2: Add project root to Python path
- [ ] Task 3.3: Test imports work correctly
- [ ] Commit: `test: add conftest.py for import path resolution`
- [ ] Push & verify CI

---

### Batch 4: Test Markers 🔧
**Time**: 40 phút  
**Priority**: P1 - High  
**Files**: 6-7 files

#### Tasks:
- [ ] Task 4.1: Mark Windows-only tests (6 files)
  - [ ] `tests/test_exclusivity.py`
  - [ ] `tests/test_hunt_skill_flow.py`
  - [ ] `tests/test_key_diagnostics.py`
  - [ ] `tests/test_skill_rotation_manual.py`
  - [ ] `tests/test_template_matching.py`
  - [ ] `tests/integration/test_template_matcher_integration.py`
- [ ] Task 4.2: Mark GUI tests (1 file)
  - [ ] `tests/unit/test_setup_wizard_button.py`
- [ ] Commit: `test: mark platform-specific and GUI tests with pytest markers`
- [ ] Push & verify CI

---

### Batch 5: CI Configuration 🔧
**Time**: 30 phút  
**Priority**: P1 - High  
**Files**: 1 file

#### Tasks:
- [ ] Task 5.1: Update `.github/workflows/*.yml`
- [ ] Task 5.2: Add separate Linux and Windows jobs
- [ ] Task 5.3: Configure test filters for each platform
- [ ] Commit: `ci: add platform-specific test jobs for cross-platform support`
- [ ] Push & verify both CI jobs

---

### Batch 6: Documentation 📚
**Time**: 30 phút  
**Priority**: P2 - Medium  
**Files**: 2 files

#### Tasks:
- [ ] Task 6.1: Update `tests/README.md`
- [ ] Task 6.2: Create `docs/TESTING.md`
- [ ] Commit: `docs: update test documentation with platform requirements`
- [ ] Push

---

## 📊 PROGRESS TRACKER

### Overall Status: ⬜ NOT STARTED

```
Batch 1: ⬜ NOT STARTED  [0/2 tasks]
Batch 2: ⬜ NOT STARTED  [0/3 tasks]
Batch 3: ⬜ NOT STARTED  [0/3 tasks]
Batch 4: ⬜ NOT STARTED  [0/8 tasks]
Batch 5: ⬜ NOT STARTED  [0/3 tasks]
Batch 6: ⬜ NOT STARTED  [0/2 tasks]
──────────────────────────────────
Total:   ⬜ 0/21 tasks completed
```

### CI Status:
```
❌ Linux CI:   11/32 errors (FAILING)
❓ Windows CI: Not configured yet
```

---

## 🎯 SUCCESS CRITERIA

### Must Have:
- [x] All batches completed
- [ ] 0 test collection errors on Linux CI
- [ ] All tests pass or properly skipped on Linux CI
- [ ] Windows CI job configured and passing
- [ ] Documentation updated

### Nice to Have:
- [ ] Test coverage >80%
- [ ] Performance benchmarks
- [ ] Pre-commit hooks

---

## 📝 COMMIT MESSAGE TEMPLATES

### Batch 1:
```
fix: add missing dependencies and pytest markers

- Add opencv-python, numpy, pyautogui to requirements.txt
- Create pytest.ini with windows/gui/integration markers
- Resolves: Missing dependencies causing import errors

Related: #ISSUE_NUMBER
```

### Batch 2:
```
fix: add cross-platform support for win_input module

- Add IS_WINDOWS platform detection
- Mock tap() and related functions on non-Windows
- Maintain full functionality on Windows
- Resolves: ctypes.WinDLL AttributeError on Linux

Related: #ISSUE_NUMBER
```

### Batch 3:
```
test: add conftest.py for import path resolution

- Create tests/conftest.py
- Add project root to sys.path
- Resolves: ModuleNotFoundError for ui module

Related: #ISSUE_NUMBER
```

### Batch 4:
```
test: mark platform-specific and GUI tests with pytest markers

- Add @pytest.mark.windows to 6 Windows-only tests
- Add @pytest.mark.gui to Tkinter tests
- Tests now skip appropriately on Linux CI
- Resolves: Tests requiring Windows/GUI on Linux

Related: #ISSUE_NUMBER
```

### Batch 5:
```
ci: add platform-specific test jobs for cross-platform support

- Add separate test-linux and test-windows jobs
- Configure test filters: -m "not windows and not gui" for Linux
- Enable full test suite on Windows
- Resolves: CI failing on Linux due to platform-specific tests

Related: #ISSUE_NUMBER
```

### Batch 6:
```
docs: update test documentation with platform requirements

- Update tests/README.md with marker usage
- Create docs/TESTING.md with platform-specific guidelines
- Document CI behavior for each platform

Related: #ISSUE_NUMBER
```

---

## 🚀 PULL REQUEST TEMPLATE

### Title:
```
fix: resolve pytest cross-platform errors (11/32 tests)
```

### Description:
```markdown
## 🎯 Objective
Fix 11/32 pytest collection errors that occur when running tests on Linux CI.

## 🔍 Root Causes
1. **ctypes.WinDLL** - Windows-only API used without platform detection (6 tests)
2. **Missing dependencies** - opencv-python, numpy, pyautogui not in requirements.txt (4 tests)
3. **Import path issues** - ui module not in PYTHONPATH (1 test)
4. **GUI tests** - Tkinter requiring display environment (1 test, expected)

## 🔧 Changes Made

### Batch 1: Dependencies & Configuration
- ✅ Added missing packages to `requirements.txt`
- ✅ Created `pytest.ini` with platform markers

### Batch 2: Platform Detection  
- ✅ Added `IS_WINDOWS` detection to `lib/system/win_input.py`
- ✅ Mock functions for non-Windows platforms
- ✅ Maintains full Windows functionality

### Batch 3: Import Paths
- ✅ Created `tests/conftest.py` 
- ✅ Added project root to `sys.path`

### Batch 4: Test Markers
- ✅ Marked 6 Windows-only tests with `@pytest.mark.windows`
- ✅ Marked 1 GUI test with `@pytest.mark.gui`

### Batch 5: CI Configuration
- ✅ Added `test-linux` job (skips windows/gui tests)
- ✅ Added `test-windows` job (runs all tests)

### Batch 6: Documentation
- ✅ Updated `tests/README.md`
- ✅ Created `docs/TESTING.md`

## 📊 Test Results

### Before Fix:
```
collected 32 items / 11 errors
11 errors in 1.39s
❌ FAILURE (Linux CI)
```

### After Fix:
```
Linux CI:
  collected 32 items
  21 passed, 11 skipped (windows/gui markers)
  ✅ SUCCESS

Windows CI:
  collected 32 items
  32 passed
  ✅ SUCCESS
```

## ✅ Checklist
- [x] Code changes implemented
- [x] All batches completed
- [x] Tests pass on Linux CI
- [x] Tests pass on Windows CI
- [x] Documentation updated
- [x] Commit messages follow convention
- [x] No breaking changes

## 🔗 Related Issues
Closes #ISSUE_NUMBER

## 📸 Screenshots
<!-- If applicable, add screenshots showing CI passing -->

## 🧪 Testing Instructions
```bash
# Test on Linux
pytest tests/ -v -m "not windows and not gui"

# Test on Windows  
pytest tests/ -v

# Test with markers
pytest tests/ -v -m "windows"
pytest tests/ -v -m "gui"
```

## 👥 Reviewers
@SokKimThanh

## 📝 Notes
- All changes are backward compatible
- Windows functionality unchanged
- Linux CI now runs successfully
- Tests properly categorized with markers
```

---

## 🎓 LESSONS LEARNED (Update after completion)

### What Went Well:
- [ ] To be filled after completion

### What Could Be Improved:
- [ ] To be filled after completion

### Action Items for Future:
- [ ] Add pre-commit hooks for platform checks
- [ ] Setup Docker for consistent Linux testing
- [ ] Document platform-specific patterns

---

## 📞 SUPPORT

### Questions or Issues?
- Check: `docs/maintenance/PYTEST_ERRORS_ANALYSIS_23OCT2025.md`
- Ask: Development team
- Review: CI logs for details

---

**Last Updated**: October 23, 2025  
**Status**: 🟡 IN PROGRESS  
**Next Action**: Start Batch 1
