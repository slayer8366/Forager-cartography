#!/usr/bin/env python3
"""coder-13 Z1 (Willow): first zoom of each layer/kind in our tiles over a box, read-only.

  first_zooms.py W S E N [PMTILES]   decodes every tile of z0-15 that the box touches (pmtiles tile, read only)
and prints, per layer and (kind, kind_detail): the first zoom present, the first zoom with a name, the first zoom
with a ref, the min_zoom attribute values seen at that zoom, and feature counts per zoom. Also writes the same as
JSON to first_zooms.json beside this file.
"""
import collections, gzip, json, math, os, subprocess, sys
sys.path.insert(0, "/home/bwann83/pi29-logs/resume/tiles")
from mvt import fields, varint, value, SRC

W, S, E, N = map(float, sys.argv[1:5])
PMT = sys.argv[5] if len(sys.argv) > 5 else SRC
GEOM = {1: "point", 2: "line", 3: "polygon"}


def tx(lon, z): return int((lon + 180) / 360 * 2**z)
def ty(lat, z):
    r = math.radians(lat); return int((1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2**z)


def tile(z, x, y):
    t = subprocess.run(["pmtiles", "tile", "-q", PMT, str(z), str(x), str(y)], capture_output=True).stdout
    return gzip.decompress(t) if t[:2] == b"\x1f\x8b" else t


def layers(t):
    for f, _, layer in fields(t):
        if f != 3:
            continue
        name, keys, vals, feats = None, [], [], []
        for lf, _, lv in fields(layer):
            if lf == 1: name = lv.decode()
            elif lf == 2: feats.append(lv)
            elif lf == 3: keys.append(lv.decode())
            elif lf == 4: vals.append(value(lv))
        out = []
        for fb in feats:
            tags, gtype = {}, 0
            for ff, _, fv in fields(fb):
                if ff == 2:
                    ints, j = [], 0
                    while j < len(fv):
                        v, j = varint(fv, j); ints.append(v)
                    for a, b in zip(ints[::2], ints[1::2]):
                        tags[keys[a]] = vals[b]
                elif ff == 3:
                    gtype = fv
            out.append((tags, GEOM.get(gtype, "?")))
        yield name, out


# rec[(layer, kind, kind_detail, geom)] = {z: [count, named, reffed, set(min_zoom values), sample names]}
rec = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0, set(), set()]))
ntiles = 0
for z in range(0, 16):
    for x in range(tx(W, z), tx(E, z) + 1):
        for y in range(ty(N, z), ty(S, z) + 1):
            t = tile(z, x, y); ntiles += 1
            if not t:
                continue
            for lname, feats in layers(t):
                for tags, g in feats:
                    k = (lname, str(tags.get("kind", "")), str(tags.get("kind_detail", "")), g)
                    r = rec[k][z]
                    r[0] += 1
                    if tags.get("name"): r[1] += 1; len(r[4]) < 3 and r[4].add(str(tags["name"]))
                    if tags.get("ref") or tags.get("shield_text"): r[2] += 1
                    if "min_zoom" in tags: r[3].add(tags["min_zoom"])
rows = []
for k in sorted(rec):
    zs = rec[k]
    first = min(zs); named = min((z for z in zs if zs[z][1]), default=None); reffed = min((z for z in zs if zs[z][2]), default=None)
    rows.append({"layer": k[0], "kind": k[1], "kind_detail": k[2], "geom": k[3], "first": first, "first_named": named,
                 "first_ref": reffed, "min_zoom_at_first": sorted(zs[first][3])[:6],
                 "counts": {z: zs[z][0] for z in sorted(zs)}, "names": sorted(zs[named][4]) if named is not None else []})
json.dump({"box": [W, S, E, N], "pmtiles": PMT, "tiles_read": ntiles, "rows": rows},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "first_zooms.json"), "w"), indent=1)
print(f"box {W},{S},{E},{N}; {ntiles} tiles read from {PMT}")
print(f"{'layer':10} {'kind':22} {'kind_detail':20} {'geom':7} first named ref  min_zoom@first  counts z:n")
for r in rows:
    c = " ".join(f"{z}:{n}" for z, n in list(r["counts"].items())[:8])
    print(f"{r['layer']:10} {r['kind'][:22]:22} {r['kind_detail'][:20]:20} {r['geom']:7} {r['first']:>5} {str(r['first_named']):>5}"
          f" {str(r['first_ref']):>4}  {str(r['min_zoom_at_first'])[:14]:14}  {c}")
