import re

with open('lib/features/hunt/scan_controller.py', 'r') as f:
    content = f.read()

# Add imports
imports = """
from lib.utils.template_storage import TemplateStorageManager
import cv2
import numpy as np
from PIL import Image
"""
content = re.sub(r'import logging', 'import logging\n' + imports, content)

# Find where frame is obtained
frame_logic_search = """                frame = scanner.screen_capture.get_frame(timeout=1.0)
                if frame is None:
                    raise Exception("Frame is None.")"""

frame_logic_replace = """                frame = scanner.screen_capture.get_frame(timeout=1.0)
                if frame is None:
                    raise Exception("Frame is None.")

                # Extract 4 bounding boxes (100x100) around the center of the frame
                h, w = frame.shape[:2]
                cx, cy = w // 2, h // 2
                half = 50
                # Define 4 offsets (e.g., center, top-left, top-right, bottom-left relative to center or just 4 distinct boxes)
                # We'll just slice 4 100x100 boxes around center with some offset
                boxes = [
                    (cx - 50, cy - 50),
                    (cx - 150, cy - 50),
                    (cx + 50, cy - 50),
                    (cx - 50, cy + 50)
                ]
                patches = []
                for bx, by in boxes:
                    x1 = max(0, bx)
                    y1 = max(0, by)
                    x2 = min(w, x1 + 100)
                    y2 = min(h, y1 + 100)
                    patch = frame[y1:y2, x1:x2]
                    if patch.size > 0:
                        patches.append(patch)

                # Save templates async
                storage_manager = TemplateStorageManager()
                storage_manager.save_templates_async(patches)

                # Create 48x36 PIL image thumbnail from the first patch
                thumbnail_pil = None
                if patches:
                    try:
                        # Resize first patch to 48x36
                        thumb_np = cv2.resize(patches[0], (48, 36))
                        # Convert BGR to RGB
                        thumb_rgb = cv2.cvtColor(thumb_np, cv2.COLOR_BGR2RGB)
                        thumbnail_pil = Image.fromarray(thumb_rgb)
                    except Exception as e:
                        self.logger.error(f"[AutoScan] Failed to create thumbnail: {e}")"""

content = content.replace(frame_logic_search, frame_logic_replace)

results_search = """                # Run scan logic
                results = scanner.run_scan()"""

results_replace = """                # Run scan logic
                results = scanner.run_scan()
                if thumbnail_pil:
                    results["thumbnail"] = thumbnail_pil"""

content = content.replace(results_search, results_replace)

with open('lib/features/hunt/scan_controller.py', 'w') as f:
    f.write(content)
