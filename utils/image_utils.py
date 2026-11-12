"""
Image utilities for preprocessing photos
"""
import os
from PIL import Image
import numpy as np


def load_and_center_image(image_path, target_size):
    """
    Load an image and center it on a white square background.
    
    Args:
        image_path (str): Path to input image
        target_size (int): Target size for square image
        
    Returns:
        PIL.Image: Centered image with white background
    """
    # Open the image
    img = Image.open(image_path)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Get original dimensions
    orig_width, orig_height = img.size
    
    # Calculate the size for the square crop (smaller dimension)
    min_dim = min(orig_width, orig_height)
    
    # Calculate crop box to center the image
    left = (orig_width - min_dim) // 2
    top = (orig_height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    
    # Crop to square
    img_square = img.crop((left, top, right, bottom))
    
    # Resize to target size
    img_resized = img_square.resize((target_size, target_size), Image.LANCZOS)
    
    return img_resized


def save_image_with_padding(image, output_path, target_size):
    """
    Save image with white padding to make it square.
    
    Args:
        image (PIL.Image): Input image
        output_path (str): Output file path
        target_size (int): Target square size
    """
    # Create a white background
    white_bg = Image.new('RGB', (target_size, target_size), (255, 255, 255))
    
    # Calculate position to center the image
    img_width, img_height = image.size
    x_offset = (target_size - img_width) // 2
    y_offset = (target_size - img_height) // 2
    
    # Paste the image onto the white background
    white_bg.paste(image, (x_offset, y_offset))
    
    # Save the result
    white_bg.save(output_path)