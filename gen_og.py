#!/usr/bin/env python3
"""Generate og.png — the 1200x630 link-preview card (Open Graph image).
Score-agnostic branding so it never goes stale. Run once; commit og.png.
Needs Pillow:  pip install Pillow
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 630
HERE = os.path.dirname(os.path.abspath(__file__))


def font(name, size):
    for path in (f"C:/Windows/Fonts/{name}",
                 f"/usr/share/fonts/truetype/dejavu/{name}"):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


BOLD = "arialbd.ttf"
REG = "arial.ttf"

# vertical gradient background
img = Image.new("RGB", (W, H))
g = ImageDraw.Draw(img)
top, bot = (16, 26, 52), (10, 14, 26)
for y in range(H):
    t = y / (H - 1)
    g.line([(0, y), (W, y)], fill=tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3)))

# soft colour glows
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([-160, -220, 540, 360], fill=(255, 93, 143, 80))
gd.ellipse([W - 540, -240, W + 160, 340], fill=(61, 165, 255, 80))
img = Image.alpha_composite(img.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(120))).convert("RGB")
d = ImageDraw.Draw(img)


def center(y, text, fnt, fill):
    w = d.textlength(text, font=fnt)
    d.text(((W - w) / 2, y), text, font=fnt, fill=fill)


center(150, "F I F A   W O R L D   C U P   2 0 2 6", font(BOLD, 30), (147, 160, 196))

# coloured title, centred
tf = font(BOLD, 112)
segs = [("Nicha", (255, 93, 143)), ("  vs  ", (147, 160, 196)), ("Daniele", (61, 165, 255))]
total = sum(d.textlength(s, font=tf) for s, _ in segs)
x, ty = (W - total) / 2, 245
for s, col in segs:
    d.text((x, ty), s, font=tf, fill=col)
    x += d.textlength(s, font=tf)

center(415, "Our live World Cup scoreboard", font(REG, 42), (210, 218, 245))
center(495, "Win +3      Draw +1      Loss 0", font(BOLD, 30), (147, 160, 196))

out = os.path.join(HERE, "og.png")
img.save(out)
print("saved", out, img.size)
