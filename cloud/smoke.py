import modal

app = modal.App("d3d-smoke")
image = modal.Image.debian_slim(python_version="3.12").pip_install("torch")

@app.function(gpu="A100", image=image, timeout=300)
def gpu_info():
    import torch
    p = torch.cuda.get_device_properties(0)
    return f"{p.name}, {p.total_memory / 1e9:.0f} GB, torch {torch.__version__}"

@app.local_entrypoint()
def main():
    print(gpu_info.remote())
