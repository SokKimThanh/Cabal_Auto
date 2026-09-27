import sqlite3
import pytest
from lib.db.schema import setup_skills_schema

def test_build_schema_has_new_fields():
    conn = sqlite3.connect(':memory:')

    # We only care about builds table for this test, but setup_skills_schema creates many tables.
    # It might fail if we don't create classes table first since we have a foreign key.
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")

    setup_skills_schema(conn)

    cursor.execute("PRAGMA table_info(builds)")
    cols = [c[1] for c in cursor.fetchall()]
    assert "attack_skill_ids" in cols
    assert "buff_skill_ids" in cols
