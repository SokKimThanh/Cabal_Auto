Dưới đây là tài liệu kế hoạch tái cấu trúc `vision_engine.py` đã được chuẩn hóa, tích hợp đầy đủ các cảnh báo kiến trúc cốt lõi (Core Combat Loop vs. Utility Engine) và xử lý triệt để toàn bộ các lỗ hổng kỹ thuật được phản biện.

---

# Kế Hoạch Tái Cấu Trúc Vision Engine (Sprint 22 — Phase 3)

**Ngày:** 2026-09-01

**Trạng thái:** Đề xuất triển khai

**Phạm vi:** `lib/vision/vision_engine.py`

**Mục tiêu:** Vá lỗi logic nội bộ, nâng cao tính tương thích OpenCV, xác thực an toàn Homography, bảo vệ buffer frame và bổ sung test cases hồi quy mà không phá vỡ interface hiện có.

---

## 1. Ranh Giới Kiến Trúc & Cảnh Báo Phạm Vi (Architectural Boundary)

> **⚠ NGUYÊN TẮC BẤT BIẾN (Theo 00-global-rules.md & CB1 → CB6):**
> * **Combat Loop Single Source of Truth:** Vòng lặp chiến đấu chính (`HuntOrchestrator`) sử dụng độc quyền **`TargetBarDetector` / `TargetNameReader**` với ROI cố định trên thanh Target Bar. Tuyệt đối **không** quét 3D toàn màn hình bằng HSV hay Feature Matching trong combat loop.
> 
> 
> * **Định vị `vision_engine.py`:** Đây là module độc lập phục vụ mục đích tiện ích (công cụ hiệu chỉnh/calibration, UI overlay preview, tracking phụ trợ, hoặc tương thích ngược), **không** được chạy song song làm tiêu tốn CPU/trùng lặp tài nguyên với pipeline combat chính.
> 
> 
> * Việc mở rộng `vision_engine.py` trong kế hoạch này thuần túy là **vá lỗi kỹ thuật nội bộ (Internal Bug Fixes)**, giữ nguyên tính độc lập của module.
> 
> 
> 
> 

---

## 2. Kế Hoạch Triển Khai Chi Tiết Theo Session (< 30 Phút)

---

### Session 1: Tương Thích Tracker OpenCV & Xác Thực Homography (25 phút)

**Mục tiêu:** Khắc phục lỗi crash khi thiếu `opencv-contrib-python`, ghi log chi tiết cho từng candidate creator, và triệt tiêu bounding box ảo do biến dạng phối cảnh.

**Bước 1 — An toàn hóa `start_track` với Debug Logging:**

Không nuốt lỗi im lặng; ghi nhận chi tiết nguyên nhân thất bại của từng candidate creator trước khi kết luận không hỗ trợ:

```python
tracker = None
candidates = [
    ("legacy", getattr(getattr(cv2, "legacy", None), f"Tracker{tracker_type}_create", None)),
    ("main", getattr(cv2, f"Tracker{tracker_type}_create", None)),
]

for source, creator in candidates:
    if callable(creator):
        try:
            tracker = creator()
            logger.debug(f"Tracker {tracker_type} created successfully from {source} module.")
            break
        except Exception as e:
            logger.debug(f"Tracker candidate {source}.Tracker{tracker_type}_create failed: {e}")

if tracker is None:
    logger.error(f"Tracker {tracker_type} is not supported or failed to initialize in current OpenCV build.")
    return ""

```

**Bước 2 — Xác thực đa giác và diện tích trong `detect_features`:**

Thêm kiểm tra tính lồi và chặn diện tích bất thường (các giá trị `20` và `0.9` là ngưỡng tham chiếu, có thể tinh chỉnh theo cấu hình):

```python
# Giả định: pts được khởi tạo theo thứ tự 4 góc tuần tự (0,0 -> 0,th -> tw,th -> tw,0)
# nên dst từ perspectiveTransform sẽ giữ nguyên thứ tự bao quanh đa giác.
pts_int = dst.astype(np.int32)
if not cv2.isContourConvex(pts_int):
    logger.debug("Feature matching rejected: Transformed polygon is non-convex or self-intersecting.")
    return []

poly_area = cv2.contourArea(pts_int)
min_poly_area = self.params.get("feature_min_poly_area", 20)
max_poly_area = self.params.get("feature_max_poly_area", frame_w * frame_h * 0.9)

if poly_area < min_poly_area or poly_area > max_poly_area:
    logger.debug(f"Feature matching rejected: Polygon area {poly_area:.1f} out of bounds ({min_poly_area}-{max_poly_area}).")
    return []

```

**Kiểm thử Session 1 (5 phút):**

* Test 1.1: Gọi `detect_features` với template không khớp $\rightarrow$ Xác nhận trả về `[]` thay vì tạo bounding box bao phủ frame.


* Test 1.2: Mock cả 2 candidate tracker đều raise Exception $\rightarrow$ Xác nhận trả về `""`, ghi đúng log debug chi tiết và log error cuối.



---

### Session 2: Tinh Chỉnh Bộ Lọc Màu HSV Độc Lập (20 phút)

