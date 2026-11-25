"""panels.json + data/panels/panel_*.png -> data/output/strip.png

Each panel is a caption band (title/bubble) above the art, so speech never covers a face.
"""
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CELL, GUTTER, MARGIN, COLS, PAD = 768, 16, 24, 2, 18
FONTS = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/System/Library/Fonts/Supplemental/Arial Bold.ttf")


def font(size):
    for p in FONTS:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrapped(d, text, f, chars):
    body = "\n".join(textwrap.wrap(text, chars))
    bb = d.multiline_textbbox((0, 0), body, font=f, spacing=6)
    return body, bb[2], bb[3]


def main():
    script = json.loads(Path("data/prompts/panels.json").read_text())
    panels = script["panels"]
    rows = (len(panels) + COLS - 1) // COLS
    page = Image.new("RGB",
                     (MARGIN * 2 + CELL * COLS + GUTTER * (COLS - 1),
                      MARGIN * 2 + CELL * rows + GUTTER * (rows - 1)), "white")
    fb, ft = font(32), font(46)
    probe = ImageDraw.Draw(page)

    for i, p in enumerate(panels):
        src = Path(f"data/panels/panel_{i}.png")
        if not src.exists():
            print("missing", src)
            continue

        # measure everything that must sit above the art
        blocks = []
        if i == 0 and script.get("title"):
            blocks.append(("title", *wrapped(probe, script["title"], ft, 26)))
        if p.get("dialogue"):
            blocks.append(("bubble", *wrapped(probe, p["dialogue"], fb, 30)))
        band = sum(h + PAD * 2 + 10 for _, _, _, h in blocks) + (PAD if blocks else 0)

        cell = Image.new("RGB", (CELL, CELL), "white")
        art = Image.open(src).convert("RGB").resize((CELL, CELL))
        # keep the TOP of the art — that's where the heads are
        cell.paste(art.crop((0, 0, CELL, CELL - band)), (0, band))

        d = ImageDraw.Draw(cell)
        y = PAD
        for kind, body, w, h in blocks:
            box = (PAD, y, PAD + w + PAD * 2, y + h + PAD * 2)
            if kind == "title":
                d.rounded_rectangle(box, radius=10, fill="#fdf6d8", outline="black", width=4)
                d.multiline_text((PAD * 2, y + PAD), body, font=ft, fill="black", spacing=6)
            else:
                d.rounded_rectangle(box, radius=22, fill="white", outline="black", width=4)
                tip = PAD + w * 0.3
                d.polygon([(tip, box[3]), (tip + 46, box[3]), (tip + 12, box[3] + 22)],
                          fill="white", outline="black")
                d.multiline_text((PAD * 2, y + PAD), body, font=fb, fill="black", spacing=6)
            y += h + PAD * 2 + 10
        d.rectangle((0, 0, CELL - 1, CELL - 1), outline="black", width=5)

        page.paste(cell, (MARGIN + (i % COLS) * (CELL + GUTTER),
                          MARGIN + (i // COLS) * (CELL + GUTTER)))

    Path("data/output").mkdir(parents=True, exist_ok=True)
    page.save("data/output/strip.png")
    print("saved data/output/strip.png")


if __name__ == "__main__":
    main()
