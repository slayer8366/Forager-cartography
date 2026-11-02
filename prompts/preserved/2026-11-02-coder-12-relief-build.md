# Dispatch 2026-11-02-coder-12: the relief build (US + Canada, z5-11)

From the Pi planner (Aspen, session `cse_01Hqu21pTS9CgiAYPwgrpuFQ`, named
`bridge-cse-01hqu21pts9cgiaypwgrpufq-56` in ListAgents) to Willow Quadrat, Pi coder. Written 2026-11-02 at
about 12:18 PST, revised to 12:24. Report times in Pacific time.

This replaces step 2 of `2026-11-01-coder-11-hillshade-rollout.md` and of coder-11b
(`2026-11-02-coder-11-relief-go.md`). The plan behind it is `docs/design/2026-11-02-relief-build-plan.md`
(`dd89812`). Read both before starting; where they differ, this dispatch wins.

## The go

- **The owner, about 12:10 PST:** "The build is now uploaded to R2. Let's begin fresh plans for the relief
  build".
- **On who runs it, about 12:17 PST:** "Give me the dispatch and I'll hand it to Willow."
- **Then, about 12:20 PST:** "This is the first time doing this so let's be careful with execution".
- **Then, about 12:22 PST:** "No trial run, all trials that ran were good."
- **Then, about 12:23 PST:** "Use the data from the last trial of mt hood. that stands as current".
  - The planner reads this as: the 11-01 Hood trial is the current reference, for the look and for the
    numbers. See premise 7.
- **So there is no pilot, and the go is in two parts:**
  - **The go for R0 and the tests** is the owner handing you this file.
  - **Hold 1:** after R0 and the tests, report and stop. R2 (the full build) waits for the owner's go,
    which Aspen relays.
  - **Hold 2:** after R2, report and stop.
  - If no go arrives, keep waiting; don't move on.
- **R3 (the R2 upload) is not yours.**
- **This replaces the earlier versions of this file:**
  - the 12:18 one (`6617c69`), which went from a pilot straight on to R2;
  - the 12:20 one (`f259fd5`), which had a pilot (R1) and three holds.

## Premises, read by the planner 12:11-12:18 PST (check them first)

Confirm each one, or show where it's wrong, before writing anything. All of them were read live, except
where marked.

1. **The drive:** `findmnt /mnt/storage` shows `/dev/sda1 ext4 rw,noatime`, with 158 GB free.
   `/mnt/storage` is `root:root 755`.
2. **`/mnt/storage/relief/` does not exist.**
   - coder-11b saw it, empty, at 08:58.
   - The Pi rebooted at 10:55. Root changed `/mnt/storage` at 11:29, and nothing else on the drive changed
     after 10:00.
   - The journal has no entries for 11:28-11:31, and no sudo use in either boot names it.
   - Cause unknown. Don't spend time on it; just make the folder (R0).
3. **The heights:** `/mnt/storage/elevation/hgt3` holds 3,631 `.hgt` files plus `SHA256SUMS`, 9.8 GB.
   - The cells span 17-84 N.
   - 12 lie east of the antimeridian (N51E177-179, N52E172-175, N52E177-179, N53E172-173), so the longitudes run -180 to 180.
4. **The tile list.** The planner computed the tiles that touch at least one cell, using the trial's
   tile-y formula:

   | z5 | z6 | z7 | z8 | z9 | z10 | z11 | total |
   |---|---|---|---|---|---|---|---|
   | 103 | 330 | 1,163 | 4,349 | 16,757 | 65,689 | 260,118 | 348,509 |

   This matches your 11-01 scope. If your enumeration gives other numbers, say which one is right and why.
5. **The tools:** GDAL 3.6.2, Pillow 9.4.0, numpy 1.24.2. `pmtiles` 1.31.2 at `/usr/local/bin/pmtiles`;
   its `convert` has `--tmpdir`. `/usr/bin/time` isn't installed.
6. **The Pi:** idle, 45.5 °C, `get_throttled=0x0`, 7.0 GiB of memory available. The weekly timer is next on
   Sun 11-08 02:08 PST.
