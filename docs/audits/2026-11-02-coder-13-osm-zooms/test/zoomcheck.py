#!/usr/bin/env python3
"""coder-13 Z2 tests 2-4 (Willow, 2026-11-02), read only: the Molalla test archives, patched (0008) and control.

  zoomcheck.py PATCHED.pmtiles CONTROL.pmtiles     prints the checks; exit 1 if any patched row fails

2. First zooms: for each data row, the first tile level a class appears at must be carto's N - 2 in the patched
   archive, and must differ in the control for every row patch 0008 moves. Rows ruled by size or population are
   checked per named feature: its first level must be its min_zoom - 1 (the level the style's per-level layers use).
3. Nothing else changes: feature counts per layer at z15 (over the core box), patched against control.
4. Size: tile bytes per zoom (gzipped, as stored), patched against control; tiles over 500 KB; the busiest tile.
"""
import collections, gzip, math, subprocess, sys
sys.path.insert(0, "/home/bwann83/pi29-logs/resume/tiles")
from mvt import fields, varint, value

BOX = (-122.95, 44.95, -122.25, 45.40)        # the extract's bounds
CORE = (-122.66, 45.10, -122.50, 45.20)       # Molalla and Liberal; z15 is decoded only here
GEOM = {1: "point", 2: "line", 3: "polygon"}


