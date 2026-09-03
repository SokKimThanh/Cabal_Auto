# 🧹 Session 3: Replace Nested Patch Chains

## 📋 Overview

| Aspect | Value |
|--------|-------|
| **Objective** | Convert nested `with patch()` chains to clean `@patch` decorators |
| **Duration** | 4-6 hours |
| **Effort** | 🟢 Low |
| **Impact** | 🟢 Low (readability improvement, ~3% mock reduction) |
| **Difficulty** | Easy (straightforward code transformation) |
| **Risk Level** | 🟢 Very Low (refactoring only, no behavior changes) |
| **Prerequisites** | None (can run parallel to Session 1-2) |
| **Files to Modify** | 3-5 files |

---

## 🎯 Objective

**Current Problem**:
```python
# Hard to read, hard to maintain:
def test_something():
    with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file), \
         patch('ui.windows.monster_manager_win.get_db', return_value=None), \
         patch('ui.windows.monster_manager_win.DataSyncManager', None), \
         patch('tkinter.messagebox.askyesno', return_value=True), \
         patch('database.find_monster_by_name_api', return_value=None):
        
        # Test code buried under 5 patch levels ❌
        result = some_function()
        assert result
```

**After Session 3**:
```python
# Clean, readable, Pythonic:
@patch('database.find_monster_by_name_api', return_value=None)
@patch('tkinter.messagebox.askyesno', return_value=True)
@patch('ui.windows.monster_manager_win.DataSyncManager', None)
@patch('ui.windows.monster_manager_win.get_db', return_value=None)
@patch('ui.windows.monster_manager_win.DATA_PATH')
def test_something(mock_data_path, mock_get_db, mock_sync, mock_confirm, mock_api):
    mock_data_path.value = temp_data_file
    # Test code at the proper indentation level ✅
    result = some_function()
    assert result
```

---

## 🔍 Problem Analysis

### Why Nested Patches Are Bad

1. **Deep Indentation**: Test code buried 5+ levels deep
   ```python
   with patch(...):           # Level 1
       with patch(...):       # Level 2
           with patch(...):   # Level 3
               with patch(...): # Level 4
                   # Test code here at Level 5 😱
   ```

2. **Hard to Read**: Can't see test intent without unwinding nesting
3. **Difficult to Modify**: Adding/removing a patch requires changing indentation
4. **Non-Standard**: Python convention is to use decorators for multiple patches
5. **Error-Prone**: Easy to add/remove wrong number of commas

### Current Problematic Files

```
tests/unit/ui/test_monster_editor_left_panel.py
├── Line 78: 3-4 level nested patches
├── Line 104: 3-4 level nested patches
├── Line 139: 3-4 level nested patches
└── Line 178-305: Multiple similar nested chains

tests/unit/ui/test_monster_editor_save.py
├── Multiple 3-4 level nested chains
└── Complex patch configurations

tests/unit/ui/test_monster_editor_data.py
├── Nested patches with multiple patches per with statement
└── Hard to track which mock corresponds to which parameter
```

---

## 💡 Solution Design

### Transformation Pattern

**Pattern 1: Convert to Decorators (Most Common)**
```python
# BEFORE: Nested with statements
def test_editor_save():
    with patch('path1', mock1), \
         patch('path2', mock2), \
         patch('path3', mock3):
        # Test code

# AFTER: Clean decorators
@patch('path3', mock3)        # Arguments reverse order!
@patch('path2', mock2)        # Bottom-most patch = leftmost parameter
@patch('path1', mock1)        # Top patch = rightmost parameter
def test_editor_save(mock1, mock2, mock3):
    # Clean, readable test code
```

**Pattern 2: Extract Fixture (For Complex Setup)**
```python
# BEFORE: Complex with chain in many tests
def test_one():
    with patch('path1'), \
         patch('path2'), \
         patch('path3'):
        # Test one code
        
def test_two():
    with patch('path1'), \
         patch('path2'), \
         patch('path3'):
        # Test two code

# AFTER: Shared fixture
@pytest.fixture
def common_patches(monkeypatch):
    with patch('path1'), \
         patch('path2'), \
         patch('path3'):
        yield

def test_one(common_patches):
    # Test one code
    
def test_two(common_patches):
    # Test two code
```

**Pattern 3: Use Parametrize (For Multiple Scenarios)**
```python
# BEFORE: Many similar tests with different patches
def test_scenario_a():
    with patch('config', {'mode': 'a'}):
        # Test A
        
def test_scenario_b():
    with patch('config', {'mode': 'b'}):
        # Test B

# AFTER: Parametrized
@pytest.mark.parametrize('config_mode', ['a', 'b'])
@patch('config')
def test_scenarios(mock_config, config_mode):
    mock_config.return_value = {'mode': config_mode}
    # Single test code for all scenarios
```

