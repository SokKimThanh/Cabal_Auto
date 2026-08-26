import copy
from typing import Any, Dict

from lib.features.hunt.hunt_config import save_hunt_config

class OverlayController:
    """Controller for overlay UI lifecycle."""

    def __init__(self, parent: Any):
        self.parent = parent

    def open_settings(self, *_args) -> None:
        from ui.utils.overlay_settings import OverlaySettingsDialog

        hunt_cfg = getattr(self.parent, "hunt_cfg", {})
        overlay_cfg = copy.deepcopy(hunt_cfg.get("overlay", {}))

        def on_apply(new_config: Dict[str, Any]) -> None:
            self.parent.hunt_cfg["overlay"] = new_config
            save_hunt_config(self.parent.hunt_cfg)

        dialog = OverlaySettingsDialog(
            parent=self.parent,
            current_config=overlay_cfg,
            lang=getattr(self.parent, "lang", "vi"),
            on_apply=on_apply,
        )
        dialog.show()
