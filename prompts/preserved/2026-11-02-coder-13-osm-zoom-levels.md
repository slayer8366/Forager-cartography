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

**Correction to the update above:** the clock read 14:26:41 PST when it was written, so the heading should say
14:26. The message to Juniper went at about 14:26, not 14:27. This supersedes the update's times.

## Update, 14:27 PST: the unneeded 11-01 download deleted (owner)

- **The owner, about 14:27:** "Delete the downloaded data that we don't need".
- **Aspen removed two files at 14:27:36** with `sudo -u forager-build rm` (observed). They came from the 13:59
  run, which was stopped:
  - `/mnt/archive/forager-build/sources-osm/us-261101.osm.pbf.part` (1,529,737,216 bytes);
  - `/srv/forager-build/sources/osm/us-261101.osm.pbf.md5` (52 bytes).
  - The SD card went from 73 to 75 GB free.
- **Kept:**
  - the four 10-30 extracts and their `.md5` files, which the zoom-fix rebuild uses;
  - `logs/usca-20261101T174337Z.log`, the live map's build log;
  - `failed-usca/latest`, the stopped run's log.
- **The owner also said "Resume rt the relief build".** It was already running, resumed at 14:16:10
  (pgid 10404). At 14:26:11: 135,328 of 348,509 tiles, 47.9/s, 147.1 GB free, 65.3 °C, `throttled=0x0`.
  Nothing was changed.

## Correction, 14:31 PST: the reference is openstreetmap-carto v6.1.0, not v5.9.0

This supersedes "`v5.9.0` was the newest `v5*` tag" under "What this is", and wherever this dispatch or Aspen's
messages name v5.9.0.

- **Found by Juniper** (message 14:33 by its clock). **Checked by Aspen at 14:30:58:**
  - OSMF's openstreetmap/chef `roles/tile.rb:104` on master reads `:revision => "v6.1.0"`, with the repository
    gravitystorm/openstreetmap-carto;
  - `git ls-remote` lists tags v6.0.0 and v6.1.0, and v6.1.0 is commit `0e52579`.
  - Juniper also read chef `e2b54e4`, "Update to osm-carto v6.1.0" (2026-09-11). Aspen didn't read it.
- **Aspen's error:** the 14:13 lookup listed only `v5*` tags, so it couldn't see v6.
  - The reference is the release that tile.openstreetmap.org actually runs, read from OSMF's own
    configuration, not the newest tag.
- **Effect:** none written yet.
  - Willow's Z1 draft (`3e1304b`) has no OSM column.
  - Juniper reads v6.1.0.
- **Also read by Juniper:** patches 0001-0007 from `53a728341` apply cleanly, in order, onto basemaps
  `ca93fc06`.

## Decision, 14:36 PST: match where things first appear in the app, carto's zoom N becomes camera zoom N − 1.5

- **Juniper's finding** (Forager `osm-zoom-levels` `7aadcbd23`, section A1b; message 14:52 by its clock):
  - The app's OpenStreetMap map is a 256 px raster source.
  - MapLibre Native picks a raster tile level as round(zoom + log2(512/256)). So carto's tile level N first
    shows at camera zoom N − 1.5, and reaches its own pixel scale at N − 1.
  - Our vector source uses 512 px and floor, so a style minzoom is a camera zoom.
- **Checked by Aspen:**
  - the app's raster source has `"tileSize": 256` (`BasemapStyles.kt`, pre-main `04746d8f0`, about line 210);
  - v4's `protomaps` source sets no `tileSize`, so it gets the 512 default (main `8d0eefdbc`).
  - MapLibre's rounding for raster versus floor for vector is Juniper's reading of the MapLibre source,
    consistent with how MapLibre is known to behave. Aspen didn't re-read the MapLibre source.
