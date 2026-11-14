"""Send data/processed/*.png to the TRELLIS.2 endpoint; save data/output/<name>_trellis.glb."""
import argparse
import os
import sys
import time
from pathlib import Path

import requests
from utils.config import config


def main():
    ap = argparse.ArgumentParser(description="TRELLIS.2 cloud client")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--only", help="process just this file name (e.g. puppy4.png)")
    ap.add_argument("--force", action="store_true", help="overwrite existing outputs")
    args = ap.parse_args()

    url = os.environ.get("D3D_ENDPOINT") or config.get("endpoint_url")
    if not url or "localhost" in url:
        sys.exit("Set D3D_ENDPOINT or endpoint_url in configs/config.yaml")
    headers = {}
    if os.environ.get("MODAL_KEY"):
        headers = {"Modal-Key": os.environ["MODAL_KEY"], "Modal-Secret": os.environ["MODAL_SECRET"]}

    src = Path(config["processed_dir"]); dst = Path(config["output_dir"])
    dst.mkdir(parents=True, exist_ok=True)
    files = sorted(src.glob("*.png"))
    if args.only:
        files = [f for f in files if f.name == args.only]

    for f in files:
        suffix = "" if args.seed == 0 else f"_s{args.seed}"
        out = dst / f"{f.stem}_trellis{suffix}.glb"
        if out.exists() and not args.force:
            print(f"skip {out.name} (exists)"); continue
        print(f"-> {f.name} (seed {args.seed}) ...", end=" ", flush=True)
        t = time.time()
        with open(f, "rb") as fh:
            r = requests.post(url, files={"image": fh}, data={"seed": str(args.seed)},
                              headers=headers, timeout=1200)  # follows Modal's 303 redirect
        if r.status_code != 200 or len(r.content) < 1000:
            print(f"FAILED HTTP {r.status_code}: {r.text[:200]}"); continue
        out.write_bytes(r.content)
        print(f"{out.name} {len(r.content)/1e6:.1f} MB in {time.time()-t:.0f}s")


if __name__ == "__main__":
    main()
