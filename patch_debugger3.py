import re

with open("ui/components/vision_snapshot_debugger.py", "r") as f:
    content = f.read()

# Remove the rest of the old methods
search = """    def _extract_and_render_rois(self, frame, detections):
        # Clear existing ROI cards in the right panel
        for widget in self.roi_scrollable_frame.winfo_children():
            widget.destroy()

        rois_data = []
        if hasattr(self.app, "state_controller") and getattr(self.app, "state_controller", None) and hasattr(self.app.state_controller, "hunt_cfg"):
            rois_config = self.app.state_controller.get_hunt_config_value("rois", {})
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
            self.toplevel = None"""

replace = """"""

new_content = content.replace(search, replace)
with open("ui/components/vision_snapshot_debugger.py", "w") as f:
    f.write(new_content)
