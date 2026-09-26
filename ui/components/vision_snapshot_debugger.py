import tkinter as tk
from tkinter import ttk
from ui.components.icon_button import create_icon_button
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

    def _get_translation(self, key: str, default: str) -> str:
        _t = getattr(self.app, "_t", None)
        if _t:
            return _t(key)
        return default

    def open_debugger(self):
        if self.toplevel is not None and self.toplevel.winfo_exists():
            self.toplevel.lift()
            return

        self.toplevel = tk.Toplevel()
        self.toplevel.title(self._get_translation("vision_debugger.title", "Vision Debugger"))
        self.toplevel.geometry("1100x700") # Wider for dual panes
        self.toplevel.configure(bg=UI.BG_BASE)

        # Main PanedWindow layout
        self.paned_window = ttk.PanedWindow(self.toplevel, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=UI.SPACE_MD, pady=UI.SPACE_MD)

        # LEFT PANE: Canvas and Header
        self.left_frame = tk.Frame(self.paned_window, bg=UI.BG_BASE)
        self.paned_window.add(self.left_frame, weight=3) # 75% width

        # Header controls
        header_frame = tk.Frame(self.left_frame, bg=UI.BG_BASE)
        header_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, UI.SPACE_MD))

        # Debt: use create_icon_button instead of tk.Button
        refresh_btn = create_icon_button(
            header_frame,
            icon_name="refresh",
            text=self._get_translation("vision_debugger.refresh", "Refresh Snapshot"),
            command=self._refresh_snapshot,
            button_type="primary"
        )
        refresh_btn.pack(side=tk.LEFT)

        # Canvas for image
        self.canvas = tk.Canvas(self.left_frame, bg=UI.BG_SURFACE, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # RIGHT PANE: ROIs Panel
        self.right_frame = tk.Frame(self.paned_window, bg=UI.BG_SURFACE)
        self.paned_window.add(self.right_frame, weight=1) # 25% width

        # Header for Right Panel
        roi_header_label = tk.Label(
            self.right_frame,
            text=self._get_translation("vision_debugger.system_rois", "System ROIs"),
            font=UI.get_font(role="header"),
            bg=UI.BG_SURFACE,
            fg=UI.TEXT_PRIMARY
        )
        roi_header_label.pack(side=tk.TOP, fill=tk.X, padx=UI.SPACE_MD, pady=UI.SPACE_MD)

        # Scrollable area for ROI cards
        self.roi_canvas = tk.Canvas(self.right_frame, bg=UI.BG_SURFACE, highlightthickness=0)
        self.roi_scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.roi_canvas.yview)

        self.roi_scrollable_frame = tk.Frame(self.roi_canvas, bg=UI.BG_SURFACE)
        self.roi_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.roi_canvas.configure(scrollregion=self.roi_canvas.bbox("all"))
        )

        self.roi_canvas_window_id = self.roi_canvas.create_window((0, 0), window=self.roi_scrollable_frame, anchor="nw")

        # Ensure scrollable frame resizes to canvas width
        self.roi_canvas.bind(
            "<Configure>",
            lambda e: self.roi_canvas.itemconfig(self.roi_canvas_window_id, width=e.width)
        )

        self.roi_canvas.configure(yscrollcommand=self.roi_scrollbar.set)
        self.roi_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.roi_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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
                text=self._get_translation("vision_debugger.no_frame", "No active frame or engine is busy."),
                fill=UI.TEXT_MUTED,
                font=UI.get_font(role="header"),
                tags="timeout_text"
            )
            return

        self._extract_and_render_rois(frame, detections)

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


    def _extract_and_render_rois(self, frame, detections):
        # Clear existing ROI cards in the right panel
        for widget in self.roi_scrollable_frame.winfo_children():
            widget.destroy()

        rois_data = []
        if hasattr(self.app, "state_controller") and getattr(self.app, "state_controller", None) and hasattr(self.app.state_controller, "hunt_cfg"):
            rois_config = self.app.state_controller.hunt_cfg.get("rois", {})
        else:
            rois_config = {}

        img_h, img_w = frame.shape[:2]

        for roi_name, roi_coords in rois_config.items():
            if not isinstance(roi_coords, (list, tuple)) or len(roi_coords) != 4:
                continue

            x, y, w, h = roi_coords
            status = "valid"
            cropped = None

            # Validation
            if w <= 0 or h <= 0:
                status = "invalid_dims"
            elif x < 0 or y < 0 or x + w > img_w or y + h > img_h:
                status = "out_of_bounds"
            else:
                cropped = frame[y:y+h, x:x+w]
                if cropped.size == 0:
                    status = "empty_crop"

            rois_data.append({
                "name": roi_name,
                "coords": roi_coords,
                "status": status,
                "cropped": cropped
            })

        self._render_roi_cards(rois_data)
        self._render_main_canvas(frame, rois_data, detections)

    def _render_roi_cards(self, rois_data):
        self._roi_images = [] # Prevent garbage collection

        if not rois_data:
            lbl = tk.Label(
                self.roi_scrollable_frame,
                text=self._get_translation("vision_debugger.no_system_rois", "No System ROIs configured."),
                bg=UI.BG_SURFACE,
                fg=UI.TEXT_MUTED
            )
            lbl.pack(pady=UI.SPACE_MD)
            return

        for data in rois_data:
            card = tk.Frame(self.roi_scrollable_frame, bg=UI.BG_BASE, bd=1, relief=tk.SOLID)
            card.pack(fill=tk.X, padx=UI.SPACE_SM, pady=UI.SPACE_SM)

            name_lbl = tk.Label(card, text=data["name"].upper(), font=UI.get_font(role="header"), bg=UI.BG_BASE, fg=UI.TEXT_PRIMARY)
            name_lbl.pack(anchor="w", padx=UI.SPACE_SM, pady=(UI.SPACE_SM, 0))

            x, y, w, h = data["coords"]
            coords_lbl = tk.Label(card, text=f"X: {x}, Y: {y} | W: {w}, H: {h}", font=UI.get_font(role="small"), bg=UI.BG_BASE, fg=UI.TEXT_MUTED)
            coords_lbl.pack(anchor="w", padx=UI.SPACE_SM)

            status = data["status"]
            if status == "valid":
                status_text = self._get_translation("vision_debugger.valid", "Valid")
                status_color = UI.COLOR_SUCCESS
            elif status == "invalid_dims":
                status_text = self._get_translation("vision_debugger.err_dims", "Error: Width or Height <= 0")
                status_color = UI.COLOR_ERROR
            elif status == "out_of_bounds":
                status_text = self._get_translation("vision_debugger.err_bounds", "Error: Out of screen bounds")
                status_color = UI.COLOR_ERROR
            else:
                status_text = self._get_translation("vision_debugger.err_unknown", "Error: Invalid image")
                status_color = UI.COLOR_ERROR

            status_lbl = tk.Label(card, text=status_text, font=UI.get_font(role="small", weight="bold"), bg=UI.BG_BASE, fg=status_color)
            status_lbl.pack(anchor="w", padx=UI.SPACE_SM, pady=(0, UI.SPACE_SM))

            if status == "valid" and data["cropped"] is not None:
                # Convert BGR to RGB for PIL
                rgb_crop = cv2.cvtColor(data["cropped"], cv2.COLOR_BGR2RGB)

                # Resize if it's too big to fit the panel
                panel_width = 250
                if rgb_crop.shape[1] > panel_width:
                    scale = panel_width / rgb_crop.shape[1]
                    new_w = int(rgb_crop.shape[1] * scale)
                    new_h = int(rgb_crop.shape[0] * scale)
                    rgb_crop = cv2.resize(rgb_crop, (new_w, new_h))

                pil_img = Image.fromarray(rgb_crop)
                tk_img = ImageTk.PhotoImage(pil_img)
                self._roi_images.append(tk_img)

                img_lbl = tk.Label(card, image=tk_img, bg=UI.BG_BASE)
                img_lbl.pack(padx=UI.SPACE_SM, pady=(0, UI.SPACE_SM))

    def _render_main_canvas(self, frame, rois_data, detections):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
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

        # Draw ROIs on main image
        for data in rois_data:
            if data["status"] != "valid":
                continue
            x, y, w, h = data["coords"]
            dx, dy, dw, dh = int(x * scale), int(y * scale), int(w * scale), int(h * scale)
            # Draw yellow box for system ROIs
            cv2.rectangle(resized_frame, (dx, dy), (dx + dw, dy + dh), (0, 255, 255), 2)
            cv2.putText(resized_frame, data["name"], (dx, max(0, dy - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        # Draw usual detections
        for det in detections:
            dx = int(det.get("x", 0) * scale)
            dy = int(det.get("y", 0) * scale)
            dw = int(det.get("w", 0) * scale)
            dh = int(det.get("h", 0) * scale)
            score = det.get("score", det.get("confidence", 0.0))
            cv2.rectangle(resized_frame, (dx, dy), (dx + dw, dy + dh), (0, 255, 0), 2)
            target_str = self._get_translation("vision_debugger.target", "Target")
            label = f"{target_str} [{score:.2f}]"
            cv2.putText(resized_frame, label, (dx, max(0, dy - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        self.current_image = ImageTk.PhotoImage(pil_image)

        self.canvas.delete("all")
        self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.current_image, anchor=tk.CENTER)

    def _on_close(self):
        self.current_image = None
        if self.toplevel:
            self.toplevel.destroy()
            self.toplevel = None
