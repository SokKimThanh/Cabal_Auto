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

from lib.ui.overlay_window_pywin32 import OverlayWindowPyWin32, DetectionBox
from lib.ui.detection_converter import detections_to_boxes, get_state_color
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
        max_boxes: int = 20
    ):
        """
        Initialize overlay controller
        
        Args:
            overlay: OverlayWindowPyWin32 instance for rendering
            detector: MonsterDetector instance for detection events
            max_boxes: Maximum number of boxes to display
        """
        self._overlay = overlay
        self._detector = detector
        self._max_boxes = max_boxes
        
        # State
        self._running = False
        self._current_state = DetectionState.SEARCHING
        
        # Statistics
        self._stats = OverlayStats()
        
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
            update_latency_ms=self._stats.update_latency_ms
        )
    
    def get_current_state(self) -> DetectionState:
        """Get current detection state"""
        return self._current_state
    
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
            boxes = detections_to_boxes(
                detections,
                state=self._current_state.value,
                max_boxes=self._max_boxes
            )
            
            # Update overlay
            self._overlay.update_detections(boxes)
            
            # Update statistics
            self._stats.updates_sent += 1
            self._stats.last_update_time = time.time()
            self._stats.update_latency_ms = (time.time() - update_start) * 1000
            
            # Log updates periodically (every 30 updates)
            if self._stats.updates_sent % 30 == 0:
                logger.debug(
                    f"[OverlayController] Updated overlay: "
                    f"{len(boxes)} boxes, latency: {self._stats.update_latency_ms:.1f}ms"
                )
            
        except Exception as e:
            logger.error(f"[OverlayController] Detection update error: {e}", exc_info=True)
    
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
