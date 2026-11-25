"""panels.json -> data/panels/panel_N.png"""
import os

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import json
from pathlib import Path

import torch
from diffusers import AutoencoderKL, StableDiffusionXLPipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("panels_json", nargs="?", default="data/prompts/panels.json")
    ap.add_argument("--model", default="John6666/obsession-illustriousxl-v31-sdxl")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--only", type=int, help="regenerate just this panel index")
    args = ap.parse_args()

    script = json.loads(Path(args.panels_json).read_text())
    vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", dtype=torch.float16)
    pipe = StableDiffusionXLPipeline.from_pretrained(
        args.model, vae=vae, dtype=torch.float16, use_safetensors=True).to("cuda")
    if hasattr(pipe.vae, "enable_tiling"):
        pipe.vae.enable_tiling()

    out = Path("data/panels")
    out.mkdir(parents=True, exist_ok=True)
    for i, p in enumerate(script["panels"]):
        if args.only is not None and i != args.only:
            continue
        img = pipe(prompt=p["prompt"], negative_prompt=p["negative"],
                   width=1024, height=1024, num_inference_steps=args.steps,
                   guidance_scale=6.0,
                   # one fixed seed across all panels also helps the character hold
                   generator=torch.Generator("cuda").manual_seed(args.seed)).images[0]
        img.save(out / f"panel_{i}.png")
        print("saved", out / f"panel_{i}.png")
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
