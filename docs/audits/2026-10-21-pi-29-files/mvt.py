# Minimal MVT reader: for the roads layer, count features by kind_detail and their min_zoom values.
import gzip, subprocess, sys, collections
SRC = "/srv/forager-build/out-usca/current/forager-usca.pmtiles"
def varint(b, i):
    r = s = 0
    while True:
        c = b[i]; i += 1; r |= (c & 0x7f) << s; s += 7
        if c < 0x80: return r, i
def fields(b):
    i = 0
    while i < len(b):
        k, i = varint(b, i); f, t = k >> 3, k & 7
        if t == 0: v, i = varint(b, i)
        elif t == 2: n, i = varint(b, i); v = b[i:i+n]; i += n
        elif t == 1: v = b[i:i+8]; i += 8
        elif t == 5: v = b[i:i+4]; i += 4
        yield f, t, v
def value(b):
    import struct
    for f, t, v in fields(b):
        if f == 1: return v.decode()
        if f == 2: return struct.unpack("<f", v)[0]
        if f == 3: return struct.unpack("<d", v)[0]
        if f in (4, 5): return v
        if f == 6: return (v >> 1) ^ -(v & 1)
        if f == 7: return bool(v)
def roads(z, x, y):
    t = subprocess.run(["pmtiles", "tile", "-q", SRC, str(z), str(x), str(y)], capture_output=True).stdout
    if t[:2] == b"\x1f\x8b": t = gzip.decompress(t)
    out = collections.Counter()
    for f, _, layer in fields(t):
        if f != 3: continue
        name, keys, vals, feats = None, [], [], []
        for lf, _, lv in fields(layer):
            if lf == 1: name = lv.decode()
            elif lf == 2: feats.append(lv)
            elif lf == 3: keys.append(lv.decode())
            elif lf == 4: vals.append(value(lv))
        if name != "roads": continue
        for ft in feats:
            for ff, _, fv in fields(ft):
                if ff == 2:
                    tags, j = [], 0
                    while j < len(fv):
                        a, j = varint(fv, j); tags.append(a)
                    p = {keys[tags[k]]: vals[tags[k+1]] for k in range(0, len(tags), 2)}
                    if p.get("kind") == "path":
                        out[(p.get("kind_detail"), p.get("min_zoom"))] += 1
    return out
for z, x, y in [tuple(map(int, a.split("/"))) for a in sys.argv[1:]]:
    print("%d/%d/%d" % (z, x, y), dict(sorted(roads(z, x, y).items(), key=str)))
