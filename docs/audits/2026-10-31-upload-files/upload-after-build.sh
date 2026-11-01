#!/usr/bin/env bash
# Aspen, 2026-10-31, owner's go: "Make sure everything we need to upload to R2 is uploaded also".
# Waits for the early run usca-20261031T193102Z to finish OK, then uploads, in order:
#   1. routing: segments4 + names1 under routing/<run>/, read back, counts; then routing/manifest.json last.
#   2. tiles: forager-usca.pmtiles -> us.pmtiles (live overwrite; rollback copy of the live file is
#      /mnt/storage/rollback/usca-20261017T202051Z-usca-20261021T111429Z/forager-usca.pmtiles).
# Stops at the first mismatch. Never sends the manifest after a failed read-back.
set -euo pipefail
RUN=usca-20261101T174337Z
U=/mnt/archive/aspen-upload-next; L=$U/upload.log; ST=/srv/forager-build/status-usca.json
log() { echo "$(TZ=America/Los_Angeles date '+%F %T %Z') $*" | tee -a $L; }
die() { log "STOP: $*"; exit 1; }

# Upload only over Wi-Fi: never push tens of GB through the phone/tablet tether (bnep0).
wait_wifi() {
  while ! ip route show default | head -1 | grep -q 'dev wlan0'; do
    log "waiting for Wi-Fi (default route: $(ip route show default | head -1))"; sleep 600
  done
}
st() { python3 -c "import json;d=json.load(open('$ST'));print(d.get('$1') or '')"; }

log "waiting for $RUN"
while :; do
  r=$(st run_id); s=$(st state); g=$(st stage)
  [[ $r == "$RUN" ]] || die "status run_id is $r, not $RUN"
  [[ $s == failed ]] && die "the run failed at stage $g: $(st message)"
  [[ $s == ok && $g == done ]] && break
  sleep 300
done
O=$(python3 -c "import json;print(json.load(open('$ST'))['last_success']['output'])")
LR=$(python3 -c "import json;print(json.load(open('$ST'))['last_success']['run_id'])")
[[ $LR == "$RUN" ]] || die "last_success is $LR"
w=$(python3 -c "import json;print(len(json.load(open('$ST'))['last_success']['warnings']))")
log "run done OK: output $O, warnings $w"
[[ $w == 0 ]] || die "the run has warnings; owner to look first"

python3 $U/mk-routing-manifest.py "$O" "$RUN" > $U/manifest.json
nf=$(python3 -c "import json;print(len(json.load(open('$U/manifest.json'))['files']))")
nn=$(python3 -c "import json;print(len(json.load(open('$U/manifest.json'))['names']))")
a=$(ls "$O"/segments/*.rd5 | wc -l); b=$(ls "$O"/names1/*.fnm | wc -l)
log "manifest: files $nf names $nn; local rd5 $a fnm $b"
[[ $nf == "$a" && $nn == "$b" && $nf -gt 150 ]] || die "manifest and output disagree"

# 1. routing
wait_wifi
D=r2:forager-maps/routing/$RUN
rclone cat r2:forager-maps/routing/manifest.json > $U/manifest-before.json
log "routing before: $(rclone lsf r2:forager-maps/routing/ | tr '\n' ' ')"
log "upload segments4"; rclone copy "$O/segments" $D/segments4 --include '*.rd5' --transfers 4 -q
log "upload names1";    rclone copy "$O/names1"   $D/names1    --include '*.fnm' --transfers 4 -q
log "read-back segments4"; rclone check "$O/segments" $D/segments4 --include '*.rd5' --download --one-way 2>&1 | tail -2 | tee -a $L
log "read-back names1";    rclone check "$O/names1"   $D/names1    --include '*.fnm' --download --one-way 2>&1 | tail -2 | tee -a $L
rclone check "$O/segments" $D/segments4 --include '*.rd5' --one-way -q || die "segments4 differ"
rclone check "$O/names1"   $D/names1    --include '*.fnm' --one-way -q || die "names1 differ"
a=$(rclone lsf --files-only $D/segments4 | grep -c '\.rd5$'); b=$(rclone lsf --files-only $D/names1 | grep -c '\.fnm$')
log "counts on R2: segments4 $a, names1 $b"
[[ $a == "$nf" && $b == "$nn" ]] || die "count mismatch, manifest not sent"
log "manifest"; rclone copyto $U/manifest.json r2:forager-maps/routing/manifest.json --header-upload 'Content-Type: application/json' -q
a=$(sha256sum $U/manifest.json | cut -c1-64); b=$(rclone cat r2:forager-maps/routing/manifest.json | sha256sum | cut -c1-64)
log "manifest sha local $a r2 $b"; [[ $a == "$b" ]] || die "manifest mismatch"
log "routing live: $RUN"

# 2. tiles
wait_wifi
P="$O/forager-usca.pmtiles"
want=$(python3 -c "import json;o=json.load(open('$O/manifest.json'));print([x['sha256'] for x in o['outputs'] if x['name']=='forager-usca.pmtiles'][0])")
have=$(sha256sum "$P" | cut -c1-64)
log "pmtiles sha256 local $have, build manifest $want"; [[ $have == "$want" ]] || die "pmtiles changed since the build"
mp=$(rclone backend list-multipart-uploads r2:forager-maps 2>&1 | tr -d ' \n')
log "multipart before: $mp"
log "tiles before: $(rclone lsl r2:forager-maps/us.pmtiles)"
log "upload us.pmtiles ($(stat -c %s "$P") B)"
rclone copyto "$P" r2:forager-maps/us.pmtiles --s3-chunk-size 64M --s3-upload-concurrency 4 \
  --header-upload 'Content-Type: application/octet-stream' --low-level-retries 30 --retries 1 -v 2>&1 | grep -E 'Copied|ERROR|NOTICE' | tee -a $L
log "tiles after: $(rclone lsl r2:forager-maps/us.pmtiles)"
rs=$(rclone lsjson r2:forager-maps/us.pmtiles | python3 -c "import json,sys;print(json.load(sys.stdin)[0]['Size'])")
[[ $rs == "$(stat -c %s "$P")" ]] || die "us.pmtiles size on R2 is $rs"
lm=$(md5sum "$P" | cut -c1-32); rm5=$(rclone md5sum r2:forager-maps/us.pmtiles | cut -c1-32)
log "us.pmtiles md5 local $lm r2 $rm5"; [[ $lm == "$rm5" ]] || die "us.pmtiles md5 mismatch"
h1=$(head -c 1048576 "$P" | sha256sum | cut -c1-64); h2=$(rclone cat --count 1048576 r2:forager-maps/us.pmtiles | sha256sum | cut -c1-64)
log "first MiB sha local $h1 r2 $h2"; [[ $h1 == "$h2" ]] || die "header mismatch"
log "DONE: routing $RUN and us.pmtiles live"
