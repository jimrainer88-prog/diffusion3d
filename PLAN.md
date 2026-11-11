# diffusion3d — Puppy photos to 3D models

## Goal
Turn 2D photos of puppies into textured 3D models (GLB).

Pipeline: `photo -> background removal -> image-to-3D -> GLB -> mesh check`

## Where things run
| Phase | Machine | Model | Why |
|---|---|---|---|
| 1. Local | Ubuntu box, RTX 3060 12 GB | TripoSR (MIT) | Fits in 12 GB, fast |
| 2. Cloud | GPU with 24 GB+ (L4 / A10 / 4090 / A100) on RunPod or Modal | TRELLIS.2 (MIT) | Better shape + textures |
| Editing | Mac | — | Code editing only, no GPU work |

Before running models on the 3060: `sudo systemctl stop ollama` (frees GPU memory).

## Versions
- Python **3.11**
- PyTorch 2.x with **CUDA 12.4** (both phases)
- TripoSR and TRELLIS.2 are installed by cloning their official GitHub repos into `third_party/` (they are not pip packages). Always follow their README for install and inference APIs.

## Project structure
```
diffusion3d/
├── PLAN.md                 this file
├── QWEN.md                 rules for the coding agent
├── README.md               how to use the project
├── .gitignore              data/, third_party/, .venv/, *.glb, weights, .idea/
├── requirements.txt        shared deps: torch, rembg, pillow, numpy, trimesh, requests, pyyaml
├── setup.sh                python3.11 venv + pip install + git clone TripoSR into third_party/
├── configs/
│   └── config.yaml         image size, paths, cloud endpoint URL
├── utils/
│   ├── __init__.py
│   ├── image_utils.py      load / crop / center on white square
│   └── mesh_utils.py       trimesh checks: vertices, faces, watertight, size
├── local/
│   ├── __init__.py
│   ├── background_removal.py   rembg wrapper
│   ├── triposr_pipeline.py     calls official TripoSR code, returns a mesh
│   └── main_local.py           CLI: data/input -> data/processed -> data/output
├── cloud/
│   ├── Dockerfile          CUDA 12.4 + TRELLIS.2 + FastAPI
│   ├── server.py           runs ON the cloud GPU: POST /generate (image in, GLB out)
│   ├── client.py           runs on YOUR machine: sends data/processed/*.png, saves GLBs
│   └── README.md           deploy steps for RunPod / Modal, cost notes
├── data/                   gitignored (keep .gitkeep files)
│   ├── input/              your puppy photos
│   ├── processed/          background removed, 1024x1024
│   └── output/             .glb files
├── third_party/            gitignored, cloned model repos
└── tests/
    ├── test_image_utils.py
    └── test_mesh_utils.py
```

## Steps — one per agent session, /clear in between
Don't start a step until the previous one passes its "Done" check.

1. **Skeleton**: create folders, empty `__init__.py` files, `.gitkeep` in data/ subfolders, `.gitignore`, short `README.md`.
   *Done:* `tree -a -I .git` matches the structure; `git status` doesn't show data/ or third_party/ contents.
2. **Setup**: `requirements.txt` and `setup.sh` (creates `.venv` with python3.11, installs PyTorch for CUDA 12.4 and requirements, clones TripoSR into third_party/ and installs its requirements).
   *Done:* on the Ubuntu box `bash setup.sh` finishes, and `.venv/bin/python -c "import torch; print(torch.cuda.is_available())"` prints `True`.
3. **Image prep**: `utils/image_utils.py` + `local/background_removal.py`, and a `main_local.py --step preprocess` mode.
   *Done:* every photo in data/input/ has a clean, centered 1024x1024 PNG in data/processed/.
4. **Local 3D**: `local/triposr_pipeline.py` + `main_local.py --step generate`.
   *Done:* at least one GLB in data/output/ opens in Blender or an online GLB viewer.
5. **Mesh check + tests**: `utils/mesh_utils.py`, `main_local.py --step check`, and the two test files (pytest).
   *Done:* check prints stats for every GLB; `pytest` passes.
6. **Cloud server**: `cloud/Dockerfile`, `cloud/server.py`, `cloud/README.md`.
   *Done:* image builds; on a 24 GB+ GPU, `curl -F image=@test.png http://HOST:8000/generate -o out.glb` returns a GLB.
7. **Cloud client**: `cloud/client.py` reads the endpoint from `configs/config.yaml` or env var `D3D_ENDPOINT`.
   *Done:* the same photos produce GLBs from the cloud; compare them with the Phase 1 results.

## Photo guidelines
- One puppy per photo, whole body visible, plain background, good light.
- 3/4 side view works best. The back side is invented by the model, so always inspect it.
- Fluffy fur comes out smooth ("clay-like") with every current model.

## Licenses
- TripoSR: MIT. TRELLIS.2: MIT (check bundled third-party components).
- Hunyuan3D-2.1 is an alternative, but its license excludes the EU, UK and South Korea.
- Never commit model weights, data/ contents or third_party/.

## Not now (maybe later)
Multiple background-removal backends, batch parallelism, benchmarks, open3d.
