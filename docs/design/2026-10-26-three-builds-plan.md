# Three Pi builds for the app: plan

Written by the planner session (Aspen), 2026-10-26, about 16:45 PDT. Times are PT.

## Source

Rowan's brief, Forager `records-after-173` at `edab1ecf2`, `prompts/preserved/2026-10-26-20-aspen-brief.md`
(RECORD -1693). The owner's words, as the brief quotes them: "Let's put Aspen to work on the build". Then
all three builds. This is a plan only. Nothing was installed, downloaded, built or uploaded. The only
network calls were read-only metadata and count queries to the two trail services.

Marks: **read** (a file, a command or a service answer, cited), **computed**, **inferred**.

## The Pi today (read, 16:15-16:40)

- **Sunday's build finished OK** at 18:01 on 10-25. Run `usca-20261025T101217Z`, OSM 2026-10-24T20:20:51Z,
  about 14.8 h (`status-usca.json`). Its 187 route squares (1.5 GB) are in `out-usca/current/segments`.
  Its extracts are still on the card (`/mnt/archive/forager-build/sources-osm/*-261024.osm.pbf`, 18.8 GB)
  until the next publish deletes them.
- **R2 still has the 261021 route squares** and the 261021 basemap. Nothing from Sunday is uploaded.
- **NVMe headroom is about 6 GB.** 162.5 GB was free at Sunday's start, and the check needed 157.2 GB
  (`logs/usca-20261025T101217Z.log:9`). Today `df` shows 152 GiB, about 163 GB, so nothing has changed.
  **Anything new that stays on the NVMe comes out of those 6 GB, one for one, and would stop the next
  weekly build at its disk check.**
- **The card has about 57 GB spare.** 100.3 GB was free at the start, and the run needs 42.6 GB there
  (`:10`).
- **The 256 GB USB storage drive is not plugged in.** `/dev/sda1` is a 57.6 GB drive labelled
  `forecast-data`. `/mnt/storage` is an empty folder on the NVMe, so the rollback copy can't be reached.
  Per [usb-storage], nothing is written there until `findmnt` shows the drive.
- **Tools:** GDAL is not installed (`apt-cache policy gdal-bin`: candidate 3.6.2). osmium 1.15.0, the
  `pmtiles` CLI 1.31.2, Node 22, the JDK and BRouter 1.7.10 are all present.
- **The weekly timer's next run is Sun 11-01, 02:13 PST.** Nothing below runs while it is building.

## Order

Rowan's order, kept: 1 (reference trails), then 2 (names), then 3 (elevation). Builds 1 and 2 are small
enough to finish before Sunday 11-01. Build 3 is a pilot this week; the full download comes after.

Each step needs its own go, as with the topo plan:

| Go | What | Pi cost |
|---|---|---|
| G1 | `apt install gdal-bin python3-gdal` (39 packages, about 88 MB; topo sizing). Needed by builds 1 and 3. | minutes |
| G2 | Build 1: fetch both services, tile, report the size. No upload. | under 1 h (inferred) |
| G3 | Build 1: upload `reference-trails.pmtiles` and its manifest to R2. | minutes |
| G4 | Build 2: measure names files on two squares from the 261024 card extracts. No install. | under 1 h (inferred) |
| G5 | Build 2: names stage in the build (Willow), run once on 261024, upload 261024 squares + names as a new run. | a few hours |
| G6 | Build 3: elevation pilot on two 5° squares (about 2-3 GB download). | half a day (inferred) |
| G7 | Build 3: full DEM download and `.bef` store (about 140 GB read, 2-3 days). | days |
| G8 | Build 3: point the weekly build at the `.bef` store. | +minutes a week (inferred) |

## 1. Official-trails archive, `reference-trails.pmtiles`

### What the app expects (read at origin/step8c-reference-tap)

- R2 object `reference-trails.pmtiles` (`forager-reference.mjs:25-26`), read by the Worker's generic
  path (`shared.ts:6-14`). There is no allowlist of archive names.
- Zooms 10-15 (`:29-30`). **The header's maxzoom must be 15.** The overflow branch (`index.ts:559-567`)
  serves any archive's z > maxzoom (up to `OVERFLOW_MAX_ZOOM = 15`, `:622`) from Protomaps' basemap.
  It also writes the result to R2 at `overflow/reference-trails/…` (`:211-212`, `:258-262`), so a z14
  archive would leave wrong tiles behind that stay.
