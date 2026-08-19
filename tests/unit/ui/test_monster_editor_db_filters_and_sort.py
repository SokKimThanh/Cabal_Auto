from pathlib import Path
import importlib

import pytest
import tkinter as tk

from database import MonsterDatabase


pytestmark = [pytest.mark.db, pytest.mark.ui]

SOURCE_DATA_DIR = Path("F:/Cabal_Auto.worktrees/tdd-automation-testing-upgrade/lib/data")


def _build_db(tmp_path: Path, monsters: list[dict]) -> MonsterDatabase:
    db = MonsterDatabase(db_path=tmp_path / "monsters.db", data_dir=SOURCE_DATA_DIR)
    db.init_db()
    db.replace_monsters(monsters)
    return db


def _load_editor_module():
    module = importlib.import_module("ui.windows.quick_monster_editor")
    return importlib.reload(module)


def test_filter_comboboxes_show_lookup_names(monkeypatch, tmp_path: Path) -> None:
    editor_module = _load_editor_module()
    db = _build_db(
        tmp_path,
        [
            {"id": "m1", "name": "Ruina Beast", "hp": 200, "damage_per_hit": 20, "serverBossType": 1, "dungeonId": "245"},
            {"id": "m2", "name": "Field Mob", "hp": 100, "damage_per_hit": 10, "serverBossType": 0, "dungeonId": None},
        ],
    )
    monkeypatch.setattr(editor_module, "get_db", lambda: db)

    root = tk.Tk()
    root.withdraw()
    editor = None
    try:
        editor = editor_module.QuickMonsterEditor(root)
        editor._refresh_filter_options()

        assert editor.monster_type_box._values[0] == editor_module.ALL_FILTER_LABEL
        assert "Map Bosses" in editor.monster_type_box._values
        assert editor.location_box._values[0] == editor_module.ALL_FILTER_LABEL
        assert "Ruina Station" in editor.location_box._values
    finally:
        if editor is not None:
            editor.destroy()
        root.destroy()


def test_left_join_keeps_monsters_with_missing_location(monkeypatch, tmp_path: Path) -> None:
    editor_module = _load_editor_module()
    db = _build_db(
        tmp_path,
        [
            {"id": "m1", "name": "Known Place", "hp": 150, "damage_per_hit": 12, "serverBossType": 0, "dungeonId": "245"},
            {"id": "m2", "name": "Unknown Place", "hp": 175, "damage_per_hit": 15, "serverBossType": 0, "dungeonId": "999999"},
        ],
    )
    monkeypatch.setattr(editor_module, "get_db", lambda: db)

    root = tk.Tk()
    root.withdraw()
    editor = None
    try:
        editor = editor_module.QuickMonsterEditor(root)
        by_name = {monster["name"]: monster for monster in editor.filtered_monsters}

        assert by_name["Known Place"]["location_name"] == "Ruina Station"
        assert by_name["Unknown Place"]["location_name"] == editor_module.UNKNOWN_LOCATION_LABEL
    finally:
        if editor is not None:
            editor.destroy()
        root.destroy()


def test_empty_database_keeps_ui_responsive(monkeypatch, tmp_path: Path) -> None:
    editor_module = _load_editor_module()
    db = _build_db(tmp_path, [])
    monkeypatch.setattr(editor_module, "get_db", lambda: db)

    root = tk.Tk()
    root.withdraw()
    editor = None
    try:
        editor = editor_module.QuickMonsterEditor(root)

        assert editor.monster_type_box._values == [editor_module.ALL_FILTER_LABEL]
        assert editor.location_box._values == [editor_module.ALL_FILTER_LABEL]
        assert editor.filtered_monsters == []
        assert "0 / 0 quái vật" in editor.stats_label.cget("text")
    finally:
        if editor is not None:
            editor.destroy()
        root.destroy()


def test_clicking_hp_header_toggles_numeric_sort(monkeypatch, tmp_path: Path) -> None:
    editor_module = _load_editor_module()
    db = _build_db(
        tmp_path,
        [
            {"id": "m1", "name": "Mob C", "hp": 40, "damage_per_hit": 8},
            {"id": "m2", "name": "Mob A", "hp": None, "damage_per_hit": 5},
            {"id": "m3", "name": "Mob B", "hp": 10, "damage_per_hit": 6},
        ],
    )
    monkeypatch.setattr(editor_module, "get_db", lambda: db)

    root = tk.Tk()
    root.withdraw()
    editor = None
    try:
        editor = editor_module.QuickMonsterEditor(root)
        editor._on_sort_column("hp")
        asc_values = [int(monster.get("hp") or 0) for monster in editor.filtered_monsters]

        editor._on_sort_column("hp")
        desc_values = [int(monster.get("hp") or 0) for monster in editor.filtered_monsters]

        assert asc_values == [0, 10, 40]
        assert desc_values == [40, 10, 0]
    finally:
        if editor is not None:
            editor.destroy()
        root.destroy()


def test_sort_click_updates_heading_state(monkeypatch, tmp_path: Path) -> None:
    editor_module = _load_editor_module()
    db = _build_db(
        tmp_path,
        [
            {"id": "m1", "name": "Mob C", "hp": 40, "damage_per_hit": 8},
            {"id": "m2", "name": "Mob A", "hp": 10, "damage_per_hit": 5},
        ],
    )
    monkeypatch.setattr(editor_module, "get_db", lambda: db)

    root = tk.Tk()
    root.withdraw()
    editor = None
    try:
        editor = editor_module.QuickMonsterEditor(root)

        editor._on_sort_column("hp")
        assert editor.sort_column == "hp"
        assert editor.sort_order == "ASC"
        assert editor.monster_table.heading("hp")["text"].endswith("▲")

        editor._on_sort_column("hp")
        assert editor.sort_order == "DESC"
        assert editor.monster_table.heading("hp")["text"].endswith("▼")
    finally:
        if editor is not None:
            editor.destroy()
        root.destroy()
