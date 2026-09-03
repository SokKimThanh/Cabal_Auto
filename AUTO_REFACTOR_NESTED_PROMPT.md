# 🚀 Hướng Dẫn Tự Động: Refactor Nested Patch Blocks

## Hướng Dẫn Cho Jules

**Copy toàn bộ text dưới đây vào Copilot Chat và bấm Enter để tự động thực hiện.**

**⚠️ QUAN TRỌNG**: Đây là refactor TRỰC TIẾP vào workspace files, KHÔNG tạo helper scripts!

---

## PROMPT TỰ ĐỘNG (Copy-Paste)

```
task: Refactor 3-5 level nested patch blocks thành @patch decorators + fixture

context:
- Project: Cabal Auto Hunt
- Files affected: 
  * tests/conftest.py (add fixture)
  * tests/unit/ui/test_monster_editor_left_panel.py (refactor patches)
  * tests/unit/ui/test_monster_editor_save.py (refactor patches)
  * tests/unit/ui/test_monster_editor_data.py (refactor patches)
- Issue: Current code has 3-5 level nested `with patch` blocks that are hard to read
- Solution: Convert to @patch decorators + shared fixture

requirements:
- DIRECT edits to workspace files (NO helper scripts)
- Backward compatibility: tests must pass IDENTICALLY
- Follow pytest conventions and project coding standards

steps:

### BƯỚC 1: Add patched_monster_editor fixture to tests/conftest.py

1.1) Open tests/conftest.py
1.2) Find the END of the file (after last fixture or marker definition)
1.3) Add this new fixture:

```python
@pytest.fixture
def patched_monster_editor(tmp_path):
    """Shared fixture for monster editor tests - patches common mocks."""
    from unittest.mock import patch, MagicMock
    from pathlib import Path
    
    # Create temp data file
    temp_data_file = tmp_path / "monsters.json"
    temp_data_file.write_text('[]', encoding='utf-8')
    
    # Create list of patches
    patches_list = [
        patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file),
        patch('ui.windows.monster_manager_win.get_db', return_value=MagicMock()),
        patch('ui.windows.monster_manager_win.DataSyncManager', autospec=True),
    ]
    
    # Apply all patches
    mocks = [p.start() for p in patches_list]
    
    yield {
        'temp_data_file': temp_data_file,
        'DATA_PATH_mock': mocks[0],
        'get_db_mock': mocks[1],
        'DataSyncManager_mock': mocks[2],
        'patches': patches_list
    }
    
    # Stop all patches
    for p in patches_list:
        p.stop()
    
    # Cleanup
    try:
        if temp_data_file.exists():
            temp_data_file.unlink()
    except (PermissionError, OSError):
        import time
        time.sleep(0.05)
        try:
            temp_data_file.unlink()
        except Exception:
            pass
```

### BƯỚC 2: Refactor tests/unit/ui/test_monster_editor_left_panel.py

2.1) Replace all test functions using this pattern:

OLD (nested patches):
```python
def test_name(self, temp_data_file):
    with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file), \
         patch('ui.windows.monster_manager_win.get_db', ...), \
         patch('ui.windows.monster_manager_win.DataSyncManager', ...):
        # test code
        pass
```

NEW (decorators + fixture):
```python
@patch('tkinter.messagebox.askyesno', return_value=True)  # if needed
@patch('ui.windows.monster_manager_win.DataSyncManager', autospec=True)
@patch('ui.windows.monster_manager_win.get_db', return_value=MagicMock())
@patch('ui.windows.monster_manager_win.DATA_PATH')
def test_name(self, mock_DATA_PATH, mock_get_db, mock_DataSyncManager, mock_askyesno, patched_monster_editor):
    # Use patched_monster_editor['temp_data_file'] for temp file
    temp_data_file = patched_monster_editor['temp_data_file']
    mock_DATA_PATH.return_value = temp_data_file
    
    # test code
    pass
