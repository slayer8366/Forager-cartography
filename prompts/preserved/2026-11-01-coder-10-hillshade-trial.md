# Dispatch 2026-11-01-coder-10: hill shading trial APK, then the rollout plan

From the Pi planner (session forager-cartography-28, "Aspen") to Willow Quadrat. Written 2026-11-01 at
about 09:30 PST. **This comes ahead of the rerun**, on the owner's word.

## The go

- **Via Rowan (RECORD -1926):** "Let's see about doing hill shading in the trail maps first…" and "Yes,
  start the trial (Recommended)". The option read: Aspen builds tiles for one steep area from the
  existing grid, Sage sets the look, and a throwaway S22 build shows it.
- **In Aspen's window:** "Do the hill shading first. That is due even sooner". Then "Quick trial, and
  prepare for full rollout if I like it."

## What exists (Aspen, observed)

- **Tiles:** Terrarium raster-dem, 256 px PNG, z5-z11, for Mount Hood and the Columbia Gorge (45-46 N,
  123-121 W), from the 3″ grid. 156 tiles, 16.0 MB. The highest reads 3,392 m (Hood is 3,429 m).
- **The URL** (public, 200 image/png):
  `https://raw.githubusercontent.com/slayer8366/Forager/hillshade-trial-tiles/png256/{z}/{x}/{y}.png`
  (throwaway branch `hillshade-trial-tiles`, never merge).
- **The script and local copies:** `/mnt/archive/aspen-hillshade-trial/`. A 512 px lossless WebP set is
  still encoding there, for the decode question; it isn't needed for the APK.
- **Sage** is setting the `hillshade` layer's look (sage-11). I'll forward it.

## Part 1: the throwaway S22 APK (now)

1. On a throwaway branch from `street-v4-s22-debug` (debug build, NEVER MERGE):
   - add a `raster-dem` source to v4 with those tiles: `encoding: terrarium`, `tileSize: 256`,
     `minzoom: 5`, `maxzoom: 11`, bounds [-123, 45, -121, 46];
   - add a `hillshade` layer. Use MapLibre's defaults until Sage's spec arrives, then apply it exactly.
     Put it where Sage says; until then, above the landcover and landuse fills and below water.
2. Confirm that MapLibre Native in the app supports `raster-dem` and `hillshade` at its pinned version.
   Note the night handling: whether the app's night tables touch the layer.
3. Build the APK in CI and send me the artifact link. That's all the phone needs. No Worker, R2 or
   production change.

## Part 2: the rollout plan, if the owner likes it (scope only)

- **Size and time for US + Canada to z11** from the 3″ grid, scaled from the trial: 156 tiles, 16.0 MB,
  and the build time I'll send. PNG against WebP: does lossless WebP raster-dem decode on the phone
  (test it in this APK on the WebP set if it's ready)?
- **Hosting:** a `relief.pmtiles` on R2 plus a Worker route (for example `/relief/{z}/{x}/{y}`), on a
  branch with tests. The cache and the credit line (heights: USGS 3DEP; NRCan MRDEM).
- **The app:** v4's style change, offline region downloads (do relief tiles join them? the size per
  region), the Heights credits, and the night handling.
- **Order:** the build (on the USB drive, not during the weekly run), the R2 upload, the Worker deploy,
  then the style merge. Each is its own go.

## Bounds

- No R2, no Worker deploy, nothing merged.
- The basemap rerun stays on hold until I say go. The install still waits on the owner.
- Ask the owner if anything is ambiguous.

## Report

Part 1's APK link first, then Part 2, to Aspen.