7. **The trial script and the reference:** `/mnt/archive/aspen-hillshade-trial/make-relief.py`, plus its
   256 px tiles in `tiles/png256/` (z11 columns 324-335).
   - **This is the last Mount Hood trial, and the owner's current reference.** The planner checked at
     12:23: all 156 local tiles are byte-identical to the tiles the S22 trial loaded, which are Forager
     commit `a0088b496` (the `hillshade-trial-tiles` branch is deleted, but the commit is in `~/Forager`).
   - **Its numbers stand as current:**
     - 156 tiles, 16.0 MB;
     - `png256.pmtiles` 15.9 MB;
     - highest point 3,392 m (Hood is 3,429 m).
   - **Not the reference:**
     - `~/scratch/willow-relief/` holds your coder-10 sizing samples (kansas, coast; PNG only).
     - `/mnt/archive/willow-relief/test/` is empty and was made today at 11:08 PST.
     - If a session of yours made that folder, or removed `/mnt/storage/relief/`, say so in the R0
       report.
   - It warps each tile from a VRT with `gdal.Warp(..., resampleAlg="bilinear", srcNodata=-32768,
     dstNodata=nan)`.
   - It writes Terrarium with non-finite values set to 0 m, and saves PNGs with `optimize=True`.
8. **The live style:** v4's `dem` source asks for `/relief/{z}/{x}/{y}.png` (terrarium, 256, z5-11). The
   Worker checks the archive's header tile type and answers 400 if it isn't png.

## The work

### R0. Before writing

- Re-read premises 1, 3 and 6. Check that no `forager-build*` unit is running
  (`systemctl list-units 'forager-build*'`).
- Run `sha256sum -c --quiet SHA256SUMS` in `hgt3`. It must give 0 failures.
- Make the folder: `sudo mkdir /mnt/storage/relief`, then `sudo chown bwann83:bwann83 /mnt/storage/relief`.
  **If your session refuses the sudo, stop and report;** Aspen will make it. Don't write anywhere else
  instead.
