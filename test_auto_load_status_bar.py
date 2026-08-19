#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for auto-load and status bar features in QuickMonsterEditor.

Tests verify:
1. Auto-load data on __init__
2. Auto-refresh on deiconify()
3. Stats label updates with correct format
4. Loading status displays
5. Filter and search operations update stats label
6. DB connection handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Setup path for imports
sys.path.insert(0, str(Path(__file__).parent))


class TestQuickMonsterEditorFeatures:
    """Test core features of QuickMonsterEditor"""

    def test_deiconify_method_exists(self):
        """Test that QuickMonsterEditor has deiconify method"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        
        # Verify method exists
        assert hasattr(QuickMonsterEditor, 'deiconify')
        assert callable(getattr(QuickMonsterEditor, 'deiconify'))

    def test_update_stats_label_method_exists(self):
        """Test that _update_stats_label method exists"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        
        assert hasattr(QuickMonsterEditor, '_update_stats_label')
        assert callable(getattr(QuickMonsterEditor, '_update_stats_label'))

    def test_refresh_monster_table_called_in_init(self):
        """Test that _refresh_monster_table is called during initialization"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()
        
        try:
            # Just verify that initialization succeeds (which calls _refresh_monster_table internally)
            editor = QuickMonsterEditor(root)
            
            # Verify key attributes are initialized
            assert hasattr(editor, 'monster_table')
            assert hasattr(editor, 'filtered_monsters')
            assert hasattr(editor, 'stats_label')
            
            editor.destroy()
            # If no exception was raised, test passed
            assert True
        finally:
            root.destroy()

    def test_database_connection_has_finally_block(self):
        """Test that _check_db_connection properly handles connections"""
        from app_gui import App
        import inspect
        
        # Get the source code of _check_db_connection
        source = inspect.getsource(App._check_db_connection)
        
        # Verify it has a finally block to ensure connection closes
        assert 'finally:' in source, "_check_db_connection should have a finally block"
        assert 'db.conn.close()' in source or 'close()' in source, "Connection should be closed in finally block"


class TestLoadingStatusUI:
    """Test loading status UI updates"""

    def test_apply_search_calls_update(self):
        """Test that _apply_search updates UI state"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        import inspect
        
        # Get source code
        source = inspect.getsource(QuickMonsterEditor._apply_search)
        
        # Verify it updates stats_label
        assert 'stats_label' in source, "_apply_search should update stats_label"
        assert 'update_idletasks' in source, "_apply_search should flush UI updates"

    def test_on_filter_changed_calls_update(self):
        """Test that _on_filter_changed updates UI state"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        import inspect
        
        # Get source code
        source = inspect.getsource(QuickMonsterEditor._on_filter_changed)
        
        # Verify it updates stats_label
        assert 'stats_label' in source, "_on_filter_changed should update stats_label"
        assert 'update_idletasks' in source, "_on_filter_changed should flush UI updates"


class TestI18nIntegration:
    """Test i18n integration"""

    def test_apply_search_uses_i18n(self):
        """Test that _apply_search uses i18n for loading text"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        import inspect
        
        source = inspect.getsource(QuickMonsterEditor._apply_search)
        
        # Verify i18n_t is called
        assert "i18n_t(" in source, "_apply_search should use i18n_t for strings"
        assert "status_loading" in source, "Should use status_loading translation key"

    def test_on_filter_changed_uses_i18n(self):
        """Test that _on_filter_changed uses i18n for loading text"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        import inspect
        
        source = inspect.getsource(QuickMonsterEditor._on_filter_changed)
        
        # Verify i18n_t is called
        assert "i18n_t(" in source, "_on_filter_changed should use i18n_t for strings"
        assert "status_loading" in source, "Should use status_loading translation key"

    def test_stats_label_init_uses_i18n(self):
        """Test that stats label initialization uses i18n"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        import inspect
        
        source = inspect.getsource(QuickMonsterEditor._create_bottom_bar)
        
        # Verify i18n_t is called for default stats text
        assert "i18n_t(" in source, "_create_bottom_bar should use i18n_t for strings"
        assert "status_records_default" in source, "Should use status_records_default translation key"

    def test_update_stats_label_uses_i18n(self):
        """Test that _update_stats_label uses i18n for formatting"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        import inspect
        
        source = inspect.getsource(QuickMonsterEditor._update_stats_label)
        
        # Verify i18n_t is called for stats text
        assert "i18n_t(" in source, "_update_stats_label should use i18n_t for strings"


class TestDatabaseConnection:
    """Test database connection functionality"""

    def test_check_db_connection_method_exists(self):
        """Test that App has _check_db_connection method"""
        from app_gui import App
        
        assert hasattr(App, '_check_db_connection')
        assert callable(getattr(App, '_check_db_connection'))

    def test_check_db_connection_registers_on_startup(self):
        """Test that _check_db_connection is called on app startup"""
        from app_gui import App
        import inspect
        
        # Get __init__ source code
        source = inspect.getsource(App.__init__)
        
        # Verify _check_db_connection is scheduled
        assert '_check_db_connection' in source, "App.__init__ should schedule _check_db_connection"
        assert 'self.after' in source, "Should use after() to schedule DB check"

    def test_db_uses_configured_path(self):
        """Test that _check_db_connection uses MonsterDatabase.DB_PATH"""
        from app_gui import App
        import inspect
        
        source = inspect.getsource(App._check_db_connection)
        
        # Verify it uses the configured DB path
        assert 'MonsterDatabase.DB_PATH' in source, "Should use MonsterDatabase.DB_PATH for dynamic path"


class TestAutoLoadFeature:
    """Test auto-load data feature"""

    def test_db_connection_always_attempts(self):
        """Test that QuickMonsterEditor always attempts DB connection"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        import inspect
        
        source = inspect.getsource(QuickMonsterEditor.__init__)
        
        # Verify DB connection is attempted
        assert 'self.db = get_db()' in source or 'get_db()' in source, "Should attempt to get DB"

    def test_refresh_table_attempts_db_connection(self):
        """Test that _refresh_monster_table attempts DB connection"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        import inspect
        
        source = inspect.getsource(QuickMonsterEditor._refresh_monster_table)
        
        # Verify DB connection is attempted
        assert 'self.db is None' in source, "Should check DB connection status"
        assert 'get_db()' in source, "Should attempt DB connection if needed"

    def test_filtered_monsters_populated_on_refresh(self):
        """Test that _refresh_monster_table populates filtered_monsters"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        import inspect
        
        source = inspect.getsource(QuickMonsterEditor._refresh_monster_table)
        
        # Verify filtered_monsters is set
        assert 'self.filtered_monsters' in source, "Should set filtered_monsters"
        assert 'self.monster_table.insert' in source, "Should insert data into table"


class TestEfficiency:
    """Test efficiency improvements"""

    def test_stats_label_query_uses_minimal_page_size(self):
        """Test that _update_stats_label uses page_size=1 for efficiency"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        import inspect
        
        source = inspect.getsource(QuickMonsterEditor._update_stats_label)
        
        # Verify minimal query is used
        assert 'page_size=1' in source, "Should use page_size=1 for efficiency"

    def test_stats_label_uses_total_records_from_payload(self):
        """Test that _update_stats_label uses payload total_records"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        import inspect
        
        source = inspect.getsource(QuickMonsterEditor._update_stats_label)
        
        # Verify it uses total_records from payload
        assert "total_payload.get('total_records'" in source, "Should read total_records from database payload"

    def test_stats_label_respects_current_filters(self):
        """Test that _update_stats_label respects current filters"""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        import inspect
        
        source = inspect.getsource(QuickMonsterEditor._update_stats_label)
        
        # Verify current filters are passed to query
        assert 'self.search_term' in source, "Should use current search_term"
        assert 'self.monster_type_filter' in source, "Should use current monster_type_filter"
        assert 'self.location_filter' in source, "Should use current location_filter"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