- Source-layers `fs_trails` and `blm_trails` (`:33`).
- Fields read: `trail_type` (exact, case-sensitive `!= "SNOW"`, `:70`), `trail_no` (shown as is, `:107`),
  `trail_name` (`:48`), `ROUTE_PRMRY_NM` (`:49`).

### Field names checked against the services today (read)

| App field | Service | Result |
|---|---|---|
| `trail_no`, `trail_name`, `trail_type` | `apps.fs.usda.gov/arcx/rest/services/EDW/EDW_TrailNFSPublish_01/MapServer/0` | **Match**, lower case, all `esriFieldTypeString` (30, 30, 5). |
| `trail_no` leading zeros | the same, `where trail_no LIKE '0%'` | **Kept as text:** `"060"`, `"072"`, `"058"`, and also `"02S20C"`. The archive must keep it a string. A number would show "1" for "001" (`OverlayFeatures.kt:45-49`). |
| `trail_type` values | the same, distinct | `SNOW`, `TERRA`, `WATER`. Upper case, so the filter works as written. |
| `ROUTE_PRMRY_NM` | `gis.blm.gov/arcgis/rest/services/transportation/BLM_Natl_GTLF_Public_Display/MapServer/2`…`/6` | **Match**, upper case, on all five layers. |

**One difference for Rowan, address only:** the BLM service's name is `BLM_Natl_GTLF_Public_Display`. The
catalogue name "Public Managed Trails" is not a service name: `/transportation` lists only `_Display`.
Layers 2-6 are the five "Trails …" layers, and 7 is "Trails Managed for Public" (excluded, as the report
says). **No field the app reads changes.**

Counts today (read): FS 86,422 features; BLM layers 2-6: 1,925 + 5,291 + 3,044 + 2,318 + 5,038 = 17,616.
The `attributesubset` values are `TrailNFS_Basic`, `TrailNFS_Centerline` and `TrailNFS_MGMT`.

### Build (proposed)

1. **Fetch:** `ogr2ogr` from each service's REST query, paged (maxRecordCount 2000, so 44 + 10 pages;
   computed), into one GeoPackage in a work folder on the NVMe (tens to low hundreds of MB, inferred).
   - FS keeps: `trail_no`, `trail_name`, `trail_type`, `trail_class`, `attributesubset`, `admin_org`.
   - BLM keeps: `ROUTE_PRMRY_NM`, `FAMS_ID`, `ADMIN_ST`, plus `gtlf_layer` (2-6), added by us.
   - Field names are kept exactly as the services spell them. Nothing is joined to OSM.
