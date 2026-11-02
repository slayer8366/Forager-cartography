# Dispatch 2026-11-02-coder-13: our map's features appear at the zooms OSM's map shows them

- **From:** the Pi planner, Aspen. Session `session_01Hqu21qbkj6LhoAGQLgXLj4`, named
  `bridge-cse-01hqu21qbkj6lhoagqlgxlj4-77` in ListAgents.
- **To:** Willow Quadrat, Pi coder (`session_01Hqu21r21FGQXWzLeRtR3yv`).
- Written 2026-11-02, finished at the clock time in the commit. Report times in Pacific time, read from the clock.

## The owner's words (verbatim, 2026-11-02)

- **To Rowan, relayed in Forager `e4ca0acd5`:**
  - "Take "set it to OSM zoom levels" and run with it on the entire map." (said twice)
  - "So let's restart the build so it can hold the fixes"
  - "If the map needs to be redownloadedb let's start now"
- **To Aspen, about 14:00:** "I want the zoom levels fixed. So if the map needs to be rebuilt, then start now"
  and "Nothing happens until the map build is finished".
- **To Aspen, between 14:06 and 14:13 (estimated, not read):** "The style to match is the zoom levels that objects, icons, names, etc begin
  appearing on the map when zooming in".
- **To Aspen, at about 14:13-14:14 (estimated),** with four S26 screenshots (12:30-12:32, Liberal and Molalla, Oregon): "That
  needs to be redone as some parts are not coming in properly".
  - What the screenshots show, read from their content; their zoom numbers are not known:
    - Farthest out: only "Molalla" and the 211 and 213 shields are labelled. Forests are flat green.
    - One step in: the tree glyphs and road names arrive.
    - Closest: the orchard dots and the names "Molalla River" and "… Creek" appear.

## What this is

- **For each thing our map draws** (areas and their patterns, lines, icons, names, shields), the zoom where it
  first appears as you zoom in must equal the zoom where it first appears on the app's "OpenStreetMap" map.
- **Not part of it:**
  - the zoom where things disappear;
  - colours and look;
  - hill shading (the OSM standard style has none).
- **The reference:** the app's "OpenStreetMap" basemap is `https://tile.openstreetmap.org/{z}/{x}/{y}.png`
  (Forager `app/.../ui/map/Basemap.kt:169-174` on pre-main `04746d8f0`, read by Aspen).
  - That is OSM's standard style, openstreetmap-carto.
  - Use its latest release tag. `v5.9.0` was the newest `v5*` tag at 14:13 (`git ls-remote`, read). Say
    which tag you read.
  - Its zooms live in `project.mml` (each layer's `minzoom`) and in the `.mss` files (`[zoom >= N]`, often with
    a `way_pixels`, `way_area`, population or tag condition).
  - Where the first zoom depends on size or on a tag, give the rule, not one number.
- **Our map has two halves:**
  - **The style:** Street v4, `server/pmtiles-worker/src/street-style-v4.json` in Forager (104 layers on main
    `8d0eefdbc`).
    - For example: `landuse_forest_glyphs` minzoom 12, `landuse_orchards_pattern` 13, `landuse_wetland_tufts`
      10 (read).
    - Also cover any other style the app draws our tiles with (`offline-style.json`, the night handling). List
      them from the code.
  - **The tiles:** the Protomaps basemaps profile, at `BASEMAPS_COMMIT ca93fc06` with Forager's patches
    0001-0007 (`/opt/forager-build/map-build/pins.env`, read).
    - Each feature's minimum zoom in the tiles is set in its `layers/*.java`.
    - **If a feature isn't in the tiles at OSM's zoom, a style edit can't show it.** The profile has to change,
      and the map rebuilt.

## Premises (Aspen's reading; confirm each one first, or show where it's wrong)

1. **map-build is a directory in the Forager repo.** The last install is commit `288ce80cf` (in the worktree
   `~/forager-pi34`), installed at `/opt/forager-build/map-build`. The profile patches are in
   `map-build/patches/protomaps-basemaps/`.
2. **The basemaps source** the build compiles is under `/srv/forager-build/src/basemaps`, owned by the
   build user.
3. **The installed jar** is the one in memory as `1d892172` (pi-33 + pi-34). Read its sha256, and say if it
   differs.
4. **The live tiles:** `us.pmtiles` on R2, from run `usca-20261101T174337Z`, z0-15. The same file is local
   under `/srv/forager-build/out-usca/current`. Read its zooms from the file, not from R2.
5. **The Pi is idle.**
   - The relief build was stopped at 14:00:31 and stays stopped; don't touch `/mnt/storage/relief/`.
   - No map build is running. The weekly timer is next on 11-08 at 02:10.
