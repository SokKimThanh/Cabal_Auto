"""
Template Loader Service - Template dataclass, caching, and loading service.
Refactored from vision_engine.py to prevent god-class architecture and keep files < 300 lines.
"""

import os
import cv2
import json
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Template:
    """Template metadata and image caches"""
    id: str
    path: str
    threshold: float = 0.7
    scales: Optional[List[float]] = None
    enabled: bool = True
    image: Optional[np.ndarray] = None  # Loaded BGR image
    thumbnail: Optional[np.ndarray] = None  # For UI preview
    image_gray: Optional[np.ndarray] = None  # Cached 1-channel grayscale image for ~3x matchTemplate speedup

    def __post_init__(self):
        if self.scales is None:
            self.scales = [1.0]  # Default: no scaling
        if self.image is not None and self.image.size > 0 and self.image_gray is None:
            if len(self.image.shape) == 3 and self.image.shape[2] in (3, 4):
                self.image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            else:
                self.image_gray = self.image

    def to_dict(self) -> Dict[str, Any]:
        """Serialize without image data"""
        return {
            'id': self.id,
            'path': self.path,
            'threshold': self.threshold,
            'scales': self.scales,
            'enabled': self.enabled
        }


class TemplateService:
    """
    Dedicated service for template loading, caching, and persistence.
    """

    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.templates_config_path = self.config_dir / "vision_templates.json"
        self.templates: Dict[str, Template] = {}
        self.load_templates_config()

    def load_templates(self, path_list: List[str]) -> Dict[str, Template]:
        """Load templates from file paths"""
        loaded = {}
        for path in path_list:
            if not os.path.exists(path):
                logger.warning(f"Template path not found: {path}")
                continue

            try:
                template_id = Path(path).stem
                image = cv2.imread(path)
                if image is None or image.size == 0:
                    logger.error(f"Failed to load image from path: {path}")
                    continue

                image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
                thumbnail = cv2.resize(image, (100, 100), interpolation=cv2.INTER_AREA)

                if template_id in self.templates:
                    template = self.templates[template_id]
                    template.image = image
                    template.image_gray = image_gray
                    template.thumbnail = thumbnail
                else:
                    template = Template(
                        id=template_id,
                        path=path,
                        threshold=0.7,
                        scales=[1.0],
                        enabled=True,
                        image=image,
                        image_gray=image_gray,
                        thumbnail=thumbnail
                    )

                loaded[template_id] = template
                self.templates[template_id] = template
                logger.info(f"Loaded template: {template_id} ({image.shape})")

            except Exception as e:
                logger.error(f"Error loading template {path}: {e}")

        return loaded

    def add_template(self, path: str, threshold: float = 0.7,
                     scales: Optional[List[float]] = None, max_scales: int = 3) -> Optional[Template]:
        """Add a single template and update persistence"""
        if scales is None:
            scales = [1.0]

        result = self.load_templates([path])
        if result:
            template_id = list(result.keys())[0]
            template = result[template_id]
            template.threshold = threshold
            template.scales = scales[:max_scales]
            self.save_templates_config()
            return template

        return None

    def remove_template(self, template_id: str) -> bool:
        """Remove a template and update persistence"""
        if template_id in self.templates:
            del self.templates[template_id]
            self.save_templates_config()
            logger.info(f"Removed template: {template_id}")
            return True
        return False

    def get_template(self, template_id: str) -> Optional[Template]:
        """Get template by ID"""
        return self.templates.get(template_id)

    def list_templates(self) -> List[Template]:
        """Get all templates"""
        return list(self.templates.values())

    def load_templates_config(self):
        """Load template metadata configuration from JSON file"""
        if not self.templates_config_path.exists():
            logger.info("No templates config found, using defaults")
            return

        try:
            with open(self.templates_config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for template_data in data.get('templates', []):
                template = Template(**template_data)
                self.templates[template.id] = template

            logger.info(f"Loaded {len(self.templates)} templates from config")
        except Exception as e:
            logger.error(f"Error loading templates config: {e}")

    def save_templates_config(self):
        """Save template metadata configuration to JSON file"""
        try:
            data = {'templates': [t.to_dict() for t in self.templates.values()]}
            with open(self.templates_config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self.templates)} templates to config")
        except Exception as e:
            logger.error(f"Error saving templates config: {e}")
