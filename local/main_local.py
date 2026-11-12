#!/usr/bin/env python3
"""
Main local processing script for diffusion3d
"""
import argparse
import os
import sys

# Ensure we can import our modules properly from any working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# Import our own modules - note that config is not a submodule but
# the module that will be loaded by Python when we run this script
try:
    from utils.image_utils import load_and_center_image, save_image_with_padding
    from local.background_removal import remove_background_batch
    from local.triposr_pipeline import generate_mesh_batch
    from utils.config import config
except ImportError as e:
    # Try to add additional paths if needed
    sys.path.insert(0, os.path.join(project_root, 'configs'))
    sys.path.insert(0, os.path.join(project_root, 'utils'))
    sys.path.insert(0, os.path.join(project_root, 'local'))

    from utils.image_utils import load_and_center_image, save_image_with_padding
    from local.background_removal import remove_background_batch
    from local.triposr_pipeline import generate_mesh_batch
    from utils.config import config


def main():
    parser = argparse.ArgumentParser(description="Local 3D processing pipeline")
    parser.add_argument("--step", choices=["preprocess", "generate", "check"],
                       help="Step to run: preprocess, generate, or check")

    args = parser.parse_args()

    if args.step == "preprocess":
        print("Running preprocessing step...")
        # Get paths from config
        input_dir = config['input_dir']
        processed_dir = config['processed_dir']
        target_size = config['image_size']

        # Ensure processed directory exists
        os.makedirs(processed_dir, exist_ok=True)

        # Remove background from all images in input directory
        print(f"Removing backgrounds from images in {input_dir}")
        remove_background_batch(input_dir, processed_dir)

        # Center and resize images to square
        print(f"Centering and resizing images to {target_size}x{target_size}")
        for filename in os.listdir(processed_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                input_path = os.path.join(processed_dir, filename)
                output_path = os.path.join(processed_dir, filename)  # Overwrite the processed image

                # Load and center the image
                centered_image = load_and_center_image(input_path, target_size)

                # Save with padding to make it square
                save_image_with_padding(centered_image, output_path, target_size)

        print("Preprocessing completed successfully!")
    elif args.step == "generate":
        print("Running generation step...")
        # Get paths from config
        processed_dir = config['processed_dir']
        output_dir = config['output_dir']
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate 3D meshes from processed images in the processed directory
        print(f"Generating 3D meshes from images in {processed_dir}")
        generated_meshes = generate_mesh_batch(processed_dir, output_dir)
        print(f"Generated {len(generated_meshes)} meshes successfully!")
    elif args.step == "check":
        print("Running mesh check step...")
        # TODO: Implement mesh checking

if __name__ == "__main__":
    main()