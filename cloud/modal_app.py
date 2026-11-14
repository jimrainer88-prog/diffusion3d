"""TRELLIS.2 image-to-3D on Modal: POST /generate (image file) -> GLB."""
import io
import os
import tempfile

import modal
from fastapi import File, Form, Response, UploadFile

app = modal.App("d3d-trellis2")
hf_cache = modal.Volume.from_name("d3d-hf-cache", create_if_missing=True)
REPO = "/opt/trellis2"
SETUP_FLAGS = ["--basic", "--flash-attn", "--nvdiffrast", "--nvdiffrec",
               "--cumesh", "--flexgemm", "--o-voxel"]

image = (
    modal.Image.from_registry("nvidia/cuda:12.4.1-devel-ubuntu22.04", add_python="3.11")
    .apt_install("git", "build-essential", "ninja-build", "libgl1", "libglib2.0-0", "libegl1")
    .pip_install("torch==2.6.0", "torchvision==0.21.0",
                 index_url="https://download.pytorch.org/whl/cu124")
    .pip_install("fastapi[standard]", "python-multipart", "pillow")
    .env({
        "TORCH_CUDA_ARCH_LIST": "8.0",          # A100; no GPU during build
        "CUDA_HOME": "/usr/local/cuda",
        "MAX_JOBS": "8",
        "HF_HOME": "/cache/hf",
        "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        "OPENCV_IO_ENABLE_OPENEXR": "1",
    })
    .run_commands(f"git clone -b main --recursive https://github.com/microsoft/TRELLIS.2.git {REPO}")
)
# One cached build step per setup.sh flag (no --new-env: no conda here)
for flag in SETUP_FLAGS:
    if flag == "--flexgemm":  # use gcc from here on
        image = image.env({"CC": "gcc", "CXX": "g++", "CUDAHOSTCXX": "g++",
                           "LDSHARED": "gcc -pthread -shared"})
    image = image.run_commands(f"cd {REPO} && bash -c '. ./setup.sh {flag}'", gpu="A100")
# Rebuild with gcc: the first attempts ran before the gcc fix and failed silently
for flag in ["--nvdiffrast", "--nvdiffrec"]:
    image = image.run_commands(f"cd {REPO} && bash -c '. ./setup.sh {flag}'", gpu="A100")
# Fail the build loudly if any compiled extension is missing
image = image.run_commands(
    "python -c 'import nvdiffrast.torch, cumesh, flex_gemm, o_voxel; print(\"extensions OK\")'",
    gpu="A100",
)
# TRELLIS.2 expects the older DINOv3 layout (model.layer) in transformers
image = image.pip_install("transformers==4.57.1")
image = image.run_commands("python -c 'import transformers; print(\"transformers\", transformers.__version__)'")
# flash-attn: the setup.sh build failed silently (pre-gcc); use the prebuilt wheel
image = image.run_commands("pip install flash-attn==2.7.4.post1 --no-build-isolation", gpu="A100")
image = image.run_commands("python -c 'import flash_attn; print(\"flash_attn\", flash_attn.__version__)'", gpu="A100")
image = image.env({"PYTHONPATH": REPO})


@app.cls(gpu="A100", max_containers=1, memory=32768, image=image, volumes={"/cache": hf_cache}, secrets=[modal.Secret.from_name("huggingface")],
         scaledown_window=120, timeout=900)
class Trellis:
    @modal.enter()
    def load(self):
        from trellis2.pipelines import Trellis2ImageTo3DPipeline
        self.pipe = Trellis2ImageTo3DPipeline.from_pretrained("microsoft/TRELLIS.2-4B")
        self.pipe.cuda()
        hf_cache.commit()  # keep downloaded weights for next cold start

    @modal.fastapi_endpoint(method="POST", requires_proxy_auth=True)
    def generate(self, image: UploadFile = File(...), seed: int = Form(0)):
        import o_voxel
        from PIL import Image

        img = Image.open(io.BytesIO(image.file.read()))
        img = self.pipe.preprocess_image(img)
        outputs = self.pipe.run(
            img,
            seed=seed,
            preprocess_image=False,
            sparse_structure_sampler_params={
                "steps": 12, "guidance_strength": 7.5, "guidance_rescale": 0.7, "rescale_t": 5.0},
            shape_slat_sampler_params={
                "steps": 12, "guidance_strength": 7.5, "guidance_rescale": 0.5, "rescale_t": 3.0},
            tex_slat_sampler_params={
                "steps": 12, "guidance_strength": 1.0, "guidance_rescale": 0.0, "rescale_t": 3.0},
            pipeline_type="1024_cascade",
        )
        mesh = outputs[0]
        mesh.simplify(16777216)  # nvdiffrast limit (from example.py)
        glb = o_voxel.postprocess.to_glb(
            vertices=mesh.vertices, faces=mesh.faces, attr_volume=mesh.attrs,
            coords=mesh.coords, attr_layout=mesh.layout, voxel_size=mesh.voxel_size,
            aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
            decimation_target=200000, texture_size=2048,
            remesh=True, remesh_band=1, remesh_project=0,
        )
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "out.glb")
            glb.export(path, extension_webp=False)
            data = open(path, "rb").read()
        return Response(content=data, media_type="model/gltf-binary")