2. **Tile:** GDAL's MVT writer to MBTiles, z10-15, two layers named `fs_trails` and `blm_trails`, with
   simplification held under about 1 m at z15 (report §7). Then `pmtiles convert`. This needs no new
   Planetiler profile and no tippecanoe (inferred; GDAL 3.6's MVT driver writes MBTiles).
3. **Check before upload:**
   - `pmtiles show`: header minzoom 10, maxzoom 15, both layers present.
   - Decode a z15 tile over a known trail with the tile tools ([tile-decode-tools]): `trail_no` a string
     with its zeros, `trail_type` present.
   - Attribution in the metadata: "USDA Forest Service" (CC BY 4.0) and "Bureau of Land Management".
4. **Coverage list (item 3):** read-only queries.
   - FS trail counts grouped by `admin_org` × `attributesubset`.
   - Compared against the list of national forests from the FS administrative-forest boundaries
     service. A forest with 0 rows publishes no geometry. A forest with only `TrailNFS_Centerline`
     rows publishes the subset.
   - Output: `reference-trails-coverage.json` and a short table in the record.
5. **Manifest (item 4):**
   `{run_id, built_at, file: {size, sha256}, sources: [{name, service_url, layers, features, last_updated}]}`.
   - `last_updated` comes from each source's own metadata: the FS metadata XML's date, and BLM's
     catalogue date (2026-10-13 per the report).
   - The services' `editingInfo` is empty (read), so the build can't use it.
6. **Upload (G3):** `rclone copy` to `r2:forager-maps/reference-trails.pmtiles` and
   `reference-trails-manifest.json`, read back by sha256, as for the route squares.
   - **No reference tile URL is requested before the upload:** the Worker caches a 404 for 24 h
     (`index.ts:502`, `:510-531`).
   - After the upload, one z10 and one z15 tile are checked through the Worker with a cache-busting query
     string. The cache key is the full URL, and the tile path is read from `pathname` (`index.ts:492`,
     `:502`).

**First number reported: the archive's size.** Unmeasured; my guess is tens of MB to about 200 MB
(inferred from the FS gdb's 119 MB, report §7).

**Question for Rowan:** does the 8d info card read the manifest as a separate R2 object (which needs a
Worker route), or from the archive's own metadata (`pmtiles` JSON metadata, already served)? I'll write
the dates into both unless told otherwise.

**Refresh:** standalone, run by hand when a source updates. It isn't part of the weekly build: the
sources aren't OSM and change on their own schedules. A monthly timer could come later; that's the
owner's call.

## 2. Trail-names file per route square

### What the Worker does today (read at origin/pre-main)

- **Area request:** `GET /routing/area.json?south&west&north&east`, with the longest side up to 50 km
  (`area.ts:13`). It answers with the 5° squares the box touches, at most four (`area.ts:81-94`).
- **Square cut:** each square is cut from R2 by ranged reads (`handler.ts:98`, `:116-130`) and served at
  `/routing/<run>/<NAME>.rd5?<box>` (`:49`, `:175`).
- **Manifest:** the parser reads only `run_id`, `osm_timestamp` and `files`, and every `files` entry
  must be `<run>/segments4/<NAME>.rd5` (`manifest.ts:41-58`). An unknown top-level key is ignored. A names
  entry inside `files` would make every routing request answer 503.

### Same extract

The build already makes the right input. `$routing_in` is the four extracts cut with `USCA_ROUTING_FILTER`
and merged (`build-usca.sh:720-730`), and it is deleted once the bands are cut (`:753`). The names stage
runs between those two steps, on that file, so names and squares come from one extract by construction.

### Content and format (proposed: "FNAM v1")

- **Which ways:** `highway=*` ways with a `name` or a `ref` in `$routing_in`. Area highways and
  `highway=proposed`/`construction` are left out. Railways and waterways are left out.
- **Per square:** one file `names1/<NAME>.fnm` per route square, with the same 5° grid and names as the
  `.rd5` files.
- **Inside, little-endian:**
  - header: magic `FNAM`, version 1, the square's west and south edges, the OSM timestamp, counts;
  - a string table of distinct names and refs (UTF-8);
  - a directory of 1/8° cells (40 × 40 per square), each with an offset and a length;
  - records, grouped by cell. Each record holds a name index, a ref index, the `highway` value as one
    byte (so the app can tell a trail from a road), a bounding box, and the points, delta-coded as
    zig-zag varints at 1e-6° (about 0.1 m).
- **Lines are split at cell edges** at build time, so each piece belongs to one cell. This doesn't affect
  matching, which compares names, not ways (report §2.1).
- **Simplified** by Douglas-Peucker at 2 m, well inside the 25 m join (`WayHome.kt:360`).
- **Worker cut:** read the header and directory, range-read the cells the area box touches (grown by
  50 m), and write a FNAM file holding only those cells. Then there is one format and one reader on the
  phone, and the cutter has the same shape as the `.rd5` one.
- **Tools:** osmium (`tags-filter`, a one-pass multi-box `extract -c`, `export` to GeoJSONSeq) and a short
  converter in Node 22, already on the Pi. No installs.

Rowan said Forager owns the reader, so this format is a proposal. If the app would rather have gzipped
GeoJSONSeq per square, the build is simpler and the files are larger. That choice is the planner's.

### Layout on R2 and the manifest

- **Files:** `routing/<run-id>/names1/<NAME>.fnm`, beside `segments4/`.
- **Manifest:** a new top-level `names: [{path, size, sha256}]` array in `routing/manifest.json`. Today's
  parser ignores it (read above), so it can go up before Hazel's Worker change and break nothing.
- **Worker change, Hazel's:** a `names` list in `area.json` and a route for `.fnm`.

### Timing (proposed)

- **G4:** measure the dense square `W75_N40` (the largest `.rd5`, 98 MB) and `W120_N45` (mountains,
  mostly trails) from the 261024 card extracts, cut the same way. This gives a size per square and a
  cut size for a 50 km area in each.
- **G5:** Willow adds the stage to `build-usca.sh` (Forager pi-build, as a patch with a test). It is
  run once by hand on the 261024 extracts **before Sunday 11-01 deletes them**. The 261024 squares and
  names then go up together as `routing/usca-20261025T101217Z/` with the manifest last. That also moves
  R2's routes from 261021 to 261024.
- **Disk:** the names files sit in the output beside the squares (`out-usca/<ts>/names`). The old
  output is removed only after the new one is published, so the NVMe holds two sets at peak. **They come
  out of the 6 GB headroom twice.** If the measurement shows more than about 1 GB per set, the disk
  check needs a decision before the stage goes into the weekly build.

**To report:** the format (above), sizes per square and per area (G4), and how it's cut (above).

## 3. Elevation (routing first, DEM shared with terrain)

### Chain (read)

- BRouter 1.7.10's jar on the Pi has `ElevationRasterTileConverter` (.hgt → .bef), `HgtReader` and
  `PosUnifier`, which reads `.bef` (`unzip -l`, `strings`). The PosUnifier usage string is
  `<srtm-data-dir> <lon> <lat>`.
- The weekly build gives PosUnifier an empty `no-elevation` folder (`build-usca.sh:765`, `:771-772`).
  Switching it on means pointing that argument at a `.bef` folder, with a pin in `pins.env`.
- The chain per 1° cell: windowed GDAL read of the COG → warp to EPSG:4326 on the hgt grid → `.hgt`.
  Then `ElevationRasterTileConverter` → one `.bef` per 5° square.

### Sources (topo rulings 5-6)

- USGS 3DEP 1″ for the US.
- NRCan MRDEM for Canada.
- One download, shared with terrain: the 1″ step is the input relief and contours will reuse.

### Where things live (proposed, because of the 6 GB)

| Data | Size | Where |
|---|---|---|
| `.bef` store at 3″ | 2-6 GB (inferred, unmeasured) | **the card**, `/mnt/archive/forager-build/elevation/bef3` (57 GB spare). Not the NVMe. PosUnifier's reads are small. |
| 1″ `.hgt`, kept for 1″ routing and for terrain | about 40-80 GB (inferred) | **the USB storage drive**, once it's plugged back in |
| staging | under 1.5 GB (sizing note) | NVMe work folder, removed per block |

If 1″ routing is chosen later, its store (20-45 GB) won't fit next to the weekly build on the NVMe or the
card. It would have to go on the USB drive, and the build would read it from there.

### Pilot (G6), after G1

Two whole 5° squares, so a real `.bef` is measured, not extrapolated:
- `W125_N45`: Olympics, Rainier and the coast, which tests the converter's "0 m = no data" at the sea
  (sizing unknown 5);
- `W100_N40`: plains.

Steps:
1. About 50 3DEP cells, roughly 2-3 GB at 1″ (inferred).
2. Make 1″ `.hgt`, then 3″, then `.bef`.
3. Rebuild those two `.rd5` squares with elevation from a cut of the 261024 card extract, in a scratch
   folder, not the build tree.

**Reported first:** `.bef` size per square at 3″, converter time, how much the `.rd5` files grow, and
PosUnifier's peak memory. Then an estimate of whether the weekly unit grows: minutes at 3″ by the sizing
note, to be confirmed.

### Full build (G7)

- About 60 GB of 3DEP for the US and about 84 GB of MRDEM, read in windows. At the sizing note's rate (about 2 days for
  128 GB on Wi-Fi), that's 2-3 days (computed).
- It runs outside Sundays, writes `.bef` to the card and 1″ `.hgt` to the USB drive, and is resumable
  by cell.
- **G8** then points the weekly build at the store. The routes only change in the app after the planner's
  own changes land: `consider_elevation` (`hiking-mountain.brf:13`) and height kept in `TrailRoute`
  (`BRouterTrailRouter.kt:114`, `TrailRouter.kt:41-45`).

## Decisions for the owner

1. **G1, install GDAL.** Recommended now: builds 1 and 3 both need it.
2. **Plug the 256 GB storage drive back in.** It's needed before G7, which writes 1″ `.hgt` there.
3. **Keep 1″ `.hgt` (about 40-80 GB on the USB drive), or discard it after making 3″?** Recommended:
   keep it, because terrain (ruling 6) and any later 1″ routing reuse it and avoid a second 2-day
   download.
4. **G5's upload moves R2's routes from 261021 to 261024.** Recommended: yes, so names and routes match.

## Not done here

- No size was measured; every size above is inferred, apart from the counts and fields read from the
  services.
- `ElevationRasterTileConverter`'s exact arguments weren't read beyond its strings. Willow reads them
  in the pilot.
- The FS metadata XML's date field wasn't read.
