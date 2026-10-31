# Sage-10b: production art for the v6 sprite patterns orchard_dots, vineyard_rows, nursery_dots (Forager's own art).
# Day ink #8ea65c on transparent, straight alpha (every pixel carries the ink RGB; only alpha varies), so no fringe
# appears when the image is scaled or premultiplied. Drawn at 8x the output size and reduced with a box filter, per
# output scale (1x and 2x), so each scale is anti-aliased on its own pixel grid. No shape touches a tile edge, so the
# cell repeats seamlessly. Night is the app's transform (plain inversion, ruled), not drawn here.
# Run: python3 make-patterns.py <out-dir>
import sys, os
from PIL import Image, ImageDraw
INK = (0x8e, 0xa6, 0x5c)
SS = 8  # supersampling factor

# Each pattern: cell size in 1x px, and shapes in 1x px units: ("dot", cx, cy, r) or ("bar", x0, y0, x1, y1).
PATTERNS = {
    # Orchard: round tree dots, r 2.4, on an offset 24 px grid (diagonal neighbours 17 px apart).
    "orchard_dots": (24, [("dot", 6, 6, 2.4), ("dot", 18, 18, 2.4)]),
    # Vineyard: vine rows, bars 1 x 5 px (on the pixel grid, so crisp at 1x; 2 x 10 at 2x); columns 8 px apart, gaps of
    # 3 px within and across tiles.
    "vineyard_rows": (16, [("bar", 4, 2, 5, 7), ("bar", 4, 10, 5, 15), ("bar", 12, 2, 13, 7), ("bar", 12, 10, 13, 15)]),
    # Plant nursery: fine dots, r 1.2, on an offset 12 px grid.
    "nursery_dots": (12, [("dot", 3, 3, 1.2), ("dot", 9, 9, 1.2)]),
}

def draw(cell, shapes, scale):
    n = cell * scale * SS
    mask = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(mask)
    k = scale * SS
    for s in shapes:
        if s[0] == "dot":
            _, cx, cy, r = s
            d.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k - 1, (cy + r) * k - 1], fill=255)
        else:
            _, x0, y0, x1, y1 = s
            d.rectangle([x0 * k, y0 * k, x1 * k - 1, y1 * k - 1], fill=255)
    alpha = mask.resize((cell * scale, cell * scale), Image.BOX)
    img = Image.new("RGBA", alpha.size, INK + (0,))
    img.putalpha(alpha)
    return img

out = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(out, exist_ok=True)
for name, (cell, shapes) in PATTERNS.items():
    draw(cell, shapes, 1).save(os.path.join(out, f"{name}.png"), optimize=True)
    draw(cell, shapes, 2).save(os.path.join(out, f"{name}@2x.png"), optimize=True)
