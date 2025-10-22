"""
Sprint 14 Demo - Buff Auto-Casting Runtime

This demo shows the new intelligent skill management system with automatic
buff recasting before expiration using duration_sec and pre_refresh_sec timing.

Sprint 14 implements the final piece of the skill system: smart buff management
that eliminates manual buff recasting and optimizes skill rotation.

Features Demonstrated:
1. SkillRuntime class with separate attack/buff lanes
2. Buff auto-casting before expiration (duration_sec - elapsed <= pre_refresh_sec)
3. Round-robin attack skill rotation with cooldown awareness
4. Per-skill timing (cooldown, cast_time, hold_ms)
5. Integration with auto_hunt.py for CLI hunting
6. Backward compatibility with existing app_gui.py implementation

Architecture:
------------
SkillRuntime Class:
- attack_skills: List[SkillInfo] - Attack skills for round-robin rotation
- buff_skills: List[SkillInfo] - Buff skills for auto-refresh management
- attack_rotation_index: Track current position in attack rotation

SkillInfo Dataclass:
- name, key, skill_type: Basic identification
- cooldown, cast_time: Timing parameters
- duration_sec: Buff uptime (0 for attacks)
- pre_refresh_sec: Recast timing before expiration
- hold_ms: Optional key hold override
- last_cast_time: Runtime tracking

Buff Auto-Casting Logic:
-----------------------
Algorithm:
1. Check if buff never cast (last_cast_time == 0) → Cast immediately
2. Calculate time_until_expire = duration_sec - (current_time - last_cast_time)
3. If time_until_expire <= pre_refresh_sec → Needs refresh
4. If needs_refresh() AND is_ready() (cooldown elapsed) → Cast

Example:
- Buff: duration_sec=60s, pre_refresh_sec=5s, cooldown=2s
- Cast at t=0s → Active until t=60s
- At t=55s: time_until_expire = 60 - 55 = 5s <= pre_refresh_sec
- System automatically casts buff again at t=55s
- New buff active from t=55s to t=115s (seamless uptime)

Attack Skill Rotation:
---------------------
Algorithm:
1. Round-robin through attack_skills list
2. Check is_ready() for current skill
3. If ready → Return key, advance rotation index
4. If not ready → Try next skill in rotation
5. After full cycle with no ready skill → Return None

Example:
- Skills: [Dark Explosion (2s cd), Bone Javelin (2.4s cd), Skull Shooter (2.2s cd)]
- t=0s: Cast Dark Explosion → rotation_index=1
- t=0.5s: Cast Bone Javelin → rotation_index=2
- t=1.0s: Cast Skull Shooter → rotation_index=0
- t=1.5s: Skip Dark Explosion (on cd) → Try Bone Javelin
- Balanced rotation with cooldown awareness

Integration with auto_hunt.py:
-----------------------------
Workflow:
1. Load skills.json at startup
2. Initialize SkillRuntime(skills_data)
3. Hunt loop:
   a. Every cycle: Cast buffs (always, regardless of combat)
      - buff_key = runtime.get_buff_to_cast(now)
      - if buff_key: tap(buff_key), mark_cast(buff_key, now)
   b. When have_target: Cast attacks
      - attack_key = runtime.get_attack_to_cast(now)
      - if attack_key: tap(attack_key), mark_cast(attack_key, now)
   c. Use skill-specific hold_ms for key press duration

Benefits:
--------
✅ Zero Manual Buff Management:
   - Buffs auto-recast before expiration
   - No need to watch buff timers
   - Seamless uptime with pre_refresh_sec safety margin

✅ Optimal Attack Rotation:
   - Round-robin ensures balanced skill usage
   - Cooldown-aware skips unavailable skills
   - Automatic fallback to next ready skill

✅ Flexible Per-Skill Timing:
   - Individual cooldown tracking
   - Custom cast_time and hold_ms per skill
   - Duration-based buff management

✅ Backward Compatible:
   - Works with legacy configs missing new fields
   - Graceful fallback to attack_keys sequence
   - app_gui.py existing implementation compatible

✅ Production Ready:
   - Separate attack/buff lanes prevent conflicts
   - Thread-safe for CLI and GUI contexts
   - Comprehensive status reporting

Example skills.json with new fields:
-----------------------------------
[
  {
    "name": "Dark Explosion",
    "key": "1",
    "type": "attack",
    "cooldown": 1.9,
    "cast_time": 1.7,
    "duration_sec": 0.0,
    "pre_refresh_sec": 0.0,
    "hold_ms": null,
    "image": "assets/images/skills/dark_explosion.png"
  },
  {
    "name": "Regeneration",
    "key": "4",
    "type": "buff",
    "cooldown": 2.2,
    "cast_time": 1.0,
    "duration_sec": 60.0,    // Buff lasts 60 seconds
    "pre_refresh_sec": 5.0,  // Recast at 55 second mark
    "hold_ms": null,
    "image": "assets/images/skills/regeneration.png"
  }
]

Testing Instructions:
--------------------
1. Setup skills.json with duration_sec and pre_refresh_sec:
   - Attack skills: duration_sec=0, pre_refresh_sec=0
   - Buff skills: Set actual duration (e.g., 60s) and refresh timing (e.g., 5s)

2. Test skill_runtime.py module:
   python skill_runtime.py
   - Verify skills loaded correctly
   - Check attack/buff categorization
   - See simulation output

3. Test with auto_hunt.py:
   python auto_hunt.py
   - Start hunt, watch console output
   - Observe "[Buff] Cast <skill>" when buff needs refresh
   - See attack rotation in action
   - Verify buffs recast automatically

4. Monitor behavior:
   - Buffs should cast even without targets
   - Attacks only when have_target
   - Check hunt.log for timing details

Expected Behavior:
-----------------
✅ Buff with 60s duration, 5s pre_refresh:
   - First cast at t=0
   - Auto-recast at t=55s (before expiration)
   - Seamless buff uptime

✅ Attack rotation:
   - Skills cast in round-robin order
   - Skip skills on cooldown
   - Balanced usage across all attacks

✅ Console output:
   [Buff] Cast Regeneration
   [Match] Template: dragon_head, Confidence: 0.95
   (attack skills cast in rotation)

Sprint 14 Complete! 🎉
All 14 sprints finished - System production-ready!
"""

