from tkinter import filedialog
from lib.ui.dialog_service import DialogService
from lib.events.event_bus import EventBus, VisionScanRegionEvent, VisionAddTemplateEvent, VisionManageTemplatesEvent

class MenuVisionController:
    """Handles vision-related actions triggered by the Main Menu"""

    def __init__(self, app, window_controller):
        self.app = app
        self.window_controller = window_controller
        self._t = getattr(self.app, "_t", lambda k, **kw: k)

        EventBus.bind(VisionScanRegionEvent, lambda e: self._scan_region())
        EventBus.bind(VisionAddTemplateEvent, lambda e: self._add_template())
        EventBus.bind(VisionManageTemplatesEvent, lambda e: self._manage_templates())

    def _scan_region(self):
        print("[Vision] Scan region - TODO Phase 2")
        DialogService.show_info(
            "Vision - Scan Region",
            "Scan Region feature will be available in Phase 2.\n\n"
            "This will allow you to:\n"
            "• Select a region on screen\n"
            "• Scan for templates in real-time\n"
            "• Save ROI coordinates",
        )

    def _add_template(self):
        print("[Vision] Auto Detect / Add Template triggered via Hotkey (Ctrl+T)")
        try:
            # We want to perform a manual scan for now to capture the screen patches
            if hasattr(self.app, "scan_controller") and self.app.scan_controller:
                self.app.scan_controller.run_scan(manual=True)
            else:
                DialogService.show_info(
                    "Vision - Auto Scan",
                    "Please ensure the application is initialized to use this feature.",
                )
        except Exception as e:
            print(f"[Vision] Error running auto detect via hotkey: {e}")
            DialogService.show_error(
                self._t("error"),
                f"Cannot perform scan:\n{e}",
            )

    def _manage_templates(self):
        print("[Vision] Manage templates - opening wizard")
        if self.window_controller:
            self.window_controller.open_vision_wizard()
