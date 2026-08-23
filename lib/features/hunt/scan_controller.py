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
        icons: Any
    ):
        self.vision_engine_getter = vision_engine_getter
        self.set_status_text = set_status_text
        self.set_status_icon = set_status_icon
        self.show_results = show_results
        self.icons = icons
        self.logger = logging.getLogger(__name__)

    def run_scan(self, manual: bool = False):
        if manual:
            print("[UI] Manual scan triggered.")
            self.set_status_text("🔍 Đang quét…")
            self.set_status_icon(self.icons.SCANING)
            print("[UI] Scan status: scanning")

        def worker():
            try:
                print("[AutoScan] Started after game window connected.")

                # Check vision engine
                vision_engine = self.vision_engine_getter()
                if not vision_engine:
                    raise Exception("Vision engine not available.")

                from lib.features.hunt.scanner import AutoScanner
                scanner = AutoScanner(vision_engine)

                # Boundary check: window
                window_info = scanner.detect_window()
                if not window_info:
                    print("[AutoScan] Warning: Game window not connected. Skipping scan.")
                    if manual:
                        self.set_status_text("❌ Lỗi khi quét: Game window chưa kết nối.")
                        self.set_status_icon(self.icons.SCAN_FAILED)
                        print("[UI] Scan status: failed")
                    return

                # Check DB connection
                from lib.db.connection import get_connection
                conn, _ = get_connection()
                if not conn:
                    print("[AutoScan] Warning: DB not ready. Skipping scan creation.")
                    if manual:
                        self.set_status_text("❌ Lỗi khi quét: DB chưa sẵn sàng.")
                        self.set_status_icon(self.icons.SCAN_FAILED)
                        print("[UI] Scan status: failed")
                    return

                try:
                    conn.close()
                except:
                    pass

                # Boundary check: template lists (if empty)
                if not vision_engine.templates and not hasattr(vision_engine, 'add_template'):
                    print("[AutoScan] Warning: Template list empty. Skipping scan.")
                    if manual:
                        self.set_status_text("❌ Lỗi khi quét: Không có templates.")
                        self.set_status_icon(self.icons.SCAN_FAILED)
                        print("[UI] Scan status: failed")
                    return

                # Get frame and check
                print("[AutoScan] Capturing frame...")

                if scanner.screen_capture is None:
                    raise Exception("Screen capture not available.")

                if not getattr(scanner.screen_capture, 'hwnd', None) == window_info['hwnd']:
                    import win32gui
                    title = win32gui.GetWindowText(window_info['hwnd'])
                    if not scanner.screen_capture.start(title):
                        raise Exception("Failed to start screen capture.")

                frame = scanner.screen_capture.get_frame(timeout=1.0)
                if frame is None:
                    raise Exception("Frame is None.")

                # Run scan logic
                results = scanner.run_scan()
                print("[AutoScan] Scan completed successfully.")

                if manual:
                    self.set_status_text("✅ Quét hoàn tất")
                    self.set_status_icon(self.icons.SCAN_COMPLETE)
                    print("[UI] Scan status: completed")
                    self.show_results(results)

                    def restore_icon():
                        import time
                        time.sleep(3)
                        self.set_status_icon(self.icons.SCAN_SCREEN)
                    threading.Thread(target=restore_icon, daemon=True).start()

            except Exception as e:
                print(f"[AutoScan] Exception during scan: {e}")
                self.logger.error(f"[AutoScan] Exception during scan: {traceback.format_exc()}")
                if manual:
                    self.set_status_text("❌ Lỗi khi quét")
                    self.set_status_icon(self.icons.SCAN_FAILED)
                    print("[UI] Scan status: failed")
                    def restore_icon():
                        import time
                        time.sleep(3)
                        self.set_status_icon(self.icons.SCAN_SCREEN)
                    threading.Thread(target=restore_icon, daemon=True).start()

        threading.Thread(target=worker, daemon=True).start()
