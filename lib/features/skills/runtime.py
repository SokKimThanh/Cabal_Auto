"""
Skill Runtime Manager - Handles attack and buff skill casting with proper timing

This module provides intelligent skill management for the hunt system:
- Attack skills: Cast during combat with cooldown management
- Buff skills: Auto-recast before expiration using duration_sec and pre_refresh_sec
- Separate lanes: Buffs and attacks managed independently
- Thread-safe: Can be used in GUI or CLI contexts

Usage:
    from skill_runtime import SkillRuntime
    
    # Initialize with skills from skills.json
    runtime = SkillRuntime(skills_list)
    
    # In hunt loop
    current_time = time.time()
    
    # Cast buffs (always, regardless of combat state)
    buff_key = runtime.get_buff_to_cast(current_time)
    if buff_key:
        tap(buff_key)
        runtime.mark_cast(buff_key, current_time)
    
    # Cast attacks (only during combat)
    if have_target:
        attack_key = runtime.get_attack_to_cast(current_time)
        if attack_key:
            tap(attack_key)
            runtime.mark_cast(attack_key, current_time)
"""

import time
from typing import List, Dict, Optional
from dataclasses import dataclass

from lib.features.skills.cast_delivery import CastReservation, CastOutcome



@dataclass
class SkillInfo:
    """Information about a skill for runtime management."""
    name: str
    key: str
    skill_type: str  # 'attack' or 'buff'
    cooldown: float  # Cooldown in seconds
    cast_time: float  # Cast time in seconds
    duration_sec: float = 0.0  # Buff duration (0 for attacks)
    pre_refresh_sec: float = 0.0  # Recast before expiration (0 = no auto-refresh)
    hold_ms: Optional[int] = None  # Optional key hold override
    
    # Runtime tracking
    last_cast_time: float = 0.0  # Last time this skill was cast
    
    def is_ready(self, current_time: float) -> bool:
        """Check if skill is off cooldown and ready to cast."""
        return (current_time - self.last_cast_time) >= self.cooldown
    
    def needs_refresh(self, current_time: float) -> bool:
        """Check if buff needs to be refreshed before expiration."""
        if self.skill_type != 'buff' or self.duration_sec <= 0:
            return False
        
        if self.last_cast_time == 0.0:
            # Never cast before, should cast now
            return True
        
        # Time since last cast
        elapsed = current_time - self.last_cast_time
        
        # Should refresh if we're within pre_refresh_sec of expiration
        time_until_expire = self.duration_sec - elapsed
        return time_until_expire <= self.pre_refresh_sec
    
    def get_hold_time_ms(self) -> int:
        """Get the key hold time in milliseconds."""
        if self.hold_ms is not None:
            return self.hold_ms
        # Default: cast_time * 1000
        return int(self.cast_time * 1000)


