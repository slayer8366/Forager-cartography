#!/bin/bash
# Read-only: list the parts of one multipart upload on R2 (ListParts), all pages.
# Usage: listparts.sh <upload-id> <out.xml-prefix>
set -euo pipefail
UID_="$1"; OUT="$2"
CONF=~/.config/rclone/rclone.conf
AK=$(awk '/^\[r2\]/{f=1;next} /^\[/{f=0} f && /^access_key_id/{print $3}' $CONF)
SK=$(awk '/^\[r2\]/{f=1;next} /^\[/{f=0} f && /^secret_access_key/{print $3}' $CONF)
EP=https://a6a899e01e2194ef8fff048c20130e14.r2.cloudflarestorage.com
ENC=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=""))' "$UID_")
marker=0; page=0
while :; do
  f="$OUT.$page.xml"
  printf 'user = "%s:%s"\n' "$AK" "$SK" | curl -sS -K - -H "x-amz-content-sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" --aws-sigv4 "aws:amz:auto:s3" --max-time 300 \
    "$EP/forager-maps/us.pmtiles?max-parts=1000&part-number-marker=$marker&uploadId=$ENC" -o "$f"
  trunc=$(grep -o '<IsTruncated>[a-z]*' "$f" | cut -d'>' -f2 || true)
  next=$(grep -o '<NextPartNumberMarker>[0-9]*' "$f" | cut -d'>' -f2 || true)
  page=$((page+1))
  [ "$trunc" = "true" ] && [ -n "$next" ] || break
  marker=$next
done
echo "pages: $page"
