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

## Records-repo setup

The clone at `/home/bwann83/forager-cartography` had no git identity and an HTTPS remote with no
credentials on the Pi, so the first commit and push failed. Repo-local `user.name slayer8366` and
`user.email armyofwann@gmail.com` were set, copied from `/home/bwann83/Forager/.git/config`. The
coder's attempt to change `origin` to `git@github.com:slayer8366/forager-cartography.git` (the
same SSH form as the Forager clone) was refused by the session's permission check. The owner then
ran that `set-url` by hand, but `git remote -v` afterwards still showed the HTTPS URL, so the push
failed again. Commits `ac1549e` and `9748ddf` (and this one) are local only, waiting on the remote.

## Amendment from Aspen Meridian (received 2026-10-21, via cross-session message)

Received from session `forager-f9` (Aspen), summarised point by point; the owner quote is verbatim
as relayed by Aspen:

> The owner, 2026-10-21, verbatim, on the backup: "I'm going to have that overwritten on
> cloudflare. I don't care to do that work."

1. Step B is dropped: no backup bucket, no mkdir, no server-side copy. The live `us.pmtiles` is
   overwritten with no R2 backup. Options 2 and 3 are not taken.
2. Reason step B became moot: the A.3 403. The R2 token cannot list buckets or reach
   `forager-maps-backup`, so B would first have needed dashboard and token work, which the owner
   declined.
3. Step C runs as written, under pi-29's original go.
4. D.3 changes: record the `X-Forager-Origin` header actually returned rather than expecting `r2`.
   Checked read-only: `server/pmtiles-worker/src/index.ts` in the Forager clone (branch checked out
   there at `a88f17ad0`; whether that is what is deployed is not checked) tries the Pi's
   `pmtiles serve` first, falls back to R2 on anything but 200/204, and its comment gives the Pi
   a z14 ceiling, so z15 tiles are expected from R2.
5. Rollback source, if one is needed:
   `/srv/forager-build/kept-usca/usca-20261019T011311Z/forager-usca.pmtiles`. It matched the live
   object on 5 x 16 MiB samples (A.6), **not** on a full comparison. It is not to be deleted until
   the owner has tested the new map in the app.
6. Repo rename: the remote URL stays as it is; the redirect to `slayer8366/Forager-cartography` is
   noted above. Changing it is a separate change for the owner to approve.

Coder's note: overwriting the live object without a backup on R2 is not reversible from R2. Before
starting C, the coder is confirming the owner's ruling with the owner directly in the coder's own
session, because it arrived second-hand.

## Remote renamed

The owner told Aspen "Change the local". Aspen ran
`git remote set-url origin git@github.com:slayer8366/Forager-cartography.git` and checked it with
`ls-remote` (main at `03a5468`). This replaces the note above that the URL was left unchanged.

## Owner's ruling on the overwrite, and the full comparison

Asked directly in the coder's session whether to overwrite the live object with no R2 backup,
the owner chose "Full-compare first": confirm, before uploading, that the rollback source
(`kept-usca/usca-20261019T011311Z/forager-usca.pmtiles`) is identical to the live
`r2:forager-maps/us.pmtiles` in full. The owner then said "Go ahead and upload after match", and
then **"Stop after the comparison. I'm switching to the cartography folder"**, which replaces it:
**step C is not started and waits for a new go**, whatever the comparison shows.

The comparison (`/home/bwann83/pi29-logs/fullcompare.sh`, read-only, detached with `setsid`) was
started at 2026-10-22T02:04:09Z. It streams the whole live object with `rclone cat` through
sha256, md5 and a byte count, without writing it to disk, at about 4 MB/s (roughly 2 h).

- Local 10-19 file (done): md5 `72e98faabc44c4f47e32927e57a6c380`, sha256
  `bbc0b65859e69808a51dd29c0441b521770e4a1c736350236de1b91ac915a272`.
- R2's stored md5 for `us.pmtiles` (`rclone hashsum md5`): `72e98faabc44c4f47e32927e57a6c380`,
  equal to the local file's. This is metadata recorded at upload time, not a read of the bytes.
- Live object streamed: **pending at this commit.** Results land in `pi29-logs/r2-live.sha256`,
  `r2-live.md5` and `r2-live.bytes`; `fullcompare.status` gets the pipeline exit code and a
  `done` line; errors go to `fullcompare-rclone.log`. A match needs all of: exit 0, bytes
  33973424728, and the sha256 and md5 equal to the local file's above.

---

Entries below were written by the planner session `forager-cartography-7b` on 2026-10-22, from the
Pi's logs and unit state, which it read at 11:51Z (04:51 PDT) unless an entry says otherwise. Earlier text in this
file is left as it was; where an entry below changes something above, it says so. The Pi's logs are
in PDT; this record gives UTC first and PDT in brackets.