- **The planner's decision:** match first appearance, at camera zoom **N − 1.5**.
  - The owner's words: "the zoom levels that objects, icons, names, etc begin appearing on the map when
    zooming in".
  - The alternative, N − 1 (OSM's tile at its full scale), is the owner's to choose instead. Their look at the
    renders comes before any merge.
- **What it means for Z2:**
  - A carto rule `[zoom >= N]` becomes a style minzoom of N − 1.5. Fractional minzooms are valid in MapLibre.
  - The feature has to be in our tiles from level N − 2.
  - Rules that depend on size or tags shift the same way.
  - The tests check first appearance at camera N − 1.5. The renders show both maps at the same camera zooms.

## Update, 14:53 PST: Hold A is passed on Juniper's table; Z2 goes, with these decisions

### The table

- **Juniper's comparison:** Forager `osm-zoom-levels` `53c5d6801`, `docs/audits/2026-11-02-osm-zoom-levels-comparison.md`.
  - 116 rows, and 114 differ.
  - 52 need style only, 43 need data, and 19 need both.
  - Targets are camera N − 1.5, with the data in tiles from level N − 2.
- **Aspen spot-checked four rows against openstreetmap-carto v6.1.0** (raw files at the tag). All match:
  - wood pattern `[zoom >= 13]`, `landcover.mss:776`;
  - orchard pattern `[zoom >= 13]`, `landcover.mss:146`;
  - river names `[zoom >= 13]`, `water.mss:393-394`;
  - river lines from 8, `water.mss:64-75`.
- **One of Juniper's open points is answered:** the live archive's manifest names `map_build_commit 53a7283`
  (Willow, premise 4). So the live tiles were built from 0001-0007.

### The planner's decisions for Z2

1. **The target:** every row of Juniper's table, where both maps draw the thing.
   - The style's minzoom goes to camera **N − 1.5**.
   - The data must be in the tiles from level **N − 2**, under Juniper's rules and size conditions.
2. **Equal both ways.** Where ours appears earlier than OSM, it moves later to match. The owner's words are
   "set it to OSM zoom levels", "on the entire map".
   - List every row that moves later. The owner sees them in the renders.
3. **Earlier owner rulings on specific zooms are superseded** by "on the entire map". Examples:
   - -1737's buildings from zoom 14;
   - -27197's glyph minzoom 12;
   - patch 0005's minor roads at z10.
   - List each one you change, with its RECORD number, so the owner can see them.
4. **The size floors change too:** land-use polygons (`L:267-268`, and the bbox filter at `L:332-348`) and water
   (`W:363-364`). They change so small areas appear at OSM's zooms. Measure the cost in Z2's size test.
5. **Not in this fix:** things only one map draws (Juniper's B2). That includes kinds our style has no layer
   for. List them for the owner, and don't add them.
6. **The style:**
   - Edit through `map-style/generate-street.mjs`, not by hand, on Forager branch `osm-zooms-style`.
   - Write the result as a new file, `map-style/forager-street-v5.json`.
   - Don't wire it into the Worker or the app.
   - **Whether it ships as v5 or replaces v4 in place** is decided before the merge, with the owner. Read
     before deciding:
     - `StreetStyle.kt:15-21` says a style URL "never changes meaning", because MapLibre keys downloaded regions
       by it;
     - the Worker serves styles with `max-age=86400`.
7. **The data:**
   - Patch `0008-osm-first-zooms.patch` on `osm-zooms-map-build`, from `53a728341`, as filed.
   - Read Natural Earth's per-feature `min_zoom` where it decides a row.
8. **The tests, as filed in Z2,** with these changes:
   - "first appears at OSM's zoom" now means camera N − 1.5, with tile level N − 2 in the decode;
   - the renders use a MapLibre page set up like the app: OSM as a 256 px raster, ours as the vector style. Both
     at the same camera zooms.
   - Include the owner's Molalla views, and one zoom either side.
9. **Timing:** writing the code can start now. **No test build runs until coder-12's convert has finished** and
   Willow has reported Hold 2.

## Update, 14:55 PST: Juniper's report complete; the two points it left open

- **Juniper's report:** complete at `53c5d6801`. It recorded Aspen's answers at `026c7748f` (Forager
  `osm-zoom-levels`).
- **v1 (and v2, v3): frozen, not changed.**
  - They're served only for regions downloaded against them (`StreetStyle.kt`: a style URL "never changes
    meaning").
  - v1's z14 streams stay as they are.
- **The offline style's missing labels:** not added in this fix. Adding labels is new content, not a zoom.
  - It goes on the owner's list with the B2 items. Its existing layers' zooms are matched, like v4's.
- **Z2's scope is unchanged:** the new v5 content, plus the offline style's existing layers, plus patch 0008.

## Correction, 14:56 PST: osm-zooms-style is cut from origin/pre-main, not origin/main

This supersedes "cut from origin/main" in Z2's Style item.

- **Found by Willow** (read at 14:58). **Checked by Aspen:**
  - origin/main `8d0eefdbc`'s `map-style/` has only v1 and v2, without `overrides/forager-fill-in.mjs` or
    `forager-reference.mjs`;
  - origin/pre-main `04746d8f0` has both, plus v3 and v4;
  - pre-main's `generate-street.mjs` imports `applyFillIn` and `withReferenceLayers` (lines 33-34);
  - main's `street-style-v4.json` came by the folder-only Worker release `328a1388f`.
- **Planner's word:** cut `osm-zooms-style` from origin/pre-main `04746d8f0`. Add `forager-street-v5.json`, wired
  to nothing. No push to main or pre-main.

## Update, 15:58 PST: the offline style's zooms go in a new file

This supersedes "match the zooms … in offline-style.json" in the Juniper update.

- **Willow's flag:** pre-main's `index.ts:372-378` says "/style/offline.json is untouched for the same reason
  (-1294)". MapLibre keys a downloaded pack by its style URL.
  - `worker.test.mjs:204-208` would pass an edit in place, but the edit would change what every older pack's
    URL means.
- **Planner's word:** the offline zooms go in a new `map-style/forager-offline-v2.json`, wired to nothing, like v5.
  `offline-style.json` stays byte for byte.
  - Whether each ships as a new file or in place is decided with the owner at the merge.
- **Willow's mapping, accepted:**
  - the offline style's 57 layers take v5's zooms;
  - `landuse_park` and `roads_other` are split by kind;
  - `water_stream` goes from 14 to 10.5 and 11.5;
  - no labels are added.
- **Relief:** the merge was at about 3 of 25 GB at 15:56 (Willow).

## Update, 17:57 PST: Hold B; a tile-size test first, then the install, then the build

- **Willow's Hold B** (`willow-osm-zooms` `41fa3ec`, `z2-report.md`; observed by Willow):
  - **The code:**
    - patch 0008 is Forager `osm-zooms-map-build` `96e4c0305`, 1,404 lines; 590 tests pass, with 77 new; jar
      `3b90772f`;
    - Street v5 is `osm-zooms-style` `50242c74c`: 181 layers, 55 of v4's 104 changed;
    - `forager-offline-v2.json` is `5d8653721`.
  - **The Molalla test:**
    - 33 data classes pass at N − 2.
    - Two fail on length, not zoom: two tiny highway=road pieces and one 44 m tunnel, under the 0.5 px line
      floor.
    - The z15 counts are equal, except +12 stream lines from merging.
    - The archive is +8.2%, and the busiest tile is 193 KB gzipped.
    - 36 render shots, with no errors.
  - **Projection** (inferred): 38-42 GB, and about 14.5-15 h for the run.
    - **The risk:** at 3-5× landuse, the densest z7-z10 tiles could reach about 1-1.5 MB gzipped.
- **Aspen's spot-check:** 0008's water values (rivers 6, streams 10, intermittent 11) are carto's 8, 12 and 13
  minus 2.
- **The planner's word:**
  1. **(a) first:** take the 5 largest z7-z10 tiles in the live archive, and build an extract over the biggest,
     patched and with the control.
     - Pass: no tile over 500 KB gzipped, and the quarter-pixel floor stays at every zoom.
     - Otherwise (b): the 2 px floor below z11. Retest and report.
  2. **If (a) passes, the install:**
     - first a rollback copy of jar `25e5b8db` and map-build `53a7283` in
       `/mnt/storage/rollback/basemap-jar-before-coder13/`;
     - then map-build `96e4c0305` and jar `3b90772f` into `/opt/forager-build`.
     - Then Hold C. No build.
  3. **Then Aspen starts `build-usca.sh --local 261030 --force`** as forager-build.
     - `--force` is needed because the extracts equal current's manifest (lines 624-628).
     - With `USCA_KEEP_GOOD_OUTPUTS=1` (pins.env:237), publishing removes the current local output. That's the
       owner's rotation rule.
     - R2's live `us.pmtiles` is untouched until the owner's upload go.
  4. **For the owner:** the renders, rail drawn at 0.45 px, the half-zoom residuals, the superseded rulings and
     the B2 list.
     - The style merge and the wiring of v5 and offline-v2 wait for the owner's look.

## Update, 18:39 PST: (a) failed on tile size; (b) passes; re-render, then install

- **Willow's results** (all observed by Willow):
  - **The 5 largest live tiles per zoom** were read from `out-usca/current`. The biggest is 8/70/97, at 352,503 B.
  - **The dense extract** covers 8/70/97 and its 8 neighbours (-82.97,37.72 to -78.75,40.98).
    - The control reproduces the live 8/70/97 exactly.
  - **(a), the quarter pixel at every zoom: FAIL.**
    - 4 tiles were over 500 KB gzipped: 7/35/48 at 1 MB, and 8/70/97, 8/71/97 and 8/69/97.
    - 8/69/96 was at 497 KB.
  - **(b), upstream's 2 px floor and bbox filter below z11, the quarter pixel from z11: PASS.**
    - It's Forager `osm-zooms-map-build` `e904af99a`; 590 tests pass. The jar is
      `5f9a8bcdf60a35f6d8332f81919ba0c131a005762855116878fe7f1dd3c3c754`.
    - No tile is over 500 KB. The largest is 8/70/97 at 387 KB, against the control's 352.
    - Landuse equals the control at z0-10. The archive is +5.1%.
- **What (b) means for the owner:** below camera zoom 11, small land fills come in 1-2 zooms after OSM's, as
  they do in v4 today. From 11 they match.
- **The planner's word:**
  1. Re-render all 12 Molalla views with the (b) jar first, keeping the (a) set labelled.
  2. Then the install: the rollback copy first, then `e904af99a` and jar `5f9a8bcd…c754`. This replaces
     `96e4c0305` and `3b90772f` in the Hold B update.
  3. Then Hold C.

## Update, 19:08 PST: installed by Aspen on the owner's word; the zoom-fix map build is running

- **Willow's session refused the install.** Its permission check called it "Modify Shared Resources". Willow
  asked Aspen to run it instead.
  - Aspen didn't run it on that request, and asked the owner (question tool, about 19:00).
  - The owner: "Yes, Aspen installs (Recommended)", which covered the install, then starting the rebuild from
    the 10-30 data.
- **Before the install** (observed by Willow, checked by Aspen):
  - the rollback copy `/mnt/storage/rollback/basemap-jar-before-coder13/` (jar `25e5b8db`, map-build
    `53a7283` as a tarball, `SHA256SUMS`): `sha256sum -c` OK;
  - the (b) renders, 12 views, in `willow-osm-zooms` `650b83e`, under `renders/0008b-as-installed/`;
  - the peak-label fix, in style `d7c57375c`.
- **The install, 19:02:55-19:02:57 (observed):**
  - from `~/scratch/coder13/forager-mapbuild`, which is clean at `e904af99a`, with `install-map-build.sh`;
  - the jar `basemap.prev-20261102` was kept, and the tested `0008b-5f9a8bcd.jar` was installed.
  - **Checked after:**
    - `map-build/COMMIT` is `e904af99ae28…`, and `pins.env` lists 0008;
    - the jar's sha256 is `5f9a8bcdf60a…c754`;
    - `map-build.prev` is `53a7283`, and the previous jar is `25e5b8db`.
- **The build:**
  - `sudo systemd-run --unit=forager-build-usca-zoomfix --uid=forager-build` with HOME and the working folder
    `/srv/forager-build`, Nice 10 and CPUWeight 20, as the weekly unit has;
  - the command is `build-usca.sh --local 261030 --force`.
  - **Started at 19:03:17** as run `usca-20261103T030317Z`:
    - the 10-30 extracts, with 0 to download;
    - the NVMe check: 161.0 GB free, and 157.1 GB needed, which includes the 10% margin.
  - **The disk guard** `forager-build-zoomfix-diskguard` stops the build if `/` falls under 4 GB free, and
    ends with the build.
  - The build's stop is `sudo systemctl stop forager-build-usca-zoomfix`. Previous outputs are left untouched
    on a stop.
- **Expected** (Willow, inferred): about 14.5-15 h, so done about 10:00 on 11-03, at 37-39 GB.
- **After the build:**
  - the build's own checks, then Aspen's against the live map;
  - the upload to R2 needs the owner's go;
  - the style merge, and the wiring of v5 and offline-v2, need the owner's look at the renders.

## Update, 20:20 PST: skip the routing rebuild; upload when the checks pass (owner)

- **The owner,** through the question tool at about 20:15:
  - "Skip routing (Recommended)";
  - "Upload when checks pass (Recommended)".
- **Why skipping is safe:**
  - The zoom fix changes only the basemap. The routing, names and BRouter stages would rebuild exactly what's
    live, from the same 10-30 extracts.
  - In the 11-01 run those stages took 4 h 47 min after Planetiler's 9 h 02 min (read from its log).
- **The chain:** `/mnt/archive/aspen-upload-us-zoomfix/chain.sh`, started 20:20:15, pgid 118004, as bwann83 under
  `setsid nohup`. It logs to `chain.log`. In order:
  1. **Waits for run `usca-20261103T030317Z` to leave the planetiler stage.**
     - It requires "planetiler … exit 0" in the run log.
     - At `routing-input` it runs `sudo systemctl stop forager-build-usca-zoomfix`.
     - A stopped run moves its `out/`, the basemap, to `failed-usca/latest/` (`build-usca.sh:139-151`).
  2. **Runs `check_map.py` on the kept basemap:**
     - the build's own archive checks (zooms 0-15, bounds, 9 layers, the six trail keys);
     - the coverage points (a z15 tile with roads at each);
     - size 33-45 GB, and addressed tiles at least the live count;
     - `versions.txt` names jar `5f9a8bcd`, and Planetiler exited 0;
     - **the zoom fix itself:** Molalla's z6 tile 6/10/23 has water lines in the new map and none in the live one.
     - **The control run, 20:1x,** with the live archive standing in as the new: every check passed except the
       two fix checks (the jar and the z6 rivers), which failed as they should.
  3. **Only if every check passes, `upload_us.py`:**
     - from 11-02's uploader, 2 parts at a time, IPv6 only;
     - it logs the live object first, then replaces `r2:forager-maps/us.pmtiles`;
     - the read-back: size, ETag from the local parts, md5 metadata, first and last MiB.
  4. **The Worker:** `/us/6/10/23.mvt` compared with the new tile.
- **Expected** (inferred): Planetiler ends about 05:00, and the upload of about 37-39 GB takes about 3.5 h, so it's
  live about 08:30-09:00.
- **Routing on R2 is unchanged.** The weekly run on 11-08 does a full build with 0008.
- **The local 11-01 output stays in `out-usca/current`,** since publish doesn't run. It's the local rollback copy.
- **Stops:**
  - the chain: `kill -TERM -- -118004` (bash);
  - the build: `sudo systemctl stop forager-build-usca-zoomfix`;
  - the upload: its pid, logged in `chain.log`.

## Update, 20:21 PST: the owner's word on skipping

- **The owner, verbatim:** "If routing still works by skipping it we should do it since the downloaded maps are so
  close together", then "I fact anything we can skip for this build, we should".
- **Routing still works** (read): the live route squares come from run `usca-20261101T174337Z`, which was built
  from the same 10-30 extracts (its log has `routing-filter-us-261030`). The new basemap is built from the same files.
- **What's left, and why none of it is skipped:**
  - Planetiler: this is the zoom fix itself.
  - `check_map.py`: 2-3 minutes, and the guard on the live map.
  - The upload: a whole-file replacement. 2 parts at a time is the most the Wi-Fi took on 11-02.
- **Already skipped:** routing, names, BRouter, the build's validate (replaced by `check_map.py`) and publish.
- **Already done:** the fetch (local) and the merge.

## Update, 22:34 PST: the NVMe would run out at the archive stage; the 11-01 output moves to the USB drive

- **The 22:30 check** (observed):
  - Planetiler is in `osm_pass2` at 3:01 elapsed, 106M ways (50%).
  - **The features file is 48 GB, against 41 GB for 11-01 at the same ways count.** At 2:30 and 2:00 the ratio is
    also about 1.15-1.17.
  - At 22:31, `/` had 84.6 GB free; memory 3.0 GiB available; 63.7 °C; `throttled=0x0`. The disk guard is active.
- **Projection** (inferred from 11-01's log and the ratio):
  - 11-01's features ended at 108 GB, and its archive at 35 GB.
  - Here: features about 125 GB, the node map (27 GB) freed after pass 2, and an archive of about 38 GB. That's
    about 166 GB at the peak, against 161 GB free at the start.
  - So the disk guard would stop the run during the archive stage, about 03:00-04:30, and the night's work would
    be lost.
- **The fix (Aspen, no data deleted):** move `out-usca/20261030T212451Z` (36 GB, the 11-01 output, the local copy of
  the live map) to `/mnt/storage/forager-build-out-usca/`.
  - Verify every manifest output's sha256 on the copy.
  - Then remove the NVMe copy and put a symlink at the old path, so `current`, `check_map.py`'s LIVE path and
    the weekly build still resolve.
  - That gives about 30 GB of headroom at the peak (inferred).
  - `/mnt/storage` is `/dev/sda1` ext4 rw with 111 GB free (read 22:33).

## Update, 23:04 PST: the 11-01 output is on the USB drive, verified; the NVMe has 105 GB free

- **The copy** (observed): `sudo rsync -a`, 22:33:47-22:58:08.
  - The check, 22:58-23:03:21: all 375 manifest outputs on the copy match their sha256, with 0 mismatches, and
    the bytes are equal at 37,609,850,859.
- **23:04** (observed):
  - the NVMe copy is removed;
  - the symlink is `out-usca/20261030T212451Z -> /mnt/storage/forager-build-out-usca/20261030T212451Z`, owned by
    forager-build;
  - `current` still resolves to it, and `pmtiles show` reads maxzoom 15 and 651,232,395 tiles;
  - `/` went from 74.6 GB free to 105 GB.
- **Projection** (inferred): about 30 GB of headroom at the peak, **if** Planetiler frees its 27 GB node map after
  `osm_pass2`. Aspen checks that at about 01:00.
- **Kept:** the 11-01 output, now on USB. It's the local rollback copy, and `check_map.py`'s LIVE control. When it's
  no longer needed, the symlink comes out with it.

## Note, 01:14 PST (11-03): words to use, from the owner

- **The owner, verbatim:** "Refer to our maps as trail maps, and not osm.. To avoid confusion".
- **From here:**
  - **"Trail Map"** means ours: the app's "Forager Trail Map", its tiles `us.pmtiles`, and its styles Street v4
    and v5.
  - **"the OpenStreetMap map"** means only the app's reference basemap, tile.openstreetmap.org.
  - **"OSM data"** stays for the source data.
- **This dispatch's title and earlier wording** ("our map", "OSM's zooms", "street map") stand as written. Read
  them in these terms.

## Note, 03:27 PST (11-03): the OpenStreetMap style is an inspiration, never published (owner, via Rowan)

- **The owner, to Rowan, verbatim** (RECORD -1985, `f244beed9`): "OSM refers to the style, but we don't want to
  publish that anywhere since it's an inspiration and not the target to copy directly."
- **Read by Aspen at about 02:0x:**
  - **Both repos are public** (`gh repo view … isPrivate` = false for slayer8366/Forager and slayer8366/Forager-cartography).
    - So today's branch names (`osm-zooms-*`, `osm-zoom-levels`), patch `0008-osm-first-zooms`, Juniper's comparison,
      these dispatches and the records are publicly visible.
  - **The served v5 and offline-v2 styles (not yet wired)** name it in their `metadata`:
    - v5: `overrides/forager-osm-zooms.mjs`;
    - offline-v2: "(OSM's first zooms)".
    - Both also carry the "© OpenStreetMap" data credit, which ODbL requires and which stays.
  - **The Trail Map archive is clean:** patch 0008 changes no archive metadata, and the live `/us.json` holds only the
    upstream description and the data credit.
    - So tonight's upload publishes nothing new on this point.
- **Waiting for the owner:** whether "publish" covers the public repos (new names only, or also renaming and
  rewriting what's already there), or only what users see (the app and the served styles and TileJSON).
- **Done in either case:** the served styles get neutral metadata before they ship.

## Note, 05:16 PST (11-03): the owner chose a full clean-up, history included

- **The owner, through the question tool:**
  - "Option 3, clean it all up". Option 3: rename branches and files, and edit or rewrite the existing records.
  - Then "Also rewrite history". That option: a force-push rewrite of both repos. Every commit id in the records,
    builds and copies changes; every session stops and re-clones; GitHub keeps the old PR commits unless
    GitHub Support purges them.
- **Read first** (02:1x):
  - no branch is protected in either repo;
  - Forager has 1,205 remote branches, 9,915 commits and no tags.
  - Rowan's Juniper inventory (`d66096114`, Forager `juniper/osm-style-name-check`, dispatch 2026-11-03-02)
    found 0 public lines and 26 internal lines in pre-main's tree that name the reference style as ours or as a
    target. Data credits and data references are out of scope.
- **Proposed to Rowan** (who owns Forager's records):
  1. one term list, kept on the Pi only, outside the repos;
  2. a dry run in mirror clones, reviewed by both planners;
  3. a pause window for every pushing session;
  4. the force-push of all refs, then a commit at each tip translating old commit ids from filter-repo's map;
  5. re-clones on the Pi.
  - Not before the Trail Map upload is done.
- **This repo's own wording from here is neutral.** The dispatch file names here change in the rewrite.

## Correction, 05:23 PST (11-03): times in tonight's notes; and the Trail Map's checks passed but the upload waited for Wi-Fi

**The times.** This supersedes the times in the three notes above, which were estimated, not read. Times from the
commit clock:
- The words-to-use note: commit `2709bcf`, at the time git shows for it.
- **The "inspiration, not the target" note** was committed at 03:27:33. The owner's word via Rowan came shortly
  before. It was not "about 02:0x".
- **The full clean-up note** was committed at 05:16:43. The owner's "Option 3, clean it all up" and "Also rewrite
  history" came shortly before. It was not "about 02:15".
- The clock read 05:18:15 at Aspen's next reading.

**The overnight chain** (`chain.log`, observed):
- **04:32:54:** the run left Planetiler for `routing-input` and was stopped. The basemap is kept:
  37,141,650,068 B at `failed-usca/latest/out/forager-usca.pmtiles`.
- **04:32:55: `check_map.py`, every check PASS:**
  - zooms 0-15, bounds equal to live, all 9 layers, the 6 trail keys;
  - size 37.1 GB, and addressed tiles 651,232,395, equal to live;
  - `versions.txt` names jar `5f9a8bcd`, and Planetiler exited 0;
  - all 9 coverage points have roads;
  - **the zoom fix: new 6/10/23 has 207 water lines (kind river), and live has 0.**
- **04:32:56: `upload_us.py` stopped**, "R2 over IPv6: False (no IPv6 route to 2606:4700:2ff9::1)". Nothing was
  uploaded, and the live `us.pmtiles` is untouched.

**Why:**
- The Wi-Fi had dropped at **20:44:04 on 11-02**: `CTRL-EVENT-ASSOC-REJECT status_code=16`, then NetworkManager
  "no-secrets", and `wlan0` was left inactive.
- Since then the Pi had run on the Bluetooth tether to "Brandon Lee's Tab S8+" (`bnep0`), which carried tonight's
  pushes and the Worker deploy checks.
- The uploader's Wi-Fi-only rule kept 37 GB off the tether.

**Rejoined:**
- At 05:19:12, "Virusdownloader" was visible: channel 44, signal 65, WPA2.
- Aspen ran `sudo nmcli --wait 45 con up Virusdownloader` at 05:19:20, and it was active at 05:19:53. IPv6 default
  route via `wlan0`; R2 answered 400 over IPv6.
- IPv4 on `wlan0` hadn't come back at that reading.

**The upload restarted at 05:23:22:** `resume-upload.sh` (`upload_us.py`, then the Worker tile compare), pgid 154695,
"R2 over IPv6: True".
- Expected about 3.4 h at about 3 MB/s, so about 09:00 (inferred).
- Then the cache version goes to "3", with Sorrel's should-fix tests.

## Update, 09:02 PST (11-03): the zoom-fix Trail Map is live on R2, read back; the Worker serves it

- **The upload** (`chain.log`, observed):
  - local size 37,141,650,068, 554 parts, sha256 `8e3f51de64dc69eeb1fcd12c778a018f2accacba5386e890782471d832e44f47`;
  - the live `us.pmtiles` before: 35,256,335,758 B, ETag `b8adb3d8bc7f8ae187c789dcfb2143d3-526`, last modified 2026-11-02 18:29:35 UTC;
  - 05:27:59-06:51:12, 554 of 554 parts, about 7.4 MB/s, 0 failed attempts.
  - **The read-back, 06:51:14-15:**
    - R2 size equals the local size;
    - the R2 ETag `1f7de3da54ff12bc925b98981770ee51-554` equals the one from the local parts;
    - the md5 metadata matches, and the first and last MiB are equal.
  - DONE.
- **The chain's Worker check** said "HTTP 200; identical: no". That's a flaw in the check, not the upload: the
  Worker sends tiles decompressed, and the archive stores them gzipped.
- **Aspen's check, 09:01-09:02:** for `/us/6/10/23.mvt`, fresh and plain URL alike, the Worker answered 200, 91,718 B,
  uncompressed protobuf.
  - Its water layer has **211 features, 207 of them river lines**. That's the same as the new local tile (gzipped,
    63,956 B). The old local tile has 4 water features and 0 lines.
  - `/us/10/163/367.mvt` (plain) has 72 water features and 69 lines.
  - Neither was a cache HIT at that Cloudflare location.
- **Next:**
  - the `CACHE_VERSION` "3" raise (coder-14, with Sorrel's should-fix tests), sent to Willow at 09:0x, for tiles
    cached at other locations between 01:47 and 06:51;
  - the style (v5, or v4 in place, with neutral metadata) waits for the owner's look at the renders.
- **Kept for rollback:** the 11-01 output, on USB with a symlink.

## Note, 11:00 PST (11-03): figures for the clean-up's term list sent to Rowan

- **Rowan's 16 items** (Q01-Q11 and F01-F06; Q10 needs none) were read from the reference stylesheet's source on the Pi
  by a read-only helper. Aspen spot-checked them, and sent them to Rowan by message, for Juniper's working list.
- **The figures and their sources stay out of the repos** (the owner's ruling, RECORD -1997, via Rowan).
- **The helper's only writes:** a scratch clone and a compute script in `/mnt/archive/history-rewrite-20261103/figures/`.

## Note, 13:41 PST (11-03): the history clean-up dry run is done (method check); Forager's list goes back to Rowan

- **A read-only helper ran it** in fresh mirrors on the Pi's SD card (`/mnt/archive/history-rewrite-20261103/`), using
  git-filter-repo 2.47.0. Nothing was pushed.
  - Bundles of both originals verify, and pushing from the backup mirrors is disabled.
- **Results:**
  - **Binary blobs:** 0 changed (filter-repo skips any blob with a NUL in its first 8 KiB).
  - **Every predicted blob id matched.**
  - **Only text changed,** across all refs.
  - **No path or ref keeps the renamed words.**
  - **Protected strings are unchanged:** data credits, osmdroid, .osm.pbf, BRouter classes, the app's Cartography feature.
- **Found, and sent to Rowan for Forager's list:**
  - filter-repo runs literal rules before regex rules, whatever the file order;
  - the button-label rules break one app test on 470 branches;
  - one citation regex also removes four BRouter file references;
  - "OSM Carto" comes out half-replaced;
  - some text is still left;
  - 2,414 commit ids cited in Forager's files need the translation commit;
  - 350 PR pages keep the old text.
- **The run used tips from before Rowan's three merges.** A repeat script re-runs it on fresh mirrors.
- **Cartography's draft list** (Forager's 249 lines plus 51 regex additions) waits for Rowan's revised list.

## Update, 14:22 PST (11-03): the owner approved the zoom; v4 is updated in place; the merges go before the rewrite

- **The owner, after looking at the renders:** "I approve the zoom. Go ahead and merge when ready".
  - Then, through the question tool: "Update v4 in place". The other option was a new version shipped with the
    next app update.
- **Style** (a helper briefed as Willow, since Willow is offline; dispatch in its brief):
  - Regenerate street-v4 (today's app) and trail-v4 (pre-main's app) with the approved first-zoom layers, from the
    one generator, and offline.json in place too.
  - v1-v3 stay byte for byte. The metadata is neutral, and the data credit stays.
  - Worker CACHE_VERSION goes 3 → 4.
  - **Rowan's five conditions:**
    1. update the frozen-v4 sha checks in the same PR;
    2. the two v4 files differ only in `name`;
    3. the PR states what an old v4 download shows;
    4. full CI green, with the run id;
    5. Rowan's #472 goes first.
  - Then a pre-main PR, Aspen's merge, and a folder-only release to main.
- **Data:** Forager PR #473 takes the installed map-build (patch 0008, `e904af99a`) into pi-build as a fast-forward.
  Rowan has had a line; Aspen merges on green CI.
- **Order, agreed with Rowan:** these merges first, then the real clean-up run on the finished state.

## Note, 14:42 PST (11-03): the clean-up waits until after the release (owner)

- **The owner, via Rowan** (RECORD -2016): "Hold until after release".
- **Kept ready** on the Pi's SD card:
  - the term list;
  - the repeat script with the id translation;
  - the verified bundles of both repos.
- **The real run starts** on fresh mirrors from the post-release tips, when Rowan says the release is out.
- **The style PR and its Worker release** go ahead as normal.

## Update, 15:19 PST (11-03): style PR #474 at Hold A; trimmed to v4 only

- **Forager PR #474** (`trail-v4-first-zooms` into pre-main, from `671b669bf`), the helper briefed as Willow
  (observed by it):
  - street-v4, trail-v4 and their previews are layer for layer identical to the approved v5: 182 of 182 layers, 0
    differences.
  - The Molalla z12 render is pixel-identical to the approved panel. A control against the old v4 differs by 2.96%.
  - v1-v3 are byte-identical.
  - The new style loads against 11-01-build tiles with no errors.
  - Worker tests 80 of 80, and the naming grep has 0 hits outside the data credit.
- **CI was red** (run 41733683461):
  - OfflineNightRecolourTest failed, from the offline-in-place commit;
  - RouteCardOnNavigationCardFont20Test fails on pre-main itself too.
- **Aspen's decisions:**
  - Drop the offline-in-place commit. Rowan's condition limits the override to v4, and offline.json reaches the
    release app's downloads, which is beyond the owner's "v4 in place". Aspen had added it on its own reading;
    that was too broad.
  - Drop the CACHE_VERSION 4 commit: styles are bundled, not edge-cached.
  - The branch is now the v4 commit only, with CI re-run.
- **Found:** a night gap in test builds. The app's night tables are keyed by layer id, so 13 of the new clone
  layers lose their named night colour until the app maps clones to originals (`forager:layer-clones`). Rowan has
  been asked: before #474, or as a follow-up.
- **Waiting on Rowan:** the pre-main test that already fails (fix or waive), and the night-gap timing.

## Update, 15:40 PST (11-03): #474 is v4 only; CI matches pre-main's known red

- **PR #474's head is `821fa67d6`** (offline and CACHE_VERSION commits dropped).
  - It changes 12 files: the v4 styles and their Worker copies, the generator, the override, the checks and the
    tests.
  - Checked by Aspen: offline-style.json is unchanged against pre-main, and CACHE_VERSION is "3".
- **CI run 41738214180:** 6 jobs pass. The two app-test jobs fail only RouteCardOnNavigationCardFont20Test, the same as
  pre-main's own run 41728736456. Rowan is fixing it, with no waiver.
- **For Rowan's app PR:** #474's body has the 13-clone night table (clone, original, intended night colour with its
  source line, today's value). That fix is needed before any promotion.
- **Next:** pre-main green, then #474 updated and green, then Aspen's line to Rowan, then the merge, then a
  folder-only Worker release to main (after #472, which is merged).
