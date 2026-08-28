"""
OpenCV vs PyAutoGUI Template Matching Comparison Test

This module tests and compares template matching performance between:
- opencv-python (cv2.matchTemplate)
- pyautogui (locateOnScreen)

Usage:
    python opencv_test.py
"""

import time
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Optional, Tuple, cast

import pytest

# Skip on non-Windows platforms because pyautogui/mouseinfo requires a GUI display
# and this module is intended to run with real screen access.
pytestmark = [pytest.mark.windows, pytest.mark.gui]

if sys.platform != "win32":
    pytest.skip("Requires Windows environment", allow_module_level=True)

cv2: Optional[ModuleType] = None
np: Optional[ModuleType] = None
pyautogui: Optional[ModuleType] = None

try:
    import cv2 as cv2_module
    import numpy as np_module
    cv2 = cv2_module
    np = np_module
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    print("⚠️  OpenCV not available. Install: pip install opencv-python")

try:
    import pyautogui as pyautogui_module
    pyautogui = pyautogui_module
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    print("⚠️  PyAutoGUI not available. Install: pip install pyautogui")


class TemplateMatchTester:
    """Test and compare template matching methods."""
    
    def __init__(self):
        self.results = {
            'opencv': {},
            'pyautogui': {}
        }
    
    def test_opencv_match(self, template_path: str, region: Optional[Tuple[int, int, int, int]] = None,
                          threshold: float = 0.8) -> Dict[str, Any]:
        """
        Test OpenCV template matching.
        
        Args:
            template_path: Path to template image
            region: (left, top, width, height) or None for full screen
            threshold: Confidence threshold (0.0-1.0)
        
        Returns:
            Dict with result info: found, box, confidence, time_ms
        """
        if not HAS_OPENCV or cv2 is None or np is None:
            return {'error': 'OpenCV not available'}

        if not HAS_PYAUTOGUI or pyautogui is None:
            return {'error': 'PyAutoGUI not available'}

        cv2_module = cast(ModuleType, cv2)
        np_module = cast(ModuleType, np)
        pyautogui_module = cast(ModuleType, pyautogui)
        
        start = time.perf_counter()
        
        try:
            # Load template
            template = cv2_module.imread(template_path)
            if template is None:
                return {'error': f'Failed to load template: {template_path}'}
            
            template_gray = cv2_module.cvtColor(template, cv2_module.COLOR_BGR2GRAY)
            th, tw = template_gray.shape[:2]
            
            # Capture screen
            screenshot = pyautogui_module.screenshot(region=region)
            screenshot_np = np_module.array(screenshot)
            screenshot_gray = cv2_module.cvtColor(screenshot_np, cv2_module.COLOR_RGB2GRAY)
            
            # Match template
            result = cv2_module.matchTemplate(screenshot_gray, template_gray, cv2_module.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2_module.minMaxLoc(result)
            
            elapsed_ms = (time.perf_counter() - start) * 1000
            
            if max_val >= threshold:
                # Found match
                left, top = max_loc
                if region:
                    left += region[0]
                    top += region[1]
                
                box = (left, top, tw, th)
                center = (left + tw // 2, top + th // 2)
                
                return {
                    'found': True,
                    'box': box,
                    'center': center,
                    'confidence': float(max_val),
                    'time_ms': round(elapsed_ms, 2),
                    'method': 'opencv'
                }
            else:
                return {
                    'found': False,
                    'max_confidence': float(max_val),
                    'time_ms': round(elapsed_ms, 2),
                    'method': 'opencv'
                }
                
        except Exception as e:
            return {'error': str(e), 'method': 'opencv'}
    
    def test_pyautogui_match(self, template_path: str, region: Optional[Tuple[int, int, int, int]] = None,
                             confidence: float = 0.8) -> Dict[str, Any]:
        """
        Test PyAutoGUI template matching.
        
        Args:
            template_path: Path to template image
            region: (left, top, width, height) or None for full screen
            confidence: Confidence threshold (0.0-1.0)
        
        Returns:
            Dict with result info: found, box, center, time_ms
        """
        if not HAS_PYAUTOGUI or pyautogui is None:
            return {'error': 'PyAutoGUI not available'}
        
        start = time.perf_counter()
        
        pyautogui_module = cast(ModuleType, pyautogui)

        try:
            # Try with confidence first (requires opencv)
            try:
                box = pyautogui_module.locateOnScreen(
                    template_path,
                    confidence=confidence,
                    region=region,
                    grayscale=True
                )
            except TypeError:
                # Fallback to basic matching without confidence
                box = pyautogui_module.locateOnScreen(
                    template_path,
                    region=region,
                    grayscale=True
                )
            
            elapsed_ms = (time.perf_counter() - start) * 1000
            
            if box:
                center = pyautogui_module.center(box)
                return {
                    'found': True,
                    'box': (box.left, box.top, box.width, box.height),
                    'center': (center.x, center.y),
                    'confidence': confidence,  # PyAutoGUI doesn't return actual confidence
                    'time_ms': round(elapsed_ms, 2),
                    'method': 'pyautogui'
                }
            else:
                return {
                    'found': False,
                    'time_ms': round(elapsed_ms, 2),
                    'method': 'pyautogui'
                }
                
        except Exception as e:
            return {'error': str(e), 'method': 'pyautogui'}
    
    def compare_methods(self, template_path: str, region: Optional[Tuple[int, int, int, int]] = None,
                        threshold: float = 0.8, iterations: int = 5) -> Dict[str, Any]:
        """
        Compare OpenCV and PyAutoGUI methods.
        
        Args:
            template_path: Path to template image
            region: Search region or None
            threshold: Confidence threshold
            iterations: Number of test iterations
        
        Returns:
            Comparison results with averages and recommendation
        """
        print(f"\n{'='*80}")
        print(f"Template Matching Comparison Test")
        print(f"{'='*80}")
        print(f"Template: {template_path}")
        print(f"Region: {region or 'Full screen'}")
        print(f"Threshold: {threshold}")
        print(f"Iterations: {iterations}")
        print(f"{'='*80}\n")
        
        opencv_times: list[float] = []
        opencv_found = 0
        opencv_confidences: list[float] = []
        opencv_avg = 0.0
        opencv_rate = 0.0
        
        pyautogui_times: list[float] = []
        pyautogui_found = 0
        pyautogui_avg = 0.0
        pyautogui_rate = 0.0
        
        # Test OpenCV
        if HAS_OPENCV:
            print("Testing OpenCV...")
            for i in range(iterations):
                result = self.test_opencv_match(template_path, region, threshold)
                if 'error' not in result:
                    opencv_times.append(result['time_ms'])
                    if result['found']:
                        opencv_found += 1
                        opencv_confidences.append(result['confidence'])
                    print(f"  Iteration {i+1}: {'✅ Found' if result['found'] else '❌ Not found'} "
                          f"({result.get('confidence', result.get('max_confidence', 0)):.3f}) "
                          f"in {result['time_ms']:.2f}ms")
                else:
                    print(f"  ❌ Error: {result['error']}")
                time.sleep(0.5)
        
        # Test PyAutoGUI
        if HAS_PYAUTOGUI:
            print("\nTesting PyAutoGUI...")
            for i in range(iterations):
                result = self.test_pyautogui_match(template_path, region, threshold)
                if 'error' not in result:
                    pyautogui_times.append(result['time_ms'])
                    if result['found']:
                        pyautogui_found += 1
                    print(f"  Iteration {i+1}: {'✅ Found' if result['found'] else '❌ Not found'} "
                          f"in {result['time_ms']:.2f}ms")
                else:
                    print(f"  ❌ Error: {result['error']}")
                time.sleep(0.5)
        
        # Calculate statistics
        print(f"\n{'='*80}")
        print("Results Summary:")
        print(f"{'='*80}")
        
        if opencv_times:
            opencv_avg = sum(opencv_times) / len(opencv_times)
            opencv_rate = (opencv_found / iterations) * 100
            print(f"\n📊 OpenCV (cv2.matchTemplate):")
            print(f"  • Detection rate: {opencv_found}/{iterations} ({opencv_rate:.1f}%)")
            print(f"  • Average time: {opencv_avg:.2f}ms")
            if opencv_confidences:
                opencv_conf_avg = sum(opencv_confidences) / len(opencv_confidences)
                print(f"  • Average confidence: {opencv_conf_avg:.3f}")
        
        if pyautogui_times:
            pyautogui_avg = sum(pyautogui_times) / len(pyautogui_times)
            pyautogui_rate = (pyautogui_found / iterations) * 100
            print(f"\n📊 PyAutoGUI (locateOnScreen):")
            print(f"  • Detection rate: {pyautogui_found}/{iterations} ({pyautogui_rate:.1f}%)")
            print(f"  • Average time: {pyautogui_avg:.2f}ms")
        
        # Recommendation
        print(f"\n{'='*80}")
        print("Recommendation:")
        print(f"{'='*80}")
        
        if opencv_times and pyautogui_times:
            if opencv_found > pyautogui_found:
                print("✅ OpenCV: Better detection rate")
            elif pyautogui_found > opencv_found:
                print("✅ PyAutoGUI: Better detection rate")
            else:
                print("⚖️  Equal detection rate")
            
            if opencv_avg < pyautogui_avg:
                speedup = (pyautogui_avg / opencv_avg)
                print(f"⚡ OpenCV: {speedup:.1f}x faster ({opencv_avg:.2f}ms vs {pyautogui_avg:.2f}ms)")
            else:
                speedup = (opencv_avg / pyautogui_avg)
                print(f"⚡ PyAutoGUI: {speedup:.1f}x faster ({pyautogui_avg:.2f}ms vs {opencv_avg:.2f}ms)")
            
            if opencv_confidences:
                print(f"📈 OpenCV provides actual confidence values (avg: {sum(opencv_confidences)/len(opencv_confidences):.3f})")
        
        print(f"\n💡 For production use:")
        if HAS_OPENCV and opencv_times and opencv_found >= pyautogui_found:
            print("   → Use OpenCV for better accuracy and confidence tracking")
        elif HAS_PYAUTOGUI:
            print("   → Use PyAutoGUI for simplicity (no OpenCV dependency)")
        
        print(f"\n{'='*80}\n")
        
        return {
            'opencv': {
                'available': HAS_OPENCV,
                'found': opencv_found,
                'rate': opencv_rate if opencv_times else 0,
                'avg_time_ms': opencv_avg if opencv_times else 0,
                'avg_confidence': sum(opencv_confidences) / len(opencv_confidences) if opencv_confidences else 0
            },
            'pyautogui': {
                'available': HAS_PYAUTOGUI,
                'found': pyautogui_found,
                'rate': pyautogui_rate if pyautogui_times else 0,
                'avg_time_ms': pyautogui_avg if pyautogui_times else 0
            }
        }


def main():
    """Run comparison tests."""
    print("\n" + "="*80)
    print("OpenCV vs PyAutoGUI Template Matching Test")
    print("="*80)
    print(f"OpenCV available: {HAS_OPENCV}")
    print(f"PyAutoGUI available: {HAS_PYAUTOGUI}")
    
    if not HAS_OPENCV and not HAS_PYAUTOGUI:
        print("\n❌ Neither OpenCV nor PyAutoGUI is available!")
        print("Install at least one: pip install opencv-python pyautogui")
        return
    
    # Test with a sample template
    template_path = "assets/images/monsters/target_frame.png"
    
    if not Path(template_path).exists():
        print(f"\n⚠️  Template not found: {template_path}")
        print("Please specify a valid template path.")
        
        # Try to find any template in monsters directory
        monsters_dir = Path("assets/images/monsters")
        if monsters_dir.exists():
            templates = list(monsters_dir.glob("*.png"))
            if templates:
                template_path = str(templates[0])
                print(f"Using found template: {template_path}")
            else:
                print("No templates found in monsters directory.")
                return
        else:
            return
    
    tester = TemplateMatchTester()
    
    # Run comparison
    results = tester.compare_methods(
        template_path=template_path,
        region=None,  # Full screen
        threshold=0.8,
        iterations=3
    )


if __name__ == '__main__':
    main()
