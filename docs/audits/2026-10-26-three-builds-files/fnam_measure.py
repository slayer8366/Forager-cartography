#!/usr/bin/env python3
"""Prototype FNAM v1 encoder, for measuring sizes only (Aspen, 2026-10-26). Not the build stage: Willow writes
that, with tests. Reads `osmium export -f geojsonseq` of one square's named highways on stdin.

Usage: fnam_measure.py <square name, e.g. W75_N40> <out.fnm> < square.geojsonseq

Simplifications against the plan (for measurement, close enough):
  - a segment goes to the cell holding its midpoint; lines are not clipped exactly at cell edges;
  - Douglas-Peucker at 2 m in a local equirectangular frame per line.
"""
import gzip, json, os, math, re, struct, sys

CELLS = 40                      # 1/8 degree over 5 degrees
STEP = 5.0 / CELLS
SCALE = 1_000_000               # 1e-6 degree units
SIMPLIFY_M = 2.0
DROP = {"proposed", "construction", "abandoned", "razed", "disused", "platform"}

name, out = sys.argv[1], sys.argv[2]
m = re.fullmatch(r"([WE])(\d+)_([NS])(\d+)", name)
west = int(m[2]) * (-1 if m[1] == "W" else 1)
south = int(m[4]) * (-1 if m[3] == "S" else 1)


def varint(n, buf):
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            buf.append(b | 0x80)
        else:
            buf.append(b)
            return


def zz(n):
    return (n << 1) ^ (n >> 63)


def dp(pts, tol_m):
    if len(pts) < 3:
        return pts
    lat0 = math.radians(pts[0][1])
    kx, ky = 111_320 * math.cos(lat0), 110_540
    xy = [(p[0] * kx, p[1] * ky) for p in pts]
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (ax, ay), (bx, by) = xy[a], xy[b]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        best, bi = -1.0, -1
        for i in range(a + 1, b):
            px, py = xy[i]
            if L2 == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
                d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
            if d > best:
                best, bi = d, i
        if best > tol_m:
            keep[bi] = True
            stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]


def cell_of(lon, lat):
    cx, cy = int((lon - west) / STEP), int((lat - south) / STEP)
    if 0 <= cx < CELLS and 0 <= cy < CELLS:
        return cy * CELLS + cx
    return None


strings, sidx = [], {}
hwvals, hidx = [], {}


def intern(s, table, index):
    if s not in index:
        index[s] = len(table)
        table.append(s)
    return index[s] + 1


cells = [[] for _ in range(CELLS * CELLS)]   # per cell: (name_i, ref_i, hw_i, [points])
ways = pieces = pts_in = pts_out = 0
for line in sys.stdin:
    line = line.strip().lstrip("\x1e")
    if not line:
        continue
    f = json.loads(line)
    g, p = f["geometry"], f["properties"]
    if g["type"] != "LineString" or p.get("highway") in DROP or p.get("area") == "yes":
        continue
    nm, rf = p.get("name"), p.get("ref")
    if not nm and not rf:
        continue
    ways += 1
    coords = g["coordinates"]
    pts_in += len(coords)
    coords = dp(coords, SIMPLIFY_M)
    ni = intern(nm, strings, sidx) if nm else 0
    ri = intern(rf, strings, sidx) if rf else 0
    hi = intern(p.get("highway"), hwvals, hidx) - 1
    cur, cur_cell = None, -1   # -1: no piece yet (None is a real value, "outside the square")
    for a, b in zip(coords, coords[1:]):
        c = cell_of((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if c != cur_cell:
            if cur and cur_cell is not None:
                cells[cur_cell].append((ni, ri, hi, cur))
            cur, cur_cell = [a], c
        cur.append(b)
    if cur and cur_cell is not None:
        cells[cur_cell].append((ni, ri, hi, cur))

bodies = []
for ci, recs in enumerate(cells):
    cx, cy = ci % CELLS, ci // CELLS
    ox, oy = round((west + cx * STEP) * SCALE), round((south + cy * STEP) * SCALE)
    buf = bytearray()
    varint(len(recs), buf)
    for ni, ri, hi, pts in recs:
        pieces += 1
        pts_out += len(pts)
        q = [(round(x * SCALE) - ox, round(y * SCALE) - oy) for x, y in pts]
        xs, ys = [a for a, _ in q], [b for _, b in q]
        varint(ni, buf); varint(ri, buf); buf.append(hi)
        if os.environ.get("FNAM_BBOX", "1") == "1":
            for v in (min(xs), min(ys), max(xs), max(ys)):
                varint(zz(v), buf)
        varint(len(q), buf)
        px, py = 0, 0
        for x, y in q:
            varint(zz(x - px), buf); varint(zz(y - py), buf)
            px, py = x, y
    bodies.append(bytes(buf))

st = bytearray()
for table in (strings, hwvals):
    varint(len(table), st)
    for s in table:
        b = s.encode()
        varint(len(b), st); st += b
header = b"FNAM" + struct.pack("<HhhqII", 1, west, south, 0, len(strings), pieces)
dir_size = CELLS * CELLS * 8
blob = bytearray(header) + st
offset = len(blob) + dir_size
dirbuf = bytearray()
for b in bodies:
    dirbuf += struct.pack("<II", offset, len(b))
    offset += len(b)
blob += dirbuf + b"".join(bodies)
open(out, "wb").write(blob)

# A 50 km x 50 km area at the square's busiest place: the 50 km window (in whole cells, grown by one) with
# the most bytes. Strings are counted as the cut would reindex them: only those its records use.
lat_mid = south + 2.5
cw_km, ch_km = STEP * 111.32 * math.cos(math.radians(lat_mid)), STEP * 110.54
wx, wy = math.ceil(50 / cw_km) + 1, math.ceil(50 / ch_km) + 1
best = (0, None)
for y0 in range(0, CELLS - wy + 1):
    for x0 in range(0, CELLS - wx + 1):
        s = sum(len(bodies[(y0 + j) * CELLS + x0 + i]) for j in range(wy) for i in range(wx))
        if s > best[0]:
            best = (s, (x0, y0))
x0, y0 = best[1]
used = set()
for j in range(wy):
    for i in range(wx):
        for ni, ri, _, _ in cells[(y0 + j) * CELLS + x0 + i]:
            used.update(k for k in (ni, ri) if k)
cut_strings = sum(len(strings[k - 1].encode()) + 2 for k in used)
cut = len(header) + cut_strings + dir_size + best[0]
print(json.dumps({
    "square": name, "ways": ways, "pieces": pieces, "points_in": pts_in, "points_out": pts_out,
    "strings": len(strings), "string_bytes": len(st),
    "file_bytes": len(blob), "file_gzip_bytes": len(gzip.compress(bytes(blob), 6)),
    "busiest_50km_area": {"cells": [wx, wy], "sw_cell": [x0, y0],
                          "sw_lonlat": [round(west + x0 * STEP, 3), round(south + y0 * STEP, 3)],
                          "bytes": cut}}))
