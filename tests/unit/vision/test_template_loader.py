"""
Unit tests for TemplateLoaderService and Template dataclass.
"""

import os
import cv2
import pytest
import numpy as np
from pathlib import Path
from lib.vision.template_loader import Template, TemplateService


@pytest.fixture
def template_service(tmp_path):
    return TemplateService(config_dir=tmp_path)


def test_template_post_init_grayscale_caching():
    """Test automatic grayscale conversion and post_init caching"""
    bgr_img = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
    template = Template(id="tpl1", path="dummy", image=bgr_img)

    assert template.image_gray is not None
    assert template.image_gray.shape == (50, 50)
    assert len(template.image_gray.shape) == 2

    # Test constructing Template with an empty numpy image
    empty_img = np.empty((0, 0, 3), dtype=np.uint8)
    empty_template = Template(id="empty_tpl", path="dummy", image=empty_img)
    assert empty_template.image_gray is None

    # Test constructing Template with an already 2D grayscale image
    gray_img = np.zeros((40, 40), dtype=np.uint8)
    gray_template = Template(id="gray_tpl", path="dummy", image=gray_img)
    assert gray_template.image_gray is not None
    assert gray_template.image_gray.shape == (40, 40)


def test_template_service_add_remove_list(template_service, tmp_path):
    """Test adding, listing, and removing templates via TemplateService"""
    img_path = tmp_path / "test_monster.png"
    sample_img = np.zeros((40, 40, 3), dtype=np.uint8)
    cv2.imwrite(str(img_path), sample_img)

    tpl = template_service.add_template(str(img_path), threshold=0.85)
    assert tpl is not None
    assert tpl.id == "test_monster"
    assert tpl.threshold == 0.85
    assert len(template_service.list_templates()) == 1

    assert template_service.get_template("test_monster") == tpl

    # Remove template
    assert template_service.remove_template("test_monster") is True
    assert len(template_service.list_templates()) == 0
    assert template_service.get_template("test_monster") is None


def test_template_service_load_nonexistent_path(template_service):
    """Test handling of non-existent image paths"""
    result = template_service.load_templates(["/invalid/path/nonexistent.png"])
    assert result == {}
