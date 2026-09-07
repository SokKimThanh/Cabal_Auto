import os
import time
import threading
import queue
import logging
from pathlib import Path
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class TemplateStorageManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(TemplateStorageManager, cls).__new__(cls)
                cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self, storage_dir="data/captured_templates", max_size_mb=5):
        self.storage_dir = Path(storage_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.queue = queue.Queue()
        self.running = True

        # Ensure directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Start worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def save_templates_async(self, images_list):
        """Enqueue images to be saved asynchronously."""
        if not images_list:
            return

        timestamp = int(time.time() * 1000)
        for i, img in enumerate(images_list):
            if isinstance(img, np.ndarray):
                self.queue.put((img, f"template_{timestamp}_{i}.png"))

    def _worker_loop(self):
        while self.running:
            try:
                # Block until an item is available
                img, filename = self.queue.get(timeout=1.0)
            except queue.Empty:
                continue

            try:
                filepath = self.storage_dir / filename
                # Use cv2.imwrite (assuming BGR numpy array) or fallback if RGB
                # We'll save it using cv2
                cv2.imwrite(str(filepath), img)

                self._enforce_size_limit()
            except Exception as e:
                logger.error(f"[TemplateStorageManager] Failed to save {filename}: {e}")
            finally:
                self.queue.task_done()

    def _enforce_size_limit(self):
        try:
            files = [f for f in self.storage_dir.iterdir() if f.is_file()]
            total_size = sum(f.stat().st_size for f in files)

            if total_size <= self.max_size_bytes:
                return

            # Sort files by modification time (oldest first)
            files.sort(key=lambda x: x.stat().st_mtime)

            for f in files:
                size = f.stat().st_size
                try:
                    f.unlink()
                    total_size -= size
                    if total_size <= self.max_size_bytes:
                        break
                except Exception as e:
                    logger.error(f"[TemplateStorageManager] Failed to delete {f}: {e}")
        except Exception as e:
            logger.error(f"[TemplateStorageManager] Error enforcing size limit: {e}")

    def shutdown(self):
        self.running = False
        if hasattr(self, 'worker_thread'):
            self.worker_thread.join(timeout=2.0)
