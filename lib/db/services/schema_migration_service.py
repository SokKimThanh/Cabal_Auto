import sqlite3
import logging
from lib.db.connection import get_connection

class SchemaMigrationService:
    def __init__(self):
        pass

    def run_migrations(self):
        conn, is_local = get_connection()
        if not conn:
            logging.error("[SchemaMigrationService] Could not get database connection.")
            return False

        try:
            cursor = conn.cursor()

            # Use additive, idempotent ALTER TABLE
            try:
                cursor.execute("ALTER TABLE synergy_effects ADD COLUMN value_text TEXT")
            except sqlite3.OperationalError:
                # Column exists or other error
                pass

            try:
                cursor.execute("ALTER TABLE synergy_effects ADD COLUMN duration_text TEXT")
            except sqlite3.OperationalError:
                pass

            conn.commit()
            return True
        except Exception as e:
            try: conn.rollback()
            except: pass
            logging.error(f"[SchemaMigrationService] Migration error: {e}")
            return False
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

if __name__ == "__main__":
    service = SchemaMigrationService()
    service.run_migrations()
