"""
Basic smoke tests for sams.py. Run with: python -m pytest tests/
Expand this file as each part of the pipeline is implemented for real -
the report needs "testing results" as a deliverable, so keep this updated.
"""

import os
import sys
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import sams  # noqa: E402


def test_is_signed_detects_ink():
    blank = np.zeros((50, 50), dtype=np.uint8)
    signed = np.zeros((50, 50), dtype=np.uint8)
    signed[10:40, 10:40] = 255  # simulate ink

    assert sams.is_signed(blank) is False
    assert sams.is_signed(signed) is True


def test_parse_roster_reads_all_students(tmp_path):
    xml_content = """<?xml version="1.0"?>
    <students>
        <student><row>1</row><index>001</index><title>Mr</title><name>Test Student</name></student>
    </students>"""
    xml_file = tmp_path / "info.xml"
    xml_file.write_text(xml_content)

    students = sams.parse_roster(str(xml_file))
    assert len(students) == 1
    assert students[0]["index"] == "001"
    assert students[0]["name"] == "Test Student"


def test_detect_signature_cells_returns_correct_row_count():
    dummy_binary = np.zeros((300, 300), dtype=np.uint8)
    cells = sams.detect_signature_cells(dummy_binary, num_rows=6)
    assert len(cells) == 6


def test_load_image_validation(tmp_path):
    # Test empty path
    with pytest.raises(ValueError, match="Image path cannot be empty"):
        sams.load_image("")

    # Test non-existent path
    with pytest.raises(FileNotFoundError, match="does not exist"):
        sams.load_image("non_existent_file.png")

    # Test directory path
    dir_path = tmp_path / "dummy_dir"
    dir_path.mkdir()
    with pytest.raises(IsADirectoryError, match="not a file"):
        sams.load_image(str(dir_path))

    # Test unsupported extension
    bad_ext_file = tmp_path / "test.txt"
    bad_ext_file.write_text("dummy text")
    with pytest.raises(ValueError, match="Unsupported image file format"):
        sams.load_image(str(bad_ext_file))

    # Test valid image load
    img_path = tmp_path / "valid_image.png"
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    import cv2
    cv2.imwrite(str(img_path), dummy_img)
    loaded = sams.load_image(str(img_path))
    assert loaded is not None
    assert loaded.shape == (100, 100, 3)


def test_to_greyscale_validation():
    # Test None input
    with pytest.raises(ValueError, match="Input image cannot be None"):
        sams.to_greyscale(None)

    # Test invalid type
    with pytest.raises(TypeError, match="must be a numpy ndarray"):
        sams.to_greyscale("not an image")

    # Test already greyscale image
    grey_img = np.zeros((100, 100), dtype=np.uint8)
    res = sams.to_greyscale(grey_img)
    assert res.shape == (100, 100)

    # Test color image (BGR)
    color_img = np.zeros((100, 100, 3), dtype=np.uint8)
    color_img[10, 10] = [10, 20, 30]
    res_color = sams.to_greyscale(color_img)
    assert len(res_color.shape) == 2
    assert res_color.shape == (100, 100)

    # Test BGRA image
    bgra_img = np.zeros((100, 100, 4), dtype=np.uint8)
    res_bgra = sams.to_greyscale(bgra_img)
    assert res_bgra.shape == (100, 100)

    # Test invalid shape image (e.g. 1D or 4D array)
    invalid_img = np.zeros((100,), dtype=np.uint8)
    with pytest.raises(ValueError, match="Invalid image array shape"):
        sams.to_greyscale(invalid_img)

