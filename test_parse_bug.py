import re

section = """
            featuredSkillSections: [{
                id: "battle-mode-2",
                title: "Battle Mode 2",
                skillSlugs: ["twin-gunner", "twin-gunner-attack-1", "fatal-shot"],
            }, {
                id: "battle-mode-3",
                title: "Battle Mode 3",
                skillSlugs: ["launcher-punisher", "launcher-attack-a", "launcher-attack-b", "launcher-specialty-level-1", "launcher-specialty-level-2", "launcher-specialty-level-3"],
            }, {
                id: "buffs",
                title: "Buffs & Utility",
                skillSlugs: ["sharp-instinct", "sprit-walk", "art-of-sniping", "quick-move", "sharpness", "vital-force", "curse-remove", "regeneration", "greater-heal", "mass-heal", "vital-recovery", "curse-of-wither"],
            }],
            comboSection: {
                id: "combos",
                title: "Combos",
                summary: "Normal-skill combo play is mostly outdated in PvE. Between battle-mode windows, use the fastest normal skills for a single target and the widest skills for packs.",
                scenarios: [{
                    id: "single-target-opener",
                    title: "Single-Target Opener",
                    description: "Force Kick is very fast and has long range, but its cooldown is too long for a normal loop. Use it as an opener, gap closer, or control tool.",
                    skillSlugs: ["force-kick"]
                }]
            },
            synergyTable: Y.S["force-archer"]
        }
"""
featured_start = section.find('featuredSkillSections:')
if featured_start != -1:
    # Find the next key at indentation level 12 (or similar) that signifies a new block
    # In JS object, it might be comboSection: or synergyTable:
    # Let's just look for lines starting with exactly 12 spaces followed by a word and colon
    next_block = re.search(r'\n {12}\w+:', section[featured_start+20:])
    end_idx = featured_start + 20 + next_block.start() if next_block else len(section)
    featured_content = section[featured_start:end_idx]
    print(featured_content)
