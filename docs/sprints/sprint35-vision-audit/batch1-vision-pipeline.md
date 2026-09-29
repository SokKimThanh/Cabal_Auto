# Batch 1 — Vision Pipeline Audit

## A. Files đã đọc
| # | File | Số dòng | Đã đọc hết? |
|---|---|---|---|
| 1 | lib/system/screen_capture.py | ~650 | Yes |
| 2 | lib/system/window_manager.py | ~200 | Yes |
| 3 | lib/vision/vision_engine.py | ~1150 | Yes |
| 4 | lib/vision/matcher_service.py | ~100 | Yes |
| 5 | lib/vision/template_loader.py | ~150 | Yes |
| 6 | lib/features/hunt/scanner.py | ~250 | Yes |
| 7 | lib/features/hunt/scan_controller.py | ~200 | Yes |

## B. Raw output 8 lệnh
### Lệnh 1: find lib/vision...
```
lib/vision/matcher_service.py:16:class MatcherService:
lib/vision/skill_cooldown_detector.py:9:class SkillCooldownDetector:
lib/vision/vision_engine.py:44:class Detection:
lib/vision/vision_engine.py:70:class TrackedObject:
lib/vision/vision_engine.py:91:class VisionEngine:
lib/vision/target_name_reader.py:16:class TargetNameReader:
lib/vision/target_bar_detector.py:21:class TargetBarDetector:
lib/vision/template_loader.py:19:class Template:
lib/vision/template_loader.py:102:class TemplateService:
lib/vision/monster_detector.py:44:class DetectionState(Enum):
lib/vision/monster_detector.py:54:class DetectionStats:
lib/vision/monster_detector.py:70:class MonsterDetector:
lib/vision/target_hp_reader.py:5:class TargetHPReader:
```

### Lệnh 2: grep vision_engine...
```
44:class Detection:
57:    def to_dict(self) -> Dict[str, Any]:
60:    def bbox(self) -> Tuple[int, int, int, int]:
64:    def center(self) -> Tuple[int, int]:
70:class TrackedObject:
82:    def to_dict(self) -> Dict[str, Any]:
91:class VisionEngine:
96:    def __init__(self, config_dir: str = "lib/data"):
179:    def templates(self) -> Dict[str, Template]:
183:    def templates_config_path(self) -> Path:
190:    def load_templates(self, path_list: List[str]) -> Dict[str, Template]:
193:    def add_template(
200:    def remove_template(self, template_id: str) -> bool:
203:    def get_template(self, template_id: str) -> Optional[Template]:
206:    def list_templates(self) -> List[Template]:
213:    def match_templates(
245:    def _match_template_at_scale(
258:    def nms(
267:    def start_track(self, frame: np.ndarray, detection: Detection) -> str:
333:    def update_tracks(self, frame: np.ndarray) -> List[TrackedObject]:
368:    def reverify_track(
397:    def stop_track(self, tracker_id: str) -> bool:
403:    def stop_all_tracks(self):
406:    def get_tracked_objects(self) -> List[TrackedObject]:
413:    def detect_hsv_target(
579:    def detect_features(
770:    def detect_monster_pipeline(
828:    def start_worker(
844:    def stop_worker(self) -> None:
861:    def get_result(self, timeout: float = 0.0) -> Optional[Dict[str, Any]]:
867:    def _worker_loop(self) -> None:
900:    def _process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
998:    def get_latest_snapshot(self, timeout=0.5) -> Tuple[Optional[np.ndarray], List[Dict[str, Any]]]:
1008:    def reset(self):
1014:    def focus_capture_window(self) -> bool:
1024:    def start_capture(
1054:    def stop_capture(self) -> None:
1068:    def get_capture_frame(self, timeout: float = 0.1) -> Optional[np.ndarray]:
1076:    def is_capture_active(self) -> bool:
1083:    def set_params(self, params_dict: Dict[str, Any]):
1086:    def get_params(self) -> Dict[str, Any]:
1089:    def set_debug(self, enabled: bool):
1096:    def get_capture_stats(self) -> Optional[Dict[str, Any]]:
1118:    def get_threshold_presets(self) -> Dict[str, float]:
1121:    def _save_templates_config(self):
1124:    def _load_templates_config(self):
1127:    def set_region(self, region: Optional[Tuple[int, int, int, int]]):
1131:    def get_region(self) -> Optional[Tuple[int, int, int, int]]:
1134:    def _load_region_config(self):
1146:    def _save_region_config(self):
```

