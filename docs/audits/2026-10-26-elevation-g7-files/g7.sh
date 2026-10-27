#!/usr/bin/env bash
# G7, the full 3" elevation store for the 187 route squares (owner's "Go on G7", 2026-10-26).
# cells.tsv (from cells.py) -> cell.sh per cell, 3 at a time -> BRouter's converter -> .bef per square.
# Written on the card under $G. 1" .hgt is not kept: the USB storage drive is not mounted.
# Resumable: done cells are skipped. Stops itself if the weekly build starts, and before Sat 22:00 PDT.
set -euo pipefail
G=/mnt/archive/aspen-elevation-g7
here="$(cd "$(dirname "$0")" && pwd)"
JAVA=/opt/forager-build/jdk/bin/java
JAR=/opt/forager-build/brouter-1.7.10/brouter-1.7.10-all.jar
mkdir -p "$G"/{hgt3,bef3,tmp,logs}
log() { echo "$(TZ=America/Los_Angeles date '+%F %T %Z') $*" | tee -a "$G/logs/g7.log"; }

log "cells: $(wc -l <"$G/cells.tsv"); already done: $(ls "$G/hgt3" | wc -l)"
# nice/ionice: the names run shares the card.
nice -n 10 ionice -c3 xargs -P 3 -L 1 "$here/cell.sh" <"$G/cells.tsv" || true
done_n=$(ls "$G"/hgt3/*.hgt "$G"/hgt3/*.empty 2>/dev/null | wc -l)
fails=$(grep -c ' FAIL ' "$G/logs/cells.log" || true)
log "cells done: $done_n of $(wc -l <"$G/cells.tsv") ($(ls "$G"/hgt3/*.hgt | wc -l) hgt, $(ls "$G"/hgt3/*.empty 2>/dev/null | wc -l) empty); FAIL lines: $fails"
[[ $done_n -eq $(wc -l <"$G/cells.tsv") ]] || { log "not all cells done; re-run to resume"; exit 1; }

log "convert"
rm -rf "$G/bef3.new"; mkdir -p "$G/bef3.new"
"$JAVA" -Xmx2g -cp "$JAR" btools.mapcreator.ElevationRasterTileConverter all "$G/hgt3" "$G/bef3.new" 3 >"$G/logs/convert.log" 2>&1
rm -rf "$G/bef3"; mv "$G/bef3.new" "$G/bef3"
log "bef: $(ls "$G"/bef3/*.bef | wc -l) files, $(du -sb "$G/bef3" | cut -f1) bytes"
log "done"