import sys
from pathlib import Path

print("=" * 70)
print("Sprint 14 Demo - Buff Auto-Casting Runtime")
print("=" * 70)

print("\n📋 Feature Overview:")
print("   • Intelligent skill management with separate attack/buff lanes")
print("   • Auto-recast buffs before expiration")
print("   • Round-robin attack rotation with cooldown awareness")
print("   • Per-skill timing configuration")

print("\n🎯 Key Components:")
print("   1. skill_runtime.py module (~320 lines)")
print("   2. SkillRuntime class")
print("   3. SkillInfo dataclass")
print("   4. get_buff_to_cast() - Auto-refresh logic")
print("   5. get_attack_to_cast() - Round-robin rotation")
print("   6. Integration with auto_hunt.py")

print("\n🔄 Buff Auto-Casting Algorithm:")
print("   1. Check if buff never cast → Cast immediately")
print("   2. Calculate time_until_expire = duration - elapsed")
print("   3. If time_until_expire <= pre_refresh_sec → Needs refresh")
print("   4. If needs_refresh AND is_ready (off cooldown) → Cast")
print("   ")
print("   Example:")
print("   • Buff: 60s duration, 5s pre_refresh, 2s cooldown")
print("   • Cast at t=0s → Active until t=60s")
print("   • At t=55s → Auto-recast (5s before expiration)")
print("   • Seamless buff uptime!")

print("\n⚔️  Attack Rotation Algorithm:")
print("   1. Round-robin through attack skills")
print("   2. Check is_ready() for cooldown")
print("   3. If ready → Cast, advance rotation")
print("   4. If not ready → Try next skill")
print("   5. Balanced usage across all attacks")

print("\n💡 Usage Example:")
print("   from skill_runtime import SkillRuntime")
print("   ")
print("   runtime = SkillRuntime(skills_data)")
print("   ")
print("   # In hunt loop")
print("   now = time.time()")
print("   ")
print("   # Cast buffs (always)")
print("   buff_key = runtime.get_buff_to_cast(now)")
print("   if buff_key:")
print("       tap(buff_key)")
print("       runtime.mark_cast(buff_key, now)")
print("   ")
print("   # Cast attacks (when have_target)")
print("   if have_target:")
print("       attack_key = runtime.get_attack_to_cast(now)")
print("       if attack_key:")
print("           tap(attack_key)")
print("           runtime.mark_cast(attack_key, now)")

print("\n✨ Benefits:")
print("   ✅ Zero manual buff management")
print("   ✅ Optimal attack rotation")
print("   ✅ Flexible per-skill timing")
print("   ✅ Backward compatible")
print("   ✅ Production ready")

print("\n📦 Integration:")
print("   • auto_hunt.py: Full integration with buff auto-casting")
print("   • app_gui.py: Compatible with existing implementation")
print("   • skills.json: New fields (duration_sec, pre_refresh_sec, hold_ms)")

print("\n🧪 Test Instructions:")
print("   1. Test module: python skill_runtime.py")
print("   2. Update skills.json with duration/pre_refresh values")
print("   3. Run: python auto_hunt.py")
print("   4. Observe buff auto-casting in console")
print("   5. Check hunt.log for timing details")

print("\n" + "=" * 70)
print("✅ Sprint 14 Complete - Buff Auto-Casting Runtime!")
print("=" * 70)

print("\n🎉 ALL 14 SPRINTS COMPLETE!")
print("   System is production-ready with:")
print("   • Complete monster/template management")
print("   • Screenshot capture & test recognition")
print("   • Enhanced logging (dual format)")
print("   • OpenCV integration (accurate confidence)")
print("   • Data-driven timing optimization")
print("   • Skills migration & portability")
print("   • Template matcher integration")
print("   • One-click timing application")
print("   • Intelligent buff auto-casting")
print("")
print("💬 Ready to hunt!")
