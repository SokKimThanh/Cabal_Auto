"""
Timing Calculator - Calculate optimal hunt timing parameters based on monster stats.

This module calculates optimal lost_timeout and attack_duration based on:
- Monster HP
- Player damage per hit
- Attack speed (attacks per second)
- Safety margin for detection lag

Usage:
    from timing_calculator import calculate_timing, TimingRecommendation
    
    rec = calculate_timing(
        monster_hp=10000,
        damage_per_hit=500,
        attacks_per_second=2.0
    )
    print(f"Recommended lost_timeout: {rec.lost_timeout_sec}s")
    print(f"Recommended attack_duration: {rec.attack_min_duration_sec}s")
"""

from dataclasses import dataclass
import logging
logger = logging.getLogger(__name__)
from typing import Optional
import math


@dataclass
class TimingRecommendation:
    """Recommended timing parameters for hunt configuration."""
    
    # Core timing values - Main 2 values
    lost_timeout_sec: float
    attack_min_duration_sec: float
    
    # Additional timing values - NEW
    attack_press_ms: int  # Key hold duration in milliseconds
    target_cycle_delay: float  # Delay between target switches
    search_interval: float  # Template search frequency
    attack_interval: float  # Delay between attacks
    
    # Calculation details
    estimated_kill_time_sec: float
    hits_to_kill: int
    
    # Safety margins applied
    lost_timeout_margin: float
    attack_duration_margin: float
    
    # Original inputs
    monster_hp: float
    damage_per_hit: float
    attacks_per_second: float
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"""Timing Recommendations:
  Lost Timeout: {self.lost_timeout_sec:.2f}s (with {self.lost_timeout_margin:.0%} margin)
  Attack Duration: {self.attack_min_duration_sec:.2f}s (with {self.attack_duration_margin:.0%} margin)
  
  Details:
  - Estimated kill time: {self.estimated_kill_time_sec:.2f}s
  - Hits to kill: {self.hits_to_kill}
  - Monster HP: {self.monster_hp:,.0f}
  - Damage per hit: {self.damage_per_hit:,.0f}
  - Attack speed: {self.attacks_per_second:.2f} hits/sec"""


