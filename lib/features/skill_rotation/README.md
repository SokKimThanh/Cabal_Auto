# Skill Rotation Module

Module tính toán chính xác timing cho skill rotation với cooldown và cast time.

## Components

- `builder.py`: Core logic for rotation calculation
- `ui.py`: GUI components for rotation builder (coming soon)

## Usage

```python
from lib.features.skill_rotation.builder import calculate_rotation_timing

skills = [
    {'name': 'Skill 1', 'key': '1', 'type': 'attack', 'cooldown': 2.0, 'cast_time': 1.5},
    {'name': 'Buff', 'key': '4', 'type': 'buff', 'cooldown': 3.0, 'cast_time': 1.0},
]

rotation = calculate_rotation_timing(skills)
print(rotation.rhythm_description)
```
