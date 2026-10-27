#!/usr/bin/env python3
"""Build reference-trails.pmtiles from the pages fetch.py saved (Aspen, 2026-10-26).

pages/*.json (Esri JSON) -> sources.gpkg (fs_trails, blm_trails) -> GDAL MVT, z10-15, MBTiles -> metadata
written in -> pmtiles convert. Field names are kept as the services spell them; trail_no stays text.
Nothing is joined to OSM. No upload here."""
import glob, json, os, re, sqlite3, subprocess, sys, datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))
run = lambda *a: subprocess.run(a, check=True)
GPKG, MBT, PMT = "sources.gpkg", "reference-trails.mbtiles", "reference-trails.pmtiles"
for f in (GPKG, MBT, PMT):
    if os.path.exists(f):
        os.remove(f)

expected = {"fs_trails": 0, "blm_trails": 0}
for path in sorted(glob.glob("pages/*.json")):
    stem = os.path.basename(path)[:-5]
    m = re.fullmatch(r"(fs|blm(\d))-\d{4}", stem)
    layer = "fs_trails" if m[1] == "fs" else "blm_trails"
    expected[layer] += len(json.load(open(path))["features"])
    extra = ["-sql", f'SELECT *, {m[2]} AS gtlf_layer FROM "{stem}"'] if m[2] else []
    run("ogr2ogr", "-f", "GPKG", "-update", "-append", GPKG, path, "-nln", layer,
        "-nlt", "MULTILINESTRING", "-t_srs", "EPSG:4326", *extra)

con = sqlite3.connect(GPKG)
got = {l: con.execute(f"SELECT COUNT(*) FROM {l}").fetchone()[0] for l in expected}
types = {l: {r[1]: r[2] for r in con.execute(f"PRAGMA table_info({l})")} for l in expected}
con.close()
print("features", got, "expected", expected, flush=True)
if got != expected:
    sys.exit("feature counts differ from the pages")
if not types["fs_trails"].get("trail_no", "").upper().startswith("TEXT"):
    sys.exit(f"trail_no is not text: {types['fs_trails'].get('trail_no')}")

# z15 is the archive's top zoom and must be: the Worker's overflow serves any z above maxzoom from the
# Protomaps basemap (index.ts:559-567 at Forager pre-main). Simplification is 0 at z15 (about 0.2 m a unit)
# and 2 units below it.
conf = {l: {"target_name": l, "minzoom": 10, "maxzoom": 15} for l in expected}
run("ogr2ogr", "-f", "MVT", MBT, GPKG, "fs_trails", "blm_trails",
    "-dsco", "FORMAT=MBTILES", "-dsco", "MINZOOM=10", "-dsco", "MAXZOOM=15",
    "-dsco", "SIMPLIFICATION=2", "-dsco", "SIMPLIFICATION_MAX_ZOOM=0",
    "-dsco", "NAME=reference-trails", "-dsco", "DESCRIPTION=Official trails: USFS TrailNFS_Publish and BLM GTLF",
    "-dsco", "CONF=" + json.dumps(conf))

sources = json.load(open("sources-meta.json"))
con = sqlite3.connect(MBT)
for k, v in {"attribution": "USDA Forest Service (CC BY 4.0); Bureau of Land Management",
             "forager_reference": json.dumps({"built_at": datetime.datetime.now(datetime.timezone.utc)
                                              .strftime("%Y-%m-%dT%H:%M:%SZ"), "sources": sources})}.items():
    con.execute("DELETE FROM metadata WHERE name = ?", (k,))
    con.execute("INSERT INTO metadata (name, value) VALUES (?, ?)", (k, v))
con.commit()
con.close()
run("pmtiles", "convert", MBT, PMT)
run("pmtiles", "show", PMT)
print("size", os.path.getsize(PMT))
