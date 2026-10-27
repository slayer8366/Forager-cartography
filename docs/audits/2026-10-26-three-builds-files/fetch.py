#!/usr/bin/env python3
"""Fetch the two official trail services to local Esri JSON pages (Aspen, 2026-10-26).
All object ids are listed first (returnIdsOnly), then fetched in ranges of 1000, four at a time.
Coordinates come at 6 decimals (geometryPrecision=6, about 0.1 m; a z15 tile unit is about 0.2 m).
Resumable: a page on disk is kept. Each page's ids must equal its range's ids exactly.
(Offset paging timed out at 32,000 rows on the FS service; keyset paging ran about a minute a page.)"""
import json, os, sys, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
FS = "https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_TrailNFSPublish_01/MapServer/0"
BLM = "https://gis.blm.gov/arcgis/rest/services/transportation/BLM_Natl_GTLF_Public_Display/MapServer"
JOBS = [("fs", FS, "objectid", "objectid,trail_no,trail_name,trail_type,trail_class,attributesubset,admin_org")] + \
       [(f"blm{l}", f"{BLM}/{l}", "OBJECTID", "OBJECTID,ROUTE_PRMRY_NM,FAMS_ID,ADMIN_ST") for l in (2, 3, 4, 5, 6)]
PAGE, WORKERS = 1000, 4
UA = {"User-Agent": "forager-cartography reference-trails build"}


def get(base, params):
    url = f"{base}/query?" + urllib.parse.urlencode(params)
    for attempt in range(7):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
                d = json.load(r)
            if "error" in d:
                raise RuntimeError(d["error"])
            return d
        except Exception as e:
            print(f"  retry {attempt + 1} {base[-30:]}: {e}", flush=True)
            time.sleep(2 ** attempt)
    raise SystemExit(f"gave up: {url}")


os.makedirs("pages", exist_ok=True)
for name, base, oid, fields in JOBS:
    ids = sorted(get(base, {"where": "1=1", "returnIdsOnly": "true", "f": "json"})["objectIds"])
    count = get(base, {"where": "1=1", "returnCountOnly": "true", "f": "json"})["count"]
    if len(ids) != count:
        sys.exit(f"{name}: {len(ids)} ids but count {count}")
    chunks = [ids[i:i + PAGE] for i in range(0, len(ids), PAGE)]

    def one(k):
        path, want = f"pages/{name}-{k:04d}.json", chunks[k]
        if not os.path.exists(path):
            d = get(base, {"where": f"{oid} >= {want[0]} AND {oid} <= {want[-1]}", "outFields": fields,
                           "outSR": 4326, "geometryPrecision": 6, "f": "json", "orderByFields": oid,
                           "resultRecordCount": PAGE + 1})
            json.dump(d, open(path + ".part", "w"))
            os.rename(path + ".part", path)
        got = [f["attributes"][oid] for f in json.load(open(path))["features"]]
        if got != want:
            raise SystemExit(f"{name} page {k}: ids differ from its range")
        return len(got)

    with ThreadPoolExecutor(WORKERS) as ex:
        total = sum(ex.map(one, range(len(chunks))))
    print(f"{name}: {total} of {count} features in {len(chunks)} pages", flush=True)
