# Topo relief and contours: read-only sizing

Written by the planner session `forager-cartography-7b` on 2026-10-22, about 12:00 PDT.

The owner, relayed by Rowan: "Size it now". This follows topo ruling 8 in
`docs/design/2026-10-22-topo-rulings.md`. Nothing was downloaded, installed or built. Each claim
is marked read, computed or inferred.

## Short answer

- **Network:** about 140 GB is read once from USGS and NRCan.
- **Output:** about 45-100 GB of archives.
- **R2:** about $0.70-1.50 a month more.
- **Tools:** GDAL from apt, a 24 MB download and about 88 MB installed. Planetiler, already on
  the Pi, can cut the contour tiles, so no tippecanoe build is needed.
- **The blocker is disk, not tools or time.** The Pi has 129 GB free today. The weekly basemap
  build alone wants 157 GB free to start. Topo outputs can't live on this disk alongside the
  basemap; they would have to go to R2 and be deleted locally, or wait for the owner's new machine.

## Inputs (read unless marked)

Source: Forager `origin/records-after-173`, `docs/navigation/2026-10-21-elevation-sizing.md`.

- **USGS 3DEP 1″:** 3,783 one-degree COGs, 130 GB in all, on a public S3 bucket. Public domain;
  the courtesy credit is "U.S. Geological Survey".
  - Ruling 5 takes 3DEP for the US only.
  - The US share of the 3,783 tiles isn't stated. By area (CONUS plus Alaska, Hawaii, PR and the
    USVI), about 55-65 GB (inferred).
- **NRCan MRDEM:** 84 GB, a single Lambert COG, Open Government Licence – Canada, plus a Copernicus
  notice that must travel with derived data.
- **Total to read:** about 140-150 GB (inferred).
  - Both sources are COGs, so GDAL can read them in windows over HTTP (`/vsicurl/`, `/vsis3/`)
    without storing whole files (inferred, a standard GDAL capability). Disk staging can stay
    small, block by block.
  - The time is set by the link. At the elevation note's figure (about 2 days for 128 GB on Wi-Fi),
    this is about 2-2.5 days on Wi-Fi, or about a week on the tether (computed).
- **Shared download:** ruling 5 shares this download with the routing `.bef` work. One windowed
  pass could write both the `.hgt` for BRouter and the relief tiles (inferred). That needs a
  pipeline written for both.

## Outputs (inferred, from Sage-04's sample)

Sage-04's sample was 126 Terrarium tiles at z14, 67-125 KB each, mountains and city only.

| Archive | Tiles | Size | Notes |
|---|---|---|---|
| `relief.pmtiles`, raster-dem Terrarium, 256 px, z0-z12 | about 0.9 M | **40-90 GB** at 50-100 KB a tile | Plains compress better, so the low end is likelier but unmeasured. Lossless WebP instead of PNG is commonly 20-35% smaller; whether MapLibre Native 13.5.0 decodes WebP raster-dem on the S22 is not checked. |
| `contours.pmtiles`, vector, z13-z14, 40 ft with 200 ft index | | **3-10 GB** (Sage's estimate) | The intermediate contour lines before tiling are unknown, possibly tens of GB for the Rockies and coast ranges at 1″ and 40 ft. This is the first thing to measure. |

## R2 (computed)

- **Storage:** 45-100 GB at $0.015 per GB-month is about **$0.68-1.50 a month**.
- **Uploads:** a few thousand Class A requests at 16 MiB parts, far inside the free million.
- **Tile reads:** Class B, likely inside the free 10 million a month at the app's current use
  (inferred).

## Tools on the Pi

Read: `apt-cache` and `apt-get -s` on Debian 12 bookworm, aarch64.

| Tool | Status | Footprint |
|---|---|---|
| `gdal-bin` and `python3-gdal` 3.6.2 | not installed | 39 new packages, 23.6 MB download, about 88 MB installed |
| `python3-numpy` | already installed | |
| `python3-rasterio` | available in apt | not needed if GDAL's Python is used |
| `tippecanoe` | not in bookworm's apt | Building it from source would need a separate go. Planetiler, which already builds the basemap (Java, `protomaps-basemap-HEAD-with-deps.jar`), can tile contour lines from a GeoPackage, so tippecanoe is not needed (inferred; it needs a small profile written). |
| `pmtiles` CLI | already installed | packs MBTiles into PMTiles |

The Terrarium encoding is a short numpy script over GDAL's warped output (inferred). There is no
apt tool for it.

## Build time on the Pi (inferred, unmeasured)

The Pi has 4 cores and 7 GiB of RAM (read: `nproc`, `free`).

- **Relief:** warp and encode about 0.9 M tiles. CPU-wise, about 6-24 hours on 3 cores. In practice
  it is bound by the 2-2.5 day network read if done in one windowed pass.
- **Contours:** `gdal_contour` per degree block, then Planetiler. About 1-2 days, unmeasured.
- **Upload:** 45-100 GB at last night's 2.9 MiB/s average is about 4.5-10 hours of transfer. The
  link stalled once last night; the resumable part-upload method from pi-29 would cover that
  (`docs/audits/2026-10-21-pi-29-files/resume.py`).

## Disk: the constraint (read, then computed)

- **Free now:** 129.0 GB on the NVMe (`df`).
- **Taking space:** `kept-usca/usca-20261019T011311Z` (the rollback copy, 32 GB) and the live
  261021 output (about 34 GB).
- **The basemap build's own start check:** the 261021 run logged "164053291008 bytes free (164.1 GB),
  this run needs 157020310761 bytes (157.0 GB)" (`logs/usca-20261021T111429Z.log`).
- **So the next weekly basemap build will not have room** while the rollback copy is kept: 129 GB
  is under 157 GB.
  - Deleting the rollback copy would give about 161 GB, which just fits.
  - That deletion is the owner's call, after the in-app test (pi-29 record).
  - This is true with or without topo.
- **Topo:** 45-100 GB of topo outputs can't be kept on this disk next to the basemap build.
  Options, for the owner when building is approved:
  - (a) Build topo between basemap runs, upload it, and delete the local copy.
  - (b) Wait for the owner's new machine.
  - (c) Build to z11 only first: about a quarter of the z12 size (inferred).

## First measurements, when a build is approved

Following the elevation note's own advice:
1. Run one mountain degree and one plains degree through the whole chain: relief tile sizes,
   contour intermediate size, and time per block.
2. Check that MapLibre Native on the S22 draws the hillshade and the contour labels.
3. Ask USGS about the provenance of 3DEP's Canadian tiles. That only matters if 3DEP were used
   for Canada; ruling 5 uses MRDEM there.
