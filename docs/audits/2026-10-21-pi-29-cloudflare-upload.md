# pi-29: back up the live map, upload the 261021 US + Canada map to R2, test it

Dispatch: `prompts/preserved/2026-10-21-pi-29.md` (Aspen Meridian to Willow Quadrat, 2026-10-21).
Status: **stopped at A.3, waiting for the owner.** Step A ran in full (read-only). Steps B, C
and D have not started. Nothing was written to R2.

Times are UTC. The Pi's clock read `Thu Oct 22 01:31:53 AM UTC 2026` at the start of step A
(local 2026-10-21 18:31).

## A. Prep (read-only)

### A.1 Local file — matches

- `/srv/forager-build/out-usca/current` resolves to
  `/srv/forager-build/out-usca/20261017T202051Z-usca-20261021T111429Z`.
- `forager-usca.pmtiles` is 34,141,705,380 bytes.
- `/srv/forager-build/status-usca.json`: `state` ok, `stage` done, `run_id`
  usca-20261021T111429Z, `warnings` empty, `last_success.at` 2026-10-22T00:06:26Z,
  `osm_timestamp` 2026-10-17T20:20:51Z.
- sha256 (`sha256sum`, run in step A):
  `ad9c0f2dd86eb48fb56bf2bc416e602bed46443a6c6f30a5ed5810041fbd40aa`.
  This equals the sha256 the build recorded for `forager-usca.pmtiles` in that output's
  `manifest.json` (`outputs[0]`, with size 34141705380). The two were computed independently
  (the build's at write time, this one now), so the file has not changed since the build.

### A.2 Live object — matches

- `rclone lsl r2:forager-maps/us.pmtiles`:
  `33973424728 2026-10-19 02:16:46.438514719 us.pmtiles`.
- `rclone backend list-multipart-uploads r2:forager-maps`: `{"forager-maps": []}` (empty).
  It took about 2.5 minutes to return; noted, not a problem.

### A.3 Buckets — DOES NOT MATCH, stop

- `rclone lsd r2:` failed: `operation error S3: ListBuckets, https response error StatusCode: 403
  ... api error AccessDenied: Access Denied`. **The buckets could not be listed.**
- To see whether `forager-maps-backup` exists, a read-only `rclone lsf r2:forager-maps-backup`
  was tried. It also returned 403 AccessDenied (`ListObjectsV2`), not `NoSuchBucket`.
  **Whether `forager-maps-backup` exists could not be determined.**

Inferred, not confirmed: the R2 token in `~/.config/rclone/rclone.conf` (remote `r2`, rclone
v1.75.1, provider Cloudflare) is scoped to specific buckets, so it can read and write
`forager-maps` but not list buckets or reach any other bucket. Cloudflare R2 returns 403
for a bucket outside a token's scope whether or not it exists, which would explain both
results. If so, `rclone mkdir r2:forager-maps-backup` (B.1) would also be refused, and a bucket
the owner creates in the dashboard would still be out of reach until the token is given access
to it (or a new token is issued). Not tried: `rclone mkdir` was not run, because A says a
mismatch is a stop before B.

### A.4 Processes — matches

`pgrep -af 'planetiler|osmium|brouter|rclone'`: none running (other than the checks themselves).

### A.5 Network — reported, not changed

- `ip route show default`:
  - `default via 10.0.0.1 dev wlan0 proto dhcp src 10.0.0.115 metric 600`
  - `default via 10.180.71.229 dev bnep0 proto dhcp src 10.180.71.146 metric 750`
  (Wi-Fi primary, Bluetooth tether as the backup route.)
- `ping -c 10 1.1.1.1`: 10/10 received, 0% loss, rtt min/avg/max/mdev
  11.040/18.413/29.923/4.932 ms.
- `iw dev wlan0 link`: SSID Virusdownloader, signal -68 dBm, rx bitrate 130.0 MBit/s, tx bitrate
  234.0 MBit/s.

### A.6 Is the failed 2026-10-19 basemap a copy of the live release? — **matches**

`/srv/forager-build/kept-usca/usca-20261019T011311Z/forager-usca.pmtiles` is 33,973,424,728
bytes, the same as the live object. Five 16 MiB (16,777,216-byte) ranges compared: local via
`dd ... iflag=skip_bytes,count_bytes`, R2 via `rclone cat --offset --count`, sha256 of each side.
Middle offsets are 1/4, 1/2 and 3/4 of the size, rounded down to a 16 MiB boundary.

| offset | sha256 (both sides) | result |
|---|---|---|
| 0 | af84f40f23a77e654ac76fb3816889aa50f4088442add75e76057fb17668cb63 | match |
| 8,489,271,296 | e95c3036d63123c6b0583e50d9d7ff87033ebef8b5302e8a1e08af87f91dc5a6 | match |
| 16,978,542,592 | b5ec908ad2c82c621652eaa8557f8d198aad293079c1d0faed21dd1f4e562725 | match |
| 25,467,813,888 | d5719ed3c6ec3a7f128220bdb40bca86225523f7a2266264941e4e5707ecc9ae | match |
| 33,956,647,512 (last 16 MiB) | 06c48a42f762f6fbef605fd3204a84f2a7a5b8a4a4a5b32ef92a28eb88384c1f | match |

Each range's hash is different from the others and none is the empty-input hash, so no range
compared two empty reads. This is a sample of 80 MiB out of about 31.6 GiB, not a full-file
comparison: "matches" on every range sampled. If it is a full copy, the local file is a second
backup of the live release in addition to the one B would make.

## Not done

- B, C, D: not started. Nothing created, copied, uploaded or deleted on R2 or on the Pi, apart
  from creating `/home/bwann83/pi29-logs/` (which B.2 asks for) and writing
  `local-sha256.txt` there.
- Nothing written to Forager's pi-build.

## Question for the owner

The R2 token can't list buckets or see `forager-maps-backup`. Options, owner's call:

1. Create `forager-maps-backup` in the Cloudflare dashboard (private, no Worker binding, no
   public access) **and** give the Pi's R2 token Object Read & Write on it (or issue a new
   token covering both buckets and put it in the Pi's rclone config). Then B runs as written.
2. Let me try `rclone mkdir r2:forager-maps-backup` anyway. Expected to fail with 403 if the
   token is bucket-scoped; harmless if it does.
3. Back up inside `forager-maps` instead (e.g. `forager-maps/backup/us-20261017T202051Z.pmtiles`),
   which the token can already write. Not in the dispatch, and it puts the backup in the bucket the
   Worker serves from, so its key could be reachable through the Worker depending on how the
   Worker maps paths (not checked).
