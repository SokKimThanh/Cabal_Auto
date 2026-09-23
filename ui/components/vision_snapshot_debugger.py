import tkinter as tk
from tkinter import ttk
from lib.ui_style_v2 import UIStyleV2 as UI
from lib.vision.vision_engine import get_vision_engine
import numpy as np

try:
    import cv2
    from PIL import Image, ImageTk
except ImportError:
    cv2 = None
    Image = None
    ImageTk = None

class VisionSnapshotDebugger:
    def __init__(self, app):
        self.app = app
        self.toplevel = None
        self.canvas = None
        self.current_image = None

        # Resolve vision engine either directly from the app (if injected/cached)
        # or via the singleton accessor
        if hasattr(self.app, "_vision_engine") and self.app._vision_engine is not None:
            self.vision_engine = self.app._vision_engine
        else:
            self.vision_engine = get_vision_engine()

    def open_debugger(self):
        if self.toplevel is not None and self.toplevel.winfo_exists():
            self.toplevel.lift()
            return

        self.toplevel = tk.Toplevel()
        self.toplevel.title(self.app._t("vision_debugger.title") if hasattr(self.app, "_t") else "Vision Debugger")
        self.toplevel.geometry("800x600")
        self.toplevel.configure(bg=UI.BG_BASE)

        # Header controls
        header_frame = tk.Frame(self.toplevel, bg=UI.BG_BASE)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=UI.SPACE_MD, pady=UI.SPACE_MD)

        refresh_btn = tk.Button(
            header_frame,
            text=self.app._t("vision_debugger.refresh") if hasattr(self.app, "_t") else "Refresh Snapshot",
            command=self._refresh_snapshot,
            **UI.get_button_style("primary")
        )
        refresh_btn.pack(side=tk.LEFT)

        # Canvas for image
        self.canvas = tk.Canvas(self.toplevel, bg=UI.BG_SURFACE, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=UI.SPACE_MD, pady=(0, UI.SPACE_MD))

        # Handle window close to clear image reference
        self.toplevel.protocol("WM_DELETE_WINDOW", self._on_close)

        # Initial load
        self._refresh_snapshot()

    def _refresh_snapshot(self):
        if not cv2 or not Image or not ImageTk:
            # Fallback if libraries are missing
            self.canvas.create_text(
                400, 300,
                text="Missing OpenCV or Pillow",
                fill=UI.TEXT_PRIMARY,
                font=UI.get_font(role="header")
            )
            return

        frame, detections = self.vision_engine.get_latest_snapshot(timeout=0.5)

        if frame is None:
            self.canvas.delete("timeout_text")
            self.canvas.create_text(
                400, 300,
                text=self.app._t("vision_debugger.no_frame") if hasattr(self.app, "_t") else "No active frame or engine is busy.",
                fill=UI.TEXT_MUTED,
                font=UI.get_font(role="header"),
                tags="timeout_text"
            )
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            # Not fully rendered yet, pick a default size
            canvas_width = 800
            canvas_height = 500

        img_h, img_w = frame.shape[:2]

        scale = min(canvas_width / max(1, img_w), canvas_height / max(1, img_h))
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        if new_w > 0 and new_h > 0:
            resized_frame = cv2.resize(frame, (new_w, new_h))
        else:
            resized_frame = frame

        # Draw bounding boxes based on scaling
        for det in detections:
            # We scale bounding boxes to match the resized_frame dimensions
            dx = int(det.get("x", 0) * scale)
            dy = int(det.get("y", 0) * scale)
            dw = int(det.get("w", 0) * scale)
            dh = int(det.get("h", 0) * scale)

            # Use provided score or confidence key
            score = det.get("score", det.get("confidence", 0.0))

            # Draw green bounding box
            cv2.rectangle(resized_frame, (dx, dy), (dx + dw, dy + dh), (0, 255, 0), 2)

            # Format text: "Mục tiêu [0.85]" or translated text
            target_str = self.app._t("vision_debugger.target") if hasattr(self.app, "_t") else "Target"
            label = f"{target_str} [{score:.2f}]"

            cv2.putText(
                resized_frame,
                label,
                (dx, dy - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )

        # Convert colorspace BGR -> RGB for Pillow
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

        # Explicitly clear old image reference for GC
        self.current_image = None

        try:
            pil_img = Image.fromarray(rgb_frame)
            self.current_image = ImageTk.PhotoImage(pil_img)
            self.canvas.delete("image")
            self.canvas.delete("timeout_text")
            # Center the image
            x_offset = (canvas_width - new_w) // 2
            y_offset = (canvas_height - new_h) // 2
            self.canvas.create_image(x_offset, y_offset, anchor="nw", image=self.current_image, tags="image")
        except Exception as e:
            print(f"Error rendering image: {e}")

    def _on_close(self):
        self.current_image = None
        if self.toplevel:
            self.toplevel.destroy()
            self.toplevel = None
