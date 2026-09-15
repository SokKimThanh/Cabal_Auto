import json
import logging
from pathlib import Path
from lib.db.services.translation_service import TranslationService
from lib.i18n.translations import GLOBAL_TRANSLATIONS

logger = logging.getLogger(__name__)

class TranslationSyncManager:
    """
    Manages synchronization of translation data between the database (SSoT)
    and static JSON files or initial seed data.
    """

    @classmethod
    def seed_initial_data(cls) -> bool:
        """
        Seeds the initial data from the hardcoded dictionary to the DB.
        Should only be called when the DB is empty.
        """
        try:
            logger.info("Seeding initial translation data...")
            service = TranslationService()

            # Using global namespace for seed data initially
            # In a real app this might be partitioned
            for lang, translations in GLOBAL_TRANSLATIONS.items():
                service.bulk_upsert("global", {lang: translations})

            logger.info("Translation data seeded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to seed initial translation data: {e}")
            return False

    @classmethod
    def export_to_json(cls) -> bool:
        """
        Fetches all translations from the database and exports them to assets/i18n/<lang>.json
        """
        try:
            service = TranslationService()
            all_translations = service.get_all()

            # Group by language then namespace/key for nested output (or flat structure based on requirements)
            # Requirements state: "group them by language, and export to assets/i18n/<lang>.json"

            data_by_lang = {}
            for row in all_translations:
                lang = row["lang"]
                ns = row["namespace"]
                key = row["key"]
                text = row["text"]

                if lang not in data_by_lang:
                    data_by_lang[lang] = {}

                # Using a flat key structure since app typically uses t(key)
                # but could use namespaced keys if required
                if ns == "global":
                    data_by_lang[lang][key] = text
                else:
                    data_by_lang[lang][f"{ns}.{key}"] = text

            i18n_dir = Path("assets/i18n")
            i18n_dir.mkdir(parents=True, exist_ok=True)

            for lang, mapping in data_by_lang.items():
                file_path = i18n_dir / f"{lang}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(mapping, f, ensure_ascii=False, indent=2)

            logger.info("Successfully exported translations to JSON.")
            return True

        except Exception as e:
            logger.error(f"Failed to export translations to JSON: {e}")
            return False