## Status (supersedes the Status line at the top)

**C done; D done except the owner's in-app test.** The 261021 map is the live
`r2:forager-maps/us.pmtiles`. The first upload failed, a re-run was started and then stopped, and the
first upload's multipart upload was resumed and completed. Details follow.

## Full comparison: result (closes "Live object streamed: pending" above)

`pi29-logs/fullcompare.status`: `start 2026-10-22T02:04:09Z`, `r2 pipeline exit=0 2026-10-22T05:30:42Z`,
`done 2026-10-22T05:30:47Z` (22:30:47 PDT on 10-21).

- `r2-live.bytes`: 33973424728
- `r2-live.sha256`: `bbc0b65859e69808a51dd29c0441b521770e4a1c736350236de1b91ac915a272`
- `r2-live.md5`: `72e98faabc44c4f47e32927e57a6c380`

**Matched**: exit 0, the byte count, and both hashes equal to the local 10-19 file's. The kept file
`kept-usca/usca-20261019T011311Z/forager-usca.pmtiles` is therefore a full copy of the release that was
live until 11:33:36Z (04:33:36 PDT) on 10-22. It is now the only rollback copy.

## Owner's go for C

Given in the planner session after the comparison, verbatim: "Check the comparison, upload when it's ready".

## C. Upload, first run: failed

Unit `forager-pi29-us-upload`, the command exactly as in the dispatch's step C.

- Started 2026-10-22T05:31:53Z (22:31:53 PDT on 10-21). Exited 09:15:58Z (02:15:58 PDT), `ExecMainStatus=5`,
  Result exit-code.
- `pi29-logs/us-upload.log`: steady progress to 29.298 GiB / 31.797 GiB at 08:33:53Z (01:33:53 PDT).
  From 08:43:53Z (01:43:53 PDT) it reads 29.765 GiB at 0 B/s. From 08:57:53Z (01:57:53 PDT) the stats
  total itself reads 29.765 GiB ("100%"), still 0 B/s, until the error.
- The error, log line 225 (lines 227 and 230 repeat it). The Pi's own public IPv6 address is replaced
  here with `[pi]`:
  `ERROR : forager-usca.pmtiles: Failed to copy: multi-thread copy: failed to open chunk writer: create
  multipart upload failed: operation error S3: CreateMultipartUpload, https response error StatusCode: 0,
  RequestID: , HostID: , request send failed, Post "https://a6a899e01e2194ef8fff048c20130e14.r2.cloudflarestorage.com/forager-maps/us.pmtiles?uploads=":
  dial tcp: lookup a6a899e01e2194ef8fff048c20130e14.r2.cloudflarestorage.com on [2001:558:feed::1]:53:
  read udp [pi]:41335->[2001:558:feed::1]:53: i/o timeout`
  followed by `failed to get rate limit token, retry quota exceeded, 0 available, 10 requested`.
- What it shows: a DNS lookup of the R2 endpoint timed out against the ISP's IPv6 resolver, and the
  S3 SDK's retry quota was used up.
- Not established: why the final error is a CreateMultipartUpload this late in the run, and what happened
  during the 32 minutes at 0 B/s.
- Not recorded: the network at the moment of failure.
- The live object was not changed (checked before the re-run, below).

## Re-run: started, then stopped

The owner, verbatim: "Re-run the upload, go ahead".

Checked first, at about 10:25Z (03:25 PDT):
- `rclone lsl r2:forager-maps/us.pmtiles` read `33973424728 2026-10-19 02:16:46.438514719`, so the old
  release was still live.
- The local source was unchanged: `current` still resolved to `20261017T202051Z-usca-20261021T111429Z`,
  and the file was 34141705380 bytes.
- The R2 endpoint resolved. The default routes matched A.5. A 5-ping to 1.1.1.1 averaged 148 ms (A.5:
  18 ms).
- `list-multipart-uploads` showed one unfinished upload for `us.pmtiles`, initiated
  `2026-10-22T05:33:19.93Z`: the first run's, left behind.

Unit `forager-pi29-us-upload-2`:
- The same command as C, except the unit name and `--log-file /home/bwann83/pi29-logs/us-upload-2.log`.
- Started 10:26:44Z (03:26:44 PDT).
- It had no ERROR lines. By 10:43:44Z (03:43:44 PDT) it was at 3.237 GiB, at 123.920 KiB/s.
- Stopped with SIGINT at 10:44:27Z (03:44:27 PDT), on the owner's choice below. Exit 130.

## Resume of the first run's multipart upload

rclone cannot resume a multipart upload. It re-sends every part. The first run's parts were still on R2,
apparently because its own abort also failed (inferred from the DNS failure, not confirmed). The planner
asked the owner whether to stop the re-run and resume those parts, or let the re-run finish. The owner
chose, verbatim: "Stop re-run, resume (Recommended)".

