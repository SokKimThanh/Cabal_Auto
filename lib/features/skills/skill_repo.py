import json
from pathlib import Path

SKILLS_PATH = Path(__file__).parent.parent.parent / "data" / "skills.json"
SKILLS_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_skill_library():
    """Load skill configurations from the library file."""
    if SKILLS_PATH.exists():
        try:
            with open(SKILLS_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error decoding skills.json: {e}")
            return {}
        except Exception as e:
            print(f"Error loading skills: {e}")
            return {}
    return {}


def save_skill_library(skills):
    """Save skill configurations to the library file."""
    try:
        with open(SKILLS_PATH, "w", encoding="utf-8") as f:
            json.dump(skills, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving skills: {e}")
        return False


def calculate_attack_speed_from_skills(skill_names):
    """
    Calculate the effective Attack Speed (Attacks Per Second - APS)
    based on a list of skill names/IDs.
    Uses cast time and cooldown properties from the skill library.

    Args:
        skill_names (list): List of skill IDs (strings)

    Returns:
        float: Effective attacks per second (APS)
    """
    if not skill_names:
        return 0.0

    skills_lib = load_skill_library()
    if not skills_lib:
        return 0.0

    total_cast_time = 0.0
    valid_skills_count = 0

    for name in skill_names:
        skill = skills_lib.get(name)
        if skill and skill.get("type") == "attack":
            cast_time = float(skill.get("cast_time", 1.5))
            # Optional: Add animation overhead
            overhead = 0.2
            total_cast_time += cast_time + overhead
            valid_skills_count += 1

    if valid_skills_count == 0 or total_cast_time == 0:
        return 0.0

    # APS = Number of skills cast / Total time taken to cast them
    aps = valid_skills_count / total_cast_time
    return round(aps, 2)
