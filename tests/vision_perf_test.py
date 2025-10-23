"""
Performance tests for Vision Engine worker thread architecture
Sprint 22 Phase 2

Tests:
- Frame latency (time from capture to result)
- Processing time per frame
- Queue throughput
- UI responsiveness (worker doesn't block main thread)
- Resource cleanup
"""

import pytest
import time
import numpy as np
import threading
from typing import Optional

# Mark as vision and slow test
pytestmark = [pytest.mark.vision, pytest.mark.slow]

# Add parent to path for imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.vision.vision_engine import get_vision_engine, VisionEngine


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def engine():
    """Get fresh engine instance for each test"""
    from lib.vision import vision_engine
    # Reset singleton
    vision_engine._engine_instance = None
    
    engine = get_vision_engine()
    yield engine
    
    # Cleanup
    engine.stop_worker()
    vision_engine._engine_instance = None


@pytest.fixture
def test_frame():
    """Create synthetic test frame (640x480 RGB)"""
    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)


# =====================================================================
# Performance Tests
# =====================================================================

def test_worker_startup_shutdown_latency(engine):
    """Test worker thread startup and shutdown time"""
    
    def dummy_callback():
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Measure startup
    start = time.time()
    engine.start_worker(dummy_callback)
    startup_time = time.time() - start
    
    # Wait for worker to run at least once
    time.sleep(0.2)
    
    # Measure shutdown
    start = time.time()
    engine.stop_worker()
    shutdown_time = time.time() - start
    
    print(f"\nWorker startup: {startup_time*1000:.2f}ms")
    print(f"Worker shutdown: {shutdown_time*1000:.2f}ms")
    
    # Assertions
    assert startup_time < 0.1, "Worker startup should be < 100ms"
    assert shutdown_time < 2.5, "Worker shutdown should be < 2.5s (timeout=2.0s)"


def test_frame_processing_latency(engine, test_frame):
    """Test latency from frame callback to result availability"""
    
    frame_count = 0
    timestamps = []
    
    def frame_callback():
        nonlocal frame_count
        frame_count += 1
        timestamps.append(('capture', time.time()))
        return test_frame.copy()
    
    # Start worker
    engine.start_worker(frame_callback)
    
    # Wait for some frames to process
    time.sleep(0.5)
    
    # Get result and measure latency
    result = engine.get_result(timeout=1.0)
    
    if result:
        result_time = result['timestamp']
        timestamps.append(('result', result_time))
        
        # Calculate latency (time from last capture to result)
        if len(timestamps) >= 2:
            capture_times = [t for label, t in timestamps if label == 'capture']
            if capture_times:
                latest_capture = max(capture_times)
                latency = result_time - latest_capture
                
                print(f"\nFrames processed: {frame_count}")
                print(f"Result latency: {latency*1000:.2f}ms")
                
                # Latency should be reasonable (< 200ms for synthetic frames)
                assert latency < 0.2, f"Latency too high: {latency*1000:.2f}ms"
    
    # Cleanup
    engine.stop_worker()


def test_queue_throughput_fps_limit(engine, test_frame):
    """Test that FPS limit is respected and queue doesn't overflow"""
    
    fps_limit = engine.params.get('fps_limit', 15)
    expected_interval = 1.0 / fps_limit
    
    def frame_callback():
        return test_frame.copy()
    
    # Start worker
    engine.start_worker(frame_callback)
    
    # Collect results for 1 second
    results = []
    start = time.time()
    while time.time() - start < 1.0:
        result = engine.get_result(timeout=0.01)
        if result:
            results.append(result['timestamp'])
        time.sleep(0.01)  # Small sleep to avoid tight loop
    
    # Calculate actual FPS
    if len(results) >= 2:
        intervals = [results[i+1] - results[i] for i in range(len(results)-1)]
        avg_interval = sum(intervals) / len(intervals)
        actual_fps = 1.0 / avg_interval
        
        print(f"\nFPS limit: {fps_limit}")
        print(f"Actual FPS: {actual_fps:.2f}")
        print(f"Results collected: {len(results)}")
        print(f"Average interval: {avg_interval*1000:.2f}ms (expected ~{expected_interval*1000:.2f}ms)")
        
        # FPS should be close to limit (within 20% tolerance)
        assert abs(actual_fps - fps_limit) / fps_limit < 0.2, \
            f"FPS {actual_fps:.2f} too far from limit {fps_limit}"
    
    # Cleanup
    engine.stop_worker()


def test_worker_non_blocking(engine, test_frame):
    """Test that worker doesn't block main thread"""
    
    def frame_callback():
        # Simulate slow processing (50ms)
        time.sleep(0.05)
        return test_frame.copy()
    
    # Start worker
    engine.start_worker(frame_callback)
    
    # Main thread should not block while worker processes
    main_thread_blocked = False
    start = time.time()
    
    # Try to do work on main thread
    for _ in range(10):
        # This should execute quickly even if worker is slow
        result = engine.get_result(timeout=0.0)  # Non-blocking
        time.sleep(0.01)
    
    elapsed = time.time() - start
    
    print(f"\nMain thread loop time: {elapsed*1000:.2f}ms")
    
    # Main thread loop should complete quickly (< 200ms)
    assert elapsed < 0.2, "Main thread appears to be blocked"
    
    # Cleanup
    engine.stop_worker()


def test_queue_overflow_handling(engine, test_frame):
    """Test that queue doesn't overflow when results accumulate"""
    
    # Set very high FPS limit to force overflow
    original_fps = engine.params['fps_limit']
    engine.params['fps_limit'] = 100  # Try to produce 100 FPS
    
    def frame_callback():
        return test_frame.copy()
    
    # Start worker
    engine.start_worker(frame_callback)
    
    # Don't consume results for a while to let queue fill
    time.sleep(0.5)
    
    # Queue should not grow unbounded (maxsize=5)
    queue_size = engine.result_queue.qsize()
    print(f"\nQueue size after 0.5s: {queue_size}")
    
    # Queue should be near max size but not crash
    assert queue_size <= 6, "Queue overflow not handled properly"
    
    # Cleanup
    engine.params['fps_limit'] = original_fps
    engine.stop_worker()


def test_resource_cleanup_on_stop(engine, test_frame):
    """Test that resources are properly cleaned up on worker stop"""
    
    def frame_callback():
        return test_frame.copy()
    
    # Start worker
    engine.start_worker(frame_callback)
    time.sleep(0.2)
    
    # Stop worker
    engine.stop_worker()
    
    # Verify cleanup
    assert not engine.worker_running, "Worker should not be running"
    assert engine.result_queue.empty(), "Queue should be drained"
    assert len(engine.trackers) == 0, "Trackers should be stopped"
    
    # Thread should be dead
    if engine.worker_thread:
        assert not engine.worker_thread.is_alive(), "Thread should be dead"
    
    print("\nResource cleanup verified")


def test_multiple_start_stop_cycles(engine, test_frame):
    """Test that worker can be started/stopped multiple times"""
    
    def frame_callback():
        return test_frame.copy()
    
    for cycle in range(3):
        print(f"\nCycle {cycle + 1}")
        
        # Start
        engine.start_worker(frame_callback)
        time.sleep(0.1)
        
        # Get at least one result
        result = engine.get_result(timeout=0.5)
        assert result is not None, f"No result in cycle {cycle + 1}"
        
        # Stop
        engine.stop_worker()
        time.sleep(0.1)
        
        # Verify stopped
        assert not engine.worker_running, f"Worker not stopped in cycle {cycle + 1}"


# =====================================================================
# Run tests
# =====================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
