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
        print("[Vision] Add template")
        try:
            filetypes = [
                ("Image files", "*.png *.jpg *.jpeg *.bmp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*"),
            ]
            file_path = filedialog.askopenfilename(
                title=self._t("vision_add_template"),
                filetypes=filetypes,
            )
            if file_path:
                print(f"[Vision] Selected template: {file_path}")
                DialogService.show_info(
                    "Vision - Add Template",
                    f"Template selected:\n{file_path}\n\n"
                    "Full integration will be available in Phase 2.\n"
                    "Use Vision Wizard (Ctrl+Shift+V) to manage templates.",
                )
        except Exception as e:
            print(f"[Vision] Error adding template: {e}")
            DialogService.show_error(
                self._t("error"),
                f"Cannot add template:\n{e}",
            )

    def _manage_templates(self):
        print("[Vision] Manage templates - opening wizard")
        if self.window_controller:
            self.window_controller.open_vision_wizard()
