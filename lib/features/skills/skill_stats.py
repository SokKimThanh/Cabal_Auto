"""
Sprint 22 Patch 1: Skill Statistics Tracker for Training Mode

This module provides real-time skill performance tracking for training mode.
Tracks cast counts, cooldown status, and success rates for each skill.

Author: Sprint 22 Implementation
Date: October 21, 2025
"""

import time
from typing import Dict, Optional, List


class SkillStats:
    """Track skill performance statistics for training mode.
    
    Features:
    - Record each skill cast with timestamp
    - Calculate cast counts
    - Track last cast time
    - Monitor cooldown status
    - Calculate success rate (cast attempts vs successful casts)
    
    Usage:
        stats = SkillStats()
        stats.record_cast('Fire Ball', success=True)
        stats.record_cast('Power Slash', success=False)
        
        all_stats = stats.get_all_stats()
        for skill, data in all_stats.items():
            print(f"{skill}: {data['cast_count']} casts, {data['success_rate']:.1f}% success")
    """
    
    def __init__(self):
        """Initialize empty skill statistics tracker."""
        # Structure: {skill_name: {'casts': [], 'successes': [], 'last_cast': timestamp}}
        self._data: Dict[str, Dict] = {}
    
    def record_cast(self, skill_name: str, success: bool = True, timestamp: Optional[float] = None):
        """Record a skill cast event.
        
        Args:
            skill_name: Name of the skill being cast
            success: Whether the cast was successful (default: True)
            timestamp: Unix timestamp of cast (default: current time)
        """
        if timestamp is None:
            timestamp = time.time()
        
        if skill_name not in self._data:
            self._data[skill_name] = {
                'casts': [],
                'successes': [],
                'last_cast': 0.0
            }
        
        # Record cast
        self._data[skill_name]['casts'].append(timestamp)
        if success:
            self._data[skill_name]['successes'].append(timestamp)
        self._data[skill_name]['last_cast'] = timestamp
    
    def get_cast_count(self, skill_name: str) -> int:
        """Get total number of casts for a skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Total cast count (0 if skill not found)
        """
        if skill_name not in self._data:
            return 0
        return len(self._data[skill_name]['casts'])
    
    def get_last_cast_time(self, skill_name: str) -> Optional[float]:
        """Get timestamp of last cast for a skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Unix timestamp of last cast, or None if never cast
        """
        if skill_name not in self._data:
            return None
        
        last_cast = self._data[skill_name]['last_cast']
        return last_cast if last_cast > 0 else None
    
    def get_time_since_last_cast(self, skill_name: str) -> Optional[float]:
        """Get seconds since last cast.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Seconds since last cast, or None if never cast
        """
        last_cast = self.get_last_cast_time(skill_name)
        if last_cast is None:
            return None
        return time.time() - last_cast
    
    def get_success_rate(self, skill_name: str) -> float:
        """Get success rate percentage for a skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Success rate as percentage (0.0 - 100.0), 0.0 if no casts
        """
        if skill_name not in self._data:
            return 0.0
        
        total_casts = len(self._data[skill_name]['casts'])
        if total_casts == 0:
            return 0.0
        
        successes = len(self._data[skill_name]['successes'])
        return (successes / total_casts) * 100.0
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get statistics for all tracked skills.
        
        Returns:
            Dictionary mapping skill names to their stats:
            {
                'Skill Name': {
                    'cast_count': int,
                    'last_cast': float (timestamp),
                    'time_since_last_cast': float (seconds) or None,
                    'success_rate': float (percentage)
                },
                ...
            }
        """
        result = {}
        current_time = time.time()
        
        for skill_name in self._data:
            last_cast = self.get_last_cast_time(skill_name)
            time_since = current_time - last_cast if last_cast else None
            
            result[skill_name] = {
                'cast_count': self.get_cast_count(skill_name),
                'last_cast': last_cast,
                'time_since_last_cast': time_since,
                'success_rate': self.get_success_rate(skill_name)
            }
        
        return result
    
    def get_skill_names(self) -> List[str]:
        """Get list of all tracked skill names.
        
        Returns:
            List of skill names that have been cast
        """
        return list(self._data.keys())
    
    def reset(self):
        """Clear all statistics."""
        self._data.clear()
    
    def reset_skill(self, skill_name: str):
        """Clear statistics for a specific skill.
        
        Args:
            skill_name: Name of the skill to reset
        """
        if skill_name in self._data:
            del self._data[skill_name]
    
    def __repr__(self) -> str:
        """String representation of stats tracker."""
        skill_count = len(self._data)
        total_casts = sum(len(data['casts']) for data in self._data.values())
        return f"<SkillStats: {skill_count} skills, {total_casts} total casts>"


# Example usage
if __name__ == '__main__':
    # Demo skill stats tracking
    stats = SkillStats()
    
    # Simulate skill casts
    print("Simulating skill casts...")
    stats.record_cast('Fire Ball', success=True)
    time.sleep(0.5)
    stats.record_cast('Power Slash', success=True)
    time.sleep(0.3)
    stats.record_cast('Fire Ball', success=True)
    time.sleep(0.2)
    stats.record_cast('Ice Storm', success=False)
    time.sleep(0.4)
    stats.record_cast('Fire Ball', success=True)
    
    # Display statistics
    print("\n" + "="*60)
    print("SKILL PERFORMANCE STATISTICS")
    print("="*60)
    
    all_stats = stats.get_all_stats()
    for skill, data in sorted(all_stats.items()):
        time_ago = data['time_since_last_cast']
        time_str = f"{time_ago:.1f}s ago" if time_ago else "Never"
        success_rate = data['success_rate']
        
        # Color code success rate
        if success_rate >= 90:
            status = "✅ EXCELLENT"
        elif success_rate >= 70:
            status = "⚠️ GOOD"
        else:
            status = "❌ POOR"
        
        print(f"\n{skill}:")
        print(f"  Casts: {data['cast_count']}")
        print(f"  Last Cast: {time_str}")
        print(f"  Success Rate: {success_rate:.1f}% {status}")
    
    print("\n" + "="*60)
    print(f"Total: {len(stats.get_skill_names())} skills tracked")
    print("="*60)
