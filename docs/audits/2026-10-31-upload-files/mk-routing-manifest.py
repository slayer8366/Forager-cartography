#!/usr/bin/env python3
"""Routing manifest for R2 (routing/manifest.json) from a build output's manifest.json.
Usage: mk-routing-manifest.py OUT_DIR RUN_ID > manifest.json
Same shape as the hand-staged 261026 manifest: run_id, osm_timestamp, osm_sequence,
files (segments4 .rd5) and names (names1 .fnm), in the build manifest's order."""
import json, sys
out, run = sys.argv[1], sys.argv[2]
o = json.load(open(f"{out}/manifest.json"))
def ent(sub, ext):
    return [{"path": f"{run}/{sub}/{x['name']}", "size": x["size"], "sha256": x["sha256"]}
            for x in o["outputs"] if x["name"].endswith(ext)]
m = {"run_id": run,
     "osm_timestamp": o["osm"]["replication_timestamp"],
     "osm_sequence": o["osm"]["replication_sequence"],
     "files": ent("segments4", ".rd5"),
     "names": ent("names1", ".fnm")}
json.dump(m, sys.stdout, indent=1)

