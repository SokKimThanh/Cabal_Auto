from typing import Optional, Dict, Any
import json
from pathlib import Path

MONSTERS_PATH = Path(__file__).parent.parent.parent / "data" / "monsters.json"
MONSTERS_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_monster_library():
    """Load monster configurations from the library file."""
    if MONSTERS_PATH.exists():
        try:
            with open(MONSTERS_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error decoding monsters.json: {e}")
            return {}
        except Exception as e:
            print(f"Error loading monsters: {e}")
            return {}
    return {}


def save_monster_library(monsters):
    """Save monster configurations to the library file."""
    try:
        with open(MONSTERS_PATH, "w", encoding="utf-8") as f:
            json.dump(monsters, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving monsters: {e}")
        return False


def calculate_monster_estimate(monster: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Given a monster config dict, calculate its estimated clear time and required DPS based on:
    - Base HP
    - Base Defense (reduces incoming damage)
    - Level (affects dodge/miss rate slightly)
    - If empty or missing stats, return default minimal fallback.

    Returns a dict:
    {
        "estimated_time_sec": float,
        "required_dps": float,
        "effective_hp": float,
        "details": str
    }
    """
    if not monster:
        return {
            "estimated_time_sec": 0.0,
            "required_dps": 0.0,
            "effective_hp": 0.0,
            "base_hp": 0,
            "defense": 0,
            "level": 0
        }

    # Get stats with defaults (Sprint 21 Phase 3 format)
    stats = monster.get("stats", {})
    # Support both flat stats structure and nested 'stats' structure
    base_hp = stats.get("hp", monster.get("hp", 100))
    base_def = stats.get("defense", monster.get("defense", 10))
    level = stats.get("level", monster.get("level", 1))

    # Check if empty/default
    if base_hp == 0 and base_def == 0 and level == 0:
        return None

    # 1. Effective HP Calculation
    # Defense reduces physical/magic damage. Simple formula:
    # Damage Multiplier = 100 / (100 + Defense)
    # Effective HP = Base HP / Damage Multiplier
    # So EHP = Base HP * (100 + Defense) / 100
    defense_multiplier = (100 + base_def) / 100.0
    effective_hp = base_hp * defense_multiplier

    # 2. Level Penalty
    # Assume 1% more effective HP per level above 1 (representing higher evasion/resistances)
    level_penalty = max(0, (level - 1) * 0.01)
    final_ehp = effective_hp * (1 + level_penalty)

    # 3. Estimated Time & DPS (Based on an assumed average mid-game character)
    # Let's assume an average character outputs 500 DPS
    # This is a baseline for relative comparison between monsters
    baseline_dps = 500.0

    # Calculate time
    estimated_time = final_ehp / baseline_dps

    # Add a minimum time (animation overhead, movement)
    minimum_overhead = 1.5
    final_time = estimated_time + minimum_overhead

    # Required DPS to kill within 5 seconds (fast clear benchmark)
    benchmark_time = 5.0
    required_dps = (
        final_ehp / (benchmark_time - minimum_overhead)
        if benchmark_time > minimum_overhead
        else final_ehp
    )

    return {
        "estimated_time_sec": round(final_time, 1),
        "required_dps": round(required_dps, 0),
        "effective_hp": round(final_ehp, 0),
        "base_hp": base_hp,
        "defense": base_def,
        "level": level,
    }


DEFAULT_MONSTER_SCHEMA = {
    "id": "0",
    "name": "Unknown Target",
    "level": "N/A",
    "hp": 10000,
    "defense": 0,
    "image_path": None,
    "is_placeholder": True,
}


def get_target_monster_info(name_or_id: str):
    """
    SINGLE SOURCE OF TRUTH for Phase 1 & 2 target info.
    Implements a safe 2-tier fallback to resolve monster metadata.
    """
    from database import get_monster_by_id_api, find_monster_by_name_api

    result = None
    try:
        if name_or_id.isdigit():
            result = get_monster_by_id_api(name_or_id)
        if not result:
            result = find_monster_by_name_api(name_or_id)

        if result:
            return {
                "id": str(result.get("id", "0")),
                "name": result.get("name") or name_or_id,
                "level": result.get("level", "N/A"),
                "hp": result.get("hp") or 10000,
                "defense": result.get("defense") or 0,
                "image_path": result.get("image_path"),
                "is_placeholder": False,
            }

    except Exception as e:
        print(f"Error resolving monster from DB: {e}")

    # Tier 2: Fallback to JSON library
    try:
        json_data = load_monster_library()
        if isinstance(json_data, dict):
            # JSON format is a dict of ID -> monster data or list
            # We'll try to find it simply
            for m_id, m_data in json_data.items():
                if str(m_id) == str(name_or_id) or m_data.get("name") == name_or_id:
                    return {
                        "id": str(m_data.get("id", "0")),
                        "name": m_data.get("name") or name_or_id,
                        "level": m_data.get("level", "N/A"),
                        "hp": m_data.get("hp") or 10000,
                        "defense": m_data.get("defense") or 0,
                        "image_path": m_data.get("image_path"),
                        "is_placeholder": False,
                    }
    except Exception as e:
        print(f"Error resolving monster from JSON fallback: {e}")

    # Tier 3: Fallback schema
    fallback = DEFAULT_MONSTER_SCHEMA.copy()
    fallback["name"] = name_or_id
    return fallback
