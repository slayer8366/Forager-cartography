#!/usr/bin/env python3
"""coder-13 Z2 renders (Willow, scratch): OSM | Street v5 (patched tiles) | Street v4 (today's tiles), one image per view."""
import glob, os, re, sys
from PIL import Image, ImageDraw, ImageFont
D = "/home/bwann83/scratch/coder13/molalla/render/shots"
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
views = sorted({re.sub(r"-(osm|v5|v4)\.png$", "", os.path.basename(p)) for p in glob.glob(f"{D}/*.png")})
for v in views:
    ims = [Image.open(f"{D}/{v}-{s}.png").convert("RGB") for s in ("osm", "v5", "v4")]
    w, h = ims[0].size
    sheet = Image.new("RGB", (3 * w + 40, h + 70), "white")
    d = ImageDraw.Draw(sheet)
    z = v.rsplit("-z", 1)[1]
    for i, (im, label) in enumerate(zip(ims, ("OpenStreetMap (as in the app)", "Street v5 + patch 0008", "Street v4 today"))):
        sheet.paste(im, (i * (w + 20), 70))
        d.text((i * (w + 20) + 10, 18), f"{label}, zoom {z}", fill="black", font=font)
    sheet.save(f"{out}/{v}.png", optimize=True)
    print(f"{out}/{v}.png")
