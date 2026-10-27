# Three builds, day one: GDAL installed, trails archive built, names measured, pi-31 dispatched

Written by the planner session (Aspen), 2026-10-26, about 18:15 PDT. Times are PDT. Plan:
`docs/design/2026-10-26-three-builds-plan.md` (`0aef91d`). Files: `2026-10-26-three-builds-files/`.

## Go

- **The owner, in this session, after the plan:** "Go ahead". Read as the local steps the plan listed
  next: G1 (install GDAL), G2 (build the trails archive, no upload) and G4 (measure names). Also sending
  the plan to Rowan. **Uploads were not taken as covered.**
- **The owner, via Rowan (Forager RECORD -1695):**
  - names format: "Aspen's compact format (Recommended)";
  - the 261024 route upload: "Go, when names are ready (Recommended)", with routes and names uploaded
    together;
  - 8d: write the dates into both the pmtiles metadata and a manifest object.
- **Rowan (RECORD -1698):** dropping the per-record bbox is accepted; "Go ahead with Willow's build stage".
  Rowan wants to be told exactly what goes up before any upload.
- **The owner, mid-session:** "Go ahead and fix the wifi" (below).

## G1: GDAL

`apt-get install gdal-bin python3-gdal` installed 3.6.2+dfsg-1+b2, using 120.5 MB of the NVMe
(162,388,570,112 → 162,268,049,408 bytes free). The MVT, GPKG and ESRIJSON drivers are present.

## Wi-Fi outage, 16:50:04-17:11:16

- NetworkManager logged `wlan0: activated -> failed (reason 'ssid-not-found')` at 16:50:04, then retried
  every ~30 s. The network "Virusdownloader" was missing from scans; other networks were visible.
- The default route fell to the Bluetooth tether (`bnep0`, "Brandon Lee's Tab S8+ Network").
- The planner paused the trails fetch (kill by PID) to keep it off mobile data, then reported to the
  owner. The owner said "Go ahead and fix the wifi".
- At 17:11:16, NetworkManager reconnected to "Virusdownloader" on its own (5220 MHz). Nothing was
  changed. Traffic was back on `wlan0`, and the FS service answered in 1.6 s.
- DNS failed briefly afterwards (`Temporary failure in name resolution`). The fetch's retries covered it.
- Cause: inferred, not known. A router restart or power loss would look like this.
- **Note for Sundays:** during an outage like this, the weekly build's downloads would run over the tether.

## G2: reference-trails.pmtiles (built, not uploaded)

### Fetch

**Fetch script:** `fetch.py`.
- **GDAL's own ESRIJSON paging** got `Recv failure: Connection reset by peer` from the FS server. `curl`
  worked.
- **Offset paging, 2000 a page:** timed out (120 s) at row 32,000.
- **Keyset paging, 1000 a page:** about a minute a page.
- **Final method:** list all object ids (`returnIdsOnly`), then fetch ranges of 1000, four at a time, at
  `geometryPrecision=6` (about 0.1 m; a z15 tile unit is about 0.2 m). Each page's ids must equal its
  range exactly.
- **Result:** FS 86,422 of 86,422 features in 87 pages. BLM layers 2-6: 1,925, 5,291, 3,044, 2,318 and
  5,038, which is 17,616. Every count matches `returnCountOnly`.
- **Not used:** the FS bulk download `S_USA.TrailNFS_Publish.gdb.zip` is dated 2025-05-11
  (`Last-Modified`), older than the live service.

### Field checks (read from the services, then from the archive)

- **FS:** `trail_no`, `trail_name` and `trail_type` are lower case, `esriFieldTypeString`.
  - In the GeoPackage, all 86,422 `trail_no` values are `text`. Leading zeros are kept: `"060"`, `"072"`,
    `"058"`, and also `"02S20C"`.
  - `trail_type`: TERRA 78,169, SNOW 8,177, WATER 76.
- **BLM:** the service is `transportation/BLM_Natl_GTLF_Public_Display/MapServer`. "Public Managed
  Trails" is the catalogue name. `ROUTE_PRMRY_NM` is present on all five layers.
- **Decoded from the archive:**
  - z15 6144/12597 has `trail_no: "060"` (a string), "CORK RIDGE - PINE", `trail_type: "TERRA"`.
  - z10 192/393 has 133 features, all string `trail_no`; all 125 rtree candidates are present.
  - z12 748/1640 holds BLM "LP519", with `ROUTE_PRMRY_NM`, `ADMIN_ST`, `FAMS_ID` and `gtlf_layer`.

### Archive (`build_archive.py`; 23 min 11 s)

- `ogr2ogr` MVT to MBTiles, z10-15, simplification 2 tile units below z15 and 0 at z15. Then
  `pmtiles convert`.
- **Size: 219,923,563 bytes.** sha256 `240423f61966e046513f0aa2495651f0104e17243a7a51fa70d3f73c4e5ad096`.
- **Header:** min zoom 10, **max zoom 15**, mvt, gzip; 447,047 tiles; bounds −164.77, 18.27 to −65.74, 68.46.
  `vector_layers`: `fs_trails` and `blm_trails`, both z10-15.
