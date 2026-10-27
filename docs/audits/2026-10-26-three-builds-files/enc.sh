#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
for s in W75_N40 W120_N45; do
  t0=$SECONDS
  [ -s $s.geojsonseq ] && [ $s.geojsonseq -nt $s.osm.pbf ] || osmium export -f geojsonseq -x print_record_separator=false --overwrite -o $s.geojsonseq $s.osm.pbf
  python3 fnam_measure.py $s $s.fnm < $s.geojsonseq > $s.json
  echo "$s encode: $((SECONDS-t0)) s"; cat $s.json
done
