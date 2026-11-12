from pathlib import Path
"""
Background removal using rembg
"""
import os
from PIL import Image
import numpy as np
from rembg import remove

def remove_background(image_path, output_path):
    """
    Remove background from image using rembg and save the result.

    Args:
        image_path (str): Path to input image
        output_path (str): Path to save output image with removed background
    """
    # Open the image
    input_image = Image.open(image_path)

    # Remove background using rembg
    output_image = remove(input_image)

    # Ensure we preserve RGBA format for transparency
    if output_image.mode != 'RGBA':
        output_image = output_image.convert('RGBA')
    
    # Save the result as PNG to maintain transparency
    output_image.save(output_path, 'PNG')

def remove_background_batch(input_dir, output_dir):
    """
    Remove backgrounds from all images in a directory.

    Args:
        input_dir (str): Directory containing input images
        output_dir (str): Directory to save output images
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each image file
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".png")

            remove_background(input_path, output_path)