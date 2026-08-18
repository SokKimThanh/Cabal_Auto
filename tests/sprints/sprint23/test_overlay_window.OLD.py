"""
Tests for Overlay Window (Sprint 23 Phase 5 - PyWin32 Implementation)

Tests:
- Overlay window creation and configuration
- Show/hide functionality
- Detection box rendering
- Color state system
- Thread-safe updates
- FPS limiting
- Transparency and click-through (manual verification)
"""

import pytest
import time
import tkinter as tk
from typing import List
from unittest.mock import Mock, patch, MagicMock

from lib.ui.overlay_window_pywin32 import (
    OverlayWindowPyWin32 as OverlayWindow,
    DetectionBox,
    create_detection_box
)


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def root_window():
    """Create a tkinter root window for testing."""
    root = tk.Tk()
    root.withdraw()  # Hide during tests
    yield root
    try:
        root.destroy()
    except Exception:
        pass


@pytest.fixture
def sample_rect():
    """Sample window rectangle."""
    return {'left': 100, 'top': 100, 'width': 800, 'height': 600}


@pytest.fixture
def sample_detections():
    """Sample detection boxes for testing."""
    return [
        create_detection_box(100, 100, 80, 80, "Monster #1", "detected", 0.95),
        create_detection_box(300, 200, 60, 60, "Monster #2", "tracking", 0.88),
        create_detection_box(500, 150, 70, 70, "Searching", "searching", 0.0),
    ]


# =====================================================================
# Unit Tests
# =====================================================================

class TestDetectionBox:
    """Test DetectionBox data class."""
    
    def test_create_detection_box(self):
        """Test detection box creation."""
        box = DetectionBox(
            x=100, y=200, w=50, h=60,
            label="Test Monster",
            color=(0, 255, 0),
            confidence=0.85
        )
        
        assert box.x == 100
        assert box.y == 200
        assert box.w == 50
        assert box.h == 60
        assert box.label == "Test Monster"
        assert box.color == (0, 255, 0)
        assert box.confidence == 0.85
    
    def test_to_tkinter_color(self):
        """Test RGB to tkinter color conversion."""
        box = DetectionBox(
            x=0, y=0, w=10, h=10,
            label="Test",
            color=(255, 128, 64)
        )
        
        color_str = box.to_tkinter_color()
        assert color_str == "#ff8040"
    
    def test_create_detection_box_with_state(self):
        """Test helper function creates box with correct colors."""
        # Detected = green
        detected = create_detection_box(0, 0, 10, 10, "Test", "detected")
        assert detected.color == (0, 255, 0)
        
        # Tracking = blue
        tracking = create_detection_box(0, 0, 10, 10, "Test", "tracking")
        assert tracking.color == (0, 0, 255)
        
        # Searching = red
        searching = create_detection_box(0, 0, 10, 10, "Test", "searching")
        assert searching.color == (255, 0, 0)
    
    def test_create_detection_box_default_state(self):
        """Test default state is detected (green)."""
        box = create_detection_box(0, 0, 10, 10, "Test", "invalid_state")
        assert box.color == (0, 255, 0)  # Default green


