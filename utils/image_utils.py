"""
Image utilities for preprocessing photos
"""
import os
from PIL import Image
import numpy as np


def load_and_center_image(image_path, target_size, margin=0.1):
    """
    Load an RGBA cut-out, crop to the subject (non-transparent pixels),
    and center it on a transparent square canvas of target_size.
    """
    img = Image.open(image_path).convert("RGBA")
    bbox = img.getchannel("A").getbbox()  # bounding box of the dog
    if bbox:
        img = img.crop(bbox)
    w, h = img.size
    side = int(max(w, h) * (1 + 2 * margin))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - w) // 2, (side - h) // 2), img)
    return canvas.resize((target_size, target_size), Image.LANCZOS)


def save_image_with_padding(image, output_path, target_size):
    """
    Save image with transparent padding to make it square.

    Args:
        image (PIL.Image): Input image
        output_path (str): Output file path
        target_size (int): Target square size
    """
    # Create a transparent background (RGBA mode)
    transparent_bg = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))

    # Calculate position to center the image
    img_width, img_height = image.size
    x_offset = (target_size - img_width) // 2
    y_offset = (target_size - img_height) // 2

    # Paste the image onto the transparent background
    transparent_bg.paste(image, (x_offset, y_offset))

    # Save the result as PNG to maintain transparency
    transparent_bg.save(output_path, 'PNG')