**Tool:** `resume.py`. It and every file it used are copied into `docs/audits/2026-10-21-pi-29-files/`.
- HTTP goes through `curl --aws-sigv4`. The keys are read from the rclone config and passed on stdin,
  never on the command line. Nothing was installed.
- `verify`: lists the parts (ListParts), then compares each part's ETag and size with the MD5 of the
  same 16 MiB chunk of the local file.
- `upload`: sends each missing or mismatched part with `Content-MD5`, and accepts it only if the returned
  ETag equals the local MD5. It tries each part up to 30 times.
- `complete`: lists the parts again, refuses unless all 2,036 match, then calls CompleteMultipartUpload.
- The upload has 2,036 parts because 34141705380 bytes is 2035 parts of 16 MiB plus 70,820 bytes.

**Run** (`resume.log`):
- Verify, 10:44:20Z (03:44:20 PDT): 1801 of 2036 parts on R2, all 1801 matching, 0 mismatched, 235
  missing (part 1801 and parts 1803 to 2036).
- Unit `forager-pi29-us-resume` ran 10:45:03Z to 11:33:36Z (03:45:03 to 04:33:36 PDT),
  `ExecMainStatus=0`.
- 12 failed attempts, each followed by a successful attempt of the same part: 11 were
  `curl exit 56 ... SSL routines::sslv3 alert bad record mac`, and 1 was `curl exit 55 ... Connection reset
  by peer`. Part 1924 took four attempts. None needed more.
- Pre-complete, 11:33:22Z (04:33:22 PDT): `2036 match, 0 mismatch, 0 missing`.
- CompleteMultipartUpload, 11:33:36Z (04:33:36 PDT): HTTP 200, ETag
  `84e23aedaed65de49781f85a198f73cf-2036`. That equals the ETag computed from the local part MD5s, so R2
  assembled the parts the local file has, in its order.

## D. Tests

Run by the planner session at about 11:35Z (04:35 PDT). Raw output is in `cmp.out`.

**D.1 Size and leftover uploads.**
- `rclone lsl` read `34141705380 ... us.pmtiles`, equal to the local file.
- `list-multipart-uploads` returned `{"forager-maps": []}`. The first run's upload had been completed,
  and the stopped re-run's upload was gone.

**D.2 us.json.** Fetched with a cache-busting query: HTTP 200, `minzoom` 0, `maxzoom` 15.
- The dispatch says "all six trail keys" without naming them.
- The `roads` layer lists `foot`, `informal`, `sac_scale`, `surface`, `tracktype` and
  `trail_visibility`, plus `access`.
- Those six were taken as the trail keys. This is an assumption, not checked against a source.

**D.3 to D.5 Tiles.** Every request was cache-busted. Each tile was decompressed where gzipped and
compared byte for byte with `pmtiles tile` on the local archive. The sha256 of each is in `cmp.out`.

| check | tile | HTTP | X-Forager-Origin | bytes | result |
|---|---|---|---|---|---|
| z15 trail | 15/5303/11553 | 200 | r2 | 12810 | match |
| z11 track | 11/331/722 | 200 | r2 | 27057 | match |
| z12 path | 12/662/1444 | 200 | r2 | 20527 | match |
| Seattle | 12/656/1430 | 200 | r2 | 85233 | match |
| Miami | 12/1135/1744 | 200 | r2 | 72897 | match |
| Anchorage | 12/342/1161 | 200 | r2 | 62402 | match |
| Honolulu | 12/251/1799 | 200 | r2 | 79747 | match |
| Toronto | 12/1144/1494 | 200 | r2 | 157735 | match |
| Whitehorse | 12/511/1172 | 200 | r2 | 24849 | match |
| St. John's | 12/1448/1431 | 200 | r2 | 41123 | match |
| San Juan | 12/1295/1834 | 200 | r2 | 84106 | match |
| Charlotte Amalie | 12/1309/1835 | 200 | r2 | 46500 | match |

**How the z11 and z12 tiles were picked.** They are the parents of the z15 tile. That they hold a track
and a path was first seen by a byte search, then confirmed by decoding the roads layer with `mvt.py`
(local archive only). Re-run at 11:52Z (04:52 PDT):
- `10/165/361`: no path-kind features;
- `11/331/722`: 5 features with kind_detail `track`, all with `min_zoom` 13;
- `12/662/1444`: 12 features with kind_detail `path`, all with `min_zoom` 14.

So tracks start in z11 tiles and paths in z12 tiles. Whether the app's style filters on `min_zoom`,
which would hide them until z13 and z14, was not checked.

**Not checked:**
- the app;
- edge caches, which may serve old tiles for up to a day.

