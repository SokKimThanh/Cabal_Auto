import datetime
from typing import List, Dict, Any, Optional
from lib.db.connection import get_connection


class TranslationService:
    def __init__(self):
        pass

    def get_total_count(self) -> int:
        """Returns the total number of translation records in the database."""
        conn, is_local = get_connection()
        if not conn:
            return 0
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM translations")
            row = cursor.fetchone()
            return row[0] if row else 0
        except Exception as e:
            print(f"[TranslationService] Count error: {e}")
            return 0
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def get_all(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            if namespace:
                cursor.execute(
                    "SELECT id, namespace, key, lang, text, updated_at FROM translations WHERE namespace = ?",
                    (namespace,),
                )
            else:
                cursor.execute(
                    "SELECT id, namespace, key, lang, text, updated_at FROM translations"
                )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[TranslationService] Read error: {e}")
            return []
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def get_all_grouped(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns all translations grouped by (namespace, key) in the format:
        [
            {
                "namespace": "global",
                "key": "hello",
                "en": "Hello",
                "vi": "Xin chào",
                "updated_at": "2024-05-20T10:00:00"
            },
            ...
        ]
        """
        conn, is_local = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()

            query = """
                SELECT namespace, key,
                       MAX(CASE WHEN lang = 'en' THEN text END) AS en,
                       MAX(CASE WHEN lang = 'vi' THEN text END) AS vi,
                       MAX(updated_at) AS updated_at
                FROM translations
            """
            params = []
            if namespace:
                query += " WHERE namespace = ?"
                params.append(namespace)

            query += " GROUP BY namespace, key"

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[TranslationService] get_all_grouped error: {e}")
            return []
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def get_namespaces(self) -> List[str]:
        """Returns a list of unique namespaces in the database."""
        conn, is_local = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT namespace FROM translations ORDER BY namespace")
            return [row["namespace"] for row in cursor.fetchall()]
        except Exception as e:
            print(f"[TranslationService] get_namespaces error: {e}")
            return []
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def update_translation(self, namespace: str, key: str, lang: str, text: str) -> bool:
        """
        Updates an existing translation or inserts a new one if it doesn't exist.
        Used by the UI when a user edits/saves a translation.
        """
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            now_str = datetime.datetime.now().isoformat()

            cursor.execute(
                """
                INSERT INTO translations (namespace, key, lang, text, updated_at)
                VALUES (:namespace, :key, :lang, :text, :updated_at)
                ON CONFLICT(namespace, key, lang) DO UPDATE SET
                    text = EXCLUDED.text,
                    updated_at = EXCLUDED.updated_at
                """,
                {
                    "namespace": namespace,
                    "key": key,
                    "lang": lang,
                    "text": text,
                    "updated_at": now_str,
                },
            )
            conn.commit()
            return True
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"[TranslationService] update_translation error: {e}")
            return False
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def delete_key(self, namespace: str, key: str) -> bool:
        """Deletes all language variants for a given namespace and key."""
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM translations WHERE namespace = ? AND key = ?",
                (namespace, key)
            )
            conn.commit()
            return True
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"[TranslationService] delete_key error: {e}")
            return False
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def upsert(self, namespace: str, key: str, lang: str, text: str) -> bool:
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()

            now_str = datetime.datetime.now().isoformat()

            cursor.execute(
                """
                INSERT INTO translations (namespace, key, lang, text, updated_at)
                VALUES (:namespace, :key, :lang, :text, :updated_at)
                ON CONFLICT(namespace, key, lang) DO NOTHING
                """,
                {
                    "namespace": namespace,
                    "key": key,
                    "lang": lang,
                    "text": text,
                    "updated_at": now_str,
                },
            )
            conn.commit()
            return True
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"[TranslationService] Upsert error: {e}")
            return False
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def bulk_upsert(
        self, namespace: str, translations: Dict[str, Dict[str, str]]
    ) -> bool:
        """
        Bulk upsert translations for a specific namespace.
        translations format: { lang: { key: text } }
        """
        conn, is_local = get_connection()
        if not conn:
            return False
        try:
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            now_str = datetime.datetime.now().isoformat()

            for lang, mapping in translations.items():
                for key, text in mapping.items():
                    cursor.execute(
                        """
                        INSERT INTO translations (namespace, key, lang, text, updated_at)
                        VALUES (:namespace, :key, :lang, :text, :updated_at)
                        ON CONFLICT(namespace, key, lang) DO NOTHING
                        """,
                        {
                            "namespace": namespace,
                            "key": key,
                            "lang": lang,
                            "text": text,
                            "updated_at": now_str,
                        },
                    )
            conn.commit()
            return True
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"[TranslationService] Bulk upsert error: {e}")
            return False
        finally:
            if is_local and conn:
                try:
                    conn.close()
                except Exception:
                    pass
