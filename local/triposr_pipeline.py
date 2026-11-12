"""
TripoSR pipeline for 3D mesh generation from processed RGBA images.
"""
import os
import sys
from pathlib import Path

# Add TripoSR to path so we can import its modules
triposr_path = os.path.join(os.path.dirname(__file__), '..', 'third_party', 'triposr')
sys.path.insert(0, triposr_path)

import torch
from PIL import Image
import numpy as np
from tsr.system import TSR
from tsr.utils import remove_background, resize_foreground

_REMBG_SESSION = None
def _get_rembg_session():
    global _REMBG_SESSION
    if _REMBG_SESSION is None:
        import rembg
        _REMBG_SESSION = rembg.new_session()
    return _REMBG_SESSION


def generate_mesh_from_image(image_path, output_dir, model, device='cuda:0', mc_resolution=256):
    """
    Generate a 3D mesh from a processed RGBA image using TripoSR.

    Args:
        image_path (str): Path to input RGBA image
        output_dir (str): Directory to save the GLB mesh
        model (TSR): Pre-initialized TripoSR model
        device (str): Device to run model on ('cuda:0' or 'cpu')
        mc_resolution (int): Marching cubes resolution for mesh extraction

    Returns:
        str: Path to generated GLB file
    """
    print(f"Processing image: {image_path}")

    # Prepare exactly like TripoSR run.py: cut out -> resize (RGBA) -> gray background
    image = Image.open(image_path)
    image = remove_background(image, _get_rembg_session())  # RGBA cut-out (skipped if already RGBA)
    image = resize_foreground(image, 0.85)                    # needs RGBA
    arr = np.array(image).astype(np.float32) / 255.0
    arr = arr[:, :, :3] * arr[:, :, 3:4] + (1 - arr[:, :, 3:4]) * 0.5
    image = Image.fromarray((arr * 255.0).astype(np.uint8))

    # Run model on the prepared image
    with torch.no_grad():
        scene_codes = model([image], device=device)

    # Extract mesh using marching cubes
    meshes = model.extract_mesh(scene_codes, not True, resolution=mc_resolution)

    # Create output file name based on input image name
    input_name = Path(image_path).stem
    output_path = os.path.join(output_dir, f"{input_name}.glb")

    # Export the mesh with vertex colors (not textures)
    print(f"Exporting mesh to: {output_path}")
    meshes[0].export(output_path)

    return output_path

def generate_mesh_batch(input_dir, output_dir, device='cuda:0', mc_resolution=256):
    """
    Generate 3D meshes from all processed RGBA images in a directory.

    Args:
        input_dir (str): Directory containing processed RGBA images
        output_dir (str): Directory to save generated GLB meshes
        device (str): Device to run model on ('cuda:0' or 'cpu')
        mc_resolution (int): Marching cubes resolution for mesh extraction

    Returns:
        list: List of paths to generated GLB files
    """
    # Initialize model once at the beginning
    if not torch.cuda.is_available():
        device = "cpu"

    print(f"Initializing TripoSR model on {device}")
    model = TSR.from_pretrained(
        "stabilityai/TripoSR",
        config_name="config.yaml",
        weight_name="model.ckpt",
    )
    model.renderer.set_chunk_size(8192)
    model.to(device)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    generated_meshes = []

    # Process each image file in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_dir, filename)

            try:
                mesh_path = generate_mesh_from_image(image_path, output_dir, model, device, mc_resolution)
                generated_meshes.append(mesh_path)
                print(f"Successfully generated: {mesh_path}")
            except Exception as e:
                import traceback; traceback.print_exc()
                print(f"Error processing {filename}: {str(e)}")
                continue

    return generated_meshes