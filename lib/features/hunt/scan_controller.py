from typing import Callable, Optional, Dict, Any
import threading
import traceback
import logging

from lib.utils.template_storage import TemplateStorageManager
import cv2
import numpy as np
from PIL import Image



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

                # Extract 4 bounding boxes (100x100) around the center of the frame
                h, w = frame.shape[:2]
                cx, cy = w // 2, h // 2
                half = 50
                # Define 4 offsets (e.g., center, top-left, top-right, bottom-left relative to center or just 4 distinct boxes)
                # We'll just slice 4 100x100 boxes around center with some offset
                boxes = [
                    (cx - 50, cy - 50),
                    (cx - 150, cy - 50),
                    (cx + 50, cy - 50),
                    (cx - 50, cy + 50)
                ]
                patches = []
                for bx, by in boxes:
                    x1 = max(0, bx)
                    y1 = max(0, by)
                    x2 = min(w, x1 + 100)
                    y2 = min(h, y1 + 100)
                    patch = frame[y1:y2, x1:x2]
                    if patch.size > 0:
                        patches.append(patch)

                # Save templates async
                storage_manager = TemplateStorageManager()
                storage_manager.save_templates_async(patches)

                # Create 48x36 PIL image thumbnail from the first patch
                thumbnail_pil = None
                if patches:
                    try:
                        # Resize first patch to 48x36
                        thumb_np = cv2.resize(patches[0], (48, 36))
                        # Convert BGR to RGB
                        thumb_rgb = cv2.cvtColor(thumb_np, cv2.COLOR_BGR2RGB)
                        thumbnail_pil = Image.fromarray(thumb_rgb)
                    except Exception as e:
                        self.logger.error(f"[AutoScan] Failed to create thumbnail: {e}")

                # Run scan logic
                results = scanner.run_scan()
                if thumbnail_pil:
                    results["thumbnail"] = thumbnail_pil
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