- **Per zoom:**

  | Zoom | Tiles | Bytes |
  |---|---|---|
  | z10 | 2,582 | 6.7 MB |
  | z11 | 6,552 | 10.0 MB |
  | z12 | 17,364 | 16.5 MB |
  | z13 | 45,799 | 28.8 MB |
  | z14 | 113,470 | 51.7 MB |
  | z15 | 261,280 | 105.5 MB |

- **Largest tile:** 32,774 bytes, far under GDAL's 500,000-byte `MAX_SIZE`, so nothing was thinned or
  dropped. The log has no warnings.
- **Metadata:**
  - `attribution` "USDA Forest Service (CC BY 4.0); Bureau of Land Management";
  - `forager_reference`, holding the sources and their dates;
  - FS dates: `metadata_pubdate` 2025-05-14, `metadata_date` 2024-07-24, `catalog_modified` 2022-08-25.
    The live service has no edit date.
  - BLM date: `catalog_modified` 2026-10-13.

### Coverage list (`reference-trails-coverage.json`)

- **Method:** FS features grouped by `admin_org[:4]` × `attributesubset`, against
  `EDW_ForestSystemBoundaries_01/MapServer/1` (112 administrative forests).
- **Counts:** 86,384 features matched, plus 38 with an empty or 2-digit `admin_org`, for 86,422 in all.
- **Status:** 102 attributed and 7 mostly Centerline (Beaverhead-Deerlodge, Nez Perce-Clearwater,
  Mendocino, Plumas, Malheur, Okanogan-Wenatchee, Cherokee). 2 are Centerline only (Umatilla 549, National
  Forests in Mississippi 87). 1 has none (Savannah River Site).

### Manifest (`reference-trails-manifest.json`)

It holds `run_id` `reference-trails-20261027T004706Z`, the file's size, sha256, zooms and layers, the
feature counts, the sources with their dates, and the coverage summary.

### Local and R2 state

- The archive is at `~/reference-trails-build/reference-trails.pmtiles`.
- The source pages and the GeoPackage moved to the card, `/mnt/archive/aspen-reference-trails-20261026/`
  (947 MB).
- The superseded pages and the MBTiles were deleted. NVMe free afterwards: 160,921,288,704 bytes.
- **R2, read 18:05 by `rclone lsf`, not through the Worker:** no `reference-trails.pmtiles`, and
  `overflow/` holds only `us/`. No reference tile URL has been requested.

## G4: names measured (prototype, Sunday's 261024 extracts)

- **Method:** `osmium tags-filter w/highway`, then `w/name w/ref`, on us and canada, then merge. Times:
  514 + 180, 163 + 17 and 127 s.
  - The named file has 198,897,393 nodes and 15,386,578 ways.
- **Square cut:** one square at a time with `complete_ways`, 56 s and 49 s.
- **OOM kills (no other process was affected):**
  - 16:49, cutting both squares straight from the full US extract;
  - 17:09, two squares at once from the named file, at 7.4 GB RSS.
- **Encoder:** `fnam_measure.py`, which assigns segments to cells by midpoint. Douglas-Peucker at 2 m.
  An encoder bug (a line whose first segment lies outside the square) was fixed before the figures were
  taken.

| Square | Named ways | Points in → out | Strings | File, with bbox | File, no bbox | Busiest 50 km area, no bbox |
|---|---|---|---|---|---|---|
| W75_N40 | 1,117,150 | 16.77 M → 7.08 M | 233,173 | 52,176,860 | 38,898,300 | 4,288,719 (SW -74.375, 40.5) |
| W120_N45 | 139,406 | 4.38 M → 2.42 M | 64,230 | 12,982,985 | 11,224,875 | 997,317 (SW -117.5, 47.375) |

- **Gzip** saves about 20%.
- **Inferred, whole set:** 0.40-0.47 of the `.rd5` bytes, so about 0.6-0.75 GB beside the 1.56 GB of
  squares.
- **Sent to Rowan.** The bbox is dropped from v1 (RECORD -1698).
- The 5.3 GB of intermediates were deleted afterwards.

## pi-31 dispatched

- The dispatch is `docs/handoffs/2026-10-26-pi-31-names-stage-dispatch.md` (`271365b`), with the full
  FNAM v1 spec.
- Willow's own session isn't listed, so a helper briefed as Willow Quadrat was started (the owner's
  rule, [coder-is-willow]). It works on Forager branch `pi-31-names-stage`, with no merge, install or
  upload.
- Its result comes in its own entry.

## Next

1. **G3, upload the trails archive.** It needs the owner's go. It would put up:
   - `r2:forager-maps/reference-trails.pmtiles` (219,923,563 bytes, sha256 above);
   - `r2:forager-maps/reference-trails-manifest.json`.

   Then a read-back by sha256, then one z10 and one z15 tile through the Worker, cache-busted. Rowan is
   told first.
2. pi-31's review, then the 261024 squares and names upload (owner's go via Rowan, -1695), described to
   Rowan before it happens.
3. G6, the elevation pilot. It needs its own go.
