# Tests Directory

This directory contains all test scripts and test-related files.

## Test Files

### `opencv_test.py`
Performance comparison test between OpenCV and PyAutoGUI template matching.

**Features:**
- Benchmarks OpenCV cv2.matchTemplate() vs PyAutoGUI
- Tests accuracy and performance
- Shows confidence value comparison
- Provides recommendations

**Usage:**
```bash
python tests/opencv_test.py
```

### `test_template_matcher_integration.py`
Integration test for the unified template_matcher module.

**Features:**
- Tests template_matcher.locate_template()
- Verifies OpenCV and PyAutoGUI integration
- Checks confidence value accuracy
- Validates fallback behavior

**Usage:**
```bash
python tests/test_template_matcher_integration.py
```

## Running Tests

### Run All Tests
```bash
# From project root
python tests/opencv_test.py
python tests/test_template_matcher_integration.py
```

### Test Requirements
- Template images in `assets/images/monsters/` or `assets/images/skills/`
- OpenCV installed (`opencv-python`)
- PyAutoGUI installed
- PIL/Pillow installed

## Test Coverage

Current test coverage:
- ✅ OpenCV template matching
- ✅ PyAutoGUI template matching
- ✅ Template matcher integration
- ✅ Confidence value accuracy
- ⏳ Skills runtime (manual testing via demo scripts)
- ⏳ Hunt logger (manual testing during hunt)
- ⏳ Timing calculator (manual testing in GUI)

## Adding New Tests

When adding new test files:
1. Name files with `test_` prefix
2. Include docstring explaining test purpose
3. Add usage instructions
4. Update this README
5. Consider adding to CI/CD pipeline (future)

## Test Best Practices

- Keep tests independent
- Use descriptive names
- Include clear error messages
- Test both success and failure cases
- Document expected results
