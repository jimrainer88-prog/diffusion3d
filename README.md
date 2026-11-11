# diffusion3d

Turn 2D photos of puppies into textured 3D models (GLB).

Pipeline: `photo -> background removal -> image-to-3D -> GLB -> mesh check`

## Project Structure

- `local/` - Local processing (TripoSR on RTX 3060)
- `cloud/` - Cloud processing (TRELLIS.2 on RunPod/Modal)
- `utils/` - Utility functions for image and mesh processing
- `data/` - Input, processed, and output data directories
- `third_party/` - Cloned model repositories

## Setup

Run `bash setup.sh` to create a virtual environment and install dependencies.

## Usage

For local processing:
```
python local/main_local.py --step preprocess
python local/main_local.py --step generate
python local/main_local.py --step check
```

For cloud processing:
```
python cloud/client.py
```