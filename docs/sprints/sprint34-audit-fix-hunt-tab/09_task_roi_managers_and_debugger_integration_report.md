# ROI Management and Vision Debugger Integration Report

## 1. Objective (Goal)
To resolve the user's confusion regarding what the vision engine actually captures when system Regions of Interest (ROIs) are defined. The goal is to provide visual feedback and strictly validate dimensions inside the `VisionSnapshotDebugger` and guarantee that these ROIs are actively utilized by the underlying hunting/scanning backend, rather than lying dormant in the configuration.

## 2. Scope
* `ui/components/vision_snapshot_debugger.py`: Refactored to a `PanedWindow` split-pane layout to show a list of ROI cards alongside the main capture canvas.
* `lib/features/hunt/scanner.py`: Updated `AutoScanner` to process user-defined `hunt_area` and `combo_bar` ROIs during monster and skill detection pipelines.
* `lib/features/hunt/scan_controller.py`: Safely injected the active `hunt_cfg` from the UI layer into the backend scanner.

## 3. Implementation Details & Technical Debt Cleared
* **Layout**: Converted `VisionSnapshotDebugger` to a `ttk.PanedWindow`. Left pane (~75% width) shows full capture, right pane (~25%) shows scrollable ROI cards.
* **Validation**: ROI data extracted from `self.app.state_controller.hunt_cfg` undergoes boundary validations (`x, y < 0`, `w, h <= 0`, out of bounds of the actual game resolution).
* **Tech Debt**:
  * Replaced native `tk.Button` with uniform `create_icon_button`.
  * Removed hardcoded English strings. Implemented a safe translation fallback via `self._get_translation("key", "default")`.
* **System Integration**: The configuration data was verified to exist only in `hunt_cfg["rois"]`. It was previously unused. Now, `ScanController` injects this data into `AutoScanner.scan_screen`, forcing the backend to bound its `cv2.matchTemplate` calls to the user's specific drawn boxes.

## 4. Definition of Done
* Debugger UI displays all configured system ROIs (like `combo_bar` or `minimap`) as cropped mini-images.
* Invalid ROIs render a clear error status (e.g., "Error: Out of bounds") in red text without crashing the canvas.
* Yellow bounding boxes demarcate ROIs on the main debugger preview.
* `scanner.py` utilizes the ROIs during its `detect_monster_pipeline` and `match_templates` processes.
* All unit tests pass.

## 5. Note on AI/Learning capabilities
As clarified during execution, the application's vision system utilizes static OpenCV Template Matching (via `cv2.matchTemplate`). There are no neural networks or automated learning processes storing images for future "learning".
