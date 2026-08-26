from typing import Any, Optional
import logging

from ui.utils.window_tracker import WindowTracker

logger = logging.getLogger(__name__)


class WindowTrackerController:
    """Controller for tracking game window bounds and overlay alignment."""

    def __init__(self, parent: Any):
        self.parent = parent
        self.tracker: Optional[WindowTracker] = None
        self._target_hwnd: Optional[int] = None

    def start(self, target_hwnd: Optional[int]) -> None:
        """
        Start the window tracker for the given HWND.
        If ``target_hwnd`` is ``None`` or otherwise invalid/falsy, no tracker is started.
        If already tracking the same HWND, prevents duplicate start.
        """
        if not target_hwnd:
            logger.warning(
                "[WindowTrackerController] Cannot start without a valid target_hwnd"
            )
            return

        if (
            self.tracker
            and self._target_hwnd == target_hwnd
            and self.tracker.is_running()
        ):
            logger.info(
                f"[WindowTrackerController] Tracker already running for HWND: {target_hwnd}"
            )
            return

        # Stop existing if tracking different window or if not running
        self.stop()

        logger.info(
            f"[WindowTrackerController] Starting tracker for HWND: {target_hwnd}"
        )
        self._target_hwnd = target_hwnd
        self.tracker = WindowTracker(target_hwnd=target_hwnd, poll_rate=60)
        self.tracker.start()

    def stop(self) -> None:
        """Stop the current window tracker."""
        if self.tracker:
            logger.info(
                f"[WindowTrackerController] Stopping tracker for HWND: {self._target_hwnd}"
            )
            self.tracker.stop()
            self.tracker = None
            self._target_hwnd = None

    def get_tracker(self) -> Optional[WindowTracker]:
        """Return the current tracker instance."""
        return self.tracker
