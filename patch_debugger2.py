import re

with open("ui/components/vision_snapshot_debugger.py", "r") as f:
    content = f.read()

# Make sure to bind event and refactor refresh_snapshot
search = """    def _refresh_snapshot(self):
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
            print(f"Error rendering image: {e}")"""

replace = """    def start_listening(self):
        from lib.events.event_bus import EventBus
        from lib.features.hunt.scan_controller import ScanCompletedEvent
        EventBus.bind(ScanCompletedEvent, self._on_scan_completed)

    def stop_listening(self):
        from lib.events.event_bus import EventBus
        from lib.features.hunt.scan_controller import ScanCompletedEvent
        EventBus.unbind(ScanCompletedEvent, self._on_scan_completed)

    def _on_scan_completed(self, event):
        # UI updates must be run on the main thread
        if hasattr(self, "after"):
            self.after(0, self._refresh_snapshot)
        else:
            self._refresh_snapshot()

    def _refresh_snapshot(self):
        if not cv2 or not Image or not ImageTk:
            self.status_label.config(text="Missing OpenCV or Pillow", fg=UI.COLOR_ERROR)
            return

        frame, detections = self.vision_engine.get_latest_snapshot(timeout=0.5)

        if frame is None:
            self.status_label.config(
                text=self._get_translation("vision_debugger.no_frame", "No active frame or engine is busy."),
                fg=UI.TEXT_MUTED
            )
            self.reason_label.config(text="")
            return

        self._process_and_render_tabs(frame, detections)

    def _process_and_render_tabs(self, frame, detections):
        # --- Tab 1: Original ROI ---
        roi_frame = frame.copy()

        # --- Tab 2: Preprocessed ---
        # Convert to grayscale and apply basic thresholding for visualization
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Convert back to BGR so it matches shape requirements if needed, or render as grayscale
        preprocessed_frame = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        # --- Tab 3: Vision Output ---
        output_frame = frame.copy()
        for det in detections:
            dx = int(det.get("x", 0))
            dy = int(det.get("y", 0))
            dw = int(det.get("w", 0))
            dh = int(det.get("h", 0))
            score = det.get("score", det.get("confidence", 0.0))

            cv2.rectangle(output_frame, (dx, dy), (dx + dw, dy + dh), (0, 255, 0), 2)
            target_str = self.app._t("vision_debugger.target") if hasattr(self.app, "_t") else "Target"
            label = f"{target_str} [{score:.2f}]"
            cv2.putText(
                output_frame, label, (dx, max(0, dy - 5)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
            )

        # Save raw frames for expansion
        self._raw_frames["roi"] = roi_frame
        self._raw_frames["processed"] = preprocessed_frame
        self._raw_frames["output"] = output_frame

        # Render to canvases
        self._render_to_canvas(self.canvas_roi, roi_frame, "roi")
        self._render_to_canvas(self.canvas_processed, preprocessed_frame, "processed")
        self._render_to_canvas(self.canvas_output, output_frame, "output")

        # --- Tab 4: Pass/Fail Status ---
        if detections and len(detections) > 0:
            self.status_label.config(
                text=self._get_translation("vision_debugger.status_pass", "PASS"),
                fg=UI.COLOR_SUCCESS
            )
            self.reason_label.config(
                text=f"{len(detections)} object(s) detected."
            )
        else:
            self.status_label.config(
                text=self._get_translation("vision_debugger.status_fail", "FAIL"),
                fg=UI.COLOR_ERROR
            )
            self.reason_label.config(
                text=self._get_translation("vision_debugger.reason_no_detect", "No objects detected in the current ROI.")
            )

    def _render_to_canvas(self, canvas, frame, tab_key):
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

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

        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

        # Explicit memory management
        self._tab_images[tab_key] = None

        try:
            pil_img = Image.fromarray(rgb_frame)
            self._tab_images[tab_key] = ImageTk.PhotoImage(pil_img)
            canvas.delete("all")
            x_offset = (canvas_width - new_w) // 2
            y_offset = (canvas_height - new_h) // 2
            canvas.create_image(x_offset, y_offset, anchor="nw", image=self._tab_images[tab_key])
        except Exception as e:
            print(f"Error rendering image to {tab_key}: {e}")

    def _expand_image(self, tab_key):
        if not self._raw_frames.get(tab_key) is not None:
            return

        frame = self._raw_frames[tab_key]

        if self.expanded_toplevel is not None and self.expanded_toplevel.winfo_exists():
            self.expanded_toplevel.destroy()

        self.expanded_toplevel = tk.Toplevel(self)
        self.expanded_toplevel.title(self._get_translation("vision_debugger.expanded_title", f"Expanded View - {tab_key}"))
        self.expanded_toplevel.geometry("1280x720")

        canvas = tk.Canvas(self.expanded_toplevel, bg=UI.BG_BASE, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        # Bind resize event to re-render image dynamically
        canvas.bind("<Configure>", lambda e: self._render_expanded(canvas, frame))

    def _render_expanded(self, canvas, frame):
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return

        img_h, img_w = frame.shape[:2]
        scale = min(canvas_width / max(1, img_w), canvas_height / max(1, img_h))
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        if new_w > 0 and new_h > 0:
            resized_frame = cv2.resize(frame, (new_w, new_h))
        else:
            resized_frame = frame

        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

        # Free memory
        self.expanded_image = None

        try:
            pil_img = Image.fromarray(rgb_frame)
            self.expanded_image = ImageTk.PhotoImage(pil_img)
            canvas.delete("all")
            x_offset = (canvas_width - new_w) // 2
            y_offset = (canvas_height - new_h) // 2
            canvas.create_image(x_offset, y_offset, anchor="nw", image=self.expanded_image)
        except Exception as e:
            print(f"Error rendering expanded image: {e}")

    def destroy(self):
        self.stop_listening()
        self._tab_images.clear()
        self._raw_frames.clear()
        self.expanded_image = None
        super().destroy()"""

new_content = content.replace(search, replace)
with open("ui/components/vision_snapshot_debugger.py", "w") as f:
    f.write(new_content)
