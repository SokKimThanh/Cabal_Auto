import logging
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
from lib.features.hunt.window_selection_service import WindowSelectionService
from lib.vision.template_matcher import locate_template

class TargetLocatorService:
    @staticmethod
    def locate_target(cfg: Dict[str, Any], current_window_bounds: Optional[list] = None) -> Tuple[Optional[Tuple[int, int, int, int]], Optional[Dict[str, Any]]]:
        bounds = WindowSelectionService.resolve_bounds(cfg, current_window_bounds)
        if not bounds:
            return None, None

        templates = []
        raw_templates = cfg.get("templates") or []
        if isinstance(raw_templates, list):
            templates.extend(t for t in raw_templates if isinstance(t, dict))
        template_path = str(cfg.get("template_path", "") or "").strip()
        if template_path and not templates:
            templates.append(
                {
                    "path": template_path,
                    "name": Path(template_path).stem,
                    "threshold": float(cfg.get("template_threshold", 0.8)),
                    "monster_name": cfg.get("monster_selected_name", ""),
                }
            )

        best_box = None
        best_info = None
        best_score = -1.0
        for template in templates:
            path = str(template.get("path", "") or "").strip()
            if not path:
                continue
            threshold = float(
                template.get("threshold", cfg.get("template_threshold", 0.8))
            )
            box, confidence = locate_template(
                path, region=tuple(bounds), threshold=threshold
            )
            if box is None or confidence < best_score:
                continue
            best_box = box
            best_score = confidence
            best_info = {
                "path": path,
                "name": template.get("name") or Path(path).stem,
                "threshold": threshold,
                "confidence": confidence,
                "monster_name": template.get("monster_name")
                or cfg.get("monster_selected_name", ""),
            }
        return best_box, best_info
