from typing import Any, Dict
from lib.features.hunt.hunt_config import load_hunt_config, save_hunt_config

class ConfigRepository:
    """
    Thủ thư: Đóng gói toàn bộ logic quản lý, đọc/ghi tập tin cấu hình (config).
    """

    def __init__(self):
        self._config: Dict[str, Any] = load_hunt_config()

    def get_config(self) -> Dict[str, Any]:
        """Trả về toàn bộ cấu hình hiện tại."""
        return self._config

    def set_config(self, new_config: Dict[str, Any]) -> None:
        """Cập nhật toàn bộ cấu hình mới."""
        self._config = new_config

    def get(self, key: str, default: Any = None) -> Any:
        """Lấy một giá trị cụ thể từ cấu hình."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Cập nhật một giá trị cụ thể trong cấu hình."""
        self._config[key] = value

    def save(self) -> bool:
        """Lưu cấu hình hiện tại xuống đĩa cứng (ổ đĩa)."""
        return save_hunt_config(self._config)
