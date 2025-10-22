# Vision Engine Basic Tests

Sprint 22 Phase 2 - Core functionality tests

## Setup

```bash
# Install OpenCV (if not already installed)
pip install opencv-python opencv-contrib-python

# Or use requirements
pip install -r ui/requirements.txt
```

## Run Tests

```bash
# Run all tests
python tests/vision_basic_test.py

# Expected output:
# ✅ All tests passed!
```

## Test Coverage

1. **Engine Initialization** - Verify engine creates successfully
2. **Template Loading** - Load templates from file paths
3. **Template Detection** - Multi-template, multi-scale matching
4. **NMS** - Non-Maximum Suppression removes duplicates
5. **Tracking** - Start/update/stop hybrid tracking
6. **Config Persistence** - Save/load templates and regions

## Sample Images

Tests automatically create sample images in `tests/samples/`:
- `test_frame.png` - Test frame with pattern
- `test_template.png` - Template to match

## Dependencies

- `opencv-python` >= 4.5.0
- `opencv-contrib-python` >= 4.5.0 (for trackers)
- `numpy`

## Notes

- Tests use synthetic images (no real game screenshots needed)
- Tracker APIs may vary between OpenCV versions
- If tracker errors occur, check OpenCV version: `cv2.__version__`
