"""
Overlay Controller - Bridge MonsterDetector and PyWin32Overlay
Sprint 23 Phase 7 Batch 2

Provides:
- Auto-connect MonsterDetector callbacks to Overlay updates
- Detection → DetectionBox conversion
- State-based color mapping
- Performance metrics display
- Window state handling

Architecture:
- Controller pattern: Mediates between detector and overlay
- Event-driven: Responds to detection callbacks
- Thread-safe: Handles cross-thread updates
- Decoupled: Detector and Overlay remain independent

Usage:
    controller = OverlayController(overlay, detector)
    controller.start()
    # ... detector runs, overlay updates automatically ...
    controller.stop()
"""

import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

from ui.windows.overlay_window import OverlayWindowPyWin32, DetectionBox
from ui.utils.detection_converter import detections_to_boxes, get_state_color
from ui.utils.window_tracker import WindowTracker, WindowState
from lib.vision.monster_detector import MonsterDetector, DetectionState, DetectionStats

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# =====================================================================
# Data Classes
# =====================================================================


@dataclass
class OverlayStats:
    """Statistics for overlay controller performance"""

    updates_sent: int = 0
    last_update_time: float = 0.0
    update_latency_ms: float = 0.0

    # Detection metrics
    current_monster_count: int = 0
    total_detections: int = 0

    # FPS tracking
    fps: float = 0.0
    last_fps_update: float = 0.0


# =====================================================================
# Overlay Controller
# =====================================================================