The owner's in-app test is still to come.

## Coder dispatch withdrawn

At about 11:40Z (04:40 PDT) the planner session dispatched a coder subagent to write the entries above
(`~/pi-handoffs/2026-10-22-pi-29-record-dispatch.md`). The owner then ruled, verbatim: "Actually planner
should be the one writing the record not coder. Next time you just write it like the EGD protocol has you
do", and then "Undo the record the coder wrote and write it yourself like EGD protocol says".

When the planner checked, the coder had already stopped:
- It had committed nothing and had not changed this file.
- It had left one untracked file, `prompts/preserved/2026-10-22-pi-29-record.md`. That file was
  identical to the dispatch, and the planner deleted it.

The dispatch is not preserved in this repo because it was withdrawn. An earlier dispatch,
`~/pi-handoffs/2026-10-22-pi-29b-dispatch.md`, was never run and is out of date.

## State after pi-29

- **Live:** `r2:forager-maps/us.pmtiles` is the 261021 build, 34141705380 bytes.
- **Rollback**, the only copy: `/srv/forager-build/kept-usca/usca-20261019T011311Z/forager-usca.pmtiles`.
  Kept until the owner has tested the new map in the app. A rollback would mean uploading it, about 31.6
  GiB.
- **Rowan** was told cross-session that the map is live, and was sent the facts for the Street switch
  (Forager PR #359). The switch goes back to the owner after the in-app test.
- **Route squares:** there are no `.rd5` files on R2 (`rclone lsf -R --files-only` returned 0). Rowan has
  asked for the layout `routing/<run-id>/segments4/<NAME>.rd5`, with `routing/manifest.json` uploaded
  last, kept private, with no Worker route. Uploading them needs a separate go from the owner.

## Rollback copy deleted (supersedes "kept until the owner has tested" above)

The owner said "Delete it" in Rowan's window, relayed to the planner. The planner then asked the
owner in its own session: "Delete the Pi's 10-19 rollback map,
/srv/forager-build/kept-usca/usca-20261019T011311Z (about 32 GB)? It's the only copy of the old map;
Cloudflare has no backup". The owner answered, verbatim: "Yes, delete it".

The reason: the Pi had 128,966,586,368 bytes free, and the weekly basemap build's start check needs
157,020,310,761 (`logs/usca-20261021T111429Z.log`).

Checks before deleting, at 2026-10-22 about 19:01Z (12:01 PDT):
- no planetiler, osmium, brouter, rclone or build process was running;
- `out-usca/current` still resolved to the 261021 output.

Deleted: `/srv/forager-build/kept-usca/usca-20261019T011311Z/forager-usca.pmtiles`, 33,973,424,728
bytes. This is the file the full comparison showed identical to the old R2 object.

Kept in the same folder, about 1 MB: the failed 10-19 build's notes, `FAILED.txt`,
`usca-20261019T011311Z.log`, `metrics.jsonl`, `versions.txt` and `bounds.txt`.

| | Bytes free |
|---|---|
| Before | 128,966,586,368 |
| After | 162,940,006,400 |

**There is now no copy of the 10-19 release anywhere.** A rollback would mean rebuilding it.

Untouched: the live 261021 output (34,141,705,380 bytes), `r2:forager-maps/us.pmtiles`, and
everything else.

## A new rollback copy, on the USB drive, 2026-10-22 23:03 PDT

The owner added a 256 GB USB flash drive, "for storage space, so the nvme can be used for building".
Asked, the owner said: "Yes, format and set up".

**Drive setup:**
- Reformatted from FAT32, which can't hold files over 4 GB, to ext4, label `forager-storage`.
- Mounted at `/mnt/storage` through fstab with `nofail`. The old fstab is `/etc/fstab.bak-20261022`.
- The owner moved it to USB 3; it runs at 5000 Mbps.

**The copy:**
- **First attempt:** failed with I/O errors, because the drive was moved mid-copy. The ext4 journal
  recovered on `e2fsck`, and nothing was written to the NVMe.
- **Second attempt:** a mount-guarded copy, 22:33:21 to 22:56:55, of the live output
  `out-usca/20261017T202051Z-usca-20261021T111429Z` to
  `/mnt/storage/rollback/usca-20261017T202051Z-usca-20261021T111429Z/`.

**Verified at 23:03:42:** all 192 files match the originals by sha256.
- `forager-usca.pmtiles` is `ad9c0f2dd86eb48fb56bf2bc416e602bed46443a6c6f30a5ed5810041fbd40aa`,
  equal to the sha256 recorded in A.1.
- The sums are in `SHA256SUMS` beside the copy.

**This is now the rollback for the live `us.pmtiles`.** The weekly build removes this output from the
NVMe when it next publishes. The NVMe copy is untouched.
