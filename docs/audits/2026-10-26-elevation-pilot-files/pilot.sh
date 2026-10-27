#!/usr/bin/env bash
# G6 elevation pilot (three-builds plan, build 3), owner's go 2026-10-26.
# Two whole 5-degree route squares, W125_N45 (coast, Olympics, Rainier) and W100_N40 (plains):
#   3DEP 1" COGs -> 1" .hgt (kept) and 3" .hgt -> BRouter .bef (3") -> the two .rd5 squares rebuilt
#   from the 261024 card extracts twice, without and with elevation, so the difference is measured.
# Everything is written under $W on the card. Nothing in the build tree, on the NVMe or on R2 is touched.
# Each step skips work already done, so the script can be re-run after a stop.
set -euo pipefail

W=/mnt/archive/aspen-elevation-pilot-20261026
JAVA=/opt/forager-build/jdk/bin/java
JAR=/opt/forager-build/brouter-1.7.10/brouter-1.7.10-all.jar
PROF=/opt/forager-build/brouter/profiles2
SRC=/mnt/archive/forager-build/sources-osm
BASE=https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current
FILTER=(w/highway w/railway w/waterway w/route r/route r/type=restriction)   # pins.env USCA_ROUTING_FILTER
# square:west:south ; band margin 1 degree as in pins.env, here in latitude too
SQUARES=("W125_N45:-125:45" "W100_N40:-100:40")

mkdir -p "$W"/{cog1,hgt1,hgt3,bef3,osm,logs,rd5}
log() { echo "$(TZ=America/Los_Angeles date '+%F %T %Z') $*" | tee -a "$W/logs/pilot.log"; }
# Elapsed time and the child's peak RSS (no /usr/bin/time on the Pi).
timed() {
  local name=$1; shift
  python3 - "$name" "$W/logs/times.log" "$@" <<'EOF'
import resource, subprocess, sys, time
name, out, cmd = sys.argv[1], sys.argv[2], sys.argv[3:]
t = time.time(); rc = subprocess.call(cmd); e = time.time() - t
peak = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
open(out, "a").write(f"{name}: {e:.1f} s, peak {peak} KB, rc {rc}\n")
sys.exit(rc)
EOF
}

# --- 1. 3DEP 1" downloads (named by their NW corner) ---
log "step 1: downloads"
for sq in "${SQUARES[@]}"; do
  IFS=: read -r name w s <<<"$sq"
  for ((lat = s; lat < s + 5; lat++)); do
    for ((lon = w; lon < w + 5; lon++)); do
      t=$(printf 'n%02dw%03d' $((lat + 1)) $((-lon)))
      f="$W/cog1/USGS_1_$t.tif"
      [[ -s "$f" || -e "$f.missing" ]] && continue
      code=$(curl -s -o "$f.part" -w '%{http_code}' --retry 4 --retry-delay 4 "$BASE/$t/USGS_1_$t.tif")
      if [[ $code == 200 ]]; then mv "$f.part" "$f"; else rm -f "$f.part"; echo "$code" >"$f.missing"; log "  $t: HTTP $code (no tile)"; fi
    done
  done
done
log "  $(ls "$W"/cog1/*.tif | wc -l) tiles, $(du -sb "$W/cog1" | cut -f1) bytes; $(ls "$W"/cog1/*.missing 2>/dev/null | wc -l) missing"

