# Dispatch 2026-11-02-coder-12: the relief build (US + Canada, z5-11)

From the Pi planner (Aspen, session `cse_01Hqu21pTS9CgiAYPwgrpuFQ`, named
`bridge-cse-01hqu21pts9cgiaypwgrpufq-56` in ListAgents) to Willow Quadrat, Pi coder. Written 2026-11-02 at
about 12:18 PST, revised 12:23. Report times in Pacific time.

This replaces step 2 of `2026-11-01-coder-11-hillshade-rollout.md` and of coder-11b
(`2026-11-02-coder-11-relief-go.md`). The plan behind it is `docs/design/2026-11-02-relief-build-plan.md`
(`dd89812`). Read both before starting; where they differ, this dispatch wins.

## The go

- **The owner, about 12:10 PST:** "The build is now uploaded to R2. Let's begin fresh plans for the relief
  build".
- **On who runs it, about 12:17 PST:** "Give me the dispatch and I'll hand it to Willow."
- **Then, about 12:20 PST:** "This is the first time doing this so let's be careful with execution".
- **Then, about 12:22 PST:** "No trial run, all trials that ran were good."
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
7. **The trial script:** `/mnt/archive/aspen-hillshade-trial/make-relief.py`, plus its 256 px tiles in
   `tiles/png256/` (z11 columns 324-335).
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
  - **Hood against the trial,** using the trial's tiles in `/mnt/archive/aspen-hillshade-trial/tiles/png256/`:
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
