"""Scratch only (dispatch 2026-10-20-pi-18 Part A). Not committed.
The Street sprite's night copy, the way the app makes it (street-cloudflare 5b270ac4): every icon through
nightColorOf per pixel (NightColour.kt:39-47, :196), alpha kept; the ring icons through nightIconPixelsOf
(:171-193) with the rings from the style's metadata (forager:night-icon-rings). Both densities."""
import json, shutil
import numpy as np
from PIL import Image

WT = "/tmp/sage04-scratch"
OUT = "/tmp/sage04-scratch/sprite-night"
RING_TOLERANCE = 16.0
rings = json.load(open(f"/tmp/sage03-scratch/styles/base.json"))["metadata"]["forager:night-icon-rings"]
hexrgb = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=float)


def night(rgb):  # rgb float array (..., 3)
    shift = 255.0 - 2.0 * rgb.sum(axis=-1, keepdims=True) / 3.0
    return np.clip(np.floor(rgb + shift + 0.5), 0, 255)  # Kotlin roundToInt: half up


def ring_night(rgb, ring):
    r, f, nr = hexrgb(ring["ring"]), hexrgb(ring["fill"]), hexrgb(ring["night"])
    nf = night(f[None, :])[0]
    axis = f - r
    t = np.clip(((rgb - r) * axis).sum(-1) / (axis * axis).sum(), 0, 1)[..., None]
    dist2 = ((rgb - (r + t * axis)) ** 2).sum(-1)
    on_ring = np.clip(np.floor(nr + t * (nf - nr) + 0.5), 0, 255)
    return np.where((dist2 > RING_TOLERANCE ** 2)[..., None], night(rgb), on_ring)


for suffix in ("", "@2x"):
    index = json.load(open(f"{WT}/sprite/light{suffix}.json"))
    img = np.array(Image.open(f"{WT}/sprite/light{suffix}.png").convert("RGBA")).astype(float)
    out = img.copy()
    out[..., :3] = night(img[..., :3])
    ringed = 0
    for name, ring in rings.items():
        if name not in index:
            raise SystemExit(f"ring icon {name} not in sprite{suffix}")
        e = index[name]
        ys, xs = slice(e["y"], e["y"] + e["height"]), slice(e["x"], e["x"] + e["width"])
        out[ys, xs, :3] = ring_night(img[ys, xs, :3], ring)
        ringed += 1
    Image.fromarray(out.astype(np.uint8), "RGBA").save(f"{OUT}/light{suffix}.png")
    shutil.copy(f"{WT}/sprite/light{suffix}.json", f"{OUT}/light{suffix}.json")
    print(f"light{suffix}: {len(index)} icons inverted, {ringed} with their night ring")