def calculate_timing(
    monster_hp: float,
    damage_per_hit: float,
    attacks_per_second: float = 2.0,
    skill_rotation: Optional[list] = None,  # NEW: List of attack skills
    lost_timeout_margin: float = 0.5,
    attack_duration_margin: float = 0.2,
    min_lost_timeout: float = 0.3,
    max_lost_timeout: float = 3.0,
    min_attack_duration: float = 1.0,
    max_attack_duration: float = 30.0
) -> TimingRecommendation:
    """
    Calculate optimal timing parameters based on monster stats and skill rotation.
    
    Args:
        monster_hp: Monster's total HP
        damage_per_hit: Player's damage per attack
        attacks_per_second: Attack speed (default 2.0) - ONLY used if skill_rotation is None
        skill_rotation: List of skill dicts with 'cooldown' and 'cast_time' (NEW!)
        lost_timeout_margin: Safety margin for lost_timeout (default 0.5 = 50%)
        attack_duration_margin: Safety margin for attack_duration (default 0.2 = 20%)
        min_lost_timeout: Minimum lost_timeout value (default 0.3s)
        max_lost_timeout: Maximum lost_timeout value (default 3.0s)
        min_attack_duration: Minimum attack_duration value (default 1.0s)
        max_attack_duration: Maximum attack_duration value (default 30.0s)
    
    Returns:
        TimingRecommendation with calculated values
    
    Examples:
        >>> # Old way (generic APS)
        >>> rec = calculate_timing(10000, 500, 2.0)
        
        >>> # New way (skill rotation)
        >>> skills = [
        ...     {'name': 'Dark Explosion', 'cooldown': 1.9, 'cast_time': 1.7},
        ...     {'name': 'Bone Javelin', 'cooldown': 2.4, 'cast_time': 1.5},
        ... ]
        >>> rec = calculate_timing(10000, 500, skill_rotation=skills)
    """
    # Validate inputs
    if monster_hp <= 0:
        raise ValueError("monster_hp must be > 0")
    if damage_per_hit <= 0:
        raise ValueError("damage_per_hit must be > 0")
    
    # Calculate hits needed to kill monster
    hits_to_kill = math.ceil(monster_hp / damage_per_hit)
    
    # === SKILL ROTATION LOGIC (NEW!) ===
    if skill_rotation and len(skill_rotation) > 0:
        # Calculate timing based on ACTUAL skill rotation
        attack_skills = [s for s in skill_rotation if s.get('type') == 'attack']
        
        if not attack_skills:
            # Fallback to generic APS if no attack skills
            attacks_per_second = attacks_per_second
            time_per_hit = 1.0 / attacks_per_second
            rotation_cycle_time = time_per_hit
        else:
            # Calculate average time per skill cast
            # cast_time = animation time
            # cooldown = time until skill available again
            avg_cast_time = sum(s.get('cast_time', 1.0) for s in attack_skills) / len(attack_skills)
            avg_cooldown = sum(s.get('cooldown', 1.5) for s in attack_skills) / len(attack_skills)
            

            # Total rotation cycle time = cast all skills once
            rotation_cycle_time = sum(s.get('cast_time', 1.0) for s in attack_skills)
            
            # Bottleneck validation
            max_cooldown = max(s.get('cooldown', 1.5) for s in attack_skills)
            if rotation_cycle_time < max_cooldown:
                longest_skills = [s.get('name', 'Unknown') for s in attack_skills if s.get('cooldown', 1.5) == max_cooldown]
                logger.warning(
                    f"Bottleneck detected: Total rotation cast time ({rotation_cycle_time:.2f}s) "
                    f"is less than max cooldown ({max_cooldown:.2f}s) for {', '.join(longest_skills)}."
                )

            # Effective attacks per second = skills per cycle / cycle time
            attacks_per_second = len(attack_skills) / rotation_cycle_time
            
            # Time per hit = rotation cycle / number of skills
            time_per_hit = rotation_cycle_time / len(attack_skills)
            
            # attack_interval = time between skill casts
            # Use the MINIMUM cooldown to ensure we don't cast too fast
            min_cooldown = min(s.get('cooldown', 1.5) for s in attack_skills)
            attack_interval_base = max(min_cooldown, avg_cast_time)
    else:
        # Fallback: Use generic attacks_per_second
        if attacks_per_second <= 0:
            raise ValueError("attacks_per_second must be > 0")
        time_per_hit = 1.0 / attacks_per_second
        rotation_cycle_time = time_per_hit
        attack_interval_base = time_per_hit
    
    # Calculate estimated kill time
    estimated_kill_time_sec = hits_to_kill / attacks_per_second
    
    # Calculate lost_timeout with margin
    # This is the time between attacks - should be short for detection lag
    lost_timeout = time_per_hit * (1.0 + lost_timeout_margin)
    lost_timeout = max(min_lost_timeout, min(max_lost_timeout, lost_timeout))
    
    # Calculate attack_min_duration with margin
    # This ensures we keep attacking even if template briefly disappears
    attack_duration = estimated_kill_time_sec * (1.0 + attack_duration_margin)
    attack_duration = max(min_attack_duration, min(max_attack_duration, attack_duration))
    
    # === Calculate additional timing parameters ===
    
    # 1. attack_press_ms: Key hold duration
    # If skill rotation provided, use average cast_time
    if skill_rotation and len([s for s in skill_rotation if s.get('type') == 'attack']) > 0:
        attack_skills = [s for s in skill_rotation if s.get('type') == 'attack']
        avg_cast_time_ms = sum(s.get('cast_time', 1.0) for s in attack_skills) / len(attack_skills) * 1000
        # Press duration = 10% of cast time (enough to trigger, not too long)
        attack_press_ms = int(max(50, min(150, avg_cast_time_ms * 0.1)))
    else:
        # Fallback: Based on generic APS
        attack_press_ms = int(max(50, min(100, 500 / attacks_per_second)))
    
    # 2. target_cycle_delay: Delay between target switches
    # Should be > time_per_hit to avoid switching mid-attack
    target_cycle_delay = round(max(0.15, time_per_hit * 1.2), 2)
    
    # 3. search_interval: Template search frequency
    # Faster search = better detection, but more CPU
    # Should be < time_per_hit for responsive detection
    search_interval = round(max(0.1, min(0.3, time_per_hit * 0.5)), 2)
    
    # 4. attack_interval: Delay between attacks
    # If skill rotation provided, use skill-based timing
    if skill_rotation and len([s for s in skill_rotation if s.get('type') == 'attack']) > 0:
        # Use the interval calculated from rotation
        attack_interval = round(max(0.1, attack_interval_base), 2)
    else:
        # Fallback: Slightly less than time_per_hit
        attack_interval = round(max(0.1, time_per_hit * 0.8), 2)
    
    return TimingRecommendation(
        lost_timeout_sec=round(lost_timeout, 2),
        attack_min_duration_sec=round(attack_duration, 2),
        attack_press_ms=attack_press_ms,
        target_cycle_delay=target_cycle_delay,
        search_interval=search_interval,
        attack_interval=attack_interval,
        estimated_kill_time_sec=round(estimated_kill_time_sec, 2),
        hits_to_kill=hits_to_kill,
        lost_timeout_margin=lost_timeout_margin,
        attack_duration_margin=attack_duration_margin,
        monster_hp=monster_hp,
        damage_per_hit=damage_per_hit,
        attacks_per_second=attacks_per_second
    )


