import copy
from typing import Any, Dict
from lib.features.hunt.hunt_config import load_hunt_config, save_hunt_config

class HuntConfigStore:
    """Central store for hunt configuration state."""

    def __init__(self):
        self._config: Dict[str, Any] = load_hunt_config()

    def get_config(self) -> Dict[str, Any]:
        """Returns a reference to the current hunt config."""
        return self._config

    def set_config(self, new_config: Dict[str, Any]) -> None:
        """Sets the current hunt config."""
        self._config = new_config

    def get(self, key: str, default: Any = None) -> Any:
        """Gets a specific value from the hunt config."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Sets a specific value in the hunt config."""
        self._config[key] = value

    def save(self) -> bool:
        """Persists the current configuration to disk."""
        return save_hunt_config(self._config)
