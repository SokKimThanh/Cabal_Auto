import urllib.request
import json
import re
import os

class_titles = {
    1: "Warrior_skills",
    2: "Blader_skills",
    3: "Wizard_skills",
    4: "Force_Archer_skills",
    5: "Force_Blader_skills",
    6: "Force_Shielder_skills",
    7: "Gladiator_skills",
    8: "Force_Gunner_skills",
    9: "Dark_Mage_skills"
}

def fetch_wiki_text(title):
    url = f"https://cabal.fandom.com/api.php?action=query&prop=revisions&rvprop=content&titles={title}&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode("utf-8"))
        pages = data["query"]["pages"]
        for page_id in pages:
            if "revisions" in pages[page_id]:
                return pages[page_id]["revisions"][0]["*"]
    except Exception as e:
        pass
    return ""

skills_data = []
skill_id_counter = 1

for class_id, title in class_titles.items():
    text = fetch_wiki_text(title)
    if not text:
        continue

    lines = text.split('\n')
    current_type = "Attack"

    for line in lines:
        if '==Magic Attack skills==' in line or '==Magic skills==' in line:
            current_type = "Magic"
        elif '==Sword Attack skills==' in line or '==Sword skills==' in line:
            current_type = "Sword"
        elif '==Buff skills==' in line:
            current_type = "Buff"

        # Matches {{i|Skill Name}} or {{i|Skill Name|params}}
        matches = re.findall(r'\{\{i\|([^\|\}]+)', line)
        for name in matches:
            name = name.strip()
            if not any(s['name'] == name and s['class_id'] == class_id for s in skills_data):
                skills_data.append({
                    "skill_id": skill_id_counter,
                    "name": name,
                    "alias": name.lower().replace(" ", "_").replace("-", "_").replace("'", ""),
                    "icon_x": 0, "icon_y": 0, "icon_w": 32, "icon_h": 32,
                    "class_id": class_id,
                    "type": current_type
                })
                skill_id_counter += 1

os.makedirs("lib/data/crawding", exist_ok=True)
with open("lib/data/crawding/skills.json", "w") as f:
    json.dump(skills_data, f, indent=4)

print(f"Scraped {len(skills_data)} skills and saved to skills.json.")
