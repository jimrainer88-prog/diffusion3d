"""Single photo -> depth relief mesh (GLB).

NOT a 3D scene: a flat grid displaced along Z by a monocular depth estimate, with the
photo as its texture. Looks convincing head-on and with small orbits; from the side it
is a bent sheet. For a real scene you need many photos and photogrammetry.
"""
import argparse
from pathlib import Path

import numpy as np
import torch
import trimesh
from PIL import Image
from transformers import pipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--out")
    ap.add_argument("--grid", type=int, default=320, help="mesh resolution on the long edge")
    ap.add_argument("--relief", type=float, default=0.25, help="depth as a fraction of width")
    ap.add_argument("--cut", type=float, default=0.12,
                    help="drop faces spanning more than this fraction of the relief")
    ap.add_argument("--model", default="depth-anything/Depth-Anything-V2-Small-hf")
    args = ap.parse_args()

    img = Image.open(args.image).convert("RGB")
    w, h = img.size
    dev = 0 if torch.cuda.is_available() else -1
    depth = pipeline("depth-estimation", model=args.model, device=dev)(img)["depth"]

    gw, gh = (args.grid, max(2, round(args.grid * h / w))) if w >= h \
        else (max(2, round(args.grid * w / h)), args.grid)

    d = np.asarray(depth.resize((gw, gh)), dtype=np.float32)
    d = (d - d.min()) / (np.ptp(d) + 1e-8)        # 0..1, larger = nearer

    aspect = h / w
    gx, gy = np.meshgrid(np.linspace(-0.5, 0.5, gw),
                         np.linspace(0.5 * aspect, -0.5 * aspect, gh))
    verts = np.stack([gx, gy, d * args.relief], axis=-1).reshape(-1, 3)

    uu, vv = np.meshgrid(np.linspace(0, 1, gw), np.linspace(0, 1, gh))
    uv = np.stack([uu, vv], axis=-1).reshape(-1, 2)

    idx = np.arange(gw * gh).reshape(gh, gw)
    a, b = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel()
    c, e = idx[1:, 1:].ravel(), idx[1:, :-1].ravel()
    # counter-clockwise seen from +Z, so the normals face the viewer
    faces = np.concatenate([np.stack([a, c, b], -1), np.stack([a, e, c], -1)])

    # drop triangles that span a big depth jump — they'd otherwise smear
    # foreground across background instead of letting it occlude
    z = verts[:, 2]
    span = np.ptp(z[faces], axis=1)
    faces = faces[span < args.cut * args.relief]

    mat = trimesh.visual.material.PBRMaterial(baseColorTexture=img,
                                              metallicFactor=0.0, roughnessFactor=0.9)
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=False,
                           visual=trimesh.visual.TextureVisuals(uv=uv, material=mat))

    out = args.out or str(Path("data/output") / (Path(args.image).stem + "_relief.glb"))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    mesh.export(out)
    print(f"saved {out}  ({len(verts)} verts, {len(faces)} faces)")


if __name__ == "__main__":
    main()
