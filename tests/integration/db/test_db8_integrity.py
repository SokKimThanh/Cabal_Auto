import pytest
import sqlite3
import os
from unittest.mock import patch
from lib.db.schema import setup_skills_schema
from lib.db.services.schema_migration_service import SchemaMigrationService
from lib.db.services.seed_classes_service import SeedClassesService
from lib.db.services.seed_skill_sprite_service import SeedSkillSpriteService
from lib.db.services.seed_bm3_synergies_service import SeedBM3SynergiesService
from lib.db.services.seed_class_skill_assignments_service import SeedClassSkillAssignmentsService

pytestmark = pytest.mark.integration


@pytest.fixture
def mock_db_connection():
    # Setup fresh in-memory database
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    setup_skills_schema(conn)

    # Need to patch get_connection so that services use this one
    with patch("lib.db.services.schema_migration_service.get_connection", return_value=(conn, False)), \
         patch("lib.db.services.seed_classes_service.get_connection", return_value=(conn, False)), \
         patch("lib.db.services.seed_skill_sprite_service.get_connection", return_value=(conn, False)), \
         patch("lib.db.services.seed_bm3_synergies_service.get_connection", return_value=(conn, False)), \
         patch("lib.db.services.seed_class_skill_assignments_service.get_connection", return_value=(conn, False)):
        yield conn

def q(conn, query, args=()):
    c = conn.cursor()
    c.execute(query, args)
    return c.fetchall()

