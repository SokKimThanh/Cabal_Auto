import json
import logging
from pathlib import Path
from lib.db.services.icon_service import IconService
from lib.db.services.ui_element_service import UIElementService
from lib.events.ui_element_registry import UIElementRegistry
from lib.events.event_bus import EventBus, IconManagerSyncEvent

logger = logging.getLogger(__name__)


class IconSyncManager:
    def __init__(
        self, icon_service: IconService, json_path: str = "ui/helpers/icons.json"
    ):
        self.icon_service = icon_service
        self.json_path = Path(json_path)
        self._bind_events()

    def _bind_events(self):
        """Đăng ký lắng nghe sự kiện đồng bộ từ EventBus."""
        EventBus.bind(IconManagerSyncEvent, self._handle_sync_event)

    def _handle_sync_event(self, event: IconManagerSyncEvent):
        """Tự động xuất ra file JSON khi nhận được sự kiện."""
        self.export_to_json()

    def import_from_json(self) -> bool:
        """
        Nạp dữ liệu từ file icons.json vào cơ sở dữ liệu.
        Chỉ chèn nếu chưa tồn tại (ON CONFLICT DO NOTHING).
        Format json: {"icon_key": ["filepath_stem", "emoji"]}
        """
        if not self.json_path.exists():
            logger.warning(f"JSON file not found: {self.json_path}")
            return False

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for icon_key, values in data.items():
                if not isinstance(values, list) or len(values) < 2:
                    continue

                filepath_stem = values[0]
                fallback_emoji = values[1]

                # Dùng icon_service.insert_ignore_icon (phải bổ sung hàm này)
                self.icon_service.insert_ignore_icon(
                    {
                        "icon_key": icon_key,
                        "name": icon_key,
                        "filepath": filepath_stem,
                        "fallback_emoji": fallback_emoji,
                        "category": "General",
                    }
                )

            # Update cache in IconHelper
            try:
                from ui.helpers.icon_helper import get_icon_helper
                helper = get_icon_helper()
                tooltip_keys = self.icon_service.get_all_tooltip_keys()
                helper.update_tooltip_keys(tooltip_keys)
            except Exception as cache_error:
                logger.error(f"Failed to update IconHelper tooltip cache: {cache_error}")

            return True
        except Exception as e:
            logger.error(f"Error importing from JSON: {e}")
            return False

    def export_to_json(self) -> bool:
        """
        Xuất dữ liệu từ cơ sở dữ liệu ra file icons.json.
        Ghi đè file. Format xuất: {"icon_key": ["filepath_stem", "emoji"]}
        """
        try:
            icons = self.icon_service.get_all_icons()

            export_data = {}
            for icon in icons:
                icon_key = icon.get("icon_key")
                filepath = icon.get("filepath", "")
                fallback_emoji = icon.get("fallback_emoji", "❓")

                # Hàm ui/helpers/icon_helper.py chỉ dùng phần stem của filepath để nối .png/.ico
                # Ví dụ filepath="btn_add.png" -> btn_add
                if filepath:
                    filepath = Path(filepath).stem
                else:
                    filepath = None

                export_data[icon_key] = [filepath, fallback_emoji]

            # Tạo thư mục cha nếu chưa có
            self.json_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)

            try:
                from ui.helpers.icon_helper import get_icon_helper
                helper = get_icon_helper()
                if hasattr(helper, 'reload_icon_map'):
                    helper.reload_icon_map()
            except Exception as e:
                logger.error(f"Failed to reload icon map: {e}")

            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False


    def refresh_icon_tooltip_cache(self):
        """Reload tooltip keys from DB and update IconHelper cache."""
        try:
            from ui.helpers.icon_helper import get_icon_helper
            helper = get_icon_helper()
            tooltip_keys = self.icon_service.get_all_tooltip_keys()
            helper.update_tooltip_keys(tooltip_keys)
        except Exception as e:
            logger.error(f"Failed to refresh IconHelper tooltip cache: {e}")

    def sync_registry_to_db(self, db_conn) -> bool:
        """
        Đọc metadata từ UIElementRegistry và đồng bộ xuống bảng ui_elements.
        """
        try:
            ui_element_service = UIElementService(db_conn)
            registry_elements = UIElementRegistry.instance().get_all()

            elements_data = []
            for desc in registry_elements:
                is_exclusive = desc.is_exclusive
                # Mặc định sidebar_button hoặc tab chính là exclusive nếu chưa được cấu hình
                if getattr(desc, 'element_type', '') in ['sidebar_button', 'tab_main'] or desc.element_id.startswith('tab_') or desc.element_id.startswith('btn_'):
                    is_exclusive = True

                elements_data.append({
                    "element_id": desc.element_id,
                    "module_name": desc.module,
                    "screen_name": desc.screen,
                    "component_type": desc.element_type,
                    "is_exclusive": is_exclusive,
                    "description": f"Auto-registered from {desc.module}/{desc.screen}"
                })

            if elements_data:
                ui_element_service.bulk_upsert_elements(elements_data)
                logger.info(f"Đã đồng bộ {len(elements_data)} UI elements từ Registry xuống DB.")
            return True
        except Exception as e:
            logger.error(f"Lỗi đồng bộ UIElementRegistry xuống DB: {e}")
            return False