class TestOverlayWindow:
    """Test OverlayWindow class."""
    
    def test_create_overlay_window(self, root_window, sample_rect):
        """Test overlay window creation."""
        overlay = OverlayWindow(
            target_rect=sample_rect,
            alpha=0.7,
            fps_limit=15
        )
        
        assert overlay.target_rect == sample_rect
        assert overlay.alpha == 0.7
        assert overlay.fps_limit == 15
        assert overlay.visible is False
        assert overlay.window is None
    
    def test_invalid_alpha_raises_error(self, sample_rect):
        """Test that invalid alpha values raise ValueError."""
        with pytest.raises(ValueError, match="Alpha must be 0.0-1.0"):
            OverlayWindow(target_rect=sample_rect, alpha=1.5)
        
        with pytest.raises(ValueError, match="Alpha must be 0.0-1.0"):
            OverlayWindow(target_rect=sample_rect, alpha=-0.1)
    
    def test_invalid_fps_raises_error(self, sample_rect):
        """Test that invalid FPS values raise ValueError."""
        with pytest.raises(ValueError, match="FPS limit must be > 0"):
            OverlayWindow(target_rect=sample_rect, fps_limit=0)
        
        with pytest.raises(ValueError, match="FPS limit must be > 0"):
            OverlayWindow(target_rect=sample_rect, fps_limit=-10)
    
    def test_create_window(self, root_window, sample_rect):
        """Test creating the tkinter window."""
        overlay = OverlayWindow(target_rect=sample_rect)
        overlay.create(parent=root_window)
        
        assert overlay.window is not None
        assert overlay.canvas is not None
        assert overlay.visible is False  # Created but not shown
    
    def test_show_without_create_raises_error(self, sample_rect):
        """Test that show() without create() raises RuntimeError."""
        overlay = OverlayWindow(target_rect=sample_rect)
        
        with pytest.raises(RuntimeError, match="Window not created"):
            overlay.show()
    
    def test_show_hide(self, root_window, sample_rect):
        """Test show and hide functionality."""
        overlay = OverlayWindow(target_rect=sample_rect)
        overlay.create(parent=root_window)
        
        # Show
        overlay.show()
        assert overlay.visible is True
        assert overlay.running is True
        
        # Hide
        overlay.hide()
        assert overlay.visible is False
    
    def test_toggle(self, root_window, sample_rect):
        """Test toggle functionality."""
        overlay = OverlayWindow(target_rect=sample_rect)
        overlay.create(parent=root_window)
        
        # Toggle on
        result = overlay.toggle()
        assert result is True
        assert overlay.visible is True
        
        # Toggle off
        result = overlay.toggle()
        assert result is False
        assert overlay.visible is False
    
    def test_update_target_rect(self, root_window, sample_rect):
        """Test updating target window rect."""
        overlay = OverlayWindow(target_rect=sample_rect)
        overlay.create(parent=root_window)
        
        new_rect = {'left': 200, 'top': 200, 'width': 1024, 'height': 768}
        overlay.update_target_rect(new_rect)
        
        assert overlay.target_rect == new_rect
        # Geometry should be updated (would need to check window geometry string)
    
    def test_update_detections_thread_safe(self, root_window, sample_rect, sample_detections):
        """Test thread-safe detection updates."""
        overlay = OverlayWindow(target_rect=sample_rect)
        overlay.create(parent=root_window)
        
        # Update detections (should not raise)
        overlay.update_detections(sample_detections)
        
        # Queue should have data
        assert not overlay._detections_queue.empty()
    
    def test_set_alpha(self, root_window, sample_rect):
        """Test changing alpha transparency."""
        overlay = OverlayWindow(target_rect=sample_rect, alpha=0.5)
        overlay.create(parent=root_window)
        
        # Change alpha
        overlay.set_alpha(0.8)
        assert overlay.alpha == 0.8
        
        # Invalid alpha
        with pytest.raises(ValueError):
            overlay.set_alpha(1.5)
    
    def test_destroy(self, root_window, sample_rect):
        """Test cleanup on destroy."""
        overlay = OverlayWindow(target_rect=sample_rect)
        overlay.create(parent=root_window)
        overlay.show()
        
        # Destroy
        overlay.destroy()
        
        assert overlay.window is None
        assert overlay.canvas is None
        assert overlay.visible is False
        assert overlay.running is False
    
    def test_fps_limiting(self, root_window, sample_rect):
        """Test FPS limiting mechanism."""
        fps_limit = 30
        overlay = OverlayWindow(target_rect=sample_rect, fps_limit=fps_limit)
        
        expected_interval = 1.0 / fps_limit
        assert overlay._frame_interval == pytest.approx(expected_interval, rel=0.01)


# =====================================================================
# Integration Tests
# =====================================================================

