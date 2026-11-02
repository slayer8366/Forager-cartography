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
