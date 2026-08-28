"""
Test template matching - Kiểm tra tại sao không detect được monster
"""
import sys
import cv2
import numpy as np
import time
from pathlib import Path
sys.path.insert(0, 'E:/Cabal_Auto')

from lib.vision.template_matcher import locate_template_opencv
import pyautogui
import json

print("=" * 70)
print("TEMPLATE MATCHING DIAGNOSTIC")
print("=" * 70)
print()

# Load config
config_path = Path('E:/Cabal_Auto/lib/data/hunt_config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

template_path = cfg.get('template_path')
confidence = cfg.get('confidence', 0.85)
grayscale = cfg.get('grayscale', True)

print(f"Template: {template_path}")
print(f"Confidence: {confidence}")
print(f"Grayscale: {grayscale}")
print()

# Check if template exists
if not Path(template_path).exists():
    print(f"❌ ERROR: Template file not found!")
    print(f"   Path: {template_path}")
    print()
    print("SOLUTIONS:")
    print("1. Capture monster template trong Setup Wizard")
    print("2. Hoặc dùng Hunt tab → Template Matcher → Capture template")
    input("\nPress ENTER to exit...")
    sys.exit(1)

print("✓ Template file exists")
print()

# Load template image
template = cv2.imread(template_path)
if template is None:
    print(f"❌ ERROR: Cannot load template image!")
    input("\nPress ENTER to exit...")
    sys.exit(1)

if grayscale:
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

print(f"✓ Template loaded: {template.shape}")
print()

# Test matching
print("=" * 70)
print("TESTING TEMPLATE MATCHING (10 attempts)")
print("=" * 70)
print()
print("⚠️ Make sure monster visible on screen!")
print("   Game window should be visible (not minimized)")
print()
print("📢 Bạn có 10 GIÂY để:")
print("   1. Mở game CABAL")
print("   2. Di chuyển đến vị trí có monster")
print("   3. Đảm bảo monster hiển thị rõ trên màn hình")
print()
input("Press ENTER khi sẵn sàng, sau đó bạn có 10s để chuẩn bị...")

print("\n⏰ COUNTDOWN - Chuẩn bị game window...")
for i in range(10, 0, -1):
    print(f"   {i} giây...", end='\r')
    time.sleep(1)
print("\n✓ Bắt đầu test!\n")

match_count = 0
for i in range(10):
    print(f"\n--- Attempt {i+1}/10 ---")
    
    try:
        # Capture screen
        screenshot = pyautogui.screenshot()
        if grayscale:
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        else:
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        if screenshot is None:
            print("  ✗ Failed to capture window")
            continue
        
        print(f"  Screenshot: {screenshot.shape}")
        
        # Try matching with OpenCV
        if len(template.shape) == 2:  # grayscale
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        else:
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            match_count += 1
            h, w = template.shape[:2]
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            center = (top_left[0] + w//2, top_left[1] + h//2)
            
            print(f"  ✓ MATCH FOUND!")
            print(f"    Box: ({top_left[0]}, {top_left[1]}, {w}, {h})")
            print(f"    Confidence: {max_val:.3f}")
            print(f"    Center: {center}")
        else:
            print(f"  ✗ No match (confidence {max_val:.3f} < {confidence})")
            
            # Try with lower confidence
            if max_val >= 0.5:
                print(f"    ℹ️ Would match with confidence 0.5: {max_val:.3f}")
                print(f"       → SUGGESTION: Lower confidence in config to ~{max_val:.2f}")
        
        time.sleep(0.5)
        
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)
print(f"Matches found: {match_count}/10")
print()

if match_count == 0:
    print("❌ NO MATCHES FOUND!")
    print()
    print("POSSIBLE CAUSES:")
    print("1. Template image không khớp với monster hiện tại")
    print("   → Capture template mới trong game")
    print()
    print("2. Confidence threshold quá cao (0.85)")
    print("   → Thử giảm xuống 0.6-0.7 trong hunt_config.json")
    print()
    print("3. Region không đúng")
    print("   → Set region = null để search toàn màn hình")
    print()
    print("4. Monster không hiển thị trên màn hình")
    print("   → Đảm bảo monster visible khi test")
    
elif match_count < 5:
    print("⚠️ LOW MATCH RATE!")
    print()
    print("SUGGESTIONS:")
    print("1. Lower confidence threshold to 0.6-0.7")
    print("2. Recapture template with better clarity")
    print("3. Test with monster closer/more visible")
    
else:
    print("✅ TEMPLATE MATCHING WORKS!")
    print()
    print("If skills still don't cast in app:")
    print("1. Check console logs for '[Hunt] Attack mode'")
    print("2. Make sure template_path in config is correct")
    print("3. Verify skill_slots configured properly")

print()
input("Press ENTER to exit...")
