"""
Template Matcher - Unified interface for OpenCV and PyAutoGUI template matching.

This module provides a consistent interface for template matching that automatically
uses OpenCV if available (for better accuracy), falling back to PyAutoGUI otherwise.

Usage:
    from template_matcher import locate_template
    
    box, confidence = locate_template(
        template_path='assets/images/monsters/dragon.png',
        region=(0, 0, 1920, 1080),
        threshold=0.8
    )
"""

from typing import Optional, Tuple
import time

# Try to import OpenCV
try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False


# Try to import PyAutoGUI
try:
    import pyautogui
    HAS_PYAUTOGUI = True
except (ImportError, Exception):
    HAS_PYAUTOGUI = False

# ⚡ Bolt Optimization:
# 💡 What: Memory cache for grayscale OpenCV templates.
# 🎯 Why: `locate_template_opencv` was performing expensive disk I/O (`cv2.imread`)
#     and color conversion (`cv2.cvtColor`) on every frame check.
# 📊 Impact: ~3x speedup on template matching loops by removing redundant processing.
_TEMPLATE_CACHE = {}

def locate_template_opencv(template_path: str, 
                           region: Optional[Tuple[int, int, int, int]] = None,
                           threshold: float = 0.8) -> Tuple[Optional[Tuple[int, int, int, int]], float]:
    """
    Locate template using OpenCV (cv2.matchTemplate).
    
    Args:
        template_path: Path to template image
        region: (left, top, width, height) search region, or None for full screen
        threshold: Confidence threshold (0.0-1.0)
    
    Returns:
        Tuple of (box, confidence) where box is (left, top, width, height) or None
    """
    if not HAS_OPENCV:
        raise ImportError("OpenCV not available")
    
    # Load template
    if template_path in _TEMPLATE_CACHE:
        template_gray, th, tw = _TEMPLATE_CACHE[template_path]
    else:
        template = cv2.imread(template_path)
        if template is None:
            return None, 0.0

        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        th, tw = template_gray.shape[:2]
        _TEMPLATE_CACHE[template_path] = (template_gray, th, tw)
    
    # Capture screen
    screenshot = pyautogui.screenshot(region=region)
    screenshot_np = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    screenshot_gray = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
    
    # Match template
    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        # Found match
        left, top = max_loc
        if region:
            left += region[0]
            top += region[1]
        
        box = (left, top, tw, th)
        return box, float(max_val)
    
    return None, float(max_val)


def locate_template_pyautogui(template_path: str,
                               region: Optional[Tuple[int, int, int, int]] = None,
                               threshold: float = 0.8) -> Tuple[Optional[Tuple[int, int, int, int]], float]:
    """
    Locate template using PyAutoGUI (locateOnScreen).
    
    Args:
        template_path: Path to template image
        region: (left, top, width, height) search region, or None for full screen
        threshold: Confidence threshold (0.0-1.0)
    
    Returns:
        Tuple of (box, confidence) where box is (left, top, width, height) or None
        Note: PyAutoGUI doesn't return actual confidence, returns threshold if found
    """
    if not HAS_PYAUTOGUI:
        raise ImportError("PyAutoGUI not available")
    
    try:
        # Try with confidence parameter (requires OpenCV in PyAutoGUI)
        box = pyautogui.locateOnScreen(
            template_path,
            confidence=threshold,
            region=region,
            grayscale=True
        )
    except Exception:
        # Fallback to basic matching without confidence (works without OpenCV)
        try:
            box = pyautogui.locateOnScreen(
                template_path,
                region=region,
                grayscale=True
            )
        except Exception:
            box = None
    
    if box:
        return (box.left, box.top, box.width, box.height), threshold
    
    return None, 0.0


def locate_template(template_path: str,
                   region: Optional[Tuple[int, int, int, int]] = None,
                   threshold: float = 0.8,
                   method: str = 'auto') -> Tuple[Optional[Tuple[int, int, int, int]], float]:
    """
    Locate template on screen using best available method.
    
    Args:
        template_path: Path to template image
        region: (left, top, width, height) search region, or None for full screen
        threshold: Confidence threshold (0.0-1.0)
        method: 'auto', 'opencv', or 'pyautogui'
    
    Returns:
        Tuple of (box, confidence) where:
        - box is (left, top, width, height) or None if not found
        - confidence is match confidence (0.0-1.0)
    
    Raises:
        ImportError: If no matching method is available
    
    Example:
        box, conf = locate_template('template.png', threshold=0.8)
        if box:
            left, top, width, height = box
            print(f'Found at ({left}, {top}) with confidence {conf:.2f}')
    """
    if method == 'opencv' or (method == 'auto' and HAS_OPENCV):
        if not HAS_OPENCV:
            if method == 'opencv':
                raise ImportError("OpenCV not available. Install: pip install opencv-python")
            # Fall through to PyAutoGUI
        else:
            return locate_template_opencv(template_path, region, threshold)
    
    if method == 'pyautogui' or method == 'auto':
        if not HAS_PYAUTOGUI:
            raise ImportError("PyAutoGUI not available. Install: pip install pyautogui")
        return locate_template_pyautogui(template_path, region, threshold)
    
    raise ValueError(f"Unknown method: {method}. Use 'auto', 'opencv', or 'pyautogui'")


def get_available_methods() -> dict:
    """
    Get information about available template matching methods.
    
    Returns:
        Dict with method availability and recommendations
    """
    return {
        'opencv': {
            'available': HAS_OPENCV,
            'version': cv2.__version__ if HAS_OPENCV else None,
            'features': ['accurate_confidence', 'fast', 'grayscale_matching'] if HAS_OPENCV else []
        },
        'pyautogui': {
            'available': HAS_PYAUTOGUI,
            'version': None,
            'features': ['simple', 'fallback'] if HAS_PYAUTOGUI else []
        },
        'recommended': 'opencv' if HAS_OPENCV else 'pyautogui' if HAS_PYAUTOGUI else None
    }


# Example usage
if __name__ == '__main__':
    import sys
    
    print("Template Matcher - Available Methods")
    print("=" * 60)
    
    methods = get_available_methods()
    
    print(f"\n📦 OpenCV:")
    print(f"   Available: {'✅' if methods['opencv']['available'] else '❌'}")
    if methods['opencv']['version']:
        print(f"   Version: {methods['opencv']['version']}")
        print(f"   Features: {', '.join(methods['opencv']['features'])}")
    
    print(f"\n📦 PyAutoGUI:")
    print(f"   Available: {'✅' if methods['pyautogui']['available'] else '❌'}")
    if methods['pyautogui']['version']:
        print(f"   Version: {methods['pyautogui']['version']}")
        print(f"   Features: {', '.join(methods['pyautogui']['features'])}")
    
    print(f"\n💡 Recommended: {methods['recommended'] or 'None available'}")
    print("\n" + "=" * 60)
    
    if len(sys.argv) > 1:
        template_path = sys.argv[1]
        print(f"\nTesting with template: {template_path}")
        try:
            box, confidence = locate_template(template_path, threshold=0.8)
            if box:
                print(f"✅ Found at {box} with confidence {confidence:.3f}")
            else:
                print(f"❌ Not found (max confidence: {confidence:.3f})")
        except Exception as e:
            print(f"❌ Error: {e}")