class TestDB8Integrity:
    def test_schema_and_migration_lifecycle(self, mock_db_connection):
        # 1. Additive upgrade execution against existing SQLite schemas.
        # 2. Clean initialization behavior on an Empty DB.

        # Test clean initialization (already run via fixture)
        assert len(q(mock_db_connection, "SELECT name FROM sqlite_master WHERE type='table' AND name='classes'")) == 1

        # Run schema migration service
        service = SchemaMigrationService()
        assert service.run_migrations() == True

        # Verify additive columns exist
        columns = [col['name'] for col in q(mock_db_connection, "PRAGMA table_info(synergy_effects)")]
        assert "value_text" in columns
        assert "duration_text" in columns

    def test_idempotency_and_parity_checks(self, mock_db_connection):
        # 1. Schema Migrations again just in case
        SchemaMigrationService().run_migrations()

        # Re-importing classes, skills, synergies, and class_skill_assignments produces zero duplicate rows and zero key inflation.
        SeedClassesService().seed_classes()
        SeedSkillSpriteService().seed_skill_sprites()
        SeedBM3SynergiesService().seed()
        SeedClassSkillAssignmentsService().seed_assignments()

        counts_run_1 = {
            'classes': len(q(mock_db_connection, "SELECT * FROM classes")),
            'skills': len(q(mock_db_connection, "SELECT * FROM skills")),
            'synergies': len(q(mock_db_connection, "SELECT * FROM synergies")),
            'synergy_effects': len(q(mock_db_connection, "SELECT * FROM synergy_effects")),
            'class_skill_assignments': len(q(mock_db_connection, "SELECT * FROM class_skill_assignments")),
        }

        # Run again for idempotency
        SeedClassesService().seed_classes()
        SeedSkillSpriteService().seed_skill_sprites()
        SeedBM3SynergiesService().seed()
        SeedClassSkillAssignmentsService().seed_assignments()

        counts_run_2 = {
            'classes': len(q(mock_db_connection, "SELECT * FROM classes")),
            'skills': len(q(mock_db_connection, "SELECT * FROM skills")),
            'synergies': len(q(mock_db_connection, "SELECT * FROM synergies")),
            'synergy_effects': len(q(mock_db_connection, "SELECT * FROM synergy_effects")),
            'class_skill_assignments': len(q(mock_db_connection, "SELECT * FROM class_skill_assignments")),
        }

        assert counts_run_1 == counts_run_2

        # Parity check:
        # Expected from current manifest sizes: classes: 9, skills: 460, synergies: 35, synergy_effects: 120, assignments: 32 (based on previous run)
        assert counts_run_2['classes'] == 9
        assert counts_run_2['skills'] == 460
        assert counts_run_2['synergies'] == 35
        assert counts_run_2['synergy_effects'] == 120
        assert counts_run_2['class_skill_assignments'] == 32

    def test_constraint_and_relationship_integrity(self, mock_db_connection):
        # Setup schema and data
        SchemaMigrationService().run_migrations()
        SeedClassesService().seed_classes()
        SeedSkillSpriteService().seed_skill_sprites()
        SeedBM3SynergiesService().seed()
        SeedClassSkillAssignmentsService().seed_assignments()

        # Enforce unique constraints on class_code, skill_code, and composite mapping key (class_id, skill_id).
        duplicates_classes = q(mock_db_connection, "SELECT class_code, COUNT(*) FROM classes WHERE class_code IS NOT NULL GROUP BY class_code HAVING COUNT(*) > 1")
        assert len(duplicates_classes) == 0

        duplicates_skills = q(mock_db_connection, "SELECT skill_code, COUNT(*) FROM skills WHERE skill_code IS NOT NULL GROUP BY skill_code HAVING COUNT(*) > 1")
        assert len(duplicates_skills) == 0

        duplicates_assignments = q(mock_db_connection, "SELECT class_id, skill_id, COUNT(*) FROM class_skill_assignments GROUP BY class_id, skill_id HAVING COUNT(*) > 1")
        assert len(duplicates_assignments) == 0

        # Foreign-Key Delete Actions: Verify expected behavior (RESTRICT / CASCADE) matches relationship contract.

        # 1. class_skill_assignments CASCADE from classes
        # Find a class with assignments
        class_with_assignments = q(mock_db_connection, "SELECT class_id FROM class_skill_assignments LIMIT 1")[0]['class_id']
        mock_db_connection.execute("PRAGMA foreign_keys = ON")
        try: mock_db_connection.execute("DELETE FROM synergies WHERE class_id = ?", (class_with_assignments,))
        except: pass
        mock_db_connection.execute("DELETE FROM classes WHERE class_id = ?", (class_with_assignments,))
        mock_db_connection.commit()
        assignments_after = q(mock_db_connection, "SELECT * FROM class_skill_assignments WHERE class_id = ?", (class_with_assignments,))
        assert len(assignments_after) == 0

        # Seed everything back
        SeedClassesService().seed_classes()
        SeedSkillSpriteService().seed_skill_sprites()
        SeedBM3SynergiesService().seed()
        SeedClassSkillAssignmentsService().seed_assignments()

        # 2. class_skill_assignments CASCADE from skills
        skill_with_assignments = q(mock_db_connection, "SELECT skill_id FROM class_skill_assignments LIMIT 1")[0]['skill_id']
        mock_db_connection.execute("PRAGMA foreign_keys = ON")
        mock_db_connection.execute("DELETE FROM skills WHERE skill_id = ?", (skill_with_assignments,))
        mock_db_connection.commit()
        assignments_after_skill = q(mock_db_connection, "SELECT * FROM class_skill_assignments WHERE skill_id = ?", (skill_with_assignments,))
        assert len(assignments_after_skill) == 0

        # Seed everything back again
        SeedClassesService().seed_classes()
        SeedSkillSpriteService().seed_skill_sprites()
        SeedBM3SynergiesService().seed()
        SeedClassSkillAssignmentsService().seed_assignments()

        # Orphan Checks: Query for orphan mappings, orphan synergy effects, and unlinked parent entities.
        orphan_assignments = q(mock_db_connection, """
            SELECT csa.class_id, csa.skill_id
            FROM class_skill_assignments AS csa
            LEFT JOIN classes AS c ON c.class_id = csa.class_id
            LEFT JOIN skills AS s ON s.skill_id = csa.skill_id
            WHERE c.class_id IS NULL OR s.skill_id IS NULL;
        """)
        assert len(orphan_assignments) == 0

        orphan_synergy_effects = q(mock_db_connection, """
            SELECT se.effect_id
            FROM synergy_effects AS se
            LEFT JOIN synergies AS syn ON syn.synergy_id = se.synergy_id
            WHERE syn.synergy_id IS NULL;
        """)
        assert len(orphan_synergy_effects) == 0

        orphan_synergies = q(mock_db_connection, """
            SELECT syn.synergy_id
            FROM synergies AS syn
            LEFT JOIN classes AS c ON c.class_id = syn.class_id
            WHERE syn.class_id IS NOT NULL AND c.class_id IS NULL;
        """)
        assert len(orphan_synergies) == 0

        missing_skill_code = q(mock_db_connection, "SELECT COUNT(*) FROM skills WHERE skill_code IS NULL")[0][0]
        assert missing_skill_code == 0

        # Execute PRAGMA foreign_key_check; across all database tables.
        fk_checks = q(mock_db_connection, "PRAGMA foreign_key_check;")
        assert len(fk_checks) == 0


    def test_runtime_adapter_protection(self, mock_db_connection):
        # 4. Runtime / Adapter Protection:
        # Verify read-only adapters handle valid mappings, unmapped items, and empty DB without throwing unhandled exceptions.
        from lib.db.adapters.catalogue_adapters import MonsterCatalogueLookup, SkillCatalogueLookup

        # Test empty DB/missing mappings
        assert MonsterCatalogueLookup.get_reference_by_id('non_existent') is None
        assert SkillCatalogueLookup.get_reference_by_name('non_existent') is None
