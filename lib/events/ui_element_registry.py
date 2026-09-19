import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

@dataclass
class UIElementDescriptor:
    element_id: str
    module: str
    screen: str
    element_type: str

class CommonUI(str, Enum):
    BTN_SAVE = "btn_save"
    BTN_CANCEL = "btn_cancel"

class UIElementRegistry:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = super(UIElementRegistry, cls).__new__(cls)
            cls._instance._elements = {}
        return cls._instance

    def __new__(cls):
        return cls.instance()

    def register(self, descriptor: UIElementDescriptor) -> None:
        key = (descriptor.module, descriptor.screen, descriptor.element_id)
        if key in self._elements:
            logger.warning(f"[UIRegistry] Duplicate registration: {descriptor.module}/{descriptor.screen}/{descriptor.element_id}")
        self._elements[key] = descriptor

    def get_all(self) -> List[UIElementDescriptor]:
        return list(self._elements.values())

    def clear(self) -> None:
        if hasattr(self, '_elements'):
            self._elements.clear()
