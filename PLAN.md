# Project Plan: 2D Puppy Photo to 3D Model Converter

## Project Overview
This project converts 2D puppy photos into 3D models (GLB format) using a two-phase pipeline:
1. Local phase (RTX 3060 with TripoSR) 
2. Cloud phase (TRELLIS.2 on 24GB+ GPU via Docker)

## Project Structure
```
puppy-3d-converter/
├── README.md
├── PLAN.md
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── local/
│   ├── __init__.py
│   ├── background_removal.py
│   ├── triposr_pipeline.py
│   └── main_local.py
├── cloud/
│   ├── __init__.py
│   ├── trellis_pipeline.py
│   └── main_cloud.py
├── utils/
│   ├── __init__.py
│   ├── image_utils.py
│   └── model_utils.py
├── data/
│   ├── input/
│   └── output/
├── tests/
│   ├── __init__.py
│   ├── test_background_removal.py
│   └── test_pipeline.py
└── configs/
    ├── local_config.yaml
    └── cloud_config.yaml
```

## Phase 1: Local Processing (RTX 3060)

### Dependencies
- Python 3.8+
- PyTorch 2.0+
- torchvision
- rembg
- trimesh
- open3d
- numpy
- opencv-python

### Key Components
1. **Background Removal** (`local/background_removal.py`)
   - Uses rembg to remove background from input images
   - Supports multiple background removal algorithms
   - Maintains image quality and transparency
   
2. **TripoSR Pipeline** (`local/triposr_pipeline.py`)
   - Implementation of TripoSR's 3D reconstruction pipeline
   - Uses local GPU resources for processing
   - Converts processed images into 3D meshes
   
3. **Local Main Module** (`local/main_local.py`)
   - Orchestrates the local processing pipeline
   - Manages input/output handling
   - Handles error cases and logging

## Phase 2: Cloud Processing (TRELLIS.2)

### Dependencies
- Docker
- CUDA toolkit 11.8+
- PyTorch 2.0+ optimized for cloud GPU
- NVIDIA container toolkit
- RunPod/Modal deployment configuration

### Key Components
1. **TRELLIS.2 Pipeline** (`cloud/trellis_pipeline.py`)
   - Optimized version of the processing pipeline for cloud GPUs
   - Utilizes larger 24GB+ VRAM for higher resolution models
   - Implements parallel processing where possible
   
2. **Cloud Main Module** (`cloud/main_cloud.py`)
   - Orchestrates cloud processing pipeline
   - Manages Docker container deployment
   - Handles communication with cloud GPU services

## Pipeline Steps

### Phase 1 (Local)
1. Input image loading from `data/input/`
2. Background removal using rembg
3. Preprocessing for 3D conversion
4. TripoSR-based 3D reconstruction 
5. Output GLB files to `data/output/`

### Phase 2 (Cloud)
1. Input image loading from `data/input/`
2. Cloud-ready preprocessing 
3. TRELLIS.2 optimization processing
4. High-resolution 3D model generation
5. Output GLB files to `data/output/`

## Docker Configuration

### Dockerfile
- Uses PyTorch CUDA base image
- Installs required dependencies
- Sets up environment variables for GPU access
- Exposes necessary ports
- Defines entrypoint and command

### Deployment Targets
- RunPod configuration
- Modal deployment setup
- Cloud GPU resource management

## Testing Approach
1. Unit tests for background removal
2. Integration tests for pipeline modules
3. Performance benchmarks between local and cloud phases
4. Quality assurance checks for 3D model outputs

## Configuration Files
- `configs/local_config.yaml`: Local GPU settings, memory limits
- `configs/cloud_config.yaml`: Cloud resource limits, environment variables

## Input/Output Handling
- Input: 2D images (JPG, PNG) from `data/input/`
- Output: GLB files in `data/output/`
- Intermediate files for processing validation

## Resource Considerations
### Local Phase (RTX 3060 - 12GB)
- Memory management for 3D reconstruction
- Image size optimization 
- Computation time limitations

### Cloud Phase (TRELLIS.2 - 24GB+)
- Utilizes higher VRAM for detailed models
- Parallel processing capabilities
- Cost optimization considerations