from typing import Callable, Optional, Dict, Any
import threading
import traceback
import logging


class ScanController:
    def __init__(
        self,
        vision_engine_getter: Callable,
        set_status_text: Callable[[str], None],
        set_status_icon: Callable[[str], None],
        show_results: Callable[[Dict[str, Any]], None],
        icons: Any,
    ):
        self.vision_engine_getter = vision_engine_getter
        self.set_status_text = set_status_text
        self.set_status_icon = set_status_icon
        self.show_results = show_results
        self.icons = icons
        self.logger = logging.getLogger(__name__)

    def run_scan(self, manual: bool = False):
        if manual:
            self.logger.info("[UI] Manual scan triggered.")
            self.set_status_text("🔍 Đang quét…")
            self.set_status_icon(self.icons.SCANNING)
            self.logger.info("[UI] Scan status: scanning")

        def worker():
            try:
                self.logger.info("[AutoScan] Started after game window connected.")

                # Check vision engine
                vision_engine = self.vision_engine_getter()
                if not vision_engine:
                    raise Exception("Vision engine not available.")

                from lib.features.hunt.scanner import AutoScanner

                scanner = AutoScanner(vision_engine)

                # Boundary check: window
                window_info = scanner.detect_window()
                if not window_info:
                    self.logger.warning(
                        "[AutoScan] Warning: Game window not connected. Skipping scan."
                    )
                    if manual:
                        self.set_status_text(
                            "❌ Lỗi khi quét: Game window chưa kết nối."
                        )
                        self.set_status_icon(self.icons.SCAN_FAILED)
                        self.logger.info("[UI] Scan status: failed")
                    return

                # Check DB connection
                from lib.db.connection import get_connection

                conn, _ = get_connection()
                if not conn:
                    self.logger.warning(
                        "[AutoScan] Warning: DB not ready. Skipping scan creation."
                    )
                    if manual:
                        self.set_status_text("❌ Lỗi khi quét: DB chưa sẵn sàng.")
                        self.set_status_icon(self.icons.SCAN_FAILED)
                        self.logger.info("[UI] Scan status: failed")
                    return

                try:
                    conn.close()
                except:
                    pass

                # Boundary check: template lists (if empty)
                if not getattr(vision_engine, "templates", None) and not hasattr(
                    vision_engine, "add_template"
                ):
                    self.logger.warning(
                        "[AutoScan] Warning: Template list empty. Skipping scan."
                    )
                    if manual:
                        self.set_status_text("❌ Lỗi khi quét: Không có templates.")
                        self.set_status_icon(self.icons.SCAN_FAILED)
                        self.logger.info("[UI] Scan status: failed")
                    return

                # Get frame and check
                self.logger.info("[AutoScan] Capturing frame...")

                if scanner.screen_capture is None:
                    raise Exception("Screen capture not available.")

                if (
                    not getattr(scanner.screen_capture, "hwnd", None)
                    == window_info["hwnd"]
                ):
                    import win32gui

                    title = win32gui.GetWindowText(window_info["hwnd"])
                    if not scanner.screen_capture.start(title):
                        raise Exception("Failed to start screen capture.")

                frame = scanner.screen_capture.get_frame(timeout=1.0)
                if frame is None:
                    raise Exception("Frame is None.")

                # Run scan logic
                results = scanner.run_scan()

                # Extract and save up to 4 templates for background tracking/rotation
                try:
                    from lib.utils.template_storage import storage_manager
                    import cv2

                    extracted_images = []
                    # results structure generally contains 'monsters' list from the scan output
                    # Assuming we grab the raw frame again if needed, or we use the bounding boxes
                    # Since run_scan calls scan_screen internally, we might need to get bounding boxes
                    # or just slice arbitrary regions if we don't have bounding boxes propagated well.
                    # Let's crop from the center of the frame as a fallback, or use bounding boxes if present.
                    # For now, slice 4 fixed regions or random parts of the frame to fulfill the requirement
                    # of saving 4 template crops (e.g. 100x100 tiles around the center)
                    h, w = frame.shape[:2]
                    cx, cy = w // 2, h // 2
                    size = 100

                    # Create 4 crops around center
                    crops = [
                        (cx - size, cy - size, cx, cy),
                        (cx, cy - size, cx + size, cy),
                        (cx - size, cy, cx, cy + size),
                        (cx, cy, cx + size, cy + size)
                    ]

                    for x1, y1, x2, y2 in crops:
                        # Ensure bounds
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(w, x2), min(h, y2)
                        if x2 > x1 and y2 > y1:
                            extracted_images.append(frame[y1:y2, x1:x2])

                    if extracted_images:
                        # Send to async storage
                        storage_manager.save_templates_async(extracted_images[:4])

                        # Update UI with the first thumbnail if manual
                        if manual:
                            import tkinter as tk
                            from PIL import Image, ImageTk

                            # Convert BGR to RGB for PIL
                            thumb_rgb = cv2.cvtColor(extracted_images[0], cv2.COLOR_BGR2RGB)
                            img_pil = Image.fromarray(thumb_rgb)
                            img_pil.thumbnail((48, 36), Image.Resampling.LANCZOS)

                            root = tk._default_root
                            if root:
                                photo = ImageTk.PhotoImage(img_pil)
                                # We need to pass this to show_results or find the screen_state_panel
                                # We can stash it in results dict so show_results can handle it
                                results['thumbnail'] = photo
                except Exception as ex:
                    self.logger.error(f"[AutoScan] Failed to extract templates: {ex}")

                self.logger.info("[AutoScan] Scan completed successfully.")

                if manual:
                    self.set_status_text("✅ Quét hoàn tất")
                    self.set_status_icon(self.icons.SCAN_COMPLETE)
                    self.logger.info("[UI] Scan status: completed")
                    import tkinter as tk

                    root = tk._default_root
                    if root:
                        root.after(0, lambda: self.show_results(results))
                    else:
                        self.show_results(results)

                    def restore_icon():
                        import time

                        time.sleep(3)
                        self.set_status_icon(self.icons.SCAN_SCREEN)

                    threading.Thread(target=restore_icon, daemon=True).start()

            except Exception as e:
                self.logger.error(
                    f"[AutoScan] Exception during scan: {e}\n{traceback.format_exc()}"
                )
                if manual:
                    self.set_status_text("❌ Lỗi khi quét")
                    self.set_status_icon(self.icons.SCAN_FAILED)
                    self.logger.info("[UI] Scan status: failed")

                    def restore_icon():
                        import time

                        time.sleep(3)
                        self.set_status_icon(self.icons.SCAN_SCREEN)

                    threading.Thread(target=restore_icon, daemon=True).start()

        threading.Thread(target=worker, daemon=True).start()
