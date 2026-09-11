import urllib.request
import json
import re
import os

titles = [
    "Warrior", "Blader", "Wizard", "Force_Archer", "Force_Blader", "Force_Shielder", "Gladiator", "Force_Gunner", "Dark_Mage"
]

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
        print(f"Error fetching {title}: {e}")
    return ""

def extract_stats(text):
    # Regex to find STR, INT, DEX values in infobox
    str_val = re.search(r'\|\s*(?:str|STR|Strength)\s*=\s*(\d+)', text)
    int_val = re.search(r'\|\s*(?:int|INT|Intelligence)\s*=\s*(\d+)', text)
    dex_val = re.search(r'\|\s*(?:dex|DEX|Dexterity)\s*=\s*(\d+)', text)

    return {
        "str_base": int(str_val.group(1)) if str_val else 0,
        "int_base": int(int_val.group(1)) if int_val else 0,
        "dex_base": int(dex_val.group(1)) if dex_val else 0,
    }

classes_data = []

# Map class names to DB paths
icon_map = {
    "Warrior": "warrior.png",
    "Blader": "blader.png",
    "Wizard": "wizard.png",
    "Force Archer": "force_archer.png",
    "Force Blader": "force_blader.png",
    "Force Shielder": "force_shielder.png",
    "Gladiator": "gladiator.png",
    "Force Gunner": "force_gunner.png",
    "Dark Mage": "dark_mage.png"
}

description_map = {
    "Warrior": 'The best melee fighter who possesses powerful fencing skills.',
    "Blader": 'The deadly blade dancer, the fastest dual sword user.',
    "Wizard": 'The ultimate destroyer, the Ruler of the Force.',
    "Force Archer": 'The sniper that fire deadly force shots that cuts through the wind.',
    "Force Blader": 'Swordsman whose blade flares with the force.',
    "Force Shielder": 'The faithful warrior that uses the force to shield others.',
    "Gladiator": 'Gladiator uses the Rage system to deal heavy damage.',
    "Force Gunner": 'Sniper who shoots force energy.',
    "Dark Mage": 'A mage that commands darkness.'
}

class_id_map = {
    "Warrior": 1,
    "Blader": 2,
    "Wizard": 3,
    "Force Archer": 4,
    "Force Blader": 5,
    "Force Shielder": 6,
    "Gladiator": 7,
    "Force Gunner": 8,
    "Dark Mage": 9
}

for title in titles:
    text = fetch_wiki_text(title)
    stats = extract_stats(text)
    class_name = title.replace("_", " ")

    class_info = {
        "class_id": class_id_map.get(class_name, len(classes_data)+1),
        "name": class_name,
        "description": description_map.get(class_name, f"{class_name} class in Cabal Online."),
        "icon_path": icon_map.get(class_name, f"{title.lower()}.png"),
        "str_base": stats["str_base"],
        "int_base": stats["int_base"],
        "dex_base": stats["dex_base"]
    }
    classes_data.append(class_info)

os.makedirs("lib/data/crawding", exist_ok=True)
with open("lib/data/crawding/classes.json", "w") as f:
    json.dump(classes_data, f, indent=4)

print("Scraped class data saved.")
