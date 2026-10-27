#!/bin/bash
# One square per pass: two at once with complete_ways reached 7.4 GB and was OOM-killed (17:09).
set -euo pipefail
cd "$(dirname "$0")"
cut() { local t0=$SECONDS; osmium extract -b "$2" -s complete_ways --overwrite -o "$1.osm.pbf" named.osm.pbf; echo "$1 cut: $((SECONDS-t0)) s"; }
cut W75_N40 -75.1,39.9,-69.9,45.1
cut W120_N45 -120.1,44.9,-114.9,50.1
for s in W75_N40 W120_N45; do
  t0=$SECONDS
  osmium export -f geojsonseq -x print_record_separator=false --overwrite -o $s.geojsonseq $s.osm.pbf
  python3 fnam_measure.py $s $s.fnm < $s.geojsonseq > $s.json
  echo "$s encode: $((SECONDS-t0)) s"; cat $s.json
done
