## 2025-08-18 - Vectorized NMS in VisionEngine
**Learning:** Standard Python loops with IoU checks during Non-Maximum Suppression (NMS) in template/monster detection scale poorly ($O(N^2)$ scalar iterations). Vectorizing bounding box intersection and union operations with NumPy yields an ~8x-10x speedup for candidate detection sets.
**Action:** Always prefer NumPy vectorized bounding box calculations for NMS and IoU evaluation in vision pipelines.

## 2025-08-19 - Grayscale Conversion & Caching in VisionEngine Template Matching
**Learning:** `cv2.matchTemplate` on 3-channel BGR images is ~3x slower than on 1-channel grayscale images. Pre-converting templates to grayscale on load and converting search frame regions to grayscale once per matching call yields a ~3x speedup without sacrificing detection accuracy.
**Action:** Always perform OpenCV `matchTemplate` on single-channel grayscale images and cache grayscale template images on load.
