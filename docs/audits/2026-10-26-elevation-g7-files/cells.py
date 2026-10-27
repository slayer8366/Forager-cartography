#!/usr/bin/env python3
"""G7 cell list: every 1-degree cell of every .rd5 route square, with its sources.

Usage: cells.py SEGMENTS_DIR POLY_DIR OUT_TSV OUT_CUTLINE_GEOJSON

A cell gets MRDEM where it touches canada.poly, then 3DEP 1" on top where it touches the US
polygons (us, puerto-rico, us-virgin-islands) and USGS publishes the tile; the 3DEP layer is
clipped to the US polygons (topo rulings 5: 3DEP for the US, MRDEM for Canada). Cells touching
neither are left out. Writes OUT_TSV (hgt name, west, south, us, ca, 3dep tile or -) and the US
cutline as GeoJSON.
"""
import json, os, re, sys, urllib.parse, urllib.request
from osgeo import ogr

seg_dir, poly_dir, out_tsv, out_cut = sys.argv[1:5]
LIST = "https://prd-tnm.s3.amazonaws.com/?list-type=2&prefix=StagedProducts/Elevation/1/TIFF/current/&delimiter=/"


def read_poly(path):
    """Osmosis .poly to an OGR MultiPolygon: each section a ring; '!' sections are holes."""
    outer, holes, cur, name = [], [], None, None
    lines = [l.strip() for l in open(path)][1:]
    for l in lines:
        if not l:
            continue
        if cur is None:
            if l == "END":
                break
            name, cur = l, []
        elif l == "END":
            (holes if name.startswith("!") else outer).append(cur)
            cur = None
        else:
            x, y = map(float, l.split()[:2])
            cur.append((x, y))
    mp = ogr.Geometry(ogr.wkbMultiPolygon)
    for ring_pts in outer:
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for x, y in ring_pts + [ring_pts[0]]:
            ring.AddPoint_2D(x, y)
        p = ogr.Geometry(ogr.wkbPolygon)
        p.AddGeometry(ring)
        mp.AddGeometry(p)
    g = mp.Buffer(0)
    for h in holes:
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for x, y in h + [h[0]]:
            ring.AddPoint_2D(x, y)
        p = ogr.Geometry(ogr.wkbPolygon)
        p.AddGeometry(ring)
        g = g.Difference(p)
    return g


def dep_tiles():
    tiles, token = set(), None
    while True:
        url = LIST + ("&continuation-token=" + urllib.parse.quote(token) if token else "")
        x = urllib.request.urlopen(url, timeout=60).read().decode()
        tiles.update(re.findall(r"current/([ns]\d{2}[ew]\d{3})/</Prefix>", x))
        m = re.search(r"<NextContinuationToken>([^<]+)</NextContinuationToken>", x)
        if not m:
            return tiles
        token = m.group(1)


us = None
for n in ("us", "puerto-rico", "us-virgin-islands"):
    g = read_poly(os.path.join(poly_dir, n + ".poly"))
    us = g if us is None else us.Union(g)
ca = read_poly(os.path.join(poly_dir, "canada.poly"))
deps = dep_tiles()
print(f"3DEP 1\" tiles listed: {len(deps)}", file=sys.stderr)

with open(out_cut, "w") as f:
    json.dump({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": "usa"}, "geometry": json.loads(us.ExportToJson())}]}, f)

rows = []
for fn in sorted(os.listdir(seg_dir)):
    m = re.fullmatch(r"([EW])(\d+)_([NS])(\d+)\.rd5", fn)
    if not m:
        continue
    w = int(m.group(2)) * (1 if m.group(1) == "E" else -1)
    s = int(m.group(4)) * (1 if m.group(3) == "N" else -1)
    for lat in range(s, s + 5):
        for lon in range(w, w + 5):
            cell = ogr.CreateGeometryFromWkt(
                f"POLYGON(({lon} {lat},{lon+1} {lat},{lon+1} {lat+1},{lon} {lat+1},{lon} {lat}))")
            in_us, in_ca = cell.Intersects(us), cell.Intersects(ca)
            if not (in_us or in_ca):
                continue
            # 3DEP names a tile by its NW corner; .hgt by its SW corner.
            t = f"{'n' if lat + 1 >= 0 else 's'}{abs(lat + 1):02d}{'e' if lon >= 0 else 'w'}{abs(lon):03d}"
            dep = t if in_us and t in deps else "-"
            hgt = f"{'N' if lat >= 0 else 'S'}{abs(lat):02d}{'E' if lon >= 0 else 'W'}{abs(lon):03d}"
            rows.append((hgt, lon, lat, int(in_us), int(in_ca), dep))

with open(out_tsv, "w") as f:
    for r in rows:
        f.write("\t".join(map(str, r)) + "\n")
print(f"cells: {len(rows)}; us {sum(r[3] for r in rows)}, ca {sum(r[4] for r in rows)}, "
      f"both {sum(r[3] and r[4] for r in rows)}, with 3DEP {sum(r[5] != '-' for r in rows)}, "
      f"us without 3DEP {sum(r[3] and r[5] == '-' for r in rows)}", file=sys.stderr)
