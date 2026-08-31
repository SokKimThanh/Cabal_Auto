import sys

def modify_file():
    with open('lib/i18n/__init__.py', 'r') as f:
        content = f.read()

    new_func = """
import logging
logger = logging.getLogger(__name__)

def load_from_db() -> None:
\t\"\"\"Load all translations from the database and feed them into the registry.\"\"\"
\ttry:
\t\tfrom lib.db.services.translation_service import TranslationService
\t\tservice = TranslationService()
\t\trows = service.get_all()
\t\tfor row in rows:
\t\t\tregister(row['namespace'], row['lang'], {row['key']: row['text']})
\t\tlogger.info(f"[i18n] Successfully hydrated {len(rows)} translations from database.")
\texcept Exception as e:
\t\tlogger.error(f"[i18n] Failed to hydrate from database: {e}. Falling back to dictionary-based self-registration.")
"""

    # Let's replace the existing load_from_db function

    if "def load_from_db" in content:
        import re
        content = re.sub(r'def load_from_db\(\) -> None:.*?print\(f"\[i18n\] Failed to hydrate from database: \{e\}\. Falling back to dictionary-based self-registration\."\)', new_func.strip(), content, flags=re.DOTALL)
        with open('lib/i18n/__init__.py', 'w') as f:
            f.write(content)
        print("Successfully updated lib/i18n/__init__.py")
    else:
        print("def load_from_db not found")

modify_file()
