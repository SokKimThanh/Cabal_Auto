import sqlite3
import datetime
from typing import List, Dict, Any, Optional
from lib.db.connection import get_connection

class TranslationService:
    def __init__(self):
        pass

    def get_all(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        conn, is_local = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            if namespace:
                cursor.execute("SELECT id, namespace, key, lang, text, updated_at FROM translations WHERE namespace = ?", (namespace,))
            else:
                cursor.execute("SELECT id, namespace, key, lang, text, updated_at FROM translations")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[TranslationService] Read error: {e}")
            return []
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

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
                ON CONFLICT(namespace, key, lang) DO UPDATE SET
                    text = excluded.text,
                    updated_at = excluded.updated_at
                """,
                {
                    "namespace": namespace,
                    "key": key,
                    "lang": lang,
                    "text": text,
                    "updated_at": now_str
                }
            )
            conn.commit()
            return True
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[TranslationService] Upsert error: {e}")
            return False
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass

    def bulk_upsert(self, namespace: str, translations: Dict[str, Dict[str, str]]) -> bool:
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
                        ON CONFLICT(namespace, key, lang) DO UPDATE SET
                            text = excluded.text,
                            updated_at = excluded.updated_at
                        """,
                        {
                            "namespace": namespace,
                            "key": key,
                            "lang": lang,
                            "text": text,
                            "updated_at": now_str
                        }
                    )
            conn.commit()
            return True
        except Exception as e:
            try: conn.rollback()
            except: pass
            print(f"[TranslationService] Bulk upsert error: {e}")
            return False
        finally:
            if is_local and conn:
                try: conn.close()
                except: pass