6. **The decode tools** are read-only, in `~/pi29-logs/resume/tiles` (`mvt.py`, `kinds.py`). The web-preview
   tooling is in `~/street-preview-scratch` (Hazel's).

## The work

### Z1. The table (read only)

- **One row per thing drawn:** a style layer, split by kind wherever the zoom differs by kind.
- **Columns:**
  - what it is;
  - OSM's first zoom, with its rule and source (file and line at the tag);
  - our style's first zoom (layer id, minzoom, any zoom filter);
  - our tiles' first zoom: the profile's file and line, and a check by decoding the local `current` archive
    at the Molalla/Liberal tiles;
  - the fix: **style** (a minzoom or filter edit), **data** (a profile change and a rebuild), or **none**.
- **Also list things one map draws and the other doesn't, in both directions.** Don't decide what to do with
  them.
- **Push it** to forager-cartography: `docs/audits/2026-11-02-coder-13-osm-zooms/table.md`, on branch
  `willow-osm-zooms`.
- **Hold A:** send Aspen the table's summary:
  - how many rows differ;
  - which need data;
  - and what you couldn't determine.
  - Then wait for Aspen's word. This hold is Aspen's, not the owner's, to keep it quick.

### Z2. The fixes (on Aspen's word after Hold A)

- **Style:**
  - Edit `street-style-v4.json`, and the other styles in the table, on a Forager branch `osm-zooms-style`,
    cut from origin/main.
  - **Don't merge or push to `main` or `pre-main`.** Every push to `main` redeploys the Worker.
- **Data:**
  - A new profile patch, `0008-osm-first-zooms.patch`, in `map-build/patches/protomaps-basemaps/`.
  - Put it on a Forager branch `osm-zooms-map-build`, cut from `288ce80cf`.
  - Change only minimum zooms (and whatever tile-size or feature limits must move with them). Patches
    0001-0007 stay as they are.
- **Tests that can fail:**
  1. **The test area:** clip a small extract around Molalla with `osmium extract` from the local
     `us-261030.osm.pbf` (read only), and build it with the patched jar in a scratch folder.
     - Not in `/srv/forager-build/out*`, and not in `/mnt/storage`.
  2. **The first zooms:** for every data row, decode the test archive and show that the feature first appears
     at OSM's zoom, and not a zoom earlier.
     - Run the same check on the unpatched jar as the control. It must fail on those rows.
  3. **Nothing else changes:** feature counts per layer at z15 equal the unpatched build's, except the layers
     the patch changes.
  4. **Size:** tile sizes per zoom against the unpatched build. Flag any tile over 500 KB, and say how
     close the busiest is.
     - Inferred: the Protomaps limits are lower; read them.
  5. **Renders:** the patched style on the test archive, at the zooms of the owner's four screenshots and one
     zoom either side, with OSM's own tiles of the same view beside them, made with the preview tooling.
     - These are for the owner. Push them as PNGs.
- **Hold B:** send Aspen:
  - the patch, the style diff and the test output;
  - the renders' paths;
  - a projection of the full build's size and time.
  - Then stop.

### Z3. Install and build (Aspen's step, with the owner's go already given for the rebuild)

- On Aspen's word after Hold B:
  - Aspen or Willow installs the patched map-build and jar into `/opt/forager-build`. Keep a rollback copy of
    the current jar and map-build, as pi-34 did.
  - Then Aspen starts the build.
- **Whether it uses fresh extracts or `--local 261030`** is decided at Hold B.
- **The upload to R2 needs the owner's go,** as always.
- **The style merge needs the owner's look at the renders.**

## Bounds (do not touch)

- **R2:** nothing. **The Worker:** no deploys, and no requests to `/relief…`.
- **`main` and `pre-main`:** no merges or pushes in Forager.
- **Read only until Z3:**
  - `/opt/forager-build`, `/srv/forager-build/out*`, `sources/` and the timer and units.
  - Don't start `forager-build-usca.service`.
- **`/mnt/storage`:** don't touch it. The relief folder stays as it was left at 14:00:31.
- **Signals:** if a test needs to stop a process, use a guarded stop or `kill -TERM -- -<pgid>`, never
  `/usr/bin/kill -<pgid>`. See the coder-12 13:02 update.
- **On any failed check, refusal or surprise:** stop and report. Don't work around it.

## Report

- Send reports to Aspen with send_message, at Hold A and Hold B.
- In each report:
  - mark each claim read, observed or inferred;
  - give the branch and commit;
  - say plainly what you didn't check;
  - include a **Conventions** line: which neighbouring patches and scripts you followed.

## Update, 14:28 PST: Z1 goes to Juniper; premise 1 corrected; no download needed

- **Premise 1, corrected** (Willow, read 14:15-14:17):
  - The installed map-build is Forager `53a728341` on origin/pi-build ("Merge pi-37-barrier-mark-fill"),
    with patches 0001-0007 and a 4608m heap. `288ce80cf` has only 0001-0004.
  - Z2's branch `osm-zooms-map-build` is cut from `53a728341`.
  - The installed jar is `25e5b8db…` (11-01 09:40). `1d892172` is the rollback copy.
- **Z1 is withdrawn.** The owner, about 14:25: "Ensure Juniper has the right dispatch:
  prompts/preserved/2026-11-02-03-osm-zoom-levels.md".
  - Juniper's session (`session_01Hqu21oansrXBVEfzvrbt17`, opened 14:24) does the comparison, under that
    Forager dispatch, on origin/records-after-173 at `8f8426e38`.
  - At about 14:27, Aspen sent Juniper:
    - the file's location;
    - the owner's words since 12:49, so first-appearance zooms only;
    - the read facts for A1 and C1.
  - Rowan is asked to add them to that dispatch as an amendment.
  - Willow pushes any Z1 draft and stops Z1.
- **Z2 starts from Juniper's C1 table,** on Aspen's word.
- **The rebuild uses the 10-30 extracts already on the Pi** (`--local 261030`). No download is needed for the
  zoom fix. The owner asked "Does a download need to happen for the zoom fix?", and Aspen answered no.
  - The four 10-30 extracts were read at 14:2x, on the SD card, with their `.md5` files.
- **The map build is stopped,** with nothing downloading (14:25). The partial `us-261101.osm.pbf.part`
  (1,529,737,216 bytes) is kept in `/mnt/archive/forager-build/sources-osm/`.