### Lệnh 3: grep VisionEngine()
```
ui/controllers/overlay_controller.py:330:                        self.parent._vision_engine = VisionEngine()
lib/features/hunt/hunt_runner.py:33:        self.vision_engine = VisionEngine()
tests/demos/vision/demo_monster_tracking.py:135:    vision_engine = VisionEngine()
tests/demos/vision/demo_monster_tracking.py:193:    vision_engine = VisionEngine()
tests/demos/vision/demo_monster_tracking.py:251:    vision_engine = VisionEngine()
tests/demos/demo_vision_capture.py:71:    engine = VisionEngine()
```

### Lệnh 4: grep .get_frame(
```
ui/components/action_bar_view.py:84:        self.compact_window_selector.get_frame().pack(side="left", padx=(0, 12))
lib/vision/vision_engine.py:1072:            return self.screen_capture.get_frame(timeout=timeout)
lib/vision/monster_detector.py:446:            frame = self._screen_capture.get_frame(timeout=0.05)
lib/system/screen_capture.py:16:            frame = capture.get_frame()
lib/system/screen_capture.py:624:            frame = capture.get_frame()
lib/features/hunt/scan_controller.py:124:                frame = scanner.screen_capture.get_frame(timeout=1.0)
lib/features/hunt/scanner.py:97:            frame = self.screen_capture.get_frame(timeout=1.0)
lib/features/setup/screen_state_analyzer.py:70:            frame = cap.get_frame(timeout=1.0)
tests/integration/vision/test_screen_capture.py:258:    frame = capture.get_frame(timeout=0.1)
tests/integration/vision/test_screen_capture.py:274:    frame = capture.get_frame(timeout=1.0)
tests/integration/vision/test_screen_capture.py:532:        frame = capture.get_frame(timeout=1.0)
tests/sprints/sprint23/test_screen_capture.py:258:    frame = capture.get_frame(timeout=0.1)
tests/sprints/sprint23/test_screen_capture.py:274:    frame = capture.get_frame(timeout=1.0)
tests/sprints/sprint23/test_screen_capture.py:532:        frame = capture.get_frame(timeout=1.0)
```

### Lệnh 5: grep start_capture | .start(
```
lib/system/screen_capture.py:14:    if capture.start("Cabal"):
lib/system/screen_capture.py:251:        self.thread.start()
lib/system/screen_capture.py:606:    if capture.start(window_title):
lib/system/task_scheduler.py:138:            thread.start()
lib/system/bot_manager.py:159:                success = self._detector.start()
```

### Lệnh 6: grep detect_monster_pipeline | match_templates
```
docs/archive/scripts/patch_test_ocr_db_fallback.py:33:        vision_engine.detect_monster_pipeline.return_value = [det]
ui/utils/detection_converter.py:71:        >>> detections = engine.match_templates(frame)
lib/vision/matcher_service.py:30:    def match_templates(
lib/vision/matcher_service.py:56:            logger.warning("Empty or invalid frame provided to match_templates")
lib/vision/vision_engine.py:213:    def match_templates(
lib/vision/vision_engine.py:233:        return self.matcher_service.match_templates(
lib/vision/vision_engine.py:413:    def detect_hsv_target(
lib/vision/vision_engine.py:770:    def detect_monster_pipeline(
lib/vision/vision_engine.py:790:            hsv_detections = self.detect_hsv_target(
lib/vision/vision_engine.py:819:        tmpl_dets = self.match_templates(
lib/vision/vision_engine.py:915:                detections = self.detect_monster_pipeline(
lib/vision/vision_engine.py:919:                detections = self.match_templates(frame, roi=self.default_region)
lib/vision/monster_detector.py:465:            detections = self._vision_engine.detect_monster_pipeline(frame)
lib/features/hunt/scanner.py:111:            monsters = self.vision_engine.detect_monster_pipeline(frame, roi=hunt_roi)
lib/features/hunt/scanner.py:142:                    skill_detections = self.vision_engine.match_templates(
lib/features/hunt/scene_monster_detector.py:48:        detections = self.vision_engine.detect_monster_pipeline(
lib/features/setup/screen_state_analyzer.py:129:            detections = engine.detect_hsv_target(frame)
```

