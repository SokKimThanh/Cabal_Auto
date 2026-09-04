"""
Unit tests for lib/features/monster_service.py.
Tests check_duplicate_name, generate_unique_name, and ensure_unique_monster_id.
"""
import pytest

pytestmark = pytest.mark.unit
import pytest
from lib.features.monster_service import (


    check_duplicate_name,
    generate_unique_name,
    ensure_unique_monster_id,
)


def test_check_duplicate_name_basic() -> None:
    monsters = [
        {'id': 'm1', 'name': 'Quái Đen'},
        {'id': 'm2', 'name': 'Quái Đỏ'},
    ]

    assert check_duplicate_name(monsters, 'Quái Đen') is True
    assert check_duplicate_name(monsters, 'quái đen') is True  # case insensitive
    assert check_duplicate_name(monsters, 'Quái Xanh') is False


def test_check_duplicate_name_ignores_current_id() -> None:
    monsters = [
        {'id': 'm1', 'name': 'Quái Đen'},
        {'id': 'm2', 'name': 'Quái Đỏ'},
    ]

    # When editing m1, 'Quái Đen' should not count as duplicate against itself
    assert check_duplicate_name(monsters, 'Quái Đen', current_id='m1') is False
    # But should count if name matches m2
    assert check_duplicate_name(monsters, 'Quái Đỏ', current_id='m1') is True


def test_generate_unique_name_no_conflict() -> None:
    monsters = [{'id': 'm1', 'name': 'Quái Đen'}]
    assert generate_unique_name(monsters, 'Quái Xanh') == 'Quái Xanh'


def test_generate_unique_name_single_conflict() -> None:
    monsters = [{'id': 'm1', 'name': 'Quái Mới'}]
    assert generate_unique_name(monsters, 'Quái Mới') == 'Quái Mới (1)'


def test_generate_unique_name_multiple_conflicts() -> None:
    monsters = [
        {'id': 'm1', 'name': 'Quái Mới'},
        {'id': 'm2', 'name': 'Quái Mới (1)'},
        {'id': 'm3', 'name': 'Quái Mới (2)'},
    ]
    assert generate_unique_name(monsters, 'Quái Mới') == 'Quái Mới (3)'
    assert generate_unique_name(monsters, 'Quái Mới (1)') == 'Quái Mới (3)'


def test_ensure_unique_monster_id() -> None:
    monster = {'name': 'Quái 1'}
    existing = [{'id': 'id-1', 'name': 'Quái Existing'}]

    m_id = ensure_unique_monster_id(monster, existing)
    assert m_id is not None
    assert len(m_id) > 0
    assert monster['id'] == m_id
