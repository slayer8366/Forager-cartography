#!/usr/bin/env bash
# coder-13 Z2 test 1 (Willow, 2026-11-02): a Molalla extract built with the patched jar (0008) and with the installed
# one (0001-0007, the control), in this scratch folder only. Reads us-261030.osm.pbf and the build's sources; writes
# nothing outside this folder. Not under /srv/forager-build/out* or /mnt/storage.
#   molalla-build.sh            cut the extract (once), then build both archives
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
JAVA=/opt/forager-build/jdk/bin/java
PATCHED_JAR=/home/bwann83/scratch/coder13/basemaps/tiles/target/protomaps-basemap-HEAD-with-deps.jar
CONTROL_JAR=/opt/forager-build/basemap/protomaps-basemap-HEAD-with-deps.jar
SRC_OSM=/srv/forager-build/sources/osm/us-261030.osm.pbf
AUX=/srv/forager-build/sources/aux
# Molalla, Liberal, Oregon City and the Molalla River's valley, with the Cascade foothills for peaks, huts and lakes.
BBOX=-122.95,44.95,-122.25,45.40
log() { printf '%s %s\n' "$(TZ=America/Los_Angeles date '+%F %T %Z')" "$*"; }

log "patched jar $(sha256sum "$PATCHED_JAR" | cut -c1-16), control jar $(sha256sum "$CONTROL_JAR" | cut -c1-16)"
if [[ ! -s "$here/molalla.osm.pbf" ]]; then
  log "osmium extract $BBOX from $SRC_OSM"
  nice -n 10 osmium extract -b "$BBOX" -s complete_ways "$SRC_OSM" -o "$here/molalla.osm.pbf" --overwrite
fi
log "extract: $(stat -c %s "$here/molalla.osm.pbf") bytes"

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
  ln -sfn "$here/molalla.osm.pbf" "$dir/data/sources/molalla.osm.pbf"
  log "planetiler: $name"
  (cd "$dir" && nice -n 10 "$JAVA" -Xmx2g -jar "$jar" --area=molalla --bounds="$BBOX" --maxzoom=15 \
    --output="$dir/molalla.pmtiles" --force --tmpdir="$dir/tmp" --storage=mmap --nodemap_storage=mmap \
    > "$dir/planetiler.log" 2>&1)
  rm -rf -- "$dir/tmp"
  log "$name: $(stat -c %s "$dir/molalla.pmtiles") bytes, $(grep -c . "$dir/planetiler.log") log lines"
}
build patched "$PATCHED_JAR"
build control "$CONTROL_JAR"
log "done"
