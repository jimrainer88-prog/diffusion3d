"""Split a novel chapter into scene files: <outdir>/<stem>_sceneN.txt"""
import argparse
import json
from pathlib import Path

import requests

OLLAMA = "http://localhost:11434/api/generate"

SPLIT = """Below are the numbered paragraphs of a novel chapter.
Identify where each new SCENE begins — a change of place, time, or who is present.
Return ONLY JSON: {{"starts": [0, 7, 15]}}
- The first value must be 0.
- Aim for about {n} scenes.
- Use only paragraph numbers that appear below.

{numbered}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chapter")
    ap.add_argument("--model", default="qwen3:8b")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--outdir", default="data/prompts")
    args = ap.parse_args()

    paras = [p.strip() for p in Path(args.chapter).read_text().split("\n\n") if p.strip()]
    numbered = "\n".join(f"[{i}] {p}" for i, p in enumerate(paras))

    r = requests.post(OLLAMA, json={"model": args.model, "stream": False, "think": False,
                                    "format": "json", "options": {"seed": 0},
                                    "prompt": SPLIT.format(n=args.n, numbered=numbered)},
                      timeout=900)
    r.raise_for_status()
    starts = sorted({i for i in json.loads(r.json()["response"]).get("starts", [])
                     if isinstance(i, int) and 0 <= i < len(paras)})
    if not starts or starts[0] != 0:
        starts = [0] + starts

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(args.chapter).stem
    bounds = starts + [len(paras)]
    for n, (a, b) in enumerate(zip(bounds, bounds[1:]), 1):
        f = out / f"{stem}_scene{n}.txt"
        f.write_text("\n\n".join(paras[a:b]))
        print(f"{f}  ({b - a} paragraphs, {len(' '.join(paras[a:b]).split())} words)")


if __name__ == "__main__":
    main()
