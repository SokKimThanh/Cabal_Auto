import threading
from typing import Callable, Dict, Any, Optional
import logging
import uuid

logger = logging.getLogger(__name__)

class TaskScheduler:
    """
    Centralized task and timer manager for the application.
    Replaces raw `root.after` and unmanaged `Thread` calls to prevent zombie loops,
    memory leaks, and Tkinter exceptions on teardown.
    """

    def __init__(self, root: Any):
        """
        Initialize the TaskScheduler.

        Args:
            root: The Tkinter root or app instance used for calling `.after`.
        """
        self.root = root
        self._after_tasks: Dict[str, str] = {}
        self._threads: Dict[str, threading.Thread] = {}
        self._is_shutting_down = False

    def schedule_task(self, task_id: Optional[str], interval_ms: int, callback: Callable, recurring: bool = False) -> str:
        """
        Schedule a UI task using Tkinter's `after`.

        Args:
            task_id: Unique identifier for the task. If None, a UUID is generated.
            interval_ms: Interval in milliseconds.
            callback: The function to execute.
            recurring: If True, the task will automatically reschedule itself.

        Returns:
            The resolved task_id string.
        """
        if self._is_shutting_down:
            return ""

        if task_id is None:
            task_id = uuid.uuid4().hex

        # Ensure we cancel any existing task with the same ID first
        self.cancel_task(task_id)

        def _wrapper():
            if self._is_shutting_down:
                return

            try:
                callback()
            except Exception as e:
                logger.error(f"[TaskScheduler] Error executing task '{task_id}': {e}")

            # Reschedule itself if still running and recurring is True
            if not self._is_shutting_down and recurring:
                try:
                    new_timer_id = self.root.root.after if hasattr(self.root, 'root') else self.root.after(interval_ms, _wrapper)
                    self._after_tasks[task_id] = new_timer_id
                except Exception as e:
                    logger.error(f"[TaskScheduler] Failed to reschedule task '{task_id}': {e}")
            elif not recurring:
                # Cleanup reference if it's a one-off task
                self._after_tasks.pop(task_id, None)

        try:
            timer_id = self.root.root.after if hasattr(self.root, 'root') else self.root.after(interval_ms, _wrapper)
            self._after_tasks[task_id] = timer_id
        except Exception as e:
            logger.error(f"[TaskScheduler] Failed to schedule task '{task_id}': {e}")

        return task_id

    def schedule_recurring_task(self, task_id: str, interval_ms: int, callback: Callable) -> str:
        """
        Helper method to schedule a recurring task.
        """
        return self.schedule_task(task_id, interval_ms, callback, recurring=True)

    def cancel_task(self, task_id: str) -> None:
        """
        Cancel a specific tracked `after` task.
        """
        if not task_id:
            return
        timer_id = self._after_tasks.pop(task_id, None)
        if timer_id:
            try:
                self.root.root.after if hasattr(self.root, 'root') else self.root.after_cancel(timer_id)
            except Exception:
                # Swallow TclError or similar if the timer is already invalid
                pass

    def cancel_all(self) -> None:
        """
        Cancel all registered tasks and signal teardown.
        Must be called during application closing sequence.
        """
        self._is_shutting_down = True

        for task_id, timer_id in list(self._after_tasks.items()):
            try:
                self.root.root.after if hasattr(self.root, 'root') else self.root.after_cancel(timer_id)
            except Exception:
                pass

        self._after_tasks.clear()
        logger.info("[TaskScheduler] All timers cancelled.")

    def run_in_thread(self, task_id: str, target: Callable, daemon: bool = True, **kwargs) -> threading.Thread:
        """
        Start a function in a background thread, optionally tracking it.

        Args:
            task_id: Unique identifier for the thread.
            target: The callable target to run.
            daemon: Whether the thread should be marked as daemon. Defaults to True.

        Returns:
            The created and started Thread object.
        """
        def _thread_wrapper():
            try:
                target(**kwargs)
            except Exception as e:
                logger.error(f"[TaskScheduler] Thread '{task_id}' crashed: {e}")
            finally:
                # Clean up tracking when thread ends naturally
                self._threads.pop(task_id, None)

        thread = threading.Thread(target=_thread_wrapper, daemon=daemon)
        self._threads[task_id] = thread

        if not self._is_shutting_down:
            thread.start()

        return thread