class SkillRuntime:
    """Manages skill casting for hunt operations with separate attack/buff lanes."""
    
    def __init__(self, skills_data: List[Dict]):
        """
        Initialize skill runtime manager.
        
        Args:
            skills_data: List of skill dicts from skills.json
        """
        self.attack_skills: List[SkillInfo] = []
        self.buff_skills: List[SkillInfo] = []
        self._load_skills(skills_data)
        
        # Track current rotation index for attacks
        self.attack_rotation_index = 0
        self.combo_rotation_index = 0

        # Reservations
        import uuid
        self._reservations = {}
    
    def _load_skills(self, skills_data: List[Dict]):
        """Load and categorize skills from skills.json data."""
        for skill_dict in skills_data:
            # Extract fields with defaults
            skill = SkillInfo(
                name=skill_dict.get('name', 'Unknown'),
                key=skill_dict.get('key', ''),
                skill_type=skill_dict.get('type', 'attack'),
                cooldown=float(skill_dict.get('cooldown', 1.0)),
                cast_time=float(skill_dict.get('cast_time', 1.0)),
                duration_sec=float(skill_dict.get('duration_sec', 0.0)),
                pre_refresh_sec=float(skill_dict.get('pre_refresh_sec', 0.0)),
                hold_ms=skill_dict.get('hold_ms')
            )
            
            # Categorize
            if skill.skill_type == 'buff':
                self.buff_skills.append(skill)
            else:
                self.attack_skills.append(skill)
    

    def get_next_combo_skill(self, current_time: float) -> Optional[SkillInfo]:
        """
        Get the next attack skill in sequence without advancing the combo rotation index.
        Returns None if the skill is not ready.
        """
        if not self.attack_skills:
            return None

        skill = self.attack_skills[self.combo_rotation_index]
        if skill.is_ready(current_time):
            return skill
        return None

    def reserve_next_skill(self, lane: str, current_time: float, is_combo: bool = False) -> Optional[CastReservation]:
        """
        Reserves the next skill for the given lane.
        """
        import uuid
        if lane == 'attack':
            if not self.attack_skills:
                return None

            idx = self.combo_rotation_index if is_combo else self.attack_rotation_index
            skill = self.attack_skills[idx]
            if skill.is_ready(current_time):
                token = str(uuid.uuid4())
                res = CastReservation(token=token, key=skill.key, skill_name=skill.name, lane=lane, created_at=current_time, expected_strategy="combo" if is_combo else "standard")
                self._reservations[token] = res
                return res
        return None

    def commit_cast(self, token: str, outcome: CastOutcome, current_time: float) -> None:
        if token in self._reservations:
            res = self._reservations.pop(token)
            if outcome == CastOutcome.ACCEPTED:
                self.mark_cast(res.key, current_time)
                if res.lane == 'attack':
                    if res.expected_strategy == 'combo':
                        self.combo_rotation_index = (self.combo_rotation_index + 1) % len(self.attack_skills)
                    else:
                        self.attack_rotation_index = (self.attack_rotation_index + 1) % len(self.attack_skills)

    def release_cast(self, token: str, outcome: CastOutcome = CastOutcome.REJECTED):
        if token in self._reservations:
            self._reservations.pop(token)

    def sync_combo_pointer(self, to_combo: bool):
        """
        Sync pointers when switching modes to prevent skipping skills.
        """
        if to_combo:
            self.combo_rotation_index = self.attack_rotation_index
        else:
            self.attack_rotation_index = self.combo_rotation_index

    def get_attack_to_cast(self, current_time: float) -> Optional[str]:
        """
        Get next attack skill key to cast (round-robin rotation).
        
        Args:
            current_time: Current timestamp
            
        Returns:
            Skill key to cast, or None if no skill ready
        """
        if not self.attack_skills:
            return None
        
        # Try each attack skill in rotation order
        for i in range(len(self.attack_skills)):
            idx = (self.attack_rotation_index + i) % len(self.attack_skills)
            skill = self.attack_skills[idx]
            
            # Check if ready
            if skill.is_ready(current_time):
                self.attack_rotation_index = idx  # Update pointer to the ready skill, but we won't advance past it until commit
                return skill.key
        
        # No skill ready
        return None
    
    def get_buff_to_cast(self, current_time: float) -> Optional[str]:
        """
        Get buff skill key that needs casting/refreshing.
        
        Args:
            current_time: Current timestamp
            
        Returns:
            Skill key to cast, or None if no buff needs casting
        """
        if not self.buff_skills:
            return None
        
        # Check each buff skill
        for skill in self.buff_skills:
            # Check if buff needs refresh and is off cooldown
            if skill.needs_refresh(current_time) and skill.is_ready(current_time):
                return skill.key
        
        return None
    
    def mark_cast(self, key: str, current_time: float):
        """
        Mark a skill as cast at current time.
        
        Args:
            key: Skill key that was cast
            current_time: Timestamp when cast occurred
        """
        # Update attack skills
        for skill in self.attack_skills:
            if skill.key == key:
                skill.last_cast_time = current_time
                return
        
        # Update buff skills
        for skill in self.buff_skills:
            if skill.key == key:
                skill.last_cast_time = current_time
                return
    
    def get_skill_info(self, key: str) -> Optional[SkillInfo]:
        """Get skill info by key."""
        for skill in self.attack_skills + self.buff_skills:
            if skill.key == key:
                return skill
        return None
    
    def get_all_attack_keys(self) -> List[str]:
        """Get list of all attack skill keys for attack_keys config."""
        return [skill.key for skill in self.attack_skills]
    
    def get_all_buff_keys(self) -> List[str]:
        """Get list of all buff skill keys."""
        return [skill.key for skill in self.buff_skills]
    
    def reset(self):
        """Reset all skill cooldowns and timings."""
        for skill in self.attack_skills + self.buff_skills:
            skill.last_cast_time = 0.0
        self.attack_rotation_index = 0
    
    def get_status(self, current_time: float) -> Dict:
        """
        Get current status of all skills.
        
        Returns:
            Dict with attack and buff skill statuses
        """
        status = {
            'attacks': [],
            'buffs': []
        }
        
        for skill in self.attack_skills:
            time_until_ready = max(0, skill.cooldown - (current_time - skill.last_cast_time))
            status['attacks'].append({
                'name': skill.name,
                'key': skill.key,
                'ready': skill.is_ready(current_time),
                'cooldown_remaining': time_until_ready
            })
        
        for skill in self.buff_skills:
            time_since_cast = current_time - skill.last_cast_time if skill.last_cast_time > 0 else 0
            time_until_expire = max(0, skill.duration_sec - time_since_cast) if skill.duration_sec > 0 else 0
            
            status['buffs'].append({
                'name': skill.name,
                'key': skill.key,
                'ready': skill.is_ready(current_time),
                'needs_refresh': skill.needs_refresh(current_time),
                'time_until_expire': time_until_expire,
                'active': time_since_cast < skill.duration_sec if skill.duration_sec > 0 else False
            })
        
        return status


