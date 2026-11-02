# Relief build plan, 2026-11-02 (fresh start)

Written by the planner (Aspen, session `cse_01Hqu21pTS9CgiAYPwgrpuFQ`) at about 12:20 PST. Times are Pacific.

## The ask

- **The owner, 2026-11-02 about 12:10 PST:** "The build is now uploaded to R2. Let's begin fresh plans for
  the relief build".
- This plan replaces step 2 of `prompts/preserved/2026-11-01-coder-11-hillshade-rollout.md` and of
  coder-11b (`prompts/preserved/2026-11-02-coder-11-relief-go.md`). Those gos were for Willow, and both Willow sessions are offline. **Nothing in this plan starts until the
  owner says go** and says who runs it.
- **What still holds from coder-11:**
  - z5-11, Terrarium PNG 256 px, from `/mnt/storage/elevation/hgt3`;
  - bilinear sampling as in the trial, so the look matches the one the owner approved on the S22;
  - attribution "Heights: USGS 3DEP; NRCan MRDEM"; no WebP;
  - up to 4 processes under `nice -n 10`;
  - MBTiles, then `pmtiles convert` to `relief.pmtiles`;
  - the R2 upload is its own step with its own go.

## What the planner read live (12:11-12:15 PST)

- **The USB drive:** `/mnt/storage` is `/dev/sda1 ext4 rw`, 158 GB free, owned by root.
- **`/mnt/storage/relief/` does not exist.**
  - coder-11b's 08:58 update saw it there and empty.
  - The Pi rebooted at 10:55. `/mnt/storage` itself was changed by root at 11:29, and nothing else on the
    drive changed after 10:00.
  - The journal has no entry for 11:28-11:31, and no sudo use in either boot names relief or storage.
  - So what removed it is not known. The plan makes it again (R0).
- **The heights:** `hgt3` holds 3,631 `.hgt` files and a `SHA256SUMS` (9.8 GB).
  - The cells span 17-84 N.
  - 12 of them lie east of the antimeridian (the Aleutians, 172-179 E), so the cells span -180 to 180.
