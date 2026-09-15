from typing import List, Dict, Any, Optional
from lib.db.services.translation_service import TranslationService
from lib.db.services.translation_sync_manager import TranslationSyncManager
from lib.events.event_bus import EventBus, TranslationDataUpdatedEvent
import logging

logger = logging.getLogger(__name__)

class LanguageManagerController:
    """
    Controller handling business logic for the Language Manager UI.
    """
    def __init__(self):
        self.translation_service = TranslationService()

    def get_all_grouped(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch all translations grouped by namespace/key."""
        return self.translation_service.get_all_grouped(namespace)

    def get_namespaces(self) -> List[str]:
        """Fetch list of all unique namespaces."""
        return self.translation_service.get_namespaces()

    def save_translation(self, namespace: str, key: str, en_text: str, vi_text: str) -> bool:
        """
        Upserts both EN and VI texts for the given namespace/key.
        Emits TranslationDataUpdatedEvent on success.
        """
        success = True
        if en_text is not None:
            if not self.translation_service.update_translation(namespace, key, "en", en_text.strip()):
                success = False

        if vi_text is not None:
            if not self.translation_service.update_translation(namespace, key, "vi", vi_text.strip()):
                success = False

        if success:
            EventBus.trigger(TranslationDataUpdatedEvent())
            logger.info(f"Saved translation for {namespace}.{key}")

        return success

    def delete_key(self, namespace: str, key: str) -> bool:
        """
        Deletes all translations for the given namespace/key.
        Emits TranslationDataUpdatedEvent on success.
        """
        if self.translation_service.delete_key(namespace, key):
            EventBus.trigger(TranslationDataUpdatedEvent())
            logger.info(f"Deleted translation for {namespace}.{key}")
            return True
        return False

    def sync_to_json(self) -> bool:
        """Exports the database contents to static JSON files."""
        return TranslationSyncManager.export_to_json()
