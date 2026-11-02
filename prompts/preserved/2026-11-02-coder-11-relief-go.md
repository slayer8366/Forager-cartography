# Dispatch 2026-11-02-coder-11b: go on the relief build (step 2 of coder-11)

From the Pi planner (session forager-cartography-d9) to Willow Quadrat. Written 2026-11-02 at about
03:35 PST. Report times in Pacific time. This is the "Aspen will say go" that
`2026-11-01-coder-11-hillshade-rollout.md` step 2 waits for; everything in that dispatch still holds
unless this one changes it.

## The go

- **The owner, 2026-11-02 about 03:30 PST:** "Tell willow to go on the build".
- They said it in answer to the planner's offer: fix the stuck uploader, restart it, then start the
  relief build once the upload finishes. So the go covers both steps below, in that order.

## What the planner saw (03:26 PST, read live)

- The rerun `usca-20261101T174337Z` finished OK at 00:00 PST: output
  `/srv/forager-build/out-usca/20261030T212451Z`, warnings 0, 187 rd5 + 187 fnm (from `upload.log`).
- **The uploader is stuck.** `/mnt/archive/aspen-upload-next/upload-after-build.sh` (pid 221905) has
  logged "waiting for Wi-Fi" 21 times since 00:00, though the first default route is `wlan0`
  (`bnep0` is second, metric 750). Nothing has gone to R2.
- **Cause (observed):** the script runs `set -euo pipefail`, and `wait_wifi` tests
  `ip route show default | head -1 | grep -q 'dev wlan0'`. When `head -1` exits, `ip` can die of
  SIGPIPE (141), and pipefail turns that into a failed test. The planner ran the same pipeline 5 times
  under pipefail: rc 0, 141, 141, 0, 141.

## The work, in order

1. **Fix the uploader and restart it.**
   - Change only the test in `wait_wifi` so it doesn't depend on a pipe that can take SIGPIPE, e.g.
     `[[ $(ip route show default | grep -m1 -o 'dev [^ ]*') == 'dev wlan0' ]]`, or read
     `ip route show default` into a variable first. Keep the rule: upload only when the first default
     route is `wlan0`, never over `bnep0`.
   - Show it works: run the new test 20 times under `set -o pipefail` and get 20 passes; then show it
     fails when `wlan0` isn't first (a stub `ip` on PATH is fine). Keep a copy of the old script.
   - `bash -n`, then stop pid 221905 and start the script the way Aspen did (`setsid nohup … &` from
     its folder). `RUN=` stays `usca-20261101T174337Z`.
   - It then does what it was written to do and the owner approved on 10-31: routing upload, read-back,
     `routing/manifest.json` last, then `forager-usca.pmtiles` -> `us.pmtiles`. Don't change any of that.
   - Watch `upload.log`. **On any STOP, stop and report**; don't retry by hand.
2. **The relief build, once `upload.log` says the upload finished cleanly.** As coder-11 step 2:
   `/mnt/storage/relief/`, from `/mnt/storage/elevation/hgt3` (3,632 entries there at 03:26),
   z5-11 Terrarium PNG 256 px, up to 4 processes under `nice -n 10`, MBTiles then `pmtiles convert`,
   attribution "Heights: USGS 3DEP; NRCan MRDEM", no WebP.
   - Check `findmnt /mnt/storage` before writing (it was `/dev/sda1 rw` at 03:26).
   - Record the time and size. `/usr/bin/time` isn't installed (the trial's `time.txt` is that error),
     so use the shell's `time` or `date` stamps.
   - Check that `pmtiles show` says tile type png.

## Bounds

- Coder-11's bounds stand, except that the uploader in step 1 does touch `us.pmtiles` and routing on
  R2; that's the approved upload, not a new one.
- The R2 upload of `relief.pmtiles` is not yours (coder-11 step 3); stop after the local file checks.
- If anything is refused or goes wrong, stop and report it.

## Report

Report to the planner after step 1 (the fix, the 20/20, the restart, then the upload result) and after
step 2. Mark claims observed, read or inferred.

## Update, about 03:40 PST: use v2; the go went to the real Willow session

- Another planner session (since closed) had already written a fix, `upload-after-build-v2.sh`. Like
  that session, the planner reviewed v2 against `upload-after-build.sh.v1-pipefail-bug`. Its Wi-Fi test
  is `ip route get 1.1.1.1` with no pipe. It adds an ERR trap that logs STOP. It also adds `|| true` on
  the two read-back display lines; the strict `rclone check -q || die` and the count check still guard
  the manifest. A helper tested it: 20/20 under pipefail (the old test passed 6/20), and it refuses
  bnep0, `wlan01` and an unreachable network.
- **Step 1 now:** start v2, not an in-place edit (pid 221905 reads the live file by byte offset). Stop
  221905, then confirm no `bash ./upload-after-build*` is left with `ps -o pid,cmd -C bash` (a bare
  pgrep also matches wrapper 221900 and log watchers), then start v2 once.
- **The owner:** "Tell Willow to go. She's waiting on you", then "Send it to Willow, I'll approve the
  prompt". Sent to the Willow session at about 03:40 PST. The helper briefed as Willow stood down.

## Update, 03:37 PST: HOLD, the old uploader got through on its own

- At 03:30:18 the old script's flaky Wi-Fi check passed and pid 221905 began uploading: upload.log reads
  "routing before: …", then "upload segments4". 221905 was still alive at 03:36:42.
- **So step 1 is now watch-only.** Don't stop 221905 and don't start v2: killing it would cut the upload
  partway through. v1 still never sends the manifest after a failed read-back (pipefail + set -e abort);
  it just doesn't log STOP. Its second Wi-Fi check, before the tiles, may wait a few rounds on the flake.