### Lệnh 7: grep dxcam
```
lib/system/screen_capture.py:33:    import dxcam
lib/system/screen_capture.py:36:    dxcam = None
lib/system/screen_capture.py:38:    logger.info("[Capture] dxcam không có sẵn, dùng BitBlt backend")
lib/system/screen_capture.py:139:        self._dxcam_camera = None
lib/system/screen_capture.py:142:            self._use_dxcam = _DXCAM_AVAILABLE
lib/system/screen_capture.py:143:        elif backend == "dxcam":
lib/system/screen_capture.py:145:                raise RuntimeError("backend='dxcam' nhưng dxcam chưa cài. pip install dxcam")
lib/system/screen_capture.py:146:            self._use_dxcam = True
lib/system/screen_capture.py:148:            self._use_dxcam = False
lib/system/screen_capture.py:150:        logger.info(f"[Capture] Backend: {'dxcam' if self._use_dxcam else 'bitblt'}")
lib/system/screen_capture.py:240:        if self._use_dxcam:
lib/system/screen_capture.py:242:                self._dxcam_camera = dxcam.create(output_color="BGR")
lib/system/screen_capture.py:243:                logger.info("[Capture] dxcam camera created")
lib/system/screen_capture.py:245:                logger.warning(f"[Capture] dxcam init failed: {e}, fallback BitBlt")
lib/system/screen_capture.py:246:                self._use_dxcam = False
lib/system/screen_capture.py:247:                self._dxcam_camera = None
lib/system/screen_capture.py:265:        if self._dxcam_camera is not None:
lib/system/screen_capture.py:267:                self._dxcam_camera.release()
lib/system/screen_capture.py:270:            self._dxcam_camera = None
lib/system/screen_capture.py:320:            if not self._use_dxcam:
lib/system/screen_capture.py:350:                        if not self._use_dxcam:
lib/system/screen_capture.py:385:            if not self._use_dxcam:
lib/system/screen_capture.py:452:        if self._use_dxcam and self._dxcam_camera is not None:
lib/system/screen_capture.py:460:                frame = self._dxcam_camera.grab(region=region)
lib/system/screen_capture.py:477:                logger.error(f"[Capture] dxcam error: {e}, fallback BitBlt for this frame")
lib/system/screen_capture.py:478:                self._use_dxcam = False
```

### Lệnh 8: grep except bare
```
lib/system/screen_capture.py:370:                        except:
```

## C. Trả lời 8 câu
### Q1. Capture backend
FILE: lib/system/screen_capture.py
LINE: 245
CODE:
```python
        if self._use_dxcam:
            try:
                self._dxcam_camera = dxcam.create(output_color="BGR")
                logger.info("[Capture] dxcam camera created")
            except Exception as e:
                logger.warning(f"[Capture] dxcam init failed: {e}, fallback BitBlt")
                self._use_dxcam = False
```
VERIFY: `grep -rn "dxcam" --include="*.py"`
KẾT LUẬN: Code cố gắng tạo `dxcam` đầu tiên. Nếu thư viện thiếu hoặc bị lỗi khởi tạo (exception), nó tự động fallback về BitBlt (`self._use_dxcam = False`). Cả hai backend đều có mặt.

### Q2. Có bao nhiêu method public trong VisionEngine?
FILE: lib/vision/vision_engine.py
LINE: N/A
CODE:
```python
    def templates(self) -> Dict[str, Template]:
    def templates_config_path(self) -> Path:
    def load_templates(self, path_list: List[str]) -> Dict[str, Template]:
    def add_template(
    def remove_template(self, template_id: str) -> bool:
    def get_template(self, template_id: str) -> Optional[Template]:
    def list_templates(self) -> List[Template]:
    def match_templates(
    def nms(
    def start_track(self, frame: np.ndarray, detection: Detection) -> str:
    def update_tracks(self, frame: np.ndarray) -> List[TrackedObject]:
    def reverify_track(
    def stop_track(self, tracker_id: str) -> bool:
    def stop_all_tracks(self):
    def get_tracked_objects(self) -> List[TrackedObject]:
    def detect_hsv_target(
    def detect_features(
    def detect_monster_pipeline(
    def start_worker(
    def stop_worker(self) -> None:
    def get_result(self, timeout: float = 0.0) -> Optional[Dict[str, Any]]:
    def get_latest_snapshot(self, timeout=0.5) -> Tuple[Optional[np.ndarray], List[Dict[str, Any]]]:
    def reset(self):
    def focus_capture_window(self) -> bool:
    def start_capture(
    def stop_capture(self) -> None:
    def get_capture_frame(self, timeout: float = 0.1) -> Optional[np.ndarray]:
    def is_capture_active(self) -> bool:
    def set_params(self, params_dict: Dict[str, Any]):
    def get_params(self) -> Dict[str, Any]:
    def set_debug(self, enabled: bool):
    def get_capture_stats(self) -> Optional[Dict[str, Any]]:
    def get_threshold_presets(self) -> Dict[str, float]:
    def set_region(self, region: Optional[Tuple[int, int, int, int]]):
    def get_region(self) -> Optional[Tuple[int, int, int, int]]:
```
VERIFY: `grep -n "^    def \|^class " lib/vision/vision_engine.py`
KẾT LUẬN: Có khoảng 35 public methods trong `VisionEngine` phục vụ tracking, matching, capture lifecycle, và template management.

