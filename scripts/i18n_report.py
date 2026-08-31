import sys
import os
import argparse
from typing import Dict, Set

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import database
from lib.db.services.translation_service import TranslationService


def report_missing_keys(lang: str):
    database.init_database()
    service = TranslationService()

    rows = service.get_all()

    # Organize data: namespace -> key -> set(langs)
    # Also find superset of keys per namespace

    ns_keys: Dict[str, Set[str]] = {}
    ns_lang_keys: Dict[str, Dict[str, Set[str]]] = {}

    for row in rows:
        ns = row['namespace']
        key = row['key']
        l = row['lang']

        if ns not in ns_keys:
            ns_keys[ns] = set()
            ns_lang_keys[ns] = {}

        ns_keys[ns].add(key)

        if l not in ns_lang_keys[ns]:
            ns_lang_keys[ns][l] = set()

        ns_lang_keys[ns][l].add(key)

    print(f"Missing keys report for language: '{lang}'")
    print("-" * 50)

    total_missing = 0
    total_keys = 0

    for ns in sorted(ns_keys.keys()):
        all_keys = ns_keys[ns]
        lang_keys = ns_lang_keys[ns].get(lang, set())

        missing = all_keys - lang_keys

        total_keys += len(all_keys)
        total_missing += len(missing)

        if missing:
            print(f"Namespace '{ns}': Missing {len(missing)} of {len(all_keys)} keys")
            for k in sorted(missing):
                print(f"  - {k}")
        else:
            print(f"Namespace '{ns}': Complete ({len(all_keys)} keys)")

    print("-" * 50)
    print(f"Total missing keys for '{lang}': {total_missing} out of {total_keys} total keys.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Report missing translation keys for a given language.")
    parser.add_argument("--lang", required=True, help="The target language code (e.g., 'en', 'vi', 'zh')")
    args = parser.parse_args()

    report_missing_keys(args.lang)