- The 03:40 go above was sent to a Willow socket that has since closed. A HOLD was queued to Willow
  [a49a3d] (offline) at about 03:38. v2 stays on disk for the next run.
- Step 2 (relief) still waits for a clean upload.

## Update, 08:58 PST: routing is live; the tile upload failed at 05:30; nothing is running

Read live by the planner at 08:58 PST.

- **Routing (observed, upload.log):** at 03:50:28 PST `usca-20261101T174337Z` went live: 187 segments4 + 187
  names1 read back with 0 differences, manifest sha256 `42f4ca89…8916e` matched on R2.
- **Tiles (observed):** the upload of `us.pmtiles` (35,256,335,758 B) started 04:13:10. At 05:30:09 rclone
  failed: a DNS lookup of the R2 host timed out against the IPv6 resolver (`[2001:558:feed::1]:53`,
  i/o timeout). With `--retries 1` that ended the copy, and v1 exited at the next `set -e` without
  logging STOP. The journal shows wlan0 losing its IPv6 lease at 05:32:43 (inferred: an IPv6 Wi-Fi blip).
- **The live map is untouched (observed):** `rclone lsl r2:forager-maps/us.pmtiles` reads
  `34141705380 2026-10-21 12:54:52`, the 10-21 file. A multipart upload only replaces the object when it
  completes.
- **Left on R2 (observed):** an unfinished multipart upload for `us.pmtiles`, started 12:14:29Z
  (04:14:29 PST), and an older one for `reference-trails.pmtiles` from 10-27. rclone can't resume them.
- No uploader or relief process is running. `/mnt/storage/relief/` is empty; `/mnt/storage` is
  `/dev/sda1 rw`, 158 GB free. Willow shows offline.
- Step 2 (relief) still waits. Retrying the tile upload needs the owner's go (the rule above: on a STOP,
  report, don't retry by hand). A v2 rerun would re-check routing (copy skips identical files, read-back
  about 8 min, same manifest) and then upload the tiles again.

## Update, 09:07 PST: the planner is resuming the tile upload (owner's go)

- **The owner, about 09:00 PST:** "Go ahead and resume the upload where it left off". The planner runs
  it, since Willow is offline.
- **What R2 held (observed, ListParts):** the 04:14:29 multipart upload of `us.pmtiles` has parts 1-282,
  no gaps, each 67,108,864 B (18,924,699,648 B, about 54%). The last part landed 04:47:41 PST. The file
  needs 526 parts.
- **The tool:** rclone can't resume a multipart upload, so the planner wrote
  `/mnt/archive/aspen-upload-next/resume/resume.py` (boto3 in `~/.venvs/s3resume`, keys read from
  rclone's `r2` remote). It hashes the local file (sha256 must match the build manifest; md5 for each
  64 MiB part), requires every part on R2 to have the matching ETag, uploads the missing parts with
  Content-MD5, completes only if all 526 parts match, then reads back the size, the multipart ETag
  computed from the local parts, the md5 metadata and the first MiB. It uploads only while every R2
  address routes via wlan0, and it logs STOP to `upload.log`.
- **Checks before uploading (observed):** `--verify-only` at 09:02-09:07: sha256 `02f9f053…d054e`
  matches the build manifest; all 282 parts on R2 match the local parts. The Wi-Fi test passed on the
  real routes and refused a stub `ip` that answered `dev bnep0`.
- The rollback copy of the live file is
  `/mnt/storage/rollback/usca-20261017T202051Z-usca-20261021T111429Z/forager-usca.pmtiles`
  (34,141,705,380 B, same size as the live `us.pmtiles`).
- Started 09:07:33 PST, pid 305513 (`setsid nohup`). 244 parts (16.3 GB) to go, 4 at a time.
- The `reference-trails.pmtiles` multipart from 10-27 is untouched; clearing it waits for the owner.

## Update, 10:29 PST: us.pmtiles is live (resumed upload); the upload step is done

- **Slow, then restarted (observed):** from about 09:22 the rate fell from 9 to about 2 MB/s with no failed
  parts and no Wi-Fi waits. At 10:06 `ss -ti` showed two of the four connections (both IPv4) at cwnd 1-2,
  0.1-0.4 Mbit/s, with heavy retransmits, and one IPv6 connection at 13 Mbit/s. On the owner's "Try
  restarting it", the planner stopped pid 305513 at 10:07:15 and started pid 309649 with
  `--reuse-hashes` (reuses the 09:11 part hashes only if the file's size and mtime are unchanged; the
  sha256 check against the build manifest still runs). R2 then held 477 parts, all matching. The new
  connections started at about 4 MB/s; one reconnected over IPv4 and collapsed again (cwnd 1, 3,145
  retransmits). Inferred, not proven: the IPv4 path is losing packets.
- **Completed 10:29:36 PST (observed, upload.log):** all 526 parts matched before CompleteMultipartUpload.
  Read back: size 35,256,335,758 on R2 and local; ETag `b8adb3d8…2143d3-526` on R2 equals the ETag
  computed from the local part md5s; `rclone md5sum` `9d8621d2…efe8ea` equals the local whole-file md5;
  first MiB sha256 `53f58222…da2634` matches. `rclone lsl` now reads `35256335758 2026-11-01 19:12:39`.
- The `us.pmtiles` multipart is gone (completed). Only the 10-27 `reference-trails.pmtiles` one is left,
  waiting for the owner.
- Not checked: the map through the Worker or in the app.
- **Step 2 (relief) can start**: the upload finished cleanly. Willow shows offline.
