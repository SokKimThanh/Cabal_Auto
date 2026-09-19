import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class CommonUI(str, Enum):
    BTN_SAVE = "btn_save"
    BTN_CANCEL = "btn_cancel"
    BTN_ADD = "btn_add"
    BTN_EDIT = "btn_edit"
    BTN_DELETE = "btn_delete"
    BTN_CLOSE = "btn_close"
    BTN_REFRESH = "btn_refresh"

@dataclass
class UIElementDescriptor:
    element_id: str
    module: str
    screen: str
    element_type: str

class UIElementRegistry:
    _instance = None
    _elements: Dict[Tuple[str, str, str], UIElementDescriptor]

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(UIElementRegistry, cls).__new__(cls, *args, **kwargs)
            cls._instance._elements = {}
        return cls._instance

    def register(self, descriptor: UIElementDescriptor) -> None:
        key = (descriptor.module, descriptor.screen, descriptor.element_id)
        if key in self._elements:
            logger.warning(f"[UIRegistry] Duplicate registration: {key}")
        self._elements[key] = descriptor

    def get_all(self) -> List[UIElementDescriptor]:
        return list(self._elements.values())

    def clear(self) -> None:
        self._elements.clear()
