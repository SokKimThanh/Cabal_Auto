import json
import logging
from pathlib import Path
from lib.db.services.icon_service import IconService
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
                # Ví dụ filepath="btn_add" -> btn_add.png
                export_data[icon_key] = [filepath, fallback_emoji]

            # Tạo thư mục cha nếu chưa có
            self.json_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)

            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False
