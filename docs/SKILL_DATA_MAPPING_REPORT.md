# Skill Data Mapping Report

This document details the relationship between the raw data files in `lib/data/` and the SQLite database schema (`cabal_bot.db`) for the skill CRUD management features.

## 1. Overview
The system splits the data into two primary paradigms:
- **Reference Catalogue (SQLite)**: Game truth data parsed from Cabal source extraction text files.
- **Runtime/User Library (JSON)**: Mutable configurations adjusted by users in the UI, decoupled from the catalogue.

## 2. Text Sources to SQLite Mapping

The tables in the SQLite database (`lib/db/schema.py`) are populated by seeding scripts located in `lib/db/services/`.

| Raw Text File | Seeding Script | Target DB Table(s) | Description |
| --- | --- | --- | --- |
| `color-skill-character-db-cabal.txt` | `seed_classes_service.py` | `classes` | Provides base classes (9 total), their class code slugs, display names, and base stats. |
| `skill-db-cabal-2.txt` | `seed_skill_sprite_service.py` | `skills` | Source for the skill catalogue (460 skills). Provides skill names, sprite coordinates (`icon_x`, `icon_y`, `icon_w`, `icon_h`), and `skill_code`. |
| `bm2-bm3-skill-db-cabal.txt` | `seed_bm3_synergies_service.py` | `synergies`, `synergy_effects` | Contains Battle Mode 3 (BM3) synergies and combat combinations. Populates synergy names, activation sequences, and stat effects. |
| (Mapping Manifest / `db5_mapping_manifest.json`) | `seed_class_skill_assignments_service.py` | `class_skill_assignments` | Resolves many-to-many canonical mappings between the 9 classes and 460 skills. |

## 3. UI and Runtime State (`skills.json`)
The file **`lib/data/skills.json`** is strictly the user's custom runtime configuration.
- It is **not** seeded into SQLite.
- It manages user-defined keys, attack types, cooldown values, cast times, durations, and UI selected image paths.
- As per `UI_DATABASE_INTEGRATION_CONTRACT.md`, the UI will read reference metadata (like icons or catalogue proper names) from SQLite, but core operational stats (like hotkey mappings and cooldowns) remain exclusively in `skills.json` to preserve custom gameplay behaviors.

## 4. Notes on Missing Data
- Initially, `synergies` and `synergy_effects` were not seeded correctly during some manual executions because the `seed_bm3_synergies_service.py` script lacked an execution block. This has been fixed, and all text files correctly propagate to their respective tables.
