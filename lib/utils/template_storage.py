import os
import time
import threading
import queue
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class TemplateStorageManager:
    def __init__(self, storage_dir="data/captured_templates", max_size_mb=5.0):
        self.storage_dir = storage_dir
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.is_running = True

        # Ensure directory exists
        os.makedirs(self.storage_dir, exist_ok=True)

        # Start worker thread
        self.worker_thread.start()

    def save_templates_async(self, images_list):
        """Non-blocking call to save templates."""
        if not images_list:
            return

        # We push data to the queue to offload I/O from main thread
        self.queue.put(images_list)

    def _worker_loop(self):
        while self.is_running:
            try:
                images_list = self.queue.get(timeout=1.0)

                # Save each image
                timestamp = int(time.time())
                for i, img in enumerate(images_list):
                    if img is None or not isinstance(img, np.ndarray) or img.size == 0:
                        continue

                    filename = f"template_{timestamp}_{i}.png"
                    filepath = os.path.join(self.storage_dir, filename)
                    cv2.imwrite(filepath, img)

                # Enforce rotation logic
                self._enforce_size_limit()

                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"[TemplateStorage] Error in worker loop: {e}")

    def _enforce_size_limit(self):
        """Rotates files if directory size exceeds max_size_bytes."""
        try:
            files = []
            total_size = 0

            # Gather all files and their sizes
            for f in os.listdir(self.storage_dir):
                filepath = os.path.join(self.storage_dir, f)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    mtime = os.path.getmtime(filepath)
                    files.append((filepath, size, mtime))
                    total_size += size

            # If within limit, do nothing
            if total_size <= self.max_size_bytes:
                return

            # Sort files by modification time (oldest first)
            files.sort(key=lambda x: x[2])

            # Delete files until we're under the limit
            for filepath, size, _ in files:
                os.remove(filepath)
                total_size -= size
                logger.debug(f"[TemplateStorage] Rotated (deleted) old file: {filepath}")
                if total_size <= self.max_size_bytes:
                    break
        except Exception as e:
            logger.error(f"[TemplateStorage] Error enforcing size limit: {e}")

    def stop(self):
        self.is_running = False
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)

# Global singleton instance for easy access
storage_manager = TemplateStorageManager()