---

## 📁 Files to Update

### Target Files (with nested patches)
1. ✅ `tests/unit/ui/test_monster_editor_left_panel.py` - Multiple nested chains
2. ✅ `tests/unit/ui/test_monster_editor_save.py` - Complex patch setup
3. ✅ `tests/unit/ui/test_monster_editor_data.py` - Nested configurations
4. ✅ `tests/unit/ui/test_monster_editor_sprint25.py` - Some nested patches
5. ✅ `tests/unit/ui/test_monster_editor_tabs.py` - Minor nested patches

### Files to Check (might have chains)
- `tests/unit/db/test_db5c_audit.py`
- `tests/unit/db/test_db8_integrity.py`
- `tests/integration/test_monster_editor_flow.py`

---

## 🔧 Step-by-Step Implementation

### Step 1: Identify All Nested Patch Chains

```bash
# Find all multi-line patch chains in test files
grep -n "with patch.*,$" tests/unit/ui/test_monster_editor_*.py
```

Expected output:
```
tests/unit/ui/test_monster_editor_left_panel.py:78:        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file), \
tests/unit/ui/test_monster_editor_left_panel.py:79:             patch('ui.windows.monster_manager_win.get_db', return_value=None), \
```

### Step 2: Create Conversion Plan

For each nested chain, determine which pattern to use:

**Conversion Decision Tree:**
```
Nested Patch Chain
├── Is it used by multiple test functions?
│   ├── YES → Extract to fixture (Pattern 2)
│   └── NO → Continue
├── Are all patches related to the same feature?
│   ├── YES → Extract to fixture with @pytest.fixture
│   └── NO → Continue
├── Is it a simple patch without complex setup?
│   ├── YES → Convert to decorators (Pattern 1)
│   └── NO → Use helper function for setup
└── Add as decorator OR keep in fixture
```

### Step 3: Convert to Decorators - Example

**File**: `tests/unit/ui/test_monster_editor_left_panel.py`

**Before** (Nested):
```python
def test_add_skill_to_monster(self, tmp_path: Path, monkeypatch) -> None:
    temp_data_file = tmp_path / "test_data.json"
    temp_data_file.write_text("{}")
    
    with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file), \
         patch('ui.windows.monster_manager_win.get_db', return_value=None), \
         patch('ui.windows.monster_manager_win.DataSyncManager', None):
        
        # Test code here
        win = MonsterManagerWin(None, self.root)
        win.selected_monster = {"skills": []}
        win._on_add_skill()
        assert len(win.selected_monster["skills"]) == 1
```

**After** (Decorators):
```python
@patch('ui.windows.monster_manager_win.DataSyncManager', None)
@patch('ui.windows.monster_manager_win.get_db', return_value=None)
@patch('ui.windows.monster_manager_win.DATA_PATH')
def test_add_skill_to_monster(
    self,
    mock_data_path,
    mock_get_db,
    mock_sync,
    tmp_path: Path,
    monkeypatch
) -> None:
    temp_data_file = tmp_path / "test_data.json"
    temp_data_file.write_text("{}")
    mock_data_path.__str__.return_value = str(temp_data_file)
    
    # Test code here - properly indented!
    win = MonsterManagerWin(None, self.root)
    win.selected_monster = {"skills": []}
    win._on_add_skill()
    assert len(win.selected_monster["skills"]) == 1
```

### Step 4: Handle Fixture-Based Patches

Some patches need to be fixtures if used multiple times.

**File**: `tests/unit/ui/test_monster_editor_left_panel.py`

**Create fixture in conftest.py**:
```python
@pytest.fixture
def monster_editor_patches(tmp_path):
    """
    Patches for MonsterEditor tests.
    
    Provides:
    - DATA_PATH pointing to temp directory
    - get_db returning None
    - DataSyncManager disabled
    """
    temp_data_file = tmp_path / "test_data.json"
    temp_data_file.write_text("{}")
    
    with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file), \
         patch('ui.windows.monster_manager_win.get_db', return_value=None), \
         patch('ui.windows.monster_manager_win.DataSyncManager', None):
        yield {"data_path": temp_data_file}
```

**Use fixture**:
```python
def test_add_skill_to_monster(self, monster_editor_patches) -> None:
    # All patches are active
    win = MonsterManagerWin(None, self.root)
    win.selected_monster = {"skills": []}
    win._on_add_skill()
    assert len(win.selected_monster["skills"]) == 1
```