class OverlayController:
    """
    Bridge between MonsterDetector and PyWin32Overlay

    Features:
    - Auto-converts Detection objects to DetectionBox format
    - State-based color mapping for visual feedback
    - Performance metrics tracking
    - Event-driven updates (no polling)

    Responsibilities:
    - Listen to detector detection events
    - Convert detections to overlay format
    - Update overlay with new boxes
    - Track update performance

    Usage:
        controller = OverlayController(overlay, detector)
        controller.start()  # Connects callbacks
        # Detector runs, overlay updates automatically
        controller.stop()   # Disconnects callbacks
    """

    def __init__(
        self,
        overlay: OverlayWindowPyWin32,
        detector: MonsterDetector,
        max_boxes: int = 20,
        show_stats: bool = True,
        stats_update_interval: float = 0.5,
        window_tracker: Optional[WindowTracker] = None,
    ):
        """
        Initialize OverlayController

        Args:
            overlay: OverlayWindowPyWin32 instance for rendering
            detector: MonsterDetector instance for detection events
            max_boxes: Maximum detection boxes to display
            show_stats: Whether to display FPS and stats overlay
            stats_update_interval: How often to update stats display (seconds)
            window_tracker: Optional WindowTracker for window state handling
        """
        self._overlay = overlay
        self._detector = detector
        self._max_boxes = max_boxes
        self._show_stats = show_stats
        self._stats_update_interval = stats_update_interval
        self._window_tracker = window_tracker

        # State tracking
        self._running = False
        self._current_state = DetectionState.SEARCHING
        self._window_minimized = False

        # Statistics
        self._stats = OverlayStats()
        self._fps_frame_count = 0
        self._fps_timer_start = time.time()

        logger.info("[OverlayController] Initialized")

    # =================================================================
    # Public API - Control
    # =================================================================

    def start(self) -> bool:
        """
        Start controller (connect callbacks to detector)

        Returns:
            True if started successfully, False if already running
        """
        if self._running:
            logger.warning("[OverlayController] Already running")
            return False

        # Register callbacks with detector
        self._detector.on_detections_changed(self._on_detections_changed)
        self._detector.on_state_changed(self._on_state_changed)

        # Register window tracker callback if available
        if self._window_tracker:
            # Note: WindowTracker uses on_state_change attribute, not method
            self._window_tracker.on_state_change = self._on_window_state_changed

        self._running = True
        logger.info("[OverlayController] Started - listening to detector events")
        return True

    def stop(self) -> bool:
        """
        Stop controller (disconnect callbacks from detector)

        Returns:
            True if stopped successfully, False if not running
        """
        if not self._running:
            logger.warning("[OverlayController] Not running")
            return False

        # Unregister callbacks
        self._detector.remove_detection_callback(self._on_detections_changed)
        self._detector.remove_state_callback(self._on_state_changed)

        # Unregister window tracker callback
        if self._window_tracker:
            self._window_tracker.on_state_change = None

        self._running = False
        logger.info("[OverlayController] Stopped")
        return True

    def is_running(self) -> bool:
        """Check if controller is running"""
        return self._running

    # =================================================================
    # Public API - Data Access
    # =================================================================

    def get_stats(self) -> OverlayStats:
        """
        Get controller statistics

        Returns:
            OverlayStats with current metrics
        """
        return OverlayStats(
            updates_sent=self._stats.updates_sent,
            last_update_time=self._stats.last_update_time,
            update_latency_ms=self._stats.update_latency_ms,
            current_monster_count=self._stats.current_monster_count,
            total_detections=self._stats.total_detections,
            fps=self._stats.fps,
            last_fps_update=self._stats.last_fps_update,
        )

    def get_current_state(self) -> DetectionState:
        """Get current detection state"""
        return self._current_state

    # =================================================================
    # Private - Stats Display
    # =================================================================

    def _create_stats_boxes(self) -> List[DetectionBox]:
        """
        Create overlay boxes for stats display

        Returns:
            List of DetectionBox objects for stats overlay
        """
        if not self._show_stats:
            return []

        stats_boxes = []

        # Stats positioned at top-left corner
        x_offset = 10
        y_offset = 10
        line_height = 20

        # FPS display
        fps_text = f"FPS: {self._stats.fps:.1f}"
        stats_boxes.append(
            DetectionBox(
                x=x_offset,
                y=y_offset,
                w=100,
                h=line_height,
                label=fps_text,
                color=(0, 255, 0),  # Green
                confidence=1.0,
            )
        )

        # Monster count
        count_text = f"Monsters: {self._stats.current_monster_count}"
        stats_boxes.append(
            DetectionBox(
                x=x_offset,
                y=y_offset + line_height,
                w=120,
                h=line_height,
                label=count_text,
                color=(0, 255, 255),  # Cyan
                confidence=1.0,
            )
        )

        # Current state
        state_text = f"State: {self._current_state.value}"
        state_color_rgb = get_state_color(self._current_state.value)
        stats_boxes.append(
            DetectionBox(
                x=x_offset,
                y=y_offset + line_height * 2,
                w=150,
                h=line_height,
                label=state_text,
                color=state_color_rgb,
                confidence=1.0,
            )
        )

        # Latency
        latency_text = f"Latency: {self._stats.update_latency_ms:.1f}ms"
        stats_boxes.append(
            DetectionBox(
                x=x_offset,
                y=y_offset + line_height * 3,
                w=140,
                h=line_height,
                label=latency_text,
                color=(255, 255, 0),  # Yellow
                confidence=1.0,
            )
        )

        return stats_boxes

    def _update_fps(self) -> None:
        """Update FPS calculation"""
        self._fps_frame_count += 1
        now = time.time()
        elapsed = now - self._fps_timer_start

        # Update FPS every stats_update_interval
        if elapsed >= self._stats_update_interval:
            self._stats.fps = self._fps_frame_count / elapsed
            self._stats.last_fps_update = now

            # Reset counters
            self._fps_frame_count = 0
            self._fps_timer_start = now

    # =================================================================
    # Private - Callback Handlers
    # =================================================================

    def _on_detections_changed(self, detections: List) -> None:
        """
        Handle detection updates from MonsterDetector

        Called by detector thread when new detections available.
        Converts detections to boxes and updates overlay.

        Args:
            detections: List of Detection objects from VisionEngine
        """
        try:
            update_start = time.time()

            # Convert detections to overlay boxes
            detection_boxes = detections_to_boxes(
                detections, state=self._current_state.value, max_boxes=self._max_boxes
            )

            # Update statistics
            self._stats.current_monster_count = len(detection_boxes)
            self._stats.total_detections += len(detections)

            # Update FPS
            self._update_fps()

            # Combine detection boxes with stats display
            all_boxes = detection_boxes + self._create_stats_boxes()

            # Update overlay
            self._overlay.update_detections(all_boxes)

            # Update statistics
            self._stats.updates_sent += 1
            self._stats.last_update_time = time.time()
            self._stats.update_latency_ms = (time.time() - update_start) * 1000

            # Log updates periodically (every 30 updates)
            if self._stats.updates_sent % 30 == 0:
                logger.debug(
                    f"[OverlayController] Updated overlay: "
                    f"{len(detection_boxes)} detections + stats, "
                    f"FPS: {self._stats.fps:.1f}, "
                    f"latency: {self._stats.update_latency_ms:.1f}ms"
                )

        except Exception as e:
            logger.error(
                f"[OverlayController] Detection update error: {e}", exc_info=True
            )

    def _on_state_changed(self, new_state: DetectionState) -> None:
        """
        Handle state changes from MonsterDetector

        Updates internal state for color mapping.
        Next detection update will use new state colors.

        Args:
            new_state: New DetectionState from detector
        """
        try:
            old_state = self._current_state
            self._current_state = new_state

            logger.info(
                f"[OverlayController] State changed: {old_state.value} -> {new_state.value}"
            )

            # If entering SEARCHING state with no detections, clear overlay
            if new_state == DetectionState.SEARCHING:
                self._overlay.update_detections([])
                logger.debug("[OverlayController] Cleared overlay (SEARCHING state)")

        except Exception as e:
            logger.error(f"[OverlayController] State change error: {e}", exc_info=True)

    def _on_window_state_changed(self, window_state: WindowState) -> None:
        """
        Handle window state changes from WindowTracker

        Pause/resume detection and hide/show overlay based on window state.

        Args:
            window_state: New WindowState from tracker
        """
        try:
            logger.info(
                f"[OverlayController] Window state changed: {window_state.value}"
            )

            # Handle minimize/restore
            if window_state == WindowState.MINIMIZED:
                if not self._window_minimized:
                    self._window_minimized = True

                    # Pause detection
                    if hasattr(self._detector, "pause"):
                        self._detector.pause()
                        logger.info(
                            "[OverlayController] Paused detection (window minimized)"
                        )

                    # Hide overlay
                    if hasattr(self._overlay, "hide"):
                        self._overlay.hide()
                        logger.debug(
                            "[OverlayController] Hid overlay (window minimized)"
                        )

            elif window_state in [WindowState.NORMAL, WindowState.MAXIMIZED]:
                if self._window_minimized:
                    self._window_minimized = False

                    # Resume detection
                    if hasattr(self._detector, "resume"):
                        self._detector.resume()
                        logger.info(
                            "[OverlayController] Resumed detection (window restored)"
                        )

                    # Show overlay (if controller is running)
                    if self._running and hasattr(self._overlay, "show"):
                        self._overlay.show()
                        logger.debug(
                            "[OverlayController] Showed overlay (window restored)"
                        )

        except Exception as e:
            logger.error(
                f"[OverlayController] Window state change error: {e}", exc_info=True
            )

    # =================================================================
    # Cleanup
    # =================================================================

    def __del__(self):
        """Cleanup on deletion"""
        if self._running:
            self.stop()


# =====================================================================
# Module Test
# =====================================================================

if __name__ == "__main__":
    print("OverlayController module loaded")
    print(f"OverlayStats fields: {OverlayStats.__dataclass_fields__.keys()}")
