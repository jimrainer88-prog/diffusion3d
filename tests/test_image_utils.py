"""
Tests for image utilities
"""
import os
import tempfile
from PIL import Image
import numpy as np

# Add project root to path so we can import our modules
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from utils.image_utils import load_and_center_image, save_image_with_padding


def test_load_and_center_image():
    """Test loading and centering an image."""
    # Create a temporary image for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a simple test image (red square)
        test_img = Image.new('RGBA', (100, 100), (255, 0, 0, 255))
        
        # Save the test image
        test_path = os.path.join(tmpdir, "test.png")
        test_img.save(test_path)
        
        # Test loading and centering it
        result = load_and_center_image(test_path, 200)
        
        # Result should be 200x200
        assert result.size == (200, 200)
        
        # The center pixel should be red
        center_pixel = result.getpixel((100, 100))
        assert center_pixel == (255, 0, 0, 255)


def test_save_image_with_padding():
    """Test saving image with padding."""
    # Create a temporary image for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a small test image (blue square)
        test_img = Image.new('RGBA', (100, 100), (0, 0, 255, 255))
        
        # Save it with padding
        output_path = os.path.join(tmpdir, "output.png")
        save_image_with_padding(test_img, output_path, 200)
        
        # Load the saved image
        saved_img = Image.open(output_path).convert('RGBA')
        
        # Should be 200x200
        assert saved_img.size == (200, 200)
        
        # Center should have blue pixels
        center_pixel = saved_img.getpixel((100, 100))
        assert center_pixel == (0, 0, 255, 255)