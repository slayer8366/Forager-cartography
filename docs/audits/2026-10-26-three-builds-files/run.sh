#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
tm() { local l="$1"; shift; local t0=$SECONDS; "$@"; echo "$l: $((SECONDS-t0)) s"; }
A=/mnt/archive/forager-build/sources-osm
for s in us canada; do
  tm "$s highway" osmium tags-filter $A/$s-261024.osm.pbf w/highway -o $s-hw.osm.pbf --overwrite
  tm "$s named" osmium tags-filter $s-hw.osm.pbf w/name w/ref -o $s-named.osm.pbf --overwrite
  rm -f $s-hw.osm.pbf
done
tm "merge" osmium merge us-named.osm.pbf canada-named.osm.pbf -o named.osm.pbf --overwrite
cat > sq.json <<'J'
{"directory": ".", "extracts": [
 {"output": "W75_N40.osm.pbf",  "bbox": [-75.1, 39.9, -69.9, 45.1]},
 {"output": "W120_N45.osm.pbf", "bbox": [-120.1, 44.9, -114.9, 50.1]}]}
J
tm "squares" osmium extract -c sq.json -s complete_ways --overwrite named.osm.pbf
ls -l *.pbf
