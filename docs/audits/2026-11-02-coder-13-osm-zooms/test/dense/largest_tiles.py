#!/usr/bin/env python3
"""coder-13 (a) (Willow, 2026-11-02), read only: the largest stored tiles per zoom in a PMTiles v3 archive, from its
directories alone (no tile data is read). Prints the top N per zoom with z/x/y and bytes as stored (gzipped).
  largest_tiles.py ARCHIVE [N] [ZMIN ZMAX]
"""
import gzip, heapq, struct, sys

path = sys.argv[1]
TOP = int(sys.argv[2]) if len(sys.argv) > 2 else 5
ZMIN, ZMAX = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (7, 10)
base = lambda z: ((1 << (2 * z)) - 1) // 3          # first tile id of zoom z
LO, HI = base(ZMIN), base(ZMAX + 1)


def varint(b, i):
    r = s = 0
    while True:
        c = b[i]; i += 1; r |= (c & 0x7F) << s; s += 7
        if c < 0x80: return r, i


def directory(b):
    n, i = varint(b, 0)
    ids, runs, lens, offs = [], [], [], []
    last = 0
    for _ in range(n):
        d, i = varint(b, i); last += d; ids.append(last)
    for _ in range(n):
        v, i = varint(b, i); runs.append(v)
    for _ in range(n):
        v, i = varint(b, i); lens.append(v)
    for k in range(n):
        v, i = varint(b, i)
        offs.append(offs[k - 1] + lens[k - 1] if v == 0 and k > 0 else v - 1)
    return list(zip(ids, runs, lens, offs))


def zxy(tid):
    z = 0
    while base(z + 1) <= tid: z += 1
    t = tid - base(z); n = 1 << z; x = y = 0; s = 1
    while s < n:
        rx = 1 & (t // 2); ry = 1 & (t ^ rx)
        if ry == 0:
            if rx == 1: x, y = s - 1 - x, s - 1 - y
            x, y = y, x
        x += s * rx; y += s * ry; t //= 4; s *= 2
    return z, x, y


with open(path, "rb") as f:
    h = f.read(127)
    assert h[:7] == b"PMTiles" and h[7] == 3, "not a PMTiles v3 archive"
    root_off, root_len, meta_off, meta_len, leaf_off, leaf_len, data_off, data_len = struct.unpack("<8Q", h[8:72])
    comp = h[97]
    def read(off, ln):
        f.seek(off); b = f.read(ln)
        return gzip.decompress(b) if comp == 2 else b
    tops = {z: [] for z in range(ZMIN, ZMAX + 1)}
    stack = [directory(read(root_off, root_len))]
    leaves_read = 0
    while stack:
        entries = stack.pop()
        for k, (tid, run, ln, off) in enumerate(entries):
            nxt = entries[k + 1][0] if k + 1 < len(entries) else 1 << 62
            if run == 0:                                   # a leaf directory covering [tid, nxt)
                if nxt > LO and tid < HI:
                    stack.append(directory(read(leaf_off + off, ln))); leaves_read += 1
                continue
            for r in range(run):                           # run-length entries share bytes (deduplicated tiles)
                t = tid + r
                if LO <= t < HI:
                    z = zxy(t)[0]
                    if len(tops[z]) < TOP: heapq.heappush(tops[z], (ln, t))
                    elif ln > tops[z][0][0]: heapq.heapreplace(tops[z], (ln, t))
                    if r > 64: break                        # long runs are identical (ocean, empty) tiles: small
print(f"{path}: leaf directories read {leaves_read}")
for z in range(ZMIN, ZMAX + 1):
    for ln, t in sorted(tops[z], reverse=True):
        zz, x, y = zxy(t)
        print(f"z{zz} {zz}/{x}/{y} {ln:,} bytes")
