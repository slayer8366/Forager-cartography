#!/usr/bin/env bash
set -euo pipefail
RUN=usca-20261025T101217Z; D=r2:forager-maps/routing/$RUN
SEG=/srv/forager-build/out-usca/current/segments; NM=/mnt/archive/aspen-names-261024/names1
L=/mnt/archive/aspen-upload-261024/upload.log
log() { echo "$(TZ=America/Los_Angeles date '+%F %T %Z') $*" | tee -a $L; }
log "before: $(rclone lsf r2:forager-maps/routing/ | tr '\n' ' ')"
log "upload segments4"; rclone copy $SEG $D/segments4 --include '*.rd5' --transfers 4 -q
log "upload names1";    rclone copy $NM  $D/names1    --include '*.fnm' --transfers 4 -q
log "read-back segments4"; rclone check $SEG $D/segments4 --download --one-way 2>&1 | tail -2 | tee -a $L
log "read-back names1";    rclone check $NM  $D/names1    --download --one-way 2>&1 | tail -2 | tee -a $L
log "counts: segments4 $(rclone lsf $D/segments4 | wc -l), names1 $(rclone lsf $D/names1 | wc -l)"
log "manifest"; rclone copyto /mnt/archive/aspen-upload-261024/manifest.json r2:forager-maps/routing/manifest.json --header-upload 'Content-Type: application/json' -q
log "manifest live"
a=$(sha256sum /mnt/archive/aspen-upload-261024/manifest.json | cut -c1-64); b=$(rclone cat r2:forager-maps/routing/manifest.json | sha256sum | cut -c1-64)
log "manifest sha local $a r2 $b"
[[ $a == $b ]] && log "done" || { log "MANIFEST MISMATCH"; exit 1; }