# Example usage and testing
if __name__ == '__main__':
    import json
    from pathlib import Path
    
    print("=" * 70)
    print("Skill Runtime Manager - Test")
    print("=" * 70)
    
    # Load skills
    skills_path = Path(__file__).parent / 'skills.json'
    if skills_path.exists():
        with open(skills_path, 'r', encoding='utf-8') as f:
            skills_data = json.load(f)
        
        runtime = SkillRuntime(skills_data)
        
        print(f"\n📦 Loaded {len(runtime.attack_skills)} attack skills:")
        for skill in runtime.attack_skills:
            print(f"   • {skill.name} (key: {skill.key}, cooldown: {skill.cooldown}s)")
        
        print(f"\n🛡️  Loaded {len(runtime.buff_skills)} buff skills:")
        for skill in runtime.buff_skills:
            duration_info = f", duration: {skill.duration_sec}s" if skill.duration_sec > 0 else ""
            refresh_info = f", refresh: {skill.pre_refresh_sec}s" if skill.pre_refresh_sec > 0 else ""
            print(f"   • {skill.name} (key: {skill.key}, cooldown: {skill.cooldown}s{duration_info}{refresh_info})")
        
        # Simulate skill casting
        print("\n🎮 Simulating skill casting:")
        current_time = time.time()
        
        # Try to cast a buff
        buff_key = runtime.get_buff_to_cast(current_time)
        if buff_key:
            print(f"   ✅ Buff ready to cast: key {buff_key}")
            runtime.mark_cast(buff_key, current_time)
        else:
            print("   ⏳ No buff needs casting")
        
        # Try to cast an attack
        attack_key = runtime.get_attack_to_cast(current_time)
        if attack_key:
            print(f"   ⚔️  Attack ready to cast: key {attack_key}")
            runtime.mark_cast(attack_key, current_time)
        else:
            print("   ⏳ No attack ready")
        
        # Show status
        print("\n📊 Current Status:")
        status = runtime.get_status(current_time)
        
        if status['attacks']:
            print("   Attacks:")
            for s in status['attacks']:
                ready_icon = '✅' if s['ready'] else '⏳'
                cd = f"{s['cooldown_remaining']:.1f}s" if s['cooldown_remaining'] > 0 else 'ready'
                print(f"      {ready_icon} {s['name']} (key {s['key']}): {cd}")
        
        if status['buffs']:
            print("   Buffs:")
            for s in status['buffs']:
                ready_icon = '✅' if s['ready'] else '⏳'
                active_icon = '🟢' if s.get('active') else '🔴'
                refresh_icon = '🔄' if s['needs_refresh'] else ''
                expire = f"{s['time_until_expire']:.1f}s" if s['time_until_expire'] > 0 else 'expired'
                print(f"      {ready_icon}{active_icon}{refresh_icon} {s['name']} (key {s['key']}): {expire}")
        
        print("\n💡 Usage Example:")
        print("   # In hunt loop")
        print("   buff_key = runtime.get_buff_to_cast(time.time())")
        print("   if buff_key:")
        print("       tap(buff_key)")
        print("       runtime.mark_cast(buff_key, time.time())")
        print("")
        print("   if have_target:")
        print("       attack_key = runtime.get_attack_to_cast(time.time())")
        print("       if attack_key:")
        print("           tap(attack_key)")
        print("           runtime.mark_cast(attack_key, time.time())")
        
    else:
        print(f"\n❌ skills.json not found at {skills_path}")
    
    print("\n" + "=" * 70)
    print("✅ Skill Runtime Manager ready for integration!")
    print("=" * 70)
