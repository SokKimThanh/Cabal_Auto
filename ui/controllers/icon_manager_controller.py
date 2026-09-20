from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class OperationResult:
    success: bool
    message: str = ""
    data: Any = None


@dataclass
class SaveIconResult:
    success: bool
    message: str = ""
    category_id: Optional[int] = None
    category_name: str = "General"

import threading
import sqlite3
import logging

from lib.db.services.icon_service import IconService
from lib.db.services.translation_service import TranslationService
from lib.events.event_bus import EventBus, TranslationDataUpdatedEvent

logger = logging.getLogger(__name__)

class IconManagerController:
    def __init__(self, app, icon_service, tree_model, image_model, icon_helper, categories_map):
        self.app = app
        self.icon_service = icon_service
        self.tree_model = tree_model
        self.image_model = image_model
        self.icon_helper = icon_helper
        self.categories_map = categories_map

    def _t(self, key: str, **kwargs) -> str:
        if hasattr(self.app, '_t'):
            return self.app._t(key, **kwargs)
        from lib.i18n import t
        lang = getattr(self.app, 'lang', 'vi')
        t_kwargs = {"lang": lang}
        if "default" in kwargs:
            t_kwargs["default"] = kwargs.pop("default")
        if "ns" in kwargs:
            t_kwargs["ns"] = kwargs.pop("ns")
        translated = t(key, **t_kwargs)
        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except Exception:
                pass
        return translated

    def update_categories_map(self, categories_map):
        self.categories_map = categories_map

    def validate_icon_data(self, form_data) -> OperationResult:
        icon_key = form_data.get('icon_key', '').strip()
        if not icon_key:
            return OperationResult(success=False, message="Icon Key is required.")
        return OperationResult(success=True)

    def save_icon(self, form_data, old_filepath=None, just_imported_file=None) -> SaveIconResult:
        validation = self.validate_icon_data(form_data)
        if not validation.success:
            return SaveIconResult(success=False, message=validation.message)

        icon_key = form_data['icon_key'].strip()
        new_filepath = form_data.get('filepath', '').strip()
        cat_name = form_data.get('category', '').strip() or "General"
        cat_id = self.categories_map.get(cat_name, 1)

        icon_data = {
            "icon_key": icon_key,
            "name": form_data.get('name', '').strip(),
            "filepath": new_filepath,
            "fallback_emoji": form_data.get('fallback_emoji', '').strip(),
            "tooltip_translation_key": form_data.get('tooltip_key', '').strip(),
            "category_id": cat_id,
            "description": ""
        }

        t_key = icon_data["tooltip_translation_key"]
        if t_key:
            val_en = form_data.get('tooltip_en', '').strip() or t_key
            val_vi = form_data.get('tooltip_vi', '').strip() or t_key
            try:
                ts = TranslationService()
                ts.upsert(namespace="", key=t_key, lang="en", text=val_en)
                ts.upsert(namespace="", key=t_key, lang="vi", text=val_vi)
                EventBus.trigger(TranslationDataUpdatedEvent())
            except Exception as e:
                logger.warning(f"Lỗi lưu bản dịch: {e}")

        success = self.icon_service.upsert_icon(icon_data)
        if success:
            if hasattr(self.icon_helper, 'clear_cache'):
                self.icon_helper.clear_cache(icon_key)
            elif hasattr(self.icon_helper, '_cache'):
                keys_to_remove = [k for k in self.icon_helper._cache.keys() if k.startswith(f"{icon_key}_")]
                for k in keys_to_remove:
                    del self.icon_helper._cache[k]

            icon_data["category_name"] = cat_name
            existing_files = set()
            if hasattr(self.icon_helper, 'icon_dirs'):
                for d in self.icon_helper.icon_dirs:
                    if d.exists():
                        try:
                            for file in d.iterdir():
                                if file.is_file():
                                    existing_files.add(file.name)
                        except Exception:
                            pass
            status = self.icon_helper.evaluate_icon_status(icon_data, existing_files_cache=existing_files)
            self.tree_model.update_icon_in_cache(icon_data, status)
            return SaveIconResult(success=True, category_id=cat_id, category_name=cat_name)
        else:
            logger.error(f"Lỗi database: Ghi icon {icon_key} thất bại.")
            if new_filepath and new_filepath != old_filepath:
                 usages = self.icon_service.get_icons_by_filepath(new_filepath)
                 if not usages:
                      if just_imported_file == new_filepath:
                          self.image_model.remove_file(new_filepath)

            return SaveIconResult(success=False, message="Failed to save icon data.")

    def delete_icon(self, icon_key) -> OperationResult:
        is_safe, usages = self.tree_model.check_safe_delete(icon_key)
        if not is_safe:
            msg = self._t("msg_icon_in_use", default=f"Icon '{icon_key}' đang được sử dụng ở {len(usages)} nơi. Vui lòng gỡ bỏ trước khi xóa.", count=len(usages), icon_key=icon_key)
            return OperationResult(success=False, message=msg, data="in_use")

        try:
            success = self.icon_service.delete_icon(icon_key)
            if success:
                self.tree_model.invalidate_icon(icon_key)
                return OperationResult(success=True)
            else:
                return OperationResult(success=False, message=f"Failed to delete icon '{icon_key}'.")
        except ValueError as e:
            if str(e) == "icon_in_use_error":
                usages = self.icon_service.get_usages(icon_key)
                msg = self._t("msg_icon_in_use", default=f"Icon '{icon_key}' đang được sử dụng ở {len(usages)} nơi. Vui lòng gỡ bỏ trước khi xóa.", count=len(usages), icon_key=icon_key)
                return OperationResult(success=False, message=msg, data="in_use")
            return OperationResult(success=False, message=str(e))

    def add_usage(self, icon_key, mod, comp, elem) -> OperationResult:
        if not icon_key:
            return OperationResult(success=False, message="Vui lòng Lưu icon trước khi gắn usages.")
        if not mod or not comp or not elem:
            return OperationResult(success=False, message="Vui lòng nhập đủ thông tin Mod, Comp, ID.")

        if self.icon_service.register_usage(icon_key, mod, comp, elem):
            self.tree_model.usage_cache.pop(icon_key, None)
            self.tree_model.load_usages_for_icon_async(icon_key, None)
            return OperationResult(success=True)
        else:
            return OperationResult(success=False, message="Không thể gắn usage, có thể bị trùng lặp.")

    def delete_usage(self, icon_key, usage_id) -> OperationResult:
        if hasattr(self.icon_service, "delete_usage") and self.icon_service.delete_usage(usage_id):
            self.tree_model.usage_cache.pop(icon_key, None)
            self.tree_model.load_usages_for_icon_async(icon_key, None)
            return OperationResult(success=True)
        else:
            return OperationResult(success=False, message="Gỡ usage thất bại.")

    def sync_system_icons_async(self, on_complete, on_error):
        def run_sync():
            try:
                from database import MonsterDatabase
                thread_conn = sqlite3.connect(MonsterDatabase.DB_PATH)
                thread_icon_service = IconService(thread_conn)

                mappings = self.icon_helper.icon_map
                count = 0
                for icon_key, (icon_stem, emoji) in mappings.items():
                    icon_data = {
                        "icon_key": icon_key,
                        "name": icon_key.capitalize(),
                        "filepath": f"{icon_stem}.png",
                        "fallback_emoji": emoji,
                        "tooltip_translation_key": f"icon_tooltip_{icon_key}",
                        "category": "System",
                        "description": f"System icon for {icon_key}"
                    }
                    existing = thread_icon_service.get_icon_by_key(icon_key)
                    if not existing:
                        thread_icon_service.upsert_icon(icon_data)
                        count += 1

                on_complete(count)
            except Exception as e:
                on_error(str(e))

        threading.Thread(target=run_sync, daemon=True).start()
