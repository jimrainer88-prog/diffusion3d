"""Novel prose -> character sheet (JSON) -> image prompt, via local Ollama."""
import argparse
import json
import re
import sys
from pathlib import Path

import requests

OLLAMA = "http://localhost:11434/api/generate"
BIBLE = Path("data/prompts/bible.json")

EXTRACT = """Extract ONE character's appearance from the passage.
Return ONLY JSON with these keys:
  name, subject, hair, outfit, accessories, expression

Rules:
- Every value is a COMPLETE descriptive phrase for an image generator, never a bare adjective.
    good: "long hair worn loose"          bad: "long"
    good: "red dress reaching the floor"  bad: "red"
- subject = age and gender only, e.g. "young woman".
- Describe ONLY what the passage states. Never invent a colour or feature it omits.
- Unknown -> ""

Passage:
<<<
{text}
>>>"""

MOTION = re.compile(
    r"\s*,?\s+(?:fluttering|billowing|blowing|waving|trailing|swaying|streaming|windblown|"
    r"caught in the wind|in the (?:gentle )?breeze|in the wind)\b[^,]*", re.I)

# CLIP truncates at 77 tokens, so both of these stay short
POSE = ("full body, standing, arms away from body, facing viewer, "
        "plain white background, soft even lighting, hair down, fabric hanging straight")
NEG = ("cropped, close-up, multiple views, 2girls, 3girls, multiple characters, text, "
       "watermark, busy background, dramatic shadows, windblown hair, flying ribbons, "
       "sash, cape, glowing weapon, aura, sitting, extra limbs, blurry")

FIELDS = ("subject", "hair", "outfit", "accessories", "expression")


def ask(model, prompt, as_json=False):
    payload = {"model": model, "prompt": prompt, "stream": False, "think": False}
    if as_json:
        payload["format"] = "json"
    r = requests.post(OLLAMA, json=payload, timeout=600)
    r.raise_for_status()
    return r.json()["response"].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("textfile", help="file with the passage (- for stdin)")
    ap.add_argument("--model", default="qwen3:8b")
    ap.add_argument("--style", default="anime key visual, full color, cel shaded")
    ap.add_argument("--out", default="data/prompts/last.json")
    args = ap.parse_args()

    text = sys.stdin.read() if args.textfile == "-" else open(args.textfile).read()
    sheet = json.loads(ask(args.model, EXTRACT.format(text=text.strip()), as_json=True))

    bible = json.loads(BIBLE.read_text()) if BIBLE.exists() else {}
    entry = bible.get(sheet.get("name", ""), {})
    for k, v in entry.items():
        if k != "style":
            sheet[k] = v                  # canon wins over one passage
    for k in list(sheet):                 # a still pose generates far better 3D
        if isinstance(sheet[k], str):
            sheet[k] = MOTION.sub("", sheet[k]).strip(" ,")

    style = ", ".join(x for x in (args.style, entry.get("style", "")) if x)
    subj = sheet.get("subject", "").lower()
    solo = "1boy, solo" if ("man" in subj or "boy" in subj) and "woman" not in subj else "1girl, solo"
    subject = ", ".join([solo] + [sheet[k] for k in FIELDS if sheet.get(k)])

    prompt = f"{style}, {subject}, {POSE}"
    out = {"sheet": sheet, "prompt": prompt, "negative": NEG}

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps(out, indent=2, ensure_ascii=False))
    words = len(prompt.split())
    if words > 55:
        print(f"\nWARNING: prompt is {words} words; CLIP cuts at ~77 tokens. "
              f"Trim the bible if the tail gets truncated.", file=sys.stderr)


if __name__ == "__main__":
    main()
