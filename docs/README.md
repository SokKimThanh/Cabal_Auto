# Documentation Directory

This directory contains all project documentation, summaries, and sprint records.

## Structure

### `/sprints/`
Contains sprint demo scripts and summary documents:
- `sprint13_demo.py` - Demo for Apply Timing to Hunt Config
- `sprint14_demo.py` - Demo for Buff Auto-Casting Runtime
- `sprint15_demo.py` - Demo for Buff Duration GUI Fields
- `SPRINT15_SUMMARY.txt` - Detailed technical summary of Sprint 15
- `SPRINT15_COMPLETE.md` - User-friendly guide for Sprint 15

### Root Documentation
- `PROJECT_SUMMARY.py` - Complete project summary (all 15 sprints)
- (Future: API documentation, user guides, etc.)

## Sprint Documentation Format

Each sprint includes:
1. **Demo Script** (`sprintXX_demo.py`): 
   - Demonstrates new features
   - Shows usage examples
   - Explains benefits

2. **Summary Document** (`SPRINTXX_SUMMARY.txt`):
   - Technical details
   - Code changes
   - Implementation notes

3. **Complete Guide** (`SPRINTXX_COMPLETE.md`):
   - User-friendly overview
   - Usage instructions
   - Benefits and examples

## Running Documentation Scripts

```bash
# Run project summary
python docs/PROJECT_SUMMARY.py

# Run sprint demos
python docs/sprints/sprint13_demo.py
python docs/sprints/sprint14_demo.py
python docs/sprints/sprint15_demo.py
```

## Contributing Documentation

When adding new sprints or features:
1. Create demo script in `/sprints/`
2. Write technical summary
3. Create user-friendly guide
4. Update PROJECT_SUMMARY.py
5. Update main README.md
