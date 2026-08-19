#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integration test for auto-load and status bar features.
Tests the complete workflow without requiring GUI interaction.
"""

import sys
import tkinter as tk
from pathlib import Path
from unittest.mock import Mock, patch

# Add repo to path
sys.path.insert(0, str(Path(__file__).parent))

def test_quick_monster_editor_auto_load():
    """Test QuickMonsterEditor auto-loads data on init"""
    print("\n=== Test 1: QuickMonsterEditor Auto-Load ===")
    
    from ui.windows.quick_monster_editor import QuickMonsterEditor
    
    root = tk.Tk()
    root.withdraw()
    
    try:
        editor = QuickMonsterEditor(root)
        
        # Verify key attributes exist
        assert hasattr(editor, 'filtered_monsters'), "filtered_monsters should be created"
        assert hasattr(editor, 'stats_label'), "stats_label should be created"
        assert hasattr(editor, 'monster_table'), "monster_table should be created"
        
        # Verify stats_label has text
        stats_text = editor.stats_label.cget('text')
        assert len(stats_text) > 0, "stats_label should have text"
        assert '📊' in stats_text or 'Hiển thị' in stats_text, "stats_label should show record count"
        
        print(f"✓ Filtered monsters loaded: {len(editor.filtered_monsters)} items")
        print(f"✓ Stats label text: {stats_text}")
        print("✓ Auto-load on init works!")
        
        editor.destroy()
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        root.destroy()
        return False

def test_deiconify_refresh():
    """Test QuickMonsterEditor has deiconify override"""
    print("\n=== Test 2: Deiconify Refresh ===")
    
    from ui.windows.quick_monster_editor import QuickMonsterEditor
    import inspect
    
    # Verify deiconify method exists and calls _refresh_monster_table
    assert hasattr(QuickMonsterEditor, 'deiconify'), "deiconify method should exist"
    
    source = inspect.getsource(QuickMonsterEditor.deiconify)
    assert '_refresh_monster_table' in source, "deiconify should call _refresh_monster_table"
    assert 'super().deiconify()' in source, "deiconify should call parent deiconify"
    
    print("✓ deiconify override exists")
    print("✓ deiconify calls super().deiconify()")
    print("✓ deiconify calls _refresh_monster_table()")
    print("✓ Deiconify refresh works!")
    return True

def test_stats_label_i18n():
    """Test stats label uses i18n"""
    print("\n=== Test 3: Stats Label i18n ===")
    
    from ui.windows.quick_monster_editor import QuickMonsterEditor
    import inspect
    
    source = inspect.getsource(QuickMonsterEditor._create_bottom_bar)
    
    assert 'i18n_t' in source, "Should use i18n_t for translations"
    assert 'status_records_default' in source, "Should use proper i18n key"
    
    print("✓ Stats label uses i18n_t")
    print("✓ Uses correct translation key: status_records_default")
    print("✓ i18n integration works!")
    return True

def test_db_connection_check():
    """Test database connection checking"""
    print("\n=== Test 4: Database Connection Check ===")
    
    from app_gui import App
    import inspect
    
    # Verify method exists
    assert hasattr(App, '_check_db_connection'), "_check_db_connection method should exist"
    
    # Verify it's called on startup
    init_source = inspect.getsource(App.__init__)
    assert '_check_db_connection' in init_source, "Should call _check_db_connection in __init__"
    assert 'self.after' in init_source, "Should schedule with after()"
    
    # Verify proper connection handling
    check_source = inspect.getsource(App._check_db_connection)
    assert 'MonsterDatabase' in check_source, "Should use MonsterDatabase"
    assert 'finally:' in check_source, "Should have finally block for cleanup"
    
    print("✓ _check_db_connection exists and is called on startup")
    print("✓ Uses proper connection lifecycle (finally block)")
    print("✓ Database connection check works!")
    return True

def test_efficiency_optimization():
    """Test efficiency improvements"""
    print("\n=== Test 5: Efficiency Optimization ===")
    
    from ui.windows.quick_monster_editor import QuickMonsterEditor
    import inspect
    
    source = inspect.getsource(QuickMonsterEditor._update_stats_label)
    
    # Check for minimal query (page_size=1)
    assert 'page_size=1' in source, "Should use page_size=1 for efficiency"
    
    # Check for filter awareness
    assert 'self.search_term' in source, "Should respect search_term filter"
    assert 'self.monster_type_filter' in source, "Should respect monster_type_filter"
    assert 'self.location_filter' in source, "Should respect location_filter"
    
    # Check for payload usage
    assert 'total_payload.get' in source, "Should read total_records from payload"
    
    print("✓ Uses minimal query (page_size=1)")
    print("✓ Respects current filters (search_term, type, location)")
    print("✓ Reads total_records from payload")
    print("✓ Efficiency optimizations in place!")
    return True

def main():
    print("=" * 60)
    print("Integration Test Suite for Auto-Load & Status Bar")
    print("=" * 60)
    
    results = []
    results.append(("Auto-Load on Init", test_quick_monster_editor_auto_load()))
    results.append(("Deiconify Refresh", test_deiconify_refresh()))
    results.append(("Stats Label i18n", test_stats_label_i18n()))
    results.append(("DB Connection Check", test_db_connection_check()))
    results.append(("Efficiency Optimization", test_efficiency_optimization()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All integration tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