def tx(lon, z): return int((lon + 180) / 360 * 2**z)
def ty(lat, z):
    r = math.radians(lat); return int((1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2**z)


def raw(pmt, z, x, y):
    return subprocess.run(["pmtiles", "tile", "-q", pmt, str(z), str(x), str(y)], capture_output=True).stdout


def decode(t):
    t = gzip.decompress(t) if t[:2] == b"\x1f\x8b" else t
    for f, _, layer in fields(t):
        if f != 3:
            continue
        name, keys, vals, feats = None, [], [], []
        for lf, _, lv in fields(layer):
            if lf == 1: name = lv.decode()
            elif lf == 2: feats.append(lv)
            elif lf == 3: keys.append(lv.decode())
            elif lf == 4: vals.append(value(lv))
        for fb in feats:
            tags, g = {}, 0
            for ff, _, fv in fields(fb):
                if ff == 2:
                    ints, j = [], 0
                    while j < len(fv):
                        v, j = varint(fv, j); ints.append(v)
                    for a, b in zip(ints[::2], ints[1::2]):
                        tags[keys[a]] = vals[b]
                elif ff == 3:
                    g = fv
            yield name, tags, GEOM.get(g, "?")


def scan(pmt):
    """Every feature of every tile of z0-14 over BOX and z15 over CORE: (z, layer, tags, geom); and tile sizes."""
    feats, sizes = [], collections.defaultdict(list)
    for z in range(0, 16):
        w, s, e, n = CORE if z == 15 else BOX
        for x in range(tx(w, z), tx(e, z) + 1):
            for y in range(ty(n, z), ty(s, z) + 1):
                t = raw(pmt, z, x, y)
                if not t:
                    continue
                sizes[z].append((len(t), f"{z}/{x}/{y}"))
                for layer, tags, g in decode(t):
                    feats.append((z, layer, tags, g))
    return feats, sizes


def kd(t): return str(t.get("kind_detail", ""))
def k(t): return str(t.get("kind", ""))
ROAD = lambda kinds, details: (lambda L, t, g: L == "roads" and k(t) in kinds and kd(t) in details)
NAMED = lambda f: (lambda L, t, g: f(L, t, g) and bool(t.get("name")))
SHIELD = lambda f: (lambda L, t, g: f(L, t, g) and bool(t.get("shield_text")))
ATTR = lambda f, a: (lambda L, t, g: f(L, t, g) and t.get(a) is True)

MAJOR = ["motorway", "trunk", "primary", "secondary"]
# (row, what, predicate, carto N - 2, moved by 0008: control's first level should differ)
ROWS = [
    (35, "motorway line", ROAD(["highway"], ["motorway"]), 4, True),
    (37, "trunk line", ROAD(["major_road"], ["trunk"]), 4, True),
    (38, "primary line", ROAD(["major_road"], ["primary"]), 6, True),
    (39, "secondary line", ROAD(["major_road"], ["secondary"]), 7, True),
    (40, "tertiary line", ROAD(["major_road"], ["tertiary"]), 8, True),
    (41, "link lines", ROAD(["highway", "major_road"], ["motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link"]), 8, True),
    (42, "residential, unclassified", ROAD(["minor_road"], ["residential", "unclassified"]), 10, False),
    (43, "highway=road", ROAD(["minor_road"], ["road"]), 8, True),
    (44, "living street", ROAD(["other"], ["living_street"]), 11, True),
    (45, "service", ROAD(["minor_road"], ["service"]), 12, True),
    (47, "pedestrian street", ROAD(["path"], ["pedestrian"]), 12, False),
    (49, "track", ROAD(["path"], ["track"]), 11, False),
    (50, "path", ROAD(["path"], ["path"]), 12, False),
    (51, "footway, steps", ROAD(["path"], ["footway", "steps"]), 12, True),
    (52, "cycleway, bridleway", ROAD(["path"], ["cycleway", "bridleway"]), 11, True),
    (53, "sidewalk, crossing", ROAD(["path"], ["sidewalk", "crossing"]), 12, True),
    (74, "trunk to secondary names", NAMED(ROAD(["major_road"], ["trunk", "primary", "secondary"])), 11, True),
    (75, "tertiary names", NAMED(ROAD(["major_road"], ["tertiary"])), 12, True),
    (76, "street names", NAMED(ROAD(["minor_road"], ["residential", "unclassified", "road"])), 13, True),
    (78, "track names", NAMED(ROAD(["path"], ["track"])), 13, True),
    (81, "motorway shields", SHIELD(ROAD(["highway"], ["motorway"])), 8, True),
    (83, "trunk, primary shields", SHIELD(ROAD(["major_road"], ["trunk", "primary"])), 9, True),
    (84, "secondary shields", SHIELD(ROAD(["major_road"], ["secondary"])), 10, True),
    (85, "tertiary shields", SHIELD(ROAD(["major_road"], ["tertiary"])), 11, True),
    (60, "major bridges", ATTR(ROAD(["highway", "major_road"], MAJOR + [m + "_link" for m in MAJOR]), "is_bridge"), 11, True),
    (61, "tertiary and street bridges", ATTR(ROAD(["major_road", "minor_road"], ["tertiary", "residential", "unclassified"]), "is_bridge"), 12, False),
    (62, "major tunnels", ATTR(ROAD(["highway", "major_road"], MAJOR + ["tertiary"]), "is_tunnel"), 10, True),
    (56, "main-line rail", lambda L, t, g: L == "roads" and k(t) == "rail" and kd(t) == "rail" and not t.get("service"), 6, True),
    (59, "rail spurs, sidings, yards", lambda L, t, g: L == "roads" and k(t) == "rail" and t.get("service") in ("spur", "siding", "yard"), 11, True),
    (66, "pier lines", ROAD(["path"], ["pier"]), 10, True),
    (65, "taxiway lines", ROAD(["aeroway"], ["taxiway"]), 9, True),
    (32, "rivers", lambda L, t, g: L == "water" and k(t) == "river" and g == "line", 6, True),
    (33, "streams", lambda L, t, g: L == "water" and k(t) == "stream" and g == "line", 10, True),
    (93, "towns", lambda L, t, g: L == "places" and kd(t) == "town", 7, False),
    (94, "villages", lambda L, t, g: L == "places" and kd(t) == "village", 10, False),
    (95, "hamlets", lambda L, t, g: L == "places" and kd(t) == "hamlet", 12, True),
    (98, "suburbs", lambda L, t, g: L == "places" and kd(t) == "suburb", 10, True),
    (105, "peaks", lambda L, t, g: L == "pois" and k(t) == "peak", 9, True),
    (107, "alpine and wilderness huts", lambda L, t, g: L == "pois" and k(t) in ("alpine_hut", "wilderness_hut"), 11, True),
    (109, "camp and picnic sites, viewpoints, shelters", lambda L, t, g: L == "pois" and k(t) in ("camp_site", "picnic_site", "viewpoint", "shelter"), 14, True),
    (69, "admin level 5", lambda L, t, g: L == "boundaries" and t.get("kind_detail") == 5, 6, True),
    (71, "admin level 7", lambda L, t, g: L == "boundaries" and t.get("kind_detail") == 7, 9, True),
    (72, "admin level 8", lambda L, t, g: L == "boundaries" and t.get("kind_detail") == 8, 10, False),
]
# Per-feature rows: named points whose level comes from size or population, checked against their own min_zoom.
PER_FEATURE = [
    (88, "lake and water labels", lambda L, t, g: L == "water" and g == "point" and bool(t.get("name"))),
    (92, "cities", lambda L, t, g: L == "places" and kd(t) == "city"),
    (102, "area names", lambda L, t, g: L == "pois" and k(t) in ("nature_reserve", "national_park", "protected_area", "forest", "park") and bool(t.get("name"))),
    (110, "parking", lambda L, t, g: L == "pois" and k(t) == "parking"),
]


def first(feats, pred):
    zs = [z for z, L, t, g in feats if pred(L, t, g)]
    return min(zs) if zs else None


def per_feature(feats, pred):
    """name -> (first level seen, the min_zoom values seen)."""
    out = {}
    for z, L, t, g in feats:
        if pred(L, t, g):
            key = (L, k(t), str(t.get("name", "")))
            f, m = out.get(key, (99, set()))
            out[key] = (min(f, z), m | {t.get("min_zoom")})
    return out


def main():
    pat, con = sys.argv[1], sys.argv[2]
    print(f"patched {pat}\ncontrol {con}\nbox {BOX}, z15 over {CORE}\n")
    P, Psz = scan(pat)
    C, Csz = scan(con)
    fails = 0
    print("2. First zooms (tile level; carto N - 2). PASS: patched equals it; control: differs where 0008 moves the row")
    print(f"{'row':>4} {'what':42} {'want':>4} {'patched':>7} {'control':>7}  result")
    for row, what, pred, want, moved in ROWS:
        p, c = first(P, pred), first(C, pred)
        if p is None:
            res = "absent here (not checked)"
        else:
            ok = p == want
            ctl = (c != want) if moved else True
            res = ("PASS" if ok else "FAIL") + ("" if not moved else (", control differs" if c != want else ", CONTROL SAME"))
            fails += (not ok) + (moved and c == want and c is not None)
        print(f"{row:>4} {what:42} {want:>4} {str(p):>7} {str(c):>7}  {res}")
    print("\n   per feature: first level = min_zoom - 1 (what the style's per-level layers read)")
    for row, what, pred in PER_FEATURE:
        pf = per_feature(P, pred)
        bad = [(n, f, m) for n, (f, m) in pf.items() if len(m) != 1 or f != next(iter(m)) - 1]
        cf = per_feature(C, pred)
        moved = sum(1 for n in pf if n in cf and pf[n][0] != cf[n][0])
        sample = sorted(pf.items(), key=lambda kv: kv[1][0])[:4]
        print(f"{row:>4} {what:42} {len(pf)} features; {len(bad)} inconsistent; {moved} first at another level than in the control;"
              f" e.g. " + "; ".join(f"{n[2] or n[1]} {f}" for n, (f, m) in sample))
        fails += len(bad)
    for name in ("Molalla", "Liberal", "Molalla River", "Oregon City", "Canby"):
        fp = min((z for z, L, t, g in P if t.get("name") == name), default=None)
        fc = min((z for z, L, t, g in C if t.get("name") == name), default=None)
        print(f"     {name}: first in patched {fp}, control {fc}")

    print("\n3. Feature counts per layer at z15 (core box), patched vs control")
    cp = collections.Counter(L for z, L, t, g in P if z == 15)
    cc = collections.Counter(L for z, L, t, g in C if z == 15)
    for L in sorted(set(cp) | set(cc)):
        print(f"   {L:12} patched {cp[L]:>7} control {cc[L]:>7} {'' if cp[L] == cc[L] else '  DIFFERENT'}")

    print("\n4. Tile bytes per zoom (as stored), patched vs control; tiles over 500 KB; the busiest")
    big = []
    for z in range(0, 16):
        sp, sc = sum(s for s, _ in Psz[z]), sum(s for s, _ in Csz[z])
        mp = max(Psz[z], default=(0, "-")); mc = max(Csz[z], default=(0, "-"))
        big += [(s, t) for s, t in Psz[z] if s > 500_000]
        print(f"   z{z:<3} tiles {len(Psz[z]):>5}  patched {sp:>11,}  control {sc:>11,}  x{sp / max(sc, 1):.2f}"
              f"  largest {mp[0]:>8,} ({mp[1]}) vs {mc[0]:>8,}")
    allp = [x for z in Psz for x in Psz[z]]
    print(f"   tiles over 500 KB in patched: {len(big)}; busiest patched tile {max(allp)[0]:,} bytes ({max(allp)[1]})")
    print(f"\nsummary: {fails} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