- **Tiles to make** (counted from the cell list; this equals Willow's 348,509):

  | z5 | z6 | z7 | z8 | z9 | z10 | z11 | total |
  |---|---|---|---|---|---|---|---|
  | 103 | 330 | 1,163 | 4,349 | 16,757 | 65,689 | 260,118 | 348,509 |

  About 59 % of the z11 work lies north of 60 N. Mercator stretches the north, so Alaska, the Yukon and
  the Arctic islands take most of the tiles.
- **The tools:** GDAL 3.6.2, Pillow 9.4.0, numpy 1.24.2, and pmtiles 1.31.2, whose `convert` has
  `--tmpdir`.
- **The Pi:**
  - idle, 45.5 °C, not throttled (`0x0`);
  - 7.0 GiB of memory available, 154 GB free on the NVMe;
  - the weekly timer is next on Sun 11-08 02:08.
- **The Worker** (live, from `main`):
  - `/relief.json` and `/relief/11/326/732.png` answer 404 "Archive not found".
  - **That 404 is cached for a day** (`cf-cache-status: HIT`, `max-age=86400`). The planner's own two
    probes at 12:13 are now cached at PDX until about 12:13 tomorrow.
  - Once the archive is there (read in `server/pmtiles-worker/src/index.ts` on `main`):
    - a missing tile in z5-11 answers 204, and so does anything above z11;
    - a request for a type other than png answers 400.
- **The style:** v4's `dem` source, live and bundled, is `/relief/{z}/{x}/{y}.png`, terrarium, 256,
  z5-11. It has no `bounds`.
- **The trial script** is `/mnt/archive/aspen-hillshade-trial/make-relief.py`: two cells, a bounding-box
  tile list, a loose PNG tree plus MBTiles, and a WebP pass.

## What changes from the trial script

1. **The tile list comes from the cells, not a bounding box.**
   - A -180..180 box would list the whole band from 17 N to 84 N, several times the tiles.
   - The Aleutian cells east of 180 get their own tiles.
2. **One VRT over all 3,631 cells**, so tiles that cross cell edges see both sides.
3. **Tiles go straight into MBTiles,** with no loose tree of 348,509 files.
   - Each worker writes its own part file, and the parts are merged into one `relief.mbtiles`.
   - A restart skips tiles already written, so a crash costs minutes, not the run.
4. **No WebP pass.**
5. **Metadata:**
   - name `forager-relief`, format `png`, minzoom 5, maxzoom 11;
   - bounds `-180,17,180,84`, encoding `terrarium`;
   - the attribution above.
6. **Sea and voids** stay at 0 m, as in the trial. Flat sea tiles are identical, so `pmtiles convert`
   stores them once.
7. **`pmtiles convert --tmpdir /mnt/storage/relief/tmp`**, so nothing large lands on the NVMe.

## The steps

### R0. Before writing (read-only, plus one folder)

- `findmnt /mnt/storage` must show `/dev/sda1` rw. Check `df`.
- Check that no `forager-build*` unit is running.
- `sha256sum -c SHA256SUMS` in `hgt3`. This reads 9.8 GB, a few minutes.
- `sudo mkdir /mnt/storage/relief`, then chown it to bwann83.

### R1. Pilot (about 10-20 minutes)

- Build four z7 subtrees (z7 down to z11):
  - Mount Hood, to compare with the trial;
  - the Brooks Range or Ellesmere, for the Arctic;
  - an Aleutian tile east of 180;
  - a coast with flat sea.
- **Checks:**
  - Hood's z11 tiles inside the trial area, away from its edge, are byte-identical to the trial's
    `tiles/png256`. If they aren't, report the largest height difference.
  - Low zooms aren't aliased. Compare 3 z7 tiles against the same tiles made with `-r average`, and report
    the height differences.
    - Inferred, to be checked: GDAL widens bilinear when shrinking, so they should agree closely.
  - Record seconds and bytes per tile at each zoom.
- **Project the full run** from those numbers.
  - If it projects over 4 hours or over 40 GB, stop and report.
  - Otherwise go on to R2 and report the pilot numbers.

### R2. The full build

- Run it under `setsid nohup`, logging to `/mnt/storage/relief/build.log`. Stamp the start and end with
  `date`; `/usr/bin/time` isn't installed.
- **Expected:** about 1-2.3 h and about 22 GB (16-34 GB), from Willow's scope. The pilot refines this.
- Then `pmtiles convert`.
- **Checks:**
  - **The tile counts** per zoom equal the R0 table. Any missing tile is listed by zoom.
  - **`pmtiles show`:** tile type png, z5-11, the attribution, and the bounds.
  - **The heights**, decoded from the archive:
    - Hood's highest z11 pixel is about 3,390 m (the trial read 3,392);
    - Denali's is near 6,190 m, and Mount Logan's near 5,959 m (bilinear at 3″ reads a little low);
    - a Gulf of Maine sea tile reads 0;
    - an Aleutian tile east of 180 exists.
  - The size and sha256 of `relief.pmtiles`.
- Keep `relief.mbtiles` until the upload is read back; there's room.

### R3. The R2 upload (its own go)

- **Who:** Aspen.
- **How:** with `resume.py` adapted (multipart, Wi-Fi only, every part checked, octet-stream), into
  `r2:forager-maps/relief.pmtiles`.
  - Offer the owner forcing IPv6. On 11-02 the IPv4 connections to R2 collapsed twice (inferred cause:
    packet loss on IPv4).
- **Read back:** the size, the multipart ETag computed from the local parts, and md5.
- **Then the Worker:** `/relief.json` with maxzoom 11, and a Hood z11 tile at 200 image/png.
  - Use URLs nobody has asked for yet, or add a query string. Earlier requests stay cached as 404 for up
    to a day.

### R4. The phone

- On the S22 with v4, the hill shading shows over Hood and over a place not opened before the upload.
- Tiles the phone viewed before the upload may stay blank for up to a day. The Worker's cached 404 is
  observed; the phone's own cache is inferred.
- If they're still blank after a day, report it.

## Bounds

- No R2 writes before R3's go. Nothing in `/opt`.
- `hgt3` is read only.
- Nothing on `/mnt/storage` outside `relief/`.
- Stop and report on any failed check or refusal.

## Follow-ups, not in this plan (each needs its own go)

- **The Worker:** don't cache "Archive not found", or cache it for minutes. Otherwise a missing archive
  stays missing for a day after it's uploaded. Sorrel reviews, then a `worker/*` release.
- **The style:** give v4's `dem` source `bounds`, so phones outside US + Canada don't ask for relief tiles
  that answer 204.
- **R2:** the 10-27 `reference-trails.pmtiles` multipart is still on R2, waiting for the owner's word.

## Waiting for the owner

- The go, and who runs R0-R2:
  - Aspen;
  - a helper briefed as Willow;
  - or wait for a Willow session.
- Willow's session couldn't start builds or use sudo on 11-01, and R0 needs sudo for the folder.

## Update, about 12:20 PST: the owner hands it to Willow

- **The owner:** "Give me the dispatch and I'll hand it to Willow."
- Dispatched as `prompts/preserved/2026-11-02-coder-12-relief-build.md` (`6617c69`): R0-R2 are Willow's,
  and R3 stays Aspen's, with its own go.
- **Added to the plan:**
  - Willow makes no requests to `/relief…` on the Worker before the upload, since each one would be
    cached as a 404 for a day.
  - The script goes on the forager-cartography branch `willow-relief-build`.
  - If Willow's session refuses the sudo or the detached start, Willow stops and Aspen does that step.

## Update, about 12:35 PST: a hold after each step

- **The owner:** "This is the first time doing this so let's be careful with execution".
- **coder-12 is now step by step** (`f259fd5`):
  - Hold 1 comes after R0 and the tests; R1 then needs Aspen's go.
  - Hold 2 comes after the pilot; R2 then needs the owner's go.
  - Hold 3 comes after R2.
- **Also added:**
  - the pilot goes in its own folder;
  - a safe stop, by process-group id, with resuming shown;
  - a progress line in the log every 10 minutes;
  - the build stops itself under 50 GB free or on under-voltage or throttling;
  - a count check before merging;
  - no deletes without Aspen's word.

## Update, about 12:23 PST: no pilot; and a correction to the times above

- **The owner, about 12:22 PST:** "No trial run, all trials that ran were good."
- **coder-12 now has no R1 pilot,** and two holds:
  - Hold 1 comes after R0 and the tests. R2 then needs the owner's go, relayed by Aspen.
  - Hold 2 comes after R2.
- **Hood against the trial** moves into R2's checks on the built archive.
- **The low-zoom `-r average` comparison is dropped.**
- **The stop-and-resume proof** is now a 20-tile test in `/tmp`, part of R0's tests, not a map trial.
- **R2's 30-minute progress line** now carries the projection. Over 4 h or 40 GB is reported, and the run
  continues.
- **Correction** (this supersedes the times in the two updates above, which were estimated, not read from
  the clock; read from the commit times):
  - The owner's "Give me the dispatch" came at about 12:17, and the dispatch was pushed at 12:18:52.
  - "Let's be careful with execution" came at about 12:20, and the holds were pushed at 12:20:47. That
    update's heading says about 12:35, which is wrong.

## Update, about 12:26 PST: the last Hood trial is the reference

- **The owner, about 12:25 PST:** "Use the data from the last trial of mt hood. that stands as current".
- **The planner checked (observed, 12:25):**
  - the 156 tiles in `/mnt/archive/aspen-hillshade-trial/tiles/png256/` are byte-identical (git blob
    hashes) to Forager `a0088b496`, the tiles the S22 trial loaded;
  - its numbers stand: 156 tiles, 16.0 MB, highest point 3,392 m.
- **coder-12 names this set as the reference** for the look and for R2's Hood check (premise 7).
- **Found while checking, not part of the reference:**
  - `~/scratch/willow-relief/`: Willow's coder-10 sizing samples, kansas and coast.
  - `/mnt/archive/willow-relief/test/`: empty, made today at 11:08 PST.
  - Willow is asked in R0 whether a session of theirs made that folder or removed `/mnt/storage/relief/`.
- **Correction to this update** (the times were estimated; the clock read 12:23:48 when it was written):
  the owner's message came at about 12:23, and the check was observed at 12:23, not 12:25 or 12:26.

## Update, 12:28 PST: coder-12 is with Willow; reports come to the new Aspen session

- **The owner, 12:27 PST:** "I sent your dispatch to willow".
- **Willow's session** is `bridge-cse-01hqu21n91prtmjcx7ojeav7-6d`. It got the handoff at 12:26:57 and began
  R0's premise checks at 12:27 (observed, list_events).
- **Aspen moved sessions.** The old session (`pts9…-56`) was archived at 12:26:51. Aspen is now
  `bridge-cse-01hqu21r2oruzgj3zvyxxlsd-c2`.
- **Willow was given the new address** at 12:28, and the dispatch carries an update
  that supersedes its report address.
- **Next:** Willow's Hold 1 report (R0 and the tests). R2 waits for the owner's go.

## Update, 13:02 PST: R0's stop test signalled every process; fixed before rerunning

- **What happened** (observed; details in coder-12's 13:02 update):
  - At 12:39:05, R0's stop-and-resume test ran `/usr/bin/kill -TERM -<pgid>`.
  - On this Pi, procps-ng 4.0.2 keeps only the first digit of that id, so the call became `kill(-1, SIGTERM)`.
  - It ended every `bwann83` process: the desktop login and the Willow and Aspen sessions.
  - The Pi was powered off at 12:53:02 and was back at 12:53:27.
  - No build ran, and nothing on the drives changed.
- **The fix, in coder-12:**
  - a guarded `relief.py stop OUT`, using `os.killpg`;
  - test 4 run inside a private PID namespace;
  - controls showing that the stop refuses a wrong group and leaves a sentinel alive;
  - flushed logs;
  - for R2, the safe stop is `relief.py stop /mnt/storage/relief`, or `kill -TERM -- -<pgid>` by hand.
- **Sessions:** Aspen is now `session_01Hqu21qbkj6LhoAGQLgXLj4` (opened 12:55 with the owner's "Go"), and Willow is
  `session_01Hqu21r21FGQXWzLeRtR3yv` (opened 12:56).
- **The owner's "Go"** is read as "finish R0". R2 still needs the owner's go after Hold 1.

## Update, 13:14 PST: Hold 1, 5 of 7 tests passed; two test changes

- **The guarded stop worked** (observed, Willow's 13:08 run, `ca3eed5`):
  - it refused three wrong groups;
  - it sent exactly one `kill(-28, SIGTERM)`;
  - and nothing else was signalled.
- **Test 4:** the stop landed after all 20 tiles were done. A test-only 1 s delay per chunk is added, and the
  build logs that it's off.
- **Test 6:** the full VRT gives 4 of 20 Hood tiles a one-pixel, 1/256 m difference from the trial's. The
  trial's VRT gives 20 of 20 identical.
  - The planner's criterion becomes "within 1/256 m". It was "byte-identical", which was inferred.
  - R2 stops before converting if any inner Hood tile differs by more than that.
  - The owner can overrule this before R2's go.
- **Next:** Willow reruns the tests. Then Hold 1, and R2 waits for the owner's go.

**Correction to the update above** (it supersedes that update's times, which were estimated, not read): the
clock read 13:11:54 PST when it was written. Willow's report came after `ca3eed5` (13:10:10) and before 13:11.
The fork default was read at about 13:11. The heading should say 13:11, not 13:14.

## Update, 13:16 PST: the owner's go for R2, given to Willow directly

- **The owner, to Willow, at about 13:11:** "That is your dispatch to work with, use it. Fix it and move on".
  - This is quoted by Willow, at 13:12. The planner couldn't see the owner's message in Willow's events, but
    read Willow's 13:12:13 reply answering it: "You've given the go to use this dispatch, fix the two tests and
    move on."
- **The planner and Willow both read it as the go for R2,** if all seven tests pass on the rerun. If any test
  fails, there's no go; stop and report.
- **Willow adds:**
  - the test delay is refused for any OUT not under `/tmp`;
  - test 6 has a control that must reject a 0.01 m offset.
- **The holds now:** no Hold 1 stop before R2. The 30-minute progress line and Hold 2 stay. R3 is still
  Aspen's, with its own go.

**Correction to the update above** (it supersedes that update's heading): the clock read 13:13:51 PST when it
was written, so the heading should say 13:13, not 13:16.
