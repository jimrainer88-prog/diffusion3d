"""Prompt JSON -> candidate images in data/input/ (ready for the existing preprocess step)."""
import os

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import json
from pathlib import Path

import torch
from diffusers import AutoencoderKL, StableDiffusionXLPipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt_json", nargs="?", default="data/prompts/last.json")
    ap.add_argument("--model", default="John6666/obsession-illustriousxl-v31-sdxl")
    ap.add_argument("--name", default="char")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--cfg", type=float, default=6.0)
    args = ap.parse_args()

    cfgj = json.loads(Path(args.prompt_json).read_text())

    # SDXL's stock VAE is broken in fp16, so diffusers upcasts it to fp32 at decode time
    # and blows past 12 GB. This drop-in VAE is fp16-safe, so no upcast happens.
    vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", dtype=torch.float16)
    pipe = StableDiffusionXLPipeline.from_pretrained(
        args.model, vae=vae, dtype=torch.float16, use_safetensors=True
    ).to("cuda")
    if hasattr(pipe.vae, "enable_tiling"):
        pipe.vae.enable_tiling()      # spatial tiling; slicing only splits a batch

    out = Path("data/input")
    out.mkdir(parents=True, exist_ok=True)
    for i in range(args.n):
        img = pipe(
            prompt=cfgj["prompt"],
            negative_prompt=cfgj["negative"],
            width=832, height=1216,
            num_inference_steps=args.steps,
            guidance_scale=args.cfg,
            generator=torch.Generator("cuda").manual_seed(i),
        ).images[0]
        p = out / f"{args.name}{i}.png"
        img.save(p)
        print("saved", p)
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