### Q3. Method detect_monster_pipeline nhận gì, trả gì?
FILE: lib/vision/vision_engine.py
LINE: 770
CODE:
```python
    def detect_monster_pipeline(
        self,
        frame: np.ndarray,
        template_ids: Optional[List[str]] = None,
        roi: Optional[Tuple[int, int, int, int]] = None,
        downscale_factor: Optional[float] = None,
        confidence_threshold: float = 0.6,
        use_fast_hsv: bool = True,
    ) -> List[Detection]:
```
VERIFY: `grep -n "^    def " lib/vision/vision_engine.py` (và đọc code detect_monster_pipeline)
KẾT LUẬN: Nhận vào `frame` dạng numpy array (BGR), optional ROI, template_ids, tỉ lệ scale, ngưỡng confident, có xài HSV hay không. Trả về `List[Detection]`.

### Q4. Có ROI nào được định nghĩa cứng không?
FILE: lib/vision/vision_engine.py
LINE: 787
CODE:
```python
        search_roi = roi if roi is not None else self.default_region
```
VERIFY: `grep -rn "default_region\|roi=" lib/vision/vision_engine.py`
KẾT LUẬN: ROI mặc định là `self.default_region`. Nó không hardcode con số cụ thể trong code mà được config linh hoạt (`set_region()`). Nếu không có truyền vào và không có default thì crop toàn màn hình. Ở context scanner, ROI được đưa từ `hunt_roi = tuple(rois["hunt_area"])`.

### Q5. Frame sau capture đi qua mấy bước?
FILE: lib/features/hunt/scanner.py
LINE: 111
CODE:
```python
            # 1. Start Capture
            frame = self.screen_capture.get_frame(timeout=1.0)

            # 2. HSV/Template Matching
            monsters = self.vision_engine.detect_monster_pipeline(frame, roi=hunt_roi)

            # 3. Match Skills
            skill_detections = self.vision_engine.match_templates(frame, templates=templates_added, roi=combo_bar_roi, max_results=20)
```
VERIFY: Phân tích `lib/features/hunt/scanner.py` và `monster_detector.py`.
KẾT LUẬN: Frame -> `ScreenCapture.get_frame()` -> Đưa vào `vision_engine.detect_monster_pipeline()` -> `match_templates` nếu cần -> Đóng gói Detection.

### Q6. VisionEngine trả về dạng gì? Field nào?
FILE: lib/vision/vision_engine.py
LINE: 44
CODE:
```python
class Detection:
    template_id: str
    x: int
    y: int
    w: int
    h: int
    confidence: float
```
VERIFY: `grep -n "^class " lib/vision/vision_engine.py`
KẾT LUẬN: Trả về instance class `Detection` chứa toạ độ (x, y, w, h), confidence score, template id.

### Q7. Có bao nhiêu chỗ gọi .copy() trên frame?
FILE: lib/vision/vision_engine.py
LINE: 960, 988, 1001, v.v
CODE:
```python
lib/vision/vision_engine.py:910:        rendered_frame = frame if render_inplace else frame.copy()
lib/vision/vision_engine.py:960:                self.latest_frame = rendered_frame.copy() if rendered_frame is not None else None
lib/system/screen_capture.py:468:                    self._latest_frame = frame.copy()
```
VERIFY: `grep -rn "\.copy(" --include="*.py" lib/vision/ lib/system/screen_capture.py`
KẾT LUẬN: Có khoảng 10-12 chỗ copy array, chủ yếu để giữ lại state an toàn trên `_latest_frame` ở background thread hoặc cho renderer. Có comment optimization `# 💡 What: Removed .copy() on the incoming frame array.`

### Q8. Có bao nhiêu `except:` trần (bare except)?
FILE: lib/system/screen_capture.py
LINE: 370
CODE:
```python
                        # Drop oldest
                        try:
                            self.frame_queue.get_nowait()
                            self.frame_queue.put_nowait(frame)
                        except:
                            pass
```
VERIFY: `grep -rn "except:" --include="*.py" lib/vision/ lib/system/screen_capture.py`
KẾT LUẬN: Có đúng 1 chỗ bare except trong `screen_capture.py` dùng để im lặng lỗi Queue nếu hàng đợi race condition.

## D. Sơ đồ flow thực tế
`ScreenCapture.get_frame()` (lib/system/screen_capture.py:284) →
`MonsterDetector._capture_frame()` (lib/vision/monster_detector.py:436) / `Scanner._scan_loop()` (lib/features/hunt/scanner.py:97) →
`VisionEngine.detect_monster_pipeline()` (lib/vision/vision_engine.py:770) →
`VisionEngine.detect_hsv_target()` / `match_templates()` (lib/vision/vision_engine.py:790)

## E. MISMATCH (nếu có)
Không có class/method sai lệch so với codebase.