```

Key conversions for each test:
- test_left_panel_creation: Remove nested patches, add @patch decorators
- test_refresh_monster_list: Same pattern
- test_monster_selection: Same pattern
- test_add_monster: Same pattern
- test_delete_monster_with_confirmation: Keep inner @patch for messagebox.askyesno
- test_delete_monster_cancelled: Same
- test_delete_monster_no_selection: Same
- test_add_multiple_monsters: Same

2.2) Ensure:
- Remove ALL `with patch(...)` blocks
- Convert to @patch decorators at function level
- Inject patched_monster_editor as last parameter
- Use patched_monster_editor['temp_data_file'] for file operations

### BƯỚC 3: Refactor tests/unit/ui/test_monster_editor_save.py

3.1) Apply SAME pattern as BƯỚC 2 to these tests:
- test_save_button_saves_all_monsters
- test_save_clears_dirty_state
- test_save_validates_monster_names
- test_save_with_no_monsters_shows_warning
- test_save_button_initially_disabled

### BƯỚC 4: Refactor tests/unit/ui/test_monster_editor_data.py

4.1) Apply SAME pattern as BƯỚC 2 to these tests:
- test_load_monsters_empty_file
- test_load_monsters_valid_data
- test_load_monsters_auto_generate_ids
- test_load_monsters_file_not_found
- test_save_monsters
- test_save_monsters_error_handling

### BƯỚC 5: Run Tests - ACTUAL VERIFICATION (NOT JUST SYNTAX CHECK)

5.1) Run pytest to verify tests pass:
```
cd f:\Cabal_Auto
python -m pytest tests/unit/ui/test_monster_editor_left_panel.py -v
python -m pytest tests/unit/ui/test_monster_editor_save.py -v
python -m pytest tests/unit/ui/test_monster_editor_data.py -v
python -m pytest tests/unit/ui/ -v
```

5.2) Expected output:
- All tests PASS (same count as before)
- No ERROR or FAILED
- No warnings about patches

### BƯỚC 6: Verify Refactoring Complete

6.1) Check conftest.py:
```
grep "def patched_monster_editor" tests/conftest.py
```
→ Must return the fixture definition

6.2) Check test files have @patch decorators:
```
grep "@patch" tests/unit/ui/test_monster_editor_left_panel.py | wc -l
```
→ Should show multiple @patch lines (not 0)

6.3) Check test files have NO nested with patches:
```
grep "with patch" tests/unit/ui/test_monster_editor_left_panel.py
```
→ Should return NOTHING (empty)

6.4) Clean up: Verify NO helper scripts in workspace
```
ls -la *.py | grep -E "(replace_|convert_|format_|fix\.py)"
```
→ Should return NOTHING (no scripts like replace_left_panel.py, etc.)

success_criteria:
- ✅ patched_monster_editor fixture exists in conftest.py
- ✅ All 3 test files use @patch decorators (NO nested with patches)
- ✅ All tests PASS with identical results
- ✅ NO helper scripts remain in workspace
- ✅ Code follows project conventions (CODING_RULES_QUICK_REFERENCE.md)
- ✅ Backward compatible: test behavior unchanged

done:
Report completion with:
- Number of @patch decorators added
- Number of nested patches removed
- Test run results (PASSED X tests)
- NO helper scripts present
```

---

## Checklist Hoàn Thành

Sau khi hoàn thành, kiểm tra:

- [ ] `tests/conftest.py` có `patched_monster_editor` fixture
- [ ] `test_monster_editor_left_panel.py` dùng @patch decorators (không `with patch`)
- [ ] `test_monster_editor_save.py` dùng @patch decorators (không `with patch`)
- [ ] `test_monster_editor_data.py` dùng @patch decorators (không `with patch`)
- [ ] `pytest tests/unit/ui/ -v` PASS (all tests)
- [ ] NO temporary helper scripts (replace_*.py, convert_*.py, format_*.py, fix.py, etc.)
- [ ] Không có `with patch(` trong 3 test files
- [ ] Có nhiều `@patch` decorators trong 3 test files

---

**QUAN TRỌNG:**
- ❌ KHÔNG tạo helper scripts (convert_*.py, format_*.py, etc.)
- ✅ Edit TRỰC TIẾP vào workspace files
- ✅ Verify bằng pytest ACTUAL EXECUTION
- ✅ COMMIT real changes vào workspace

**Khi xong, báo tin cho tôi và tôi sẽ xem xét toàn bộ code! 🚀**
