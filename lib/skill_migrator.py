"""
Skills Migration Helper - Migrate skills.json to new schema and copy images to project.

New schema adds:
- duration_sec: Buff uptime (0 for attack skills)
- pre_refresh_sec: When to recast buff before expiration (0 = no auto-refresh)
- hold_ms: Optional key hold time override (None = use cast_time)
- image: Relative path in assets/images/skills/ (auto-copied from absolute paths)

Usage:
    python skill_migrator.py
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Any
import re
from datetime import datetime


class SkillMigrator:
    """Migrate skills to new schema and copy images to project."""
    
    def __init__(self, skills_json_path: str = 'skills.json'):
        self.skills_json_path = Path(skills_json_path)
        self.project_images_dir = Path('assets/images/skills')
        self.project_images_dir.mkdir(parents=True, exist_ok=True)
        
        # Track copied files for cleanup
        self.copied_files = []
    
    def sanitize_filename(self, name: str) -> str:
        """Convert skill name to safe filename slug."""
        # Convert to lowercase, replace spaces with underscore
        slug = name.lower().replace(' ', '_')
        # Remove special characters, keep only alphanumeric and underscore
        slug = re.sub(r'[^a-z0-9_]', '', slug)
        return slug
    
    def copy_image_to_project(self, image_path: str, skill_name: str) -> str:
        """
        Copy skill image to project directory.
        
        Args:
            image_path: Source image path (can be absolute)
            skill_name: Skill name for filename generation
        
        Returns:
            Relative path in project (e.g., 'assets/images/skills/dark_explosion_1729123456.png')
        """
        source = Path(image_path)
        
        if not source.exists():
            print(f"⚠️  Warning: Image not found: {image_path}")
            return image_path  # Return original if file doesn't exist
        
        # Generate unique filename
        slug = self.sanitize_filename(skill_name)
        timestamp = int(datetime.now().timestamp() * 1000)  # Milliseconds
        extension = source.suffix or '.png'
        filename = f"{slug}_{timestamp}{extension}"
        
        destination = self.project_images_dir / filename
        
        # Copy file
        try:
            shutil.copy2(source, destination)
            relative_path = str(destination).replace('\\', '/')
            self.copied_files.append(relative_path)
            print(f"✅ Copied: {source.name} → {relative_path}")
            return relative_path
        except Exception as e:
            print(f"❌ Error copying {source}: {e}")
            return image_path  # Return original on error
    
    def migrate_skill(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate a single skill to new schema.
        
        Args:
            skill: Old skill dict
        
        Returns:
            New skill dict with added fields
        """
        migrated = skill.copy()
        
        # Add new fields with defaults
        if 'duration_sec' not in migrated:
            # Default: 0 for attack skills, could be set manually for buffs
            migrated['duration_sec'] = 0.0
        
        if 'pre_refresh_sec' not in migrated:
            # Default: 0 (no auto-refresh)
            migrated['pre_refresh_sec'] = 0.0
        
        if 'hold_ms' not in migrated:
            # Default: None (use cast_time * 1000)
            migrated['hold_ms'] = None
        
        # Handle image path - copy to project if absolute path
        if 'image' in migrated and migrated['image']:
            image_path = migrated['image']
            
            # Check if absolute path (Windows/Unix)
            if Path(image_path).is_absolute():
                # Copy to project
                migrated['image'] = self.copy_image_to_project(image_path, skill['name'])
            else:
                # Already relative, keep as is
                print(f"ℹ️  Keeping relative path: {image_path}")
        
        return migrated
    
    def migrate_all(self, backup: bool = True) -> List[Dict[str, Any]]:
        """
        Migrate all skills in skills.json.
        
        Args:
            backup: Create backup before migration
        
        Returns:
            List of migrated skills
        """
        if not self.skills_json_path.exists():
            print(f"❌ Error: {self.skills_json_path} not found!")
            return []
        
        # Load existing skills
        with open(self.skills_json_path, 'r', encoding='utf-8') as f:
            skills = json.load(f)
        
        print(f"\n{'='*70}")
        print(f"Skills Migration - Processing {len(skills)} skills")
        print(f"{'='*70}\n")
        
        # Backup original file
        if backup:
            backup_path = self.skills_json_path.with_suffix('.json.backup')
            shutil.copy2(self.skills_json_path, backup_path)
            print(f"📦 Backup created: {backup_path}\n")
        
        # Migrate each skill
        migrated_skills = []
        for i, skill in enumerate(skills, 1):
            print(f"[{i}/{len(skills)}] Migrating: {skill['name']}")
            migrated = self.migrate_skill(skill)
            migrated_skills.append(migrated)
            print()
        
        # Save migrated skills
        with open(self.skills_json_path, 'w', encoding='utf-8') as f:
            json.dump(migrated_skills, f, indent=2, ensure_ascii=False)
        
        print(f"{'='*70}")
        print(f"✅ Migration complete! {len(migrated_skills)} skills migrated")
        print(f"📁 Images copied: {len(self.copied_files)}")
        print(f"💾 Saved to: {self.skills_json_path}")
        print(f"{'='*70}\n")
        
        return migrated_skills
    
    def validate_schema(self, skills: List[Dict[str, Any]]) -> bool:
        """
        Validate migrated skills schema.
        
        Args:
            skills: List of skills to validate
        
        Returns:
            True if all skills have required fields
        """
        required_fields = ['name', 'key', 'type', 'cooldown', 'cast_time', 'duration_sec', 'pre_refresh_sec']
        
        print(f"\n{'='*70}")
        print("Schema Validation")
        print(f"{'='*70}\n")
        
        all_valid = True
        for skill in skills:
            missing = [field for field in required_fields if field not in skill]
            if missing:
                print(f"❌ {skill['name']}: Missing fields: {missing}")
                all_valid = False
            else:
                # Check types
                errors = []
                if not isinstance(skill['cooldown'], (int, float)):
                    errors.append('cooldown must be numeric')
                if not isinstance(skill['cast_time'], (int, float)):
                    errors.append('cast_time must be numeric')
                if not isinstance(skill['duration_sec'], (int, float)):
                    errors.append('duration_sec must be numeric')
                if not isinstance(skill['pre_refresh_sec'], (int, float)):
                    errors.append('pre_refresh_sec must be numeric')
                if skill['hold_ms'] is not None and not isinstance(skill['hold_ms'], (int, float)):
                    errors.append('hold_ms must be numeric or null')
                
                if errors:
                    print(f"❌ {skill['name']}: {', '.join(errors)}")
                    all_valid = False
                else:
                    print(f"✅ {skill['name']}: Valid")
        
        print(f"\n{'='*70}")
        if all_valid:
            print("✅ All skills validated successfully!")
        else:
            print("❌ Some skills have validation errors")
        print(f"{'='*70}\n")
        
        return all_valid
    
    def print_summary(self, skills: List[Dict[str, Any]]):
        """Print summary of migrated skills."""
        print(f"\n{'='*70}")
        print("Migration Summary")
        print(f"{'='*70}\n")
        
        # Count by type
        attack_skills = [s for s in skills if s.get('type') == 'attack']
        buff_skills = [s for s in skills if s.get('type') == 'buff']
        
        print(f"Total skills: {len(skills)}")
        print(f"  - Attack skills: {len(attack_skills)}")
        print(f"  - Buff skills: {len(buff_skills)}")
        print(f"\nImages in project: {len(self.copied_files)}")
        
        # List buff skills that might need duration setup
        buffs_need_duration = [s for s in buff_skills if s.get('duration_sec', 0) == 0]
        if buffs_need_duration:
            print(f"\n⚠️  Buff skills with duration_sec=0 (needs manual setup):")
            for skill in buffs_need_duration:
                print(f"   - {skill['name']}: Set duration_sec and pre_refresh_sec")
        
        print(f"\n{'='*70}\n")


def main():
    """Run migration."""
    migrator = SkillMigrator('skills.json')
    
    # Migrate all skills
    migrated_skills = migrator.migrate_all(backup=True)
    
    if migrated_skills:
        # Validate schema
        migrator.validate_schema(migrated_skills)
        
        # Print summary
        migrator.print_summary(migrated_skills)
        
        # Instructions
        print("📋 Next Steps:")
        print("1. Review migrated skills in skills.json")
        print("2. For buff skills, set duration_sec (buff uptime in seconds)")
        print("3. For buff skills, set pre_refresh_sec (recast before expiration)")
        print("4. Optional: Set hold_ms for skills that need specific hold times")
        print("5. Test skills in game to verify timing")


if __name__ == '__main__':
    main()
