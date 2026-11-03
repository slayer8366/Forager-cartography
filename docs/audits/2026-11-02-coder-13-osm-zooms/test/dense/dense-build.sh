#!/usr/bin/env bash
# coder-13 (a) (Willow, 2026-11-02): a dense-landuse extract built with the patched jar (0008) and with the installed
# one (0001-0007, the control), in this scratch folder only. Reads us-261030.osm.pbf and the build's sources; writes
# nothing outside this folder. Not under /srv/forager-build/out* or /mnt/storage.
#   dense-build.sh              cut the extract (once), then build both archives
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
JAVA=/opt/forager-build/jdk/bin/java
PATCHED_JAR=/home/bwann83/scratch/coder13/basemaps/tiles/target/protomaps-basemap-HEAD-with-deps.jar
CONTROL_JAR=/opt/forager-build/basemap/protomaps-basemap-HEAD-with-deps.jar
SRC_OSM=/srv/forager-build/sources/osm/us-261030.osm.pbf
AUX=/srv/forager-build/sources/aux
# 8/70/97, the live archive's largest tile (352,503 bytes, West Virginia), with its eight z8 neighbours (Aspen's (a)).
BBOX=-82.97,37.72,-78.75,40.98
log() { printf '%s %s\n' "$(TZ=America/Los_Angeles date '+%F %T %Z')" "$*"; }

log "patched jar $(sha256sum "$PATCHED_JAR" | cut -c1-16), control jar $(sha256sum "$CONTROL_JAR" | cut -c1-16)"
if [[ ! -s "$here/dense.osm.pbf" ]]; then
  log "osmium extract $BBOX from $SRC_OSM"
  nice -n 10 osmium extract -b "$BBOX" -s complete_ways "$SRC_OSM" -o "$here/dense.osm.pbf" --overwrite
fi
log "extract: $(stat -c %s "$here/dense.osm.pbf") bytes"

build() { # name jar
  local name="$1" jar="$2" dir="$here/$1"
  rm -rf -- "$dir/tmp"
  mkdir -p "$dir/data/sources"
  for f in natural_earth_vector.gpkg.zip water-polygons-split-3857.zip land-polygons-split-3857.zip \
    qrank.csv.gz pgf-encoding.zip; do
    ln -sfn "$AUX/$f" "$dir/data/sources/$f"
  done
  # A GeoPackage is SQLite, which writes a journal beside the file, so this one is a copy (the build's is only read).
  rm -f "$dir/data/sources/daylight-landcover.gpkg"
  cp "$AUX/daylight-landcover.gpkg" "$dir/data/sources/daylight-landcover.gpkg"
  ln -sfn "$here/dense.osm.pbf" "$dir/data/sources/dense.osm.pbf"
  log "planetiler: $name"
  (cd "$dir" && nice -n 10 "$JAVA" -Xmx3g -jar "$jar" --area=dense --bounds="$BBOX" --maxzoom=15 \
    --output="$dir/dense.pmtiles" --force --tmpdir="$dir/tmp" --storage=mmap --nodemap_storage=mmap \
    > "$dir/planetiler.log" 2>&1)
  rm -rf -- "$dir/tmp"
  log "$name: $(stat -c %s "$dir/dense.pmtiles") bytes, $(grep -c . "$dir/planetiler.log") log lines"
}
[[ "${ONLY:-}" == control ]] || build patched "$PATCHED_JAR"
[[ "${ONLY:-}" == patched ]] || build control "$CONTROL_JAR"
log "done"