# --- 2. .hgt at 1" and 3" (named by SW corner, pixel-centre grid on whole degrees) ---
log "step 2: hgt"
for f in "$W"/cog1/USGS_1_*.tif; do
  t=$(basename "$f" .tif); t=${t#USGS_1_}
  lat=$((10#${t:1:2} - 1)); lon=$((-10#${t:4:3}))
  h=$(printf 'N%02dW%03d.hgt' "$lat" $((-lon)))
  for res in 1 3; do
    out="$W/hgt$res/$h"; [[ -s "$out" ]] && continue
    n=$(( res == 1 ? 3601 : 1201 )); r=$(( res == 1 ? 0 : 1 ))
    half=$(python3 -c "print($res/7200)")
    te=$(python3 -c "print($lon-$half, $lat-$half, $lon+1+$half, $lat+1+$half)")
    timed "warp-$res-$h" gdalwarp -q -overwrite -t_srs EPSG:4326 -te $te -ts $n $n \
      -r $([[ $res == 1 ]] && echo bilinear || echo average) -ot Int16 -dstnodata -32768 "$f" "$W/hgt$res/$h.tif"
    gdal_translate -q -of SRTMHGT "$W/hgt$res/$h.tif" "$out"
    rm -f "$W/hgt$res/$h.tif" "$W/hgt$res/$h.aux.xml"
  done
done
log "  hgt1 $(du -sb "$W/hgt1" | cut -f1) bytes, hgt3 $(du -sb "$W/hgt3" | cut -f1) bytes"

# --- 3. .bef at 3" ---
log "step 3: bef"
if ! ls "$W"/bef3/*.bef >/dev/null 2>&1; then
  timed "bef-convert-3" "$JAVA" -Xmx2g -cp "$JAR" btools.mapcreator.ElevationRasterTileConverter all "$W/hgt3" "$W/bef3" 3 \
    >"$W/logs/bef.log" 2>&1
fi
log "  $(ls -l "$W"/bef3/ | tail -n +2)"

# --- 4. OSM cut per square from the 261024 extracts, filtered as the build does ---
log "step 4: osm cuts"
for sq in "${SQUARES[@]}"; do
  IFS=: read -r name w s <<<"$sq"
  out="$W/osm/$name-routing.osm.pbf"; [[ -s "$out" ]] && continue
  parts=()
  for x in us canada; do
    p="$W/osm/$name-$x.osm.pbf"
    timed "extract-$name-$x" osmium extract -b "$((w - 1)),$((s - 1)),$((w + 6)),$((s + 6))" -s complete_ways --overwrite \
      -o "$p" "$SRC/$x-261024.osm.pbf"
    timed "filter-$name-$x" osmium tags-filter --overwrite "$p" "${FILTER[@]}" -o "$p.f.osm.pbf"
    rm -f "$p"; parts+=("$p.f.osm.pbf")
  done
  timed "merge-$name" osmium merge --overwrite "${parts[@]}" -o "$out"
  rm -f "${parts[@]}"
  log "  $name: $(stat -c%s "$out") bytes"
done

# --- 5. BRouter's three steps, without and with elevation ---
log "step 5: brouter"
bjava=("$JAVA" -Xmx4g -cp "$JAR")
mkdir -p "$W/no-elevation"
for sq in "${SQUARES[@]}"; do
  IFS=: read -r name w s <<<"$sq"
  for mode in none bef3; do
    dest="$W/rd5/$mode/$name.rd5"; [[ -s "$dest" ]] && continue
    elev=$([[ $mode == none ]] && echo "$W/no-elevation" || echo "$W/bef3")
    br="$W/br-$name-$mode"; rm -rf "$br"; mkdir -p "$br"/{nodetiles,waytiles,waytiles55,nodes55,unodes55,segments} "$W/rd5/$mode"
    (cd "$br" && timed "cut-$name-$mode" "${bjava[@]}" -Ddeletetmpfiles=true btools.mapcreator.OsmFastCutter \
      "$PROF/lookups.dat" nodetiles waytiles nodes55 waytiles55 bordernids.dat relations.dat restrictions.dat \
      "$PROF/all.brf" "$PROF/trekking.brf" "$PROF/softaccess.brf" "$W/osm/$name-routing.osm.pbf") >"$W/logs/br-$name-$mode.log" 2>&1
    (cd "$br" && timed "unify-$name-$mode" "${bjava[@]}" -Ddeletetmpfiles=true btools.mapcreator.PosUnifier \
      nodes55 unodes55 bordernids.dat bordernodes.dat "$elev") >>"$W/logs/br-$name-$mode.log" 2>&1
    (cd "$br" && timed "link-$name-$mode" "${bjava[@]}" -DskipEncodingCheck=true btools.mapcreator.WayLinker \
      unodes55 waytiles55 bordernodes.dat restrictions.dat "$PROF/lookups.dat" "$PROF/all.brf" segments rd5) >>"$W/logs/br-$name-$mode.log" 2>&1
    mv "$br/segments/$name.rd5" "$dest"
    rm -rf "$br"
    log "  $name $mode: $(stat -c%s "$dest") bytes"
  done
done
log "done"