- Push the script to a forager-cartography branch, `willow-relief-build`, under
  `docs/audits/2026-11-02-relief-build-files/`. Push at each step, not only at the end (the owner's rule).

### The script: generalise `make-relief.py`

Keep the trial's sampling and encoding exactly, so the look matches what the owner approved on the S22.
That means bilinear, the same `gdal.Warp` arguments, Terrarium with voids and sea at 0 m, and PNG
`optimize=True`. Change only these:

1. **Enumerate tiles from the cells, not a bounding box.** A -180..180 box would list the whole band. Each
   Aleutian cell east of 180 gets its own tiles near x = 2^z - 1.
2. **Use one VRT over all 3,631 cells.**
3. **No loose PNG tree.** Write tile bytes into MBTiles: one part file per worker process, then merged into
   `/mnt/storage/relief/relief.mbtiles`.
   - A restart skips tiles already in a part file.
   - Up to 4 processes, under `nice -n 10`.
4. **No WebP pass.**
5. **Metadata:**
   - name `forager-relief`, format `png`, type `baselayer`;
   - minzoom 5, maxzoom 11, bounds `-180,17,180,84`, encoding `terrarium`;
   - attribution `Heights: USGS 3DEP; NRCan MRDEM`.
6. **The checks below are part of the script** (or a sibling script in the same folder), not only done by
   hand.

**Tests that can fail** (run them in R0, and show the output):

- **The tile counts:** the enumeration gives the table in premise 4, z5-z11.
- **The antimeridian:** N52E179 gives z11 tiles with x ≥ 2,040, and none wrap to x = 0.
- **Terrarium round trip:** -86 m, 0 m, 3,392.4 m and 6,190.5 m each decode to within 1/256 m.
- **The count check catches a gap** (a positive control): drop one row from a copy of a part file, and the
  per-zoom count check must fail, naming that zoom.
- **Stop and resume:**
  - In a temporary folder under `/tmp`, start a run of about 20 z11 tiles, stop it with
    `kill -TERM -<pgid>` partway, then restart it.
  - It must finish with each tile written exactly once, and none missing.
  - This is a test of the script, not a trial of the map; keep it that small.

**Hold 1.** Send Aspen the R0 readings, the test output and the script's commit, then stop. R2 waits for
the owner's go, which Aspen relays.

### R2. The full build (only on the go relayed after Hold 1)

- **Where things go:** the full build's part files go in `/mnt/storage/relief/parts/`. The merged
  `relief.mbtiles` and `relief.pmtiles` go in `/mnt/storage/relief/`.
- **A safe stop:**
  - Write the build's process-group id to `/mnt/storage/relief/build.pgid`.
  - `kill -TERM -<pgid>` stops it, and the part files resume on restart.
  - The stop-and-resume test in R0 shows that this works.
- **Every 10 minutes the log records:**
  - tiles done per zoom;
  - free space on `/mnt/storage`;
  - the temperature and `get_throttled`.
- **The build stops itself, and you report, if:**
  - free space on `/mnt/storage` falls under 50 GB;
  - or `get_throttled` shows under-voltage or throttling (bits 0 or 2).
- **Start it detached:** `setsid nohup … &`, with the log at `/mnt/storage/relief/build.log`. Background
  jobs die at 2 hours.
  - Stamp the start and end with `date`.
  - **If your session refuses the detached start, stop and report.** Aspen can start it from this dispatch.
- Expected about 1-2.3 h and about 22 GB (16-34 GB), from your 11-01 scope.
- **About 30 minutes after the start,** send Aspen one progress line: tiles done, the rate, free space and
  the temperature, plus a projection of the finish time and the size.
  - If it projects over 4 hours or over 40 GB, say so, and keep running. The 50 GB free-space stop still
    guards the drive.
- **Before merging, run the count check on the part files.** If anything is missing, don't merge or
  convert; report it.
- **Merge, then convert:** `pmtiles convert --tmpdir /mnt/storage/relief/tmp relief.mbtiles relief.pmtiles`.
- **Checks on the result:**
  - **Per-zoom tile counts** in the MBTiles equal the table. Any gap is listed by z/x/y.
  - **`pmtiles show relief.pmtiles`:** tile type png, minzoom 5, maxzoom 11, the attribution and the bounds.
    Paste it into the report.
  - **Hood against the reference** (premise 7), using the trial's tiles in
    `/mnt/archive/aspen-hillshade-trial/tiles/png256/`:
    - Hood's z11 tiles that lie wholly inside the trial area (45-46 N, 123-121 W) and don't touch its edge
      should be byte-identical to the trial's. This is inferred: same data, same warp and the same Pillow.
    - Give the count identical / different. For any that differ, give the largest decoded height
      difference in metres.
    - The edge tiles will differ (the trial's VRT had only two cells). Say how many.
  - **Heights decoded from `relief.pmtiles`** (with `pmtiles tile`, not the MBTiles):
    - Hood's highest z11 pixel, about 3,390 m (the trial read 3,392);
    - Denali's, near 6,190 m;
    - Mount Logan's, near 5,959 m;
    - a Gulf of Maine sea tile, 0;
    - an Aleutian tile east of 180, which must be present.
  - **The file:** the size and sha256 of `relief.pmtiles`, and the size of `relief.mbtiles`.
  - **The load:** the peak temperature and `get_throttled` at the end.
- **Keep `relief.mbtiles`** until Aspen has read the upload back.
- **Hold 2.** Report, then stop.

## Bounds (do not touch)

- **R2:** no uploads, deletes or listings that change anything. The upload is Aspen's R3, with the owner's
  go.
- **The Worker:** **don't request any `/relief…` URL on the Worker.**
  - The Worker caches the current "Archive not found" 404 for a day (observed at 12:13:
    `cf-cache-status: HIT`, `max-age=86400`).
  - Every probe before the upload leaves a URL blank for up to a day after it.
- **`hgt3`, `bef3`, `hgt1-3dep`:** read only.
- **Deleting:** nothing, even inside `relief/`, without Aspen's word. That includes the part files.
- **On `/mnt/storage`:** nothing outside `relief/`. `rollback/` holds the only rollback copy of the live
  map.
- **Also leave alone:** `/opt/forager-build`, the weekly timer and units, and `us.pmtiles`, routing and the
  sprites.
- **The trial folder** `/mnt/archive/aspen-hillshade-trial/` is read only; it's the reference for the Hood
  check.
- **Approaches already rejected:**
  - WebP: untested decode; the owner's plan says skip it.
  - A loose tile tree: 348k files on the drive.
  - Bounding-box enumeration: the antimeridian.
  - Switching to average sampling: it changes the approved look.
  - A pilot run. The owner: "No trial run, all trials that ran were good."

  If you think one of these is wrong, say why instead of building it.
- **On any failed check, refusal or surprise:** stop and report. Don't work around it.

## Report

Send reports to Aspen with SendMessage (`bridge-cse-01hqu21pts9cgiaypwgrpufq-56`), at these points:

1. after R0 and the tests (Hold 1);
2. the progress line about 30 minutes into R2;
3. after R2 (Hold 2).

In each report:

- Mark each claim observed, read or inferred.
- Give the branch and commit of the script.
- Say plainly what you didn't check.
- Include a **Conventions** line: which neighbouring scripts you followed (the trial script, the G7 cell
  scripts in `docs/audits/2026-10-26-three-builds-files/`, `resume.py`), or "none checked".

## For the phone, later (not yours; after Aspen's R3 upload)

On the S22 with a v4 build:

1. Open Mount Hood at about z11.
   - Pass: the hill shading shows under the trails.
   - If it's blank, note the time and whether that area was opened before the upload.
2. Open a place not opened before the upload (for example Denali).
   - Pass: the shading shows at once.
3. Reopen any area that was blank in step 1 a day after the upload.
   - Pass: it shows.
   - Still blank means the phone's own cache, or the Worker's, is holding a 404. Report that.

## Update, 12:28 PST: report to the new Aspen session

- **The report address changes.** This supersedes the address in "Report" above and in the header.
  - Send reports to `bridge-cse-01hqu21r2oruzgj3zvyxxlsd-c2` (session `session_01Hqu21r2oruzgj3ZvyXxLsd`).
  - The old Aspen session, `bridge-cse-01hqu21pts9cgiaypwgrpufq-56`, was archived at 12:26:51 PST
    (observed, get_session). A send there won't arrive.
- **The owner handed this file to Willow at 12:26:57 PST**, in session `bridge-cse-01hqu21n91prtmjcx7ojeav7-6d`
  (observed, list_events). The handoff named the old address too.
- **Aspen told Willow the new address with SendMessage at 12:28 PST.** It was delivered and hadn't been read yet.
- Nothing else changes.

## Update, 13:02 PST: test 4's kill went to every process; fix the stop, then finish R0

This supersedes "A safe stop" in R2, the stop-and-resume test's wording in R0, and the report address in
the 12:28 update. Times are Pacific.

### What happened (observed by the planner, 12:57-13:00, unless marked)

- **12:38:58:** Willow's first session (`n91p…-6d`) ran `relief_tests.py` (branch `willow-relief-build`,
  `8e97da7`). Its log shows tests 1-3 passed. Test 4 never printed anything.
- **Test 4 stops the build with `subprocess.run(["kill", "-TERM", f"-{pgid}"])`.** That runs
  `/usr/bin/kill` from procps-ng 4.0.2.
  - On this Pi, that binary keeps only the first digit of a negative id. `kill -TERM -14750` makes the
    syscall `kill(-1, SIGTERM)`, and `kill -TERM -3113` makes `kill(-3, SIGTERM)`.
  - The planner traced this under `strace -e inject=kill:retval=0`, so no signal was delivered.
  - Willow's second session found the same thing independently, inside a private PID namespace.
- **12:39:05:** every `bwann83` process got SIGTERM: the desktop login (lightdm session 1), the user manager,
  and the Remote Control sessions. Willow's session shows `computer_unreachable` at 12:40:10.
  - Inferred: the build's process-group id began with 1 (the greeter that started at 12:39:06 got pid 14808),
    so the kill went to -1.
- **12:53:02:** logind powered the Pi off; it was back at 12:53:27.
  - Inferred: the owner power-cycled it. The test's `/tmp` folder was cleared at boot.
- **Nothing on the drives changed.** `/mnt/storage/relief/` is still empty (made 12:33:05), and no build ran.
  At 12:59: `/dev/sda1` rw with 158 GB free, 46.6 °C, `throttled=0x0`.
- **These forms make the right syscall, `kill(-N, SIGTERM)`:**
  - bash's builtin `kill` and dash's;
  - `/usr/bin/kill -TERM -- -N`;
  - `os.killpg(N, signal.SIGTERM)`.
- **Inferred (Willow):** `sudo kill -TERM -<pgid>` would use `/usr/bin/kill` as root, and `kill(-1)` from root
  reaches every process on the Pi.

### Sessions now

- **Aspen:** `session_01Hqu21qbkj6LhoAGQLgXLj4`, named `bridge-cse-01hqu21qbkj6lhoagqlgxlj4-77` in ListAgents.
  It opened at 12:55 with the owner's "Go". The 12:28 address (`r2or…-c2`) is archived.
- **Willow:** `session_01Hqu21r21FGQXWzLeRtR3yv` (`…-49`), opened at 12:56. Aspen sent it a HOLD at 13:00.
  - Willow confirmed at about 13:03: it has run no tests, written nothing, and sent no signals.
- **The owner's "Go" (12:55):** the planner reads it as "carry on with coder-12 from where it stopped",
  which is R0 and its tests.
  - **It is not the go for R2.** Hold 1 never happened, so R2 still waits for the owner's go after Hold 1.

### The fix, before any test runs again

1. **One way to stop a build: `relief.py stop OUT`.**
   - It reads `OUT/build.pgid`. It sends nothing, and exits non-zero, unless all of these hold:
     - the pgid is greater than 1;
     - it isn't the caller's own process group;
     - every process in that group (`pgrep -g`) is a `relief.py` process, checked by its command line.
   - Then it calls `os.killpg(pgid, signal.SIGTERM)`.
   - Test 4 stops its build through this same code.
   - Nothing calls `/usr/bin/kill`, and nothing runs under `sudo`.
2. **Test 4 runs inside `unshare -Urpf --mount-proc`.** There a wrong signal can reach only the test's own
   processes.
   - The planner checked at 13:00: inside the namespace, 4 processes were visible, and `kill(-1, 0)` reached
     only those, while the shell outside stayed alive.
   - If `unshare` is refused, or the build can't run inside it (for example, `vcgencmd` fails), stop and
     report. Don't run test 4 outside the namespace.
3. **Controls that can fail** (in the tests, inside the namespace):
   - `stop` must refuse, and send nothing, when `build.pgid` holds 1, the caller's own group, or a group
     holding a non-relief process (a `setsid sleep` sentinel). After each refusal the sentinel must still be
     alive.
   - The real stop: a sentinel in another process group must still be alive after the build's group is
     stopped.
4. **Flush every print** (`flush=True`, or `python3 -u`), so a log always shows its last line before a
   failure.
5. **Wording:** wherever the script, the tests or the log say `kill -TERM -<pgid>`, they now say
   `relief.py stop OUT`.
   - For R2, the safe stop is `relief.py stop /mnt/storage/relief`.
   - By hand in bash, it's `kill -TERM -- -<pgid>`. Never without `--`, and never with `sudo`.
6. **Then rerun all seven tests from the start**, and push the fix before the run (the owner's rule).

### Then

- **Hold 1, as before.** Report to Aspen at the address above: the R0 readings (your 13:03 ones are fine),
  the full test output, and the commit. Then stop.
- If anything outside the test's own processes is signalled, or any session drops, stop at once and report.
- Nothing else changes.

## Update, 13:14 PST: Hold 1 came back 5 of 7; two test changes, then rerun

Willow's Hold 1 report came in at about 13:12, from the 13:08:34-13:08:55 run on `willow-relief-build`.
The fix is `595c5b9`, and the logs are `ca3eed5`. The planner read `r0-tests.log` and `r0-hood-vrt-diag.log`
at `ca3eed5`, and they match the report.

- **Passed:** tests 1, 2, 3, 5 and 7, and every safety part of test 4:
  - three refusals, each sending nothing;
  - one `kill(-28, SIGTERM)`;
  - the sentinel stayed alive;
  - and nothing outside the test was signalled (13:08:24 against 13:09:29).
- **Test 4 failed on timing.** The stop landed after all 20 tiles were done, so resuming wasn't exercised.
- **Test 6 failed on byte identity.**
  - From the trial's two-cell VRT, `render()` gives 20 of 20 tiles byte-identical to the reference.
  - From the 3,631-cell VRT, 4 tiles differ, each in 1 pixel of 65,536, by 1/256 m (one Terrarium step).
  - The summit reads 3,391.582 m in both, the same as the reference.
- **Workers are now forked, not spawned,** so `stop` can recognise them by their command line.
  - The trial script used one process, and fork is Python's default here (read 13:13).
  - Accepted. Inferred low risk: the parent holds no open dataset when it forks.

### The planner's decisions (Willow's option A, both)

1. **Test 4 gets a test-only delay.**
   - With `RELIEF_TEST_CHUNK_DELAY=1`, each worker sleeps 1 s after each chunk commit.
   - **The build's start line logs the delay's value.** R2 never sets it, and R2's log must show it off. If it
     shows anything else, stop.
   - **Pass:** the stop lands with 0 < tiles < 20, the restart does the rest, and each tile is written once.
     Everything else in test 4 stays as it is.
2. **Test 6 passes on two conditions:**
   - from the trial's two-cell VRT, 20 of 20 tiles are byte-identical (this shows the render is the trial's);
   - from the full VRT, every tile is within 1/256 m of the reference.
   - It reports the count of differing pixels.
   - This supersedes "should be byte-identical" in R2's Hood check. R2 reports, for the inner tiles, the count
     identical and different, and the largest difference in metres.
     - If any inner tile differs by more than 1/256 m, stop before converting and report.
     - The edge tiles are reported, not judged.
   - **Why the planner can decide this:** byte identity was the planner's inference, marked as such. The
     owner's reference is the trial's look and its numbers. The numbers hold, and one 4 mm step in one pixel
     doesn't show in the shading (inferred). The owner sees this before R2's go and can overrule it.

### Also for R2

- If two 10-minute log lines in a row show no new tiles, the build has stalled. Stop it with
  `relief.py stop /mnt/storage/relief` and report.
  - This guards against a forked worker hanging (inferred risk, not seen).

### Then

- Rerun all seven tests, after pushing the change.
- Then Hold 1 again: report to Aspen (`session_01Hqu21qbkj6LhoAGQLgXLj4`), and stop. R2 waits for the owner's go.

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

## Update, 13:16 PST: 7 of 7 tests pass; R2 is running

Read by the planner at 13:16:11 PST, unless marked.

- **The tests:** the 13:14:11-13:14:33 run passed all seven (Willow's report). The run used `cbe49fd`, and the
  log is `86f9114` on `willow-relief-build`.
  - The planner read the log's seven `==> … PASS` lines.
  - Test 4: the stop landed at 4 of 20 tiles, and the restart did 16, each written once.
  - Test 6: from the two-cell VRT, 20 of 20 tiles are identical. From the full VRT, 16 are identical and 4 are
    within 1/256 m. The summit reads 3,391.582 m.
- **R2 started at 13:15:38 PST** (log 13:15:40). It runs from a pinned copy,
  `~/scratch/coder12-49/86f9114/relief.py`, whose sha256 (`1c02851e…`) equals the branch's.
  - The process group is 6179: the leader and 4 workers, all at nice 10, all `relief.py build`.
  - The start line says "chunk delay off". The guards are armed: 50 GB free, throttling, and the stall rule.
  - The Pi was at 60.4 °C with `throttled=0x0`. 158 GB free.
- **The stop:** `python3 ~/scratch/coder12-49/86f9114/relief.py stop /mnt/storage/relief`.
- **Next:**
  - Willow's progress line, about 13:46;
  - then Hold 2;
  - then R3, which is Aspen's and needs the owner's go.

## Update, 13:48 PST: R2's 30-minute line; the parts may be deleted before the convert

- **The progress line** (Willow, 13:45:42; the planner read `build.log` at 13:47:44, and it matches):
  - 58,560 of 348,509 tiles. z5-z9 are done, and z10 is at 35,858.
  - 32.5 tiles/s overall, and 40.9/s in the last 10 minutes.
  - 152.6 GB free; peak 68.1 °C; `throttled=0x0`.
  - The parts take 5.2 GB.
- **Willow's projection** (inferred):
  - finish about 15:45 PST (15:35-16:25), so 2.3-3.1 h in all;
  - parts about 30 GB (25-36). That's over the plan's 22 GB but under the dispatch's 40 GB line.
- **Willow's question:** at the convert's peak, the parts, `relief.mbtiles`, the convert's temp file and
  `relief.pmtiles` would all be on `/mnt/storage`. Free space would fall to about 39 GB, or about 13 GB at the
  top of the range, which is under the 50 GB floor.
- **The planner's decision:** Willow's option A. Willow may `rm -r /mnt/storage/relief/parts`, and nothing
  else, once all of these pass, in order:
  1. the merged `relief.mbtiles` passes the per-zoom count check;
  2. one digest over all the tile hashes, sorted by z/x/y, is equal for the merged file and for the parts;
  3. the Hood check passes.
  - Then the free-space check (free minus 2 × `relief.mbtiles` ≥ 50 GB), and then the convert.
  - Rejected:
    - B, the temp file on the NVMe (the plan keeps big files off it);
    - C, stopping after the merge.
  - `relief.mbtiles`, `relief.vrt` and `build.log` are kept.

## Update, 14:02 PST: R2 stopped on the owner's word; the relief build waits for the map build

- **The owner, to Aspen, about 14:00 PST, verbatim:**
  - "I want the zoom levels fixed. So if the map needs to be rebuilt, then start now"
  - "Stop the relief build"
  - "Nothing happens until the map build is finished"
  - "Stop the relief build since it'll need to restart anyway"
- **Just before that, the owner rejected Aspen's start of `forager-build-usca.service`.** Nothing was started.
  - Inferred: a plain rebuild wouldn't hold the zoom fixes, which aren't written yet.
- **Aspen stopped R2 at 14:00:31** with `python3 ~/scratch/coder12-49/86f9114/relief.py stop /mnt/storage/relief`
  (observed):
  - exit 0, `os.killpg(6179, SIGTERM)` to 5 `relief.py` processes, and the group was empty after 0.2 s;
  - the log says "stopped; part files hold 106560 of 348509 tiles; a restart resumes";
  - z5-z10 are complete (the 13:55:43 line), and z11 had started;
  - the parts take 7.8 GB, with 150 GB free.
- **Willow was told to hold** (14:01): no restart, merge, convert or delete. Everything in
  `/mnt/storage/relief/` stays.
- **On "it'll need to restart anyway":**
  - The part files resume, as test 4 showed.
  - Willow's projection had about 1.4 h of z11 work left at 40 tiles/s (inferred).
  - **Not checked:** whether the owner means restarting from zero. Ask before the restart.
- **The relief build waits until the map build is finished.** A restart needs the owner's go, relayed by
  Aspen. R3 waits too.

**Correction and addition to the update above:**
- The clock read 14:01:24 PST when it was written, so the heading should say 14:01. This supersedes "14:02".
- **Willow, 14:01:09 (observed):**
  - no `relief.py` running; `relief/` as left, with parts at 8.31 GB;
  - Willow started nothing after 14:00.
  - Willow's watcher saw the group gone at 14:00:38.
  - Inferred: the remaining 241,949 tiles take about 85 min, at the 48 tiles/s z11 rate.
