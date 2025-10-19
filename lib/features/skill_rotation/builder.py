"""
Skill Rotation Builder
Tính toán chính xác timing giữa các skill với cooldown và cast time
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SkillTiming:
    """Timing information for a single skill press"""
    skill_name: str
    key: str
    skill_type: str  # 'attack' or 'buff'
    cast_time: float  # seconds
    cooldown: float  # seconds
    press_duration_ms: int  # milliseconds to hold key
    
    # Calculated timing in rotation
    start_time: float = 0.0  # When to press this skill
    cast_finish_time: float = 0.0  # When cast animation finishes
    cooldown_ready_time: float = 0.0  # When skill is ready again
    wait_after_cast: float = 0.0  # Extra wait time after cast


@dataclass
class SkillRotation:
    """Complete skill rotation with timing"""
    skills: List[SkillTiming]
    total_cycle_time: float  # Total time for one complete rotation
    skills_per_cycle: int
    rhythm_description: str  # Human-readable timeline
    
    # For hunt_config.json
    attack_interval: float  # Average time between attacks
    attack_press_ms: int  # Average press duration
    rotation_cycle_ms: int  # Total cycle in milliseconds


def calculate_press_duration(cast_time: float) -> int:
    """
    Calculate how long to hold key based on cast time
    
    Args:
        cast_time: Skill cast time in seconds
        
    Returns:
        Press duration in milliseconds
    """
    # 10% of cast time, between 50-200ms
    duration_ms = int(cast_time * 1000 * 0.1)
    return max(50, min(200, duration_ms))


def calculate_rotation_timing(skills: List[dict]) -> SkillRotation:
    """
    Calculate precise timing for skill rotation
    
    Args:
        skills: List of skill dicts with 'name', 'key', 'type', 'cooldown', 'cast_time'
        
    Returns:
        SkillRotation with complete timing analysis
    """
    if not skills:
        raise ValueError("Rotation must have at least one skill")
    
    skill_timings: List[SkillTiming] = []
    current_time = 0.0
    
    # Track when each skill was last used (for cooldown tracking)
    skill_cooldowns: dict = {}
    
    # First pass: Calculate basic timings
    for i, skill in enumerate(skills):
        skill_name = skill.get('name', f'Skill {i+1}')
        key = skill.get('key', '1')
        skill_type = skill.get('type', 'attack')
        cast_time = float(skill.get('cast_time', 1.0))
        cooldown = float(skill.get('cooldown', 1.5))
        
        # Calculate press duration
        press_ms = calculate_press_duration(cast_time)
        
        # Check if skill is on cooldown
        if skill_name in skill_cooldowns:
            cooldown_ready = skill_cooldowns[skill_name]
            if current_time < cooldown_ready:
                # Need to wait for cooldown
                wait_time = cooldown_ready - current_time
                current_time = cooldown_ready
        
        # Create timing entry
        timing = SkillTiming(
            skill_name=skill_name,
            key=key,
            skill_type=skill_type,
            cast_time=cast_time,
            cooldown=cooldown,
            press_duration_ms=press_ms,
            start_time=current_time,
            cast_finish_time=current_time + cast_time,
            cooldown_ready_time=current_time + cooldown,
            wait_after_cast=0.0  # Will calculate below
        )
        
        skill_timings.append(timing)
        
        # Update cooldown tracker
        skill_cooldowns[skill_name] = current_time + cooldown
        
        # Move to next skill start time (after cast finishes)
        current_time += cast_time
        
        # Add small buffer between skills (100ms for human-like timing)
        current_time += 0.1
    
    # Calculate wait times between skills
    for i in range(len(skill_timings) - 1):
        current_skill = skill_timings[i]
        next_skill = skill_timings[i + 1]
        current_skill.wait_after_cast = next_skill.start_time - current_skill.cast_finish_time
    
    # Last skill waits until rotation restarts
    if len(skill_timings) > 0:
        last_skill = skill_timings[-1]
        # Wait for last skill's cooldown OR until all skills are ready
        max_cooldown_ready = max(s.cooldown_ready_time for s in skill_timings)
        rotation_end = max(last_skill.cast_finish_time, max_cooldown_ready)
        last_skill.wait_after_cast = rotation_end - last_skill.cast_finish_time
        total_cycle_time = rotation_end
    else:
        total_cycle_time = 0.0
    
    # Generate rhythm description
    rhythm_lines = ["🎵 Skill Rotation Timeline:"]
    rhythm_lines.append(f"{'─'*70}")
    
    for i, timing in enumerate(skill_timings, 1):
        rhythm_lines.append(
            f"{i}. [{timing.key}] {timing.skill_name} ({timing.skill_type})"
        )
        rhythm_lines.append(f"   ⏱️  Start: {timing.start_time:.2f}s")
        rhythm_lines.append(f"   🎯 Press key for {timing.press_duration_ms}ms")
        rhythm_lines.append(f"   ⏳ Cast time: {timing.cast_time:.2f}s")
        rhythm_lines.append(f"   ✅ Cast finish: {timing.cast_finish_time:.2f}s")
        rhythm_lines.append(f"   🔄 Cooldown ready: {timing.cooldown_ready_time:.2f}s")
        if timing.wait_after_cast > 0:
            rhythm_lines.append(f"   ⏸️  Wait: {timing.wait_after_cast:.2f}s")
        rhythm_lines.append("")
    
    rhythm_lines.append(f"🔁 Rotation restarts at: {total_cycle_time:.2f}s")
    rhythm_lines.append(f"{'─'*70}")
    
    rhythm_description = "\n".join(rhythm_lines)
    
    # Calculate averages for hunt_config
    attack_skills = [s for s in skill_timings if s.skill_type == 'attack']
    if attack_skills:
        avg_attack_interval = total_cycle_time / len(attack_skills)
        avg_press_ms = sum(s.press_duration_ms for s in attack_skills) // len(attack_skills)
    else:
        avg_attack_interval = total_cycle_time / len(skill_timings)
        avg_press_ms = sum(s.press_duration_ms for s in skill_timings) // len(skill_timings)
    
    return SkillRotation(
        skills=skill_timings,
        total_cycle_time=total_cycle_time,
        skills_per_cycle=len(skill_timings),
        rhythm_description=rhythm_description,
        attack_interval=round(avg_attack_interval, 2),
        attack_press_ms=avg_press_ms,
        rotation_cycle_ms=int(total_cycle_time * 1000)
    )


def generate_rotation_preview(rotation: SkillRotation) -> str:
    """
    Generate simple Vietnamese preview of rotation
    
    Args:
        rotation: SkillRotation object
        
    Returns:
        Vietnamese description for display
    """
    lines = ["📋 CHU KỲ CHIÊU THỨC:"]
    lines.append(f"{'─'*60}")
    lines.append(f"⏱️  Thời gian 1 vòng: {rotation.total_cycle_time:.2f} giây")
    lines.append(f"🎮 Số chiêu: {rotation.skills_per_cycle} chiêu")
    lines.append(f"⚡ Tốc độ đánh: {rotation.attack_interval:.2f} giây/chiêu")
    lines.append(f"🔘 Giữ phím: {rotation.attack_press_ms} mili-giây")
    lines.append("")
    lines.append("🎵 NHỊP ĐIỆU THỰC HIỆN:")
    lines.append(f"{'─'*60}")
    
    for i, skill in enumerate(rotation.skills, 1):
        lines.append(f"{i}. Giây thứ {skill.start_time:.2f}:")
        lines.append(f"   → Bấm phím [{skill.key}] {skill.skill_name}")
        lines.append(f"   → Giữ {skill.press_duration_ms} mili-giây")
        lines.append(f"   → Đợi {skill.cast_time:.2f}s (đang cast)")
        if skill.wait_after_cast > 0:
            lines.append(f"   → Đợi thêm {skill.wait_after_cast:.2f}s")
        lines.append("")
    
    lines.append(f"🔁 Sau {rotation.total_cycle_time:.2f}s → Lặp lại từ đầu")
    lines.append(f"{'─'*60}")
    
    return "\n".join(lines)


def generate_execution_preview(rotation: SkillRotation) -> str:
    """
    Generate execution preview (what auto will do)
    
    Args:
        rotation: SkillRotation object
        
    Returns:
        Vietnamese description of execution
    """
    lines = ["🤖 AUTO SẼ THỰC HIỆN NHƯ SAU:"]
    lines.append(f"{'='*60}")
    lines.append("")
    lines.append("📂 Lưu vào: lib/data/hunt_config.json")
    lines.append("")
    lines.append("🔧 Các số đã lưu:")
    lines.append(f"  • Chu kỳ tổng: {rotation.total_cycle_time:.2f} giây")
    lines.append(f"  • Số chiêu: {rotation.skills_per_cycle} chiêu")
    lines.append(f"  • Giữ phím trung bình: {rotation.attack_press_ms} mili-giây")
    lines.append(f"  • Khoảng cách chiêu: {rotation.attack_interval:.2f} giây")
    lines.append("")
    lines.append(f"{'─'*60}")
    lines.append("⚡ QUÁ TRÌNH THỰC THI:")
    lines.append(f"{'─'*60}")
    lines.append("")
    
    for i, skill in enumerate(rotation.skills, 1):
        lines.append(f"BƯỚC {i}: Giây thứ {skill.start_time:.2f}")
        lines.append(f"  1. Bấm phím [{skill.key}] - {skill.skill_name}")
        lines.append(f"  2. Giữ phím {skill.press_duration_ms} mili-giây")
        lines.append(f"  3. Thả phím")
        lines.append(f"  4. Đợi {skill.cast_time:.2f}s (animation đang chạy)")
        if skill.wait_after_cast > 0:
            lines.append(f"  5. Đợi thêm {skill.wait_after_cast:.2f}s (cooldown)")
        lines.append("")
    
    lines.append(f"BƯỚC {len(rotation.skills) + 1}: Lặp lại")
    lines.append(f"  → Quay về BƯỚC 1")
    lines.append(f"  → Cứ thế lặp đi lặp lại mãi mãi")
    lines.append("")
    lines.append(f"{'='*60}")
    lines.append("✅ XÁC NHẬN: AUTO SẼ NHẤN ĐÚNG THỨ TỰ NÀY!")
    lines.append(f"{'='*60}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test với example skills
    test_skills = [
        {
            'name': 'Dark Explosion',
            'key': '1',
            'type': 'attack',
            'cooldown': 1.9,
            'cast_time': 1.7
        },
        {
            'name': 'Regeneration',
            'key': '4',
            'type': 'buff',
            'cooldown': 2.2,
            'cast_time': 1.0
        },
        {
            'name': 'Bone Javelin',
            'key': '2',
            'type': 'attack',
            'cooldown': 2.4,
            'cast_time': 1.5
        }
    ]
    
    rotation = calculate_rotation_timing(test_skills)
    
    print(rotation.rhythm_description)
    print("\n" + "="*70 + "\n")
    print(generate_rotation_preview(rotation))
    print("\n" + "="*70 + "\n")
    print(generate_execution_preview(rotation))
