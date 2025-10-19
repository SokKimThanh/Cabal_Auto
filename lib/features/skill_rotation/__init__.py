"""
Skill Rotation Module
Precise skill rotation timing calculation with cooldown tracking
"""

from .builder import (
    SkillTiming,
    SkillRotation,
    calculate_rotation_timing,
    calculate_press_duration,
    generate_rotation_preview,
    generate_execution_preview
)

from .ui_integration import (
    SkillRotationUI,
    integrate_rotation_builder
)

__all__ = [
    'SkillTiming',
    'SkillRotation',
    'calculate_rotation_timing',
    'calculate_press_duration',
    'generate_rotation_preview',
    'generate_execution_preview',
    'SkillRotationUI',
    'integrate_rotation_builder'
]

__version__ = '1.0.0'
