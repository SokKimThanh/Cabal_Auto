import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib
import pkgutil
import lib.i18n
from lib.db.services.translation_service import TranslationService
import database

def migrate_translations():
    print("Starting translation migration...")

    # Initialize DB (which creates the translations table if it doesn't exist)
    database.init_database()

    service = TranslationService()

    # Find all *_TRANSLATIONS dictionaries in lib.i18n
    package = lib.i18n

    # Reload package to ensure we capture all dynamically imported namespaces
    importlib.reload(package)

    # We will import all modules in lib.i18n to ensure they self-register
    for _, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        if not is_pkg:
            try:
                importlib.import_module(module_name)
            except Exception as e:
                print(f"Failed to import {module_name}: {e}")

    # Use the registry to fetch the currently registered namespaces and dicts
    # The dictionary structure is _REGISTRY[namespace][lang] = { key: text }
    # So we can just access it using the internal registry data, but to be clean,
    # we can use the private registry variable since we're a script inside the app,
    # or expose a method. Since we only need the dicts, we'll access _REGISTRY directly.
    registry = getattr(lib.i18n, '_REGISTRY', {})

    total_namespaces = len(registry)
    print(f"Found {total_namespaces} namespaces to migrate.")

    total_keys = 0

    for namespace, translations in registry.items():
        print(f"Migrating namespace: {namespace}")

        # translations format is { lang: { key: text } }
        success = service.bulk_upsert(namespace, translations)

        if success:
            keys_count = sum(len(mapping) for mapping in translations.values())
            total_keys += keys_count
            print(f"  -> Successfully migrated {keys_count} translation items.")
        else:
            print(f"  -> Failed to migrate namespace: {namespace}")

    print(f"Migration complete. Total translation items migrated: {total_keys}")

    # Display final row count
    try:
        rows = service.get_all()
        print(f"Current row count in translations table: {len(rows)}")
    except Exception as e:
        print(f"Failed to fetch row count: {e}")

if __name__ == "__main__":
    migrate_translations()
