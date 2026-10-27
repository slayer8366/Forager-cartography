#!/usr/bin/env bash
# One G7 cell: hgt-name west south us ca dep-tile  ->  $G/hgt3/<name>.hgt (3", 1201^2), or <name>.empty.
# MRDEM first where the cell touches Canada, then 3DEP 1" on top, clipped to the US polygons.
# The grid is as in the elevation pilot (2026-10-26-elevation-pilot.md): cell centres on whole
# degrees, Int16, nodata -32768, averaged to 3".
set -uo pipefail
G=/mnt/archive/aspen-elevation-g7
MRDEM=/vsicurl/https://canelevation-dem.s3.ca-central-1.amazonaws.com/mrdem-30/mrdem-30-dtm.tif
BASE=https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current
export GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR CPL_VSIL_CURL_ALLOWED_EXTENSIONS=.tif GDAL_HTTP_MAX_RETRY=5 GDAL_HTTP_RETRY_DELAY=4
name=$1 w=$2 s=$3 us=$4 ca=$5 dep=$6
out=$G/hgt3/$name.hgt
[[ -s $out || -e $G/hgt3/$name.empty ]] && exit 0
# Never alongside the weekly build, and stopped well before Sunday's.
systemctl is-active --quiet forager-build-usca.service && exit 0
[[ $(date +%s) -lt $(date -d '2026-10-31 22:00 PDT' +%s) ]] || exit 0

t0=$(date +%s); tmp=$G/tmp/$name; rm -rf "$tmp"; mkdir -p "$tmp"; tif=$tmp/$name.tif
read -r xmin ymin xmax ymax < <(python3 -c "h=1.5/3600; print($w-h, $s-h, $w+1+h, $s+1+h)")
grid=(-t_srs EPSG:4326 -te "$xmin" "$ymin" "$xmax" "$ymax" -ts 1201 1201 -ot Int16 -dstnodata -32768)
src=()
fail() { echo "$name FAIL $*" >>"$G/logs/cells.log"; rm -rf "$tmp"; exit 1; }

if [[ $ca == 1 ]]; then
  gdalwarp -q -overwrite "${grid[@]}" -r average "$MRDEM" "$tif" 2>>"$tmp/err" || fail "mrdem $(tail -1 "$tmp/err")"
  src+=(mrdem)
fi
if [[ $dep != - ]]; then
  cog=$tmp/USGS_1_$dep.tif
  curl -sf --retry 5 --retry-delay 4 -o "$cog" "$BASE/$dep/USGS_1_$dep.tif" || fail "3dep download $dep"
  if [[ -e $tif ]]; then
    gdalwarp -q -r average -cutline "$G/usa-cutline.geojson" "$cog" "$tif" 2>>"$tmp/err" || fail "3dep warp $(tail -1 "$tmp/err")"
  else
    gdalwarp -q "${grid[@]}" -r average -cutline "$G/usa-cutline.geojson" "$cog" "$tif" 2>>"$tmp/err" || fail "3dep warp $(tail -1 "$tmp/err")"
  fi
  src+=("3dep:$dep:$(stat -c%s "$cog")")
  rm -f "$cog"
fi

valid=0
if [[ -e $tif ]]; then
  valid=$(gdalinfo -stats "$tif" 2>/dev/null | sed -n 's/.*STATISTICS_VALID_PERCENT=//p' | head -1)
  valid=${valid:-0}
fi
if python3 -c "import sys; sys.exit(0 if float('$valid') > 0 else 1)"; then
  gdal_translate -q -of SRTMHGT "$tif" "$tmp/$name.hgt" 2>>"$tmp/err" || fail "translate $(tail -1 "$tmp/err")"
  mv "$tmp/$name.hgt" "$out"
  stats=$(gdalinfo -stats "$tif" 2>/dev/null | sed -n 's/.*STATISTICS_\(MINIMUM\|MAXIMUM\)=/\1 /p' | tr '\n' ' ')
  echo "$name ok ${src[*]:-none} valid=$valid $stats $(( $(date +%s) - t0 ))s" >>"$G/logs/cells.log"
else
  touch "$G/hgt3/$name.empty"
  echo "$name empty ${src[*]:-none} $(( $(date +%s) - t0 ))s" >>"$G/logs/cells.log"
fi
rm -rf "$tmp"