**Mục tiêu:** Tách biệt hoàn toàn giữa chế độ quét dải màu tùy biến và chế độ quét theo threat levels để tránh vô tình kích hoạt bộ lọc loại trừ màu đỏ mặc định.

**Bước 1 — Sửa điều kiện `apply_red_filter` trong `detect_hsv_target`:**

```python
if lower_hsv is not None and upper_hsv is not None:
    # Chế độ dải tùy biến: Tắt bộ lọc loại trừ đỏ mặc định để không can thiệp dải màu caller chỉ định
    apply_red_filter = False
    lower_b = np.array(lower_hsv, dtype=np.uint8)
    upper_b = np.array(upper_hsv, dtype=np.uint8)
    if lower_b[0] > upper_b[0]:
        m1 = cv2.inRange(hsv, np.array([0, lower_b[1], lower_b[2]], dtype=np.uint8), upper_b)
        m2 = cv2.inRange(hsv, lower_b, np.array([180, upper_b[1], upper_b[2]], dtype=np.uint8))
        mask = cv2.bitwise_or(m1, m2)
    else:
        mask = cv2.inRange(hsv, lower_b, upper_b)
else:
    # Chế độ nhiều dải theo threat levels
    apply_red_filter = "red" not in active_levels_lower

```

**Kiểm thử Session 2 (5 phút):**

* Test 2.1: Quét dải màu đỏ tùy biến `lower_hsv=(0, 100, 100)`, `upper_hsv=(10, 255, 255)` $\rightarrow$ Xác nhận phát hiện đúng contour đỏ mà không bị `red_mask` loại trừ.



---

### Session 3: Tối Ưu Buffer Frame & Safe Rendering (20 phút)

**Mục tiêu:** Cho phép tùy chọn giữ nguyên frame sạch không bị vẽ đè, đồng thời đảm bảo 100% tương thích ngược với hành vi cũ.

**Bước 1 — Thêm cờ cấu hình trong `__init__`:**

Bổ sung `"render_inplace": True` vào `self.params` để giữ nguyên hành vi mặc định (tiết kiệm bộ nhớ).

**Bước 2 — Cập nhật `_process_frame`:**

```python
render_inplace = self.params.get("render_inplace", True)
rendered_frame = frame if render_inplace else frame.copy()

```

**Kiểm thử Session 3 (5 phút):**

* Test 3.1 (`render_inplace=False`): Xác nhận frame gốc truyền vào không bị thay đổi pixel sau khi qua `_process_frame`.


* Test 3.2 (`render_inplace=True`): Xác nhận frame gốc được vẽ trực tiếp như hành vi ban đầu (backward compatibility).



---

### Session 4: Khả Năng Cấu Hình Pipeline & Auto-Track Selection Strategy (25 phút)

**Mục tiêu:** Mở rộng worker loop có thể cấu hình pipeline và áp dụng chiến lược lựa chọn mục tiêu rõ ràng (`selection_strategy`) khi auto-tracking.

**Bước 1 — Mở rộng tham số cấu hình trong `__init__`:**

Bổ sung `"worker_pipeline": "template"`, `"auto_track": False`, và `"target_selection_strategy": "highest_confidence"` vào `self.params`.

**Bước 2 — Cập nhật luồng xử lý trong `_process_frame`:**

```python
if len(self.trackers) == 0:
    pipeline_mode = self.params.get("worker_pipeline", "template")
    if pipeline_mode == "monster":
        detections = self.detect_monster_pipeline(frame, roi=self.default_region)
    else:
        detections = self.match_templates(frame, roi=self.default_region)
    
    if self.params.get("auto_track", False) and detections:
        strategy = self.params.get("target_selection_strategy", "highest_confidence")
        if strategy == "center_screen":
            fh, fw = frame.shape[:2]
            cx, cy = fw // 2, fh // 2
            best_det = min(detections, key=lambda d: (d.center()[0] - cx)**2 + (d.center()[1] - cy)**2)
        else:  # "highest_confidence"
            best_det = max(detections, key=lambda d: d.score)
        
        self.start_track(frame, best_det)

```

**Kiểm thử Session 4 (5 phút):**

* Test 4.1: Chạy `worker_pipeline="monster"` $\rightarrow$ Xác nhận queue trả về format `{"type": "detections", ...}` chuẩn.


* Test 4.2: Có nhiều detection + `auto_track=True` $\rightarrow$ Xác nhận tracker chọn đúng phần tử có confidence cao nhất hoặc gần tâm nhất tùy theo `target_selection_strategy`.



---

## 3. Tiêu Chí Nghiệm Thu Tổng Thể (Acceptance Criteria)

* Khởi tạo tracker bắt exception an toàn, log debug rõ nguyên nhân từng candidate, không crash khi thiếu `cv2.legacy`.


* `detect_features` loại bỏ triệt để các bounding box phi lồi/tự cắt.


* `detect_hsv_target` hỗ trợ dải màu đỏ tùy biến chính xác.


* Backward-compatible 100%: Mọi cấu hình mặc định (`render_inplace=True`, `worker_pipeline="template"`) giữ nguyên hành vi cũ và không can thiệp vào Target Bar Combat Loop.