### Step 5: Transform Each File

#### File 1: test_monster_editor_left_panel.py

**Count nested chains**: ~6-8 locations with nested patches

**Transformation**:
1. Extract common patches to fixture
2. Convert remaining patches to decorators
3. Add fixture parameter to test functions

**Example changes**:
```python
# Define once in conftest or at top of file
@pytest.fixture
def monster_editor_temp_data(tmp_path):
    temp_file = tmp_path / "test_data.json"
    temp_file.write_text("{}")
    with patch('ui.windows.monster_manager_win.DATA_PATH', temp_file), \
         patch('ui.windows.monster_manager_win.get_db', return_value=None), \
         patch('ui.windows.monster_manager_win.DataSyncManager', None):
        yield temp_file

# Use in every test
@patch('tkinter.messagebox.showwarning')
def test_delete_monster(self, mock_warning, monster_editor_temp_data):
    # Clean test code
    pass
```

#### File 2: test_monster_editor_save.py

Similar transformation - identify 5-6 nested chains and convert each.

#### File 3: test_monster_editor_data.py

Transform 4-5 nested chains.

### Step 6: Verification

```python
# Verify patches are applied correctly
def test_patches_work():
    """Verify that converted patches work correctly."""
    with patch('some.module.func') as mock_func:
        # Test that mock works
        assert mock_func is not None
```

### Step 7: Commit Changes

```bash
git add tests/unit/ui/test_monster_editor_*.py tests/conftest.py

git commit -m "refactor: replace nested patch chains with decorators

- Convert nested 'with patch()' chains to clean @patch decorators
- Improve readability by reducing indentation levels
- Create reusable patches fixture for common editor test setup
- Affected files:
  * tests/unit/ui/test_monster_editor_left_panel.py (6 chains)
  * tests/unit/ui/test_monster_editor_save.py (5 chains)
  * tests/unit/ui/test_monster_editor_data.py (4 chains)
  * tests/unit/ui/test_monster_editor_sprint25.py (2 chains)
  * tests/unit/ui/test_monster_editor_tabs.py (1 chain)

Benefits:
- Test code more readable
- Easier to add/remove patches
- Follows Python testing conventions
- No behavior changes, same test coverage"
```

---

## ✅ Testing Checklist

### Verification Steps
- [ ] All nested chains converted to decorators or fixtures
- [ ] Decorators are in correct order (reverse of execution order)
- [ ] Mock parameters in function signature match decorator order
- [ ] `pytest tests/unit/ui/test_monster_editor_*.py -v` → All pass
- [ ] `python analyze_mocks.py` → Verify no regression
- [ ] Code readability improved (less indentation)
- [ ] No functionality changes

### Code Quality Checks
- [ ] Test functions properly indented (4 spaces)
- [ ] Decorator stack is clean and readable
- [ ] Fixture docstrings are clear
- [ ] Mock parameters clearly named

### Performance Verification
```bash
# Run tests to ensure no performance regression
time pytest tests/unit/ui/test_monster_editor_left_panel.py -v
```

---

## 📊 Expected Results

### Before Session 3
```
Total Mock/Patch Instances: 494 (after Session 2)
Nested patch chains: 18-20 (deeply indented)
Test readability: Medium (some hard to read)
```

### After Session 3
```
Total Mock/Patch Instances: 464 (-30, mostly refactoring)
Nested patch chains: 0 (all converted)
Test readability: High (clean, Pythonic code)
```

### Mock Count Changes
| File | Before | After | Notes |
|------|--------|-------|-------|
| test_monster_editor_left_panel.py | 11 | 8 | -3 (consolidated) |
| test_monster_editor_save.py | 12 | 9 | -3 (consolidated) |
| test_monster_editor_data.py | 9 | 7 | -2 (consolidated) |
| conftest.py | +4 fixtures | +6 fixtures | +2 new fixtures |
| **TOTAL** | **494** | **464** | **-30** |

---

## 🎓 What You'll Learn

1. **@patch Decorator Usage**: Proper syntax and parameter ordering
2. **Decorator Stacking**: How multiple decorators interact
3. **Context Manager vs Decorator**: When to use each
4. **Parametrization**: Using parametrize with patches
5. **Fixture Integration**: Combining patches and fixtures

---

## ⚠️ Common Issues & Solutions

