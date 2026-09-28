import queue
import tkinter as tk
import logging

logger = logging.getLogger(__name__)

class UIDispatcher:
    """
    Thread-safe UI dispatcher.
    Allows worker threads to post callbacks that will be safely executed on the main UI thread.
    """
    _instance = None

    def __init__(self, root: tk.Tk):
        self.root = root
        self.queue = queue.Queue()
        self._is_shutting_down = False
        self._process_queue()
        UIDispatcher._instance = self

    @classmethod
    def get_instance(cls):
        return cls._instance

    @classmethod
    def post(cls, task):
        if cls._instance and not cls._instance._is_shutting_down:
            cls._instance.queue.put(task)
        else:
            logger.warning("[UIDispatcher] Dispatcher not initialized or shutting down, task dropped.")

    def _process_queue(self):
        if self._is_shutting_down:
            return

        try:
            while not self.queue.empty():
                task = self.queue.get_nowait()
                try:
                    task()
                except Exception as e:
                    logger.error(f"[UIDispatcher] Error executing task: {e}")
                finally:
                    self.queue.task_done()
        except queue.Empty:
            pass
        finally:
            if not self._is_shutting_down:
                self.root.after(100, self._process_queue)

    def shutdown(self):
        self._is_shutting_down = True