class TestOverlayIntegration:
    """Integration tests for overlay with other systems."""
    
    @pytest.mark.slow
    def test_overlay_rendering_performance(self, root_window, sample_rect, sample_detections):
        """Test overlay rendering performance (15+ FPS)."""
        overlay = OverlayWindow(target_rect=sample_rect, fps_limit=15)
        overlay.create(parent=root_window)
        overlay.show()
        
        # Update detections multiple times
        start_time = time.time()
        frame_count = 30
        
        for _ in range(frame_count):
            overlay.update_detections(sample_detections)
            root_window.update()  # Process events
            time.sleep(0.01)  # Small delay
        
        elapsed = time.time() - start_time
        fps = frame_count / elapsed
        
        # Should achieve at least 10 FPS (allow some overhead)
        assert fps >= 10.0, f"FPS too low: {fps:.2f}"
        
        overlay.destroy()
    
    @pytest.mark.manual
    def test_click_through_manual(self, root_window, sample_rect, sample_detections):
        """Manual test for click-through functionality.
        
        Run this test manually and verify that:
        1. Overlay is visible with detection boxes
        2. You can click through the overlay to windows below
        3. Overlay stays on top (topmost)
        """
        overlay = OverlayWindow(
            target_rect=sample_rect,
            alpha=0.7,
            fps_limit=15,
            enable_click_through=True
        )
        overlay.create(parent=root_window)
        overlay.show()
        overlay.update_detections(sample_detections)
        
        print("\n" + "="*60)
        print("MANUAL TEST: Click-through overlay")
        print("="*60)
        print("1. You should see a transparent overlay window")
        print("2. Try clicking on the overlay - clicks should pass through")
        print("3. Overlay should stay on top of other windows")
        print("4. Press any key in console to close...")
        print("="*60)
        
        input()  # Wait for user confirmation
        overlay.destroy()
    
    @pytest.mark.manual
    def test_transparency_levels_manual(self, root_window, sample_rect, sample_detections):
        """Manual test for different transparency levels.
        
        Verify that alpha transparency works correctly.
        """
        for alpha in [0.3, 0.5, 0.7, 0.9]:
            overlay = OverlayWindow(
                target_rect=sample_rect,
                alpha=alpha,
                fps_limit=15
            )
            overlay.create(parent=root_window)
            overlay.show()
            overlay.update_detections(sample_detections)
            
            print(f"\nShowing overlay with alpha={alpha}")
            print("Press Enter to continue to next alpha...")
            input()
            
            overlay.destroy()


# =====================================================================
# Edge Case Tests
# =====================================================================

class TestOverlayEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_detections(self, root_window, sample_rect):
        """Test rendering with no detections."""
        overlay = OverlayWindow(target_rect=sample_rect)
        overlay.create(parent=root_window)
        overlay.show()
        
        # Update with empty list
        overlay.update_detections([])
        root_window.update()
        
        # Should not crash
        overlay.destroy()
    
    def test_many_detections(self, root_window, sample_rect):
        """Test rendering with many detection boxes."""
        overlay = OverlayWindow(target_rect=sample_rect)
        overlay.create(parent=root_window)
        overlay.show()
        
        # Create 50 detection boxes
        many_detections = [
            create_detection_box(
                x=i*20, y=i*20, w=50, h=50,
                label=f"Det {i}",
                state="detected",
                confidence=0.8
            )
            for i in range(50)
        ]
        
        overlay.update_detections(many_detections)
        root_window.update()
        
        # Should not crash
        overlay.destroy()
    
    def test_rapid_toggle(self, root_window, sample_rect):
        """Test rapid show/hide toggling."""
        overlay = OverlayWindow(target_rect=sample_rect)
        overlay.create(parent=root_window)
        
        # Toggle 10 times rapidly
        for _ in range(10):
            overlay.toggle()
            root_window.update()
        
        overlay.destroy()
    
    def test_update_detections_queue_overflow(self, root_window, sample_rect, sample_detections):
        """Test that queue overflow is handled gracefully."""
        overlay = OverlayWindow(target_rect=sample_rect)
        overlay.create(parent=root_window)
        
        # Fill queue beyond maxsize (should drop old frames)
        for _ in range(10):
            overlay.update_detections(sample_detections)
        
        # Should not crash or block
        overlay.destroy()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
