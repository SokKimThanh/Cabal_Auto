# -*- coding: utf-8 -*-
"""
Project Restructure Utility (Dry-run by default)

Usage (PowerShell):
  # Show plan only (no changes)
  python scripts/restructure_project.py

  # Apply changes (move files + rewrite imports)
  python scripts/restructure_project.py --apply

  # Custom dry-run (explicit)
  python scripts/restructure_project.py --dry-run

Notes:
- Creates necessary folders automatically when applying
- Writes a JSON backup mapping for rollback in scripts/restructure_backups/
- Rewrites common import statements based on a predefined map
- Safe to run multiple times; it will skip already-moved files

Roll back options:
- Preferred: use git to discard changes (git restore / git reset --hard)
- Manual: use the generated backup JSON to move files back
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

# Files to move -> new relative locations
MOVE_MAP: Dict[str, str] = {
    # Top-level UI entries
    "app_gui.py": "ui/app_gui.py",
    "setup_wizard.py": "ui/setup_wizard.py",

    # UI helpers
    "lib/library_manager.py": "lib/ui/library_manager.py",
    "lib/icon_helper.py": "lib/ui/icon_helper.py",
    "lib/capture_helper.py": "lib/ui/capture_helper.py",
    "lib/tooltip.py": "lib/ui/tooltip.py",

    # i18n
    "lib/translations.py": "lib/i18n/translations.py",

    # System/integration
    "lib/win_input.py": "lib/system/win_input.py",
    "lib/hunt_logger.py": "lib/system/hunt_logger.py",

    # Vision / recognition
    "lib/template_matcher.py": "lib/vision/template_matcher.py",

    # Features: skills & timing
    "lib/skill_runtime.py": "lib/features/skills/runtime.py",
    "lib/skill_migrator.py": "lib/features/skills/migrator.py",
    "lib/timing_calculator.py": "lib/features/timing/calculator.py",
}

# Import replacements (exact substring replacements)
IMPORT_REPLACE_MAP: List[Tuple[str, str]] = [
    ("from lib.template_matcher import", "from lib.vision.template_matcher import"),
    ("import lib.template_matcher", "import lib.vision.template_matcher"),

    ("from lib.skill_runtime import", "from lib.features.skills.runtime import"),
    ("from lib.skill_migrator import", "from lib.features.skills.migrator import"),
    ("from lib.timing_calculator import", "from lib.features.timing.calculator import"),

    ("from lib.library_manager import", "from lib.ui.library_manager import"),
    ("from lib.icon_helper import", "from lib.ui.icon_helper import"),
    ("from lib.capture_helper import", "from lib.ui.capture_helper import"),
    ("from lib.tooltip import", "from lib.ui.tooltip import"),

    ("from lib.translations import", "from lib.i18n.translations import"),

    ("from lib.win_input import", "from lib.system.win_input import"),
    ("from lib.hunt_logger import", "from lib.system.hunt_logger import"),
]

PY_GLOB = "**/*.py"

@dataclass
class PlanEntry:
    src: Path
    dst: Path
    exists: bool
    will_move: bool


def build_plan() -> List[PlanEntry]:
    plan: List[PlanEntry] = []
    for src_rel, dst_rel in MOVE_MAP.items():
        src = ROOT / src_rel
        dst = ROOT / dst_rel
        plan.append(PlanEntry(src=src, dst=dst, exists=src.exists(), will_move=(src.exists() and src.resolve() != dst.resolve())))
    return plan


def scan_import_impact() -> Dict[str, List[Path]]:
    impact: Dict[str, List[Path]] = {}
    for before, _ in IMPORT_REPLACE_MAP:
        impact[before] = []

    for path in ROOT.glob(PY_GLOB):
        if path.is_dir():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for before, _ in IMPORT_REPLACE_MAP:
            if before in text:
                impact[before].append(path.relative_to(ROOT))
    return impact


def apply_moves(plan: List[PlanEntry]) -> List[Tuple[Path, Path]]:
    moved: List[Tuple[Path, Path]] = []
    for entry in plan:
        if not entry.exists:
            continue
        if entry.src.resolve() == entry.dst.resolve():
            continue
        entry.dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(entry.src), str(entry.dst))
        moved.append((entry.src, entry.dst))
    return moved


def apply_import_rewrites() -> List[Path]:
    modified: List[Path] = []
    for path in ROOT.glob(PY_GLOB):
        if path.is_dir():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        new_text = text
        for before, after in IMPORT_REPLACE_MAP:
            if before in new_text:
                new_text = new_text.replace(before, after)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            modified.append(path.relative_to(ROOT))
    return modified


def write_backup(moved: List[Tuple[Path, Path]], modified_imports: List[Path]) -> Path:
    backup_dir = ROOT / "scripts" / "restructure_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"backup_{ts}.json"

    payload = {
        "moved": [{"src": str(src.relative_to(ROOT)), "dst": str(dst.relative_to(ROOT))} for src, dst in moved],
        "modified_imports": [str(p) for p in modified_imports],
        "root": str(ROOT),
        "timestamp": ts,
    }
    backup_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return backup_file


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Project restructure utility")
    parser.add_argument("--apply", action="store_true", help="Apply changes (move files + rewrite imports)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no changes). Overrides --apply if both given.")
    args = parser.parse_args(argv)

    dry_run = not args.apply or args.dry_run

    print("Root:", ROOT)

    plan = build_plan()
    import_impact = scan_import_impact()

    print("\n=== Move Plan ===")
    for p in plan:
        status = "MISSING" if not p.exists else ("OK" if p.will_move else "SKIP")
        print(f"- {p.src.relative_to(ROOT)} -> {p.dst.relative_to(ROOT)} [{status}]")

    print("\n=== Import Impact (where replacements will occur) ===")
    for before, files in import_impact.items():
        if files:
            print(f"- '{before}' in {len(files)} files")
            for f in files[:10]:
                print(f"  · {f}")
            if len(files) > 10:
                print(f"  · ... (+{len(files)-10} more)")

    if dry_run:
        print("\nDry-run mode: no changes were made.")
        print("Use --apply to perform the moves and import rewrites.")
        return 0

    moved = apply_moves(plan)
    modified_imports = apply_import_rewrites()
    backup_path = write_backup(moved, modified_imports)

    print("\nAPPLIED!")
    print(f"- Files moved: {len(moved)}")
    for src, dst in moved:
        print(f"  · {src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")
    print(f"- Files with imports rewritten: {len(modified_imports)}")
    print(f"- Backup mapping saved to: {backup_path}")
    print("\nRollback options:")
    print("- Use git to restore (preferred): git restore .  OR  git reset --hard")
    print(f"- Manual: see backup file for original -> new paths: {backup_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