def calculate_timing_from_monster(
    monster: dict,
    attacks_per_second: float = 2.0,
    skill_rotation: Optional[list] = None,  # NEW!
    **kwargs
) -> Optional[TimingRecommendation]:
    """
    Calculate timing from monster dict (from monsters.json) with optional skill rotation.
    
    Args:
        monster: Monster dict with 'hp' and 'damage_per_hit' keys
        attacks_per_second: Attack speed (fallback if no skill_rotation)
        skill_rotation: List of skill dicts with 'cooldown', 'cast_time', 'type' (NEW!)
        **kwargs: Additional args passed to calculate_timing
    
    Returns:
        TimingRecommendation or None if monster lacks required stats
    
    Examples:
        >>> monster = {"name": "Dragon", "hp": 10000, "damage_per_hit": 500}
        >>> skills = [
        ...     {'name': 'Skill1', 'cooldown': 1.9, 'cast_time': 1.7, 'type': 'attack'},
        ...     {'name': 'Skill2', 'cooldown': 2.4, 'cast_time': 1.5, 'type': 'attack'},
        ... ]
        >>> rec = calculate_timing_from_monster(monster, skill_rotation=skills)
        >>> rec.attack_interval  # Based on actual skill timings!
        1.6
    """
    hp = monster.get('hp')
    damage = monster.get('damage_per_hit')
    
    if hp is None or damage is None or hp <= 0 or damage <= 0:
        return None
    
    return calculate_timing(
        monster_hp=float(hp),
        damage_per_hit=float(damage),
        attacks_per_second=attacks_per_second,
        skill_rotation=skill_rotation,  # Pass skill rotation!
        **kwargs
    )


def format_timing_recommendation(rec: TimingRecommendation, 
                                 language: str = 'en') -> dict:
    """
    Format timing recommendation for display in GUI.
    
    Args:
        rec: TimingRecommendation to format
        language: 'en' or 'vi'
    
    Returns:
        Dict with formatted strings for display
    """
    if language == 'vi':
        return {
            'lost_timeout': f"{rec.lost_timeout_sec:.2f}s",
            'attack_duration': f"{rec.attack_min_duration_sec:.2f}s",
            'kill_time': f"{rec.estimated_kill_time_sec:.2f}s",
            'hits': f"{rec.hits_to_kill} đòn",
            'summary': (
                f"Khuyến nghị: Lost timeout {rec.lost_timeout_sec:.2f}s, "
                f"Attack duration {rec.attack_min_duration_sec:.2f}s\n"
                f"Dự kiến: {rec.hits_to_kill} đòn, {rec.estimated_kill_time_sec:.2f}s để hạ gục"
            )
        }
    else:
        return {
            'lost_timeout': f"{rec.lost_timeout_sec:.2f}s",
            'attack_duration': f"{rec.attack_min_duration_sec:.2f}s",
            'kill_time': f"{rec.estimated_kill_time_sec:.2f}s",
            'hits': f"{rec.hits_to_kill} hits",
            'summary': (
                f"Recommended: Lost timeout {rec.lost_timeout_sec:.2f}s, "
                f"Attack duration {rec.attack_min_duration_sec:.2f}s\n"
                f"Estimated: {rec.hits_to_kill} hits, {rec.estimated_kill_time_sec:.2f}s to kill"
            )
        }


def get_timing_presets() -> dict:
    """
    Get common timing presets for different scenarios.
    
    Returns:
        Dict of preset name -> (attacks_per_second, description)
    """
    return {
        'slow': (1.0, 'Slow attacks (1 hit/sec) - Heavy weapons, slow skills'),
        'normal': (2.0, 'Normal speed (2 hits/sec) - Default attack speed'),
        'fast': (3.0, 'Fast attacks (3 hits/sec) - Light weapons, fast skills'),
        'very_fast': (4.0, 'Very fast (4 hits/sec) - Rapid fire skills'),
    }


# Example usage and testing
if __name__ == '__main__':
    print("Timing Calculator - Examples")
    print("=" * 70)
    
    # Example 1: Normal monster
    print("\n📊 Example 1: Normal Monster")
    print("-" * 70)
    rec1 = calculate_timing(
        monster_hp=10000,
        damage_per_hit=500,
        attacks_per_second=2.0
    )
    print(rec1)
    
    # Example 2: Boss monster
    print("\n\n📊 Example 2: Boss Monster (High HP)")
    print("-" * 70)
    rec2 = calculate_timing(
        monster_hp=100000,
        damage_per_hit=1000,
        attacks_per_second=2.0
    )
    print(rec2)
    
    # Example 3: Weak monster
    print("\n\n📊 Example 3: Weak Monster (Low HP)")
    print("-" * 70)
    rec3 = calculate_timing(
        monster_hp=1000,
        damage_per_hit=500,
        attacks_per_second=2.0
    )
    print(rec3)
    
    # Example 4: Fast attack speed
    print("\n\n📊 Example 4: Fast Attack Speed")
    print("-" * 70)
    rec4 = calculate_timing(
        monster_hp=10000,
        damage_per_hit=300,
        attacks_per_second=4.0
    )
    print(rec4)
    
    # Show presets
    print("\n\n📋 Available Presets:")
    print("-" * 70)
    presets = get_timing_presets()
    for name, (aps, desc) in presets.items():
        print(f"{name:12s}: {desc}")
    
    print("\n" + "=" * 70)