### Issue 1: Mock Parameters in Wrong Order
**Problem**: Mock parameter doesn't match expected mock
```python
# WRONG - Parameters in wrong order!
@patch('module.a')
@patch('module.b')
def test(mock_b, mock_a):  # ← WRONG ORDER!
    pass

# RIGHT - Reverse order of decorators
@patch('module.b')  # Applied second
@patch('module.a')  # Applied first
def test(mock_a, mock_b):  # Correct order
    pass
```
**Solution**: Remember - decorators are applied bottom-up, parameters are left-to-right

### Issue 2: Missing Mock Parameter
**Problem**: Decorated function missing parameter
```python
@patch('module.func')
def test(self):  # ← FORGOT THE MOCK PARAMETER!
    pass
```
**Solution**: Add mock parameter after self (if it's a method)

### Issue 3: Patch Not Applied
**Problem**: Patch decorator but import statement at top of file uses old import
```python
from module import func  # ← Imported before patch!

@patch('module.func')
def test(mock_func):
    func()  # Still calls original!
```
**Solution**: Patch where it's used, not where it's defined:
```python
@patch('my_test_module.func')  # Patch where test imports it
def test(mock_func):
    # Now it's mocked
```

### Issue 4: Parametrize + Patch Confusion
**Problem**: Combining @parametrize with @patch gets parameters mixed up
```python
@pytest.mark.parametrize('value', [1, 2, 3])
@patch('module.func')
def test(value, mock_func):  # ← Which parameter is value?
    pass
```
**Solution**: Parametrize decorator goes ABOVE patch decorators:
```python
@pytest.mark.parametrize('value', [1, 2, 3])
@patch('module.func')
def test(mock_func, value):  # parametrize params come last
    pass
```

---

## 📝 Reference: Decorator Order

### Rule
- Decorators are applied **bottom-to-top**
- Parameters are **left-to-right** in function signature
- **Reverse the order** of decorators to get parameter order

### Example
```python
@patch('c')     # ← Applied third, parameter rightmost
@patch('b')     # ← Applied second, parameter middle
@patch('a')     # ← Applied first, parameter leftmost
def test(mock_a, mock_b, mock_c):  # Left-to-right = bottom-to-top patches
    pass
```

### With pytest.mark.parametrize
```python
@pytest.mark.parametrize('scenario', ['a', 'b'])  # ← Goes TOP
@patch('module.z')    # ← Third
@patch('module.y')    # ← Second
@patch('module.x')    # ← First
def test(mock_x, mock_y, mock_z, scenario):  # scenario from parametrize goes last
    pass
```

---

## 💾 Transformation Checklist

### For Each File to Transform

- [ ] Identify all nested patch chains
- [ ] Decide conversion strategy (decorators vs fixture)
- [ ] Create fixture if needed
- [ ] Convert chains to decorators
- [ ] Verify parameter order is correct
- [ ] Add fixture parameters to function signature
- [ ] Test the file: `pytest tests/unit/ui/test_file.py -v`
- [ ] Verify no regression in mock count
- [ ] Review for readability

---

## 📚 Additional Resources

### Documentation
- [unittest.mock.patch documentation](https://docs.python.org/3/library/unittest.mock.html#patch)
- [Multiple patches tutorial](https://docs.python.org/3/library/unittest.mock.html#patch-multiple)
- [Pytest parametrize guide](https://docs.pytest.org/en/stable/how-to/parametrize.html)

### Best Practices
- [Reducing deeply nested with statements](https://docs.python.org/3/library/unittest.mock.html#patch-multiple)
- [Fixture vs patch decorator](https://docs.pytest.org/en/stable/how-to/fixtures.html#coupling-fixtures-through-dependency-injection)

---

## 🎯 Session Complete Criteria

✅ **This session is complete when:**
1. All nested `with patch()` chains converted
2. 18-20 chain locations transformed to decorators or fixtures
3. Mock parameters in correct order in all functions
4. All tests pass: `pytest tests/unit/ui/ -v`
5. Mock count reduced by ~30 instances
6. Code readability significantly improved
7. Changes committed with proper message
8. No behavior changes or regressions

---

**Status**: 🟢 Ready to Start (can be parallel to Sessions 1-2)
**Estimated Time**: 4-6 hours
**Next Session**: [SESSION_4_ORCHESTRATOR_REFACTOR.md](SESSION_4_ORCHESTRATOR_REFACTOR.md) (can wait)

---

## 🚀 Quick Start

```bash
cd f:\Cabal_Auto

# Find all nested patch chains to convert
grep -rn "with patch.*,$" tests/unit/ui/

# After converting:
pytest tests/unit/ui/test_monster_editor*.py -v

# Verify mock reduction
python analyze_mocks.py

# Commit changes
git add tests/
git commit -m "refactor: replace nested patch chains with decorators"
```
