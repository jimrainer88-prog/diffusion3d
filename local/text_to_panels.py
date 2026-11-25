"""Prose -> comic panel script (JSON) via local Ollama, with the character bible merged in.

--rebuild re-derives prompts from an existing script without calling the LLM, so bible
or style changes never reshuffle the story.
"""
import argparse
import json
import sys
from pathlib import Path

import requests

OLLAMA = "http://localhost:11434/api/generate"
BIBLE = Path("data/prompts/bible.json")

PANELS = """Turn the passage into a {n}-panel comic script.
Return ONLY JSON: {{"title": "...", "panels": [{{"shot": "...", "setting": "...",
"character": "...", "action": "...", "dialogue": "..."}}]}}

Rules:
- shot: one of wide, medium, close-up.
- setting and action: short visual phrases, under 10 words, no trailing period.
- character: the name of the ONE character in the panel, or "" if none.
- dialogue: under 15 words, or "" for a silent panel.
- Use only what the passage states.

Passage:
<<<
{text}
>>>"""

STYLE = "comic panel, anime style, clean lineart, flat cel shading"
NEG = "text, speech bubble, watermark, signature, multiple panels, border, blurry"
FIELDS = ("subject", "hair", "outfit", "expression")
# "close-up"/"medium"/"wide" are not Danbooru tags, so the model improvises the framing.
# These are real tags and frame predictably.
SHOT = {"wide": "full body, wide shot", "medium": "upper body", "close-up": "portrait"}
KEYS = {"shot", "setting", "character", "action", "dialogue", "prompt", "negative"}


def script_path(tag):
    return Path(f"data/prompts/panels_{tag}.json")


# Xianxia prose calls people "Fairy Leng Tian" or "Senior Sister Leng"; the bible
# keys on the bare name. Try aliases first, then strip the honorific.
HONORIFICS = ("fairy", "senior sister", "senior brother", "junior sister",
              "junior brother", "elder", "master", "lord")


def resolve(name, bible):
    if name in bible:
        return bible[name]
    for who in bible.values():
        if name in who.get("aliases", []):
            return who
    low = name.lower()
    for h in HONORIFICS:
        if low.startswith(h + " "):
            bare = low[len(h):].strip()
            for key, who in bible.items():
                k = key.lower()
                if k.startswith(bare) or bare.startswith(k):
                    return who
    return {}


def build_prompts(script):
    bible = json.loads(BIBLE.read_text()) if BIBLE.exists() else {}
    for i, p in enumerate(script["panels"]):
        for k in set(p) - KEYS:            # catch hand-edit typos like "dialog,ue"
            print(f"WARNING: panel {i} has unknown key {k!r}", file=sys.stderr)
        name = p.get("character", "").strip()
        who = resolve(name, bible)
        if name and not who:
            print(f"WARNING: no bible entry for {name!r} — that panel will have no character",
                  file=sys.stderr)
        bits = [STYLE, who.get("style", "")]
        if who:
            subj = who.get("subject", "").lower()
            male = ("man" in subj or "boy" in subj) and "woman" not in subj
            bits.append("1boy, solo" if male else "1girl, solo")
            bits.append(", ".join(who[k] for k in FIELDS if who.get(k)))
        bits += [SHOT.get(p.get("shot", "").lower(), "upper body"),
                 p.get("action", ""), p.get("setting", "")]
        p["prompt"] = ", ".join(b.rstrip(" .") for b in bits if b)
        p["negative"] = NEG
    return script


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("textfile", nargs="?")
    ap.add_argument("--tag", help="page id; default: the textfile's stem")
    ap.add_argument("--rebuild", action="store_true",
                    help="re-derive prompts from the existing script; no LLM, story unchanged")
    ap.add_argument("--model", default="qwen3:8b")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    tag = args.tag or (Path(args.textfile).stem if args.textfile else "default")
    out = script_path(tag)

    if args.rebuild:
        script = json.loads(out.read_text())
    else:
        if not args.textfile:
            sys.exit("give a textfile, or use --rebuild --tag <tag>")
        text = sys.stdin.read() if args.textfile == "-" else open(args.textfile).read()
        r = requests.post(OLLAMA, json={"model": args.model, "stream": False, "think": False,
                                        "format": "json", "options": {"seed": args.seed},
                                        "prompt": PANELS.format(n=args.n, text=text.strip())},
                          timeout=900)
        r.raise_for_status()
        script = json.loads(r.json()["response"])

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_prompts(script), indent=2, ensure_ascii=False))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
