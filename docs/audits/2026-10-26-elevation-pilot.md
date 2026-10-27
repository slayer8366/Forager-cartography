# Elevation pilot (G6): two 5° route squares with 3″ elevation

Aspen, 2026-10-26, 20:04-21:05 PDT, on the owner's "Go on elevation" (three-builds plan `0aef91d`, build 3,
G6). Script and logs: `2026-10-26-elevation-pilot-files/`. All the work is on the card, in
`/mnt/archive/aspen-elevation-pilot-20261026` (4.3 GB, kept). The NVMe, the build tree and R2 were not touched.

Marks: **read** (a log, a file or a command), **computed**, **inferred**.

## Chain (read)

| Step | What | Result |
|---|---|---|
| 1 | 3DEP 1″ COGs, `prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1/TIFF/current/` | 50 of 50 present; 2,458,515,810 bytes in 14.5 min |
| 2 | `gdalwarp` to EPSG:4326 on the hgt grid (cell centres on whole degrees), Int16, nodata −32768, then `gdal_translate -of SRTMHGT` | 1″ bilinear, 3601²: 1.5 s per tile. 3″ average, 1201²: 0.4 s. 1″ total 1.30 GB, 3″ total 144 MB. N40W096 reads 250-409 m. |
| 3 | `ElevationRasterTileConverter all hgt3 bef3 3` | `srtm_12_03.bef` 26,562,953 B (W125_N45), `srtm_17_04.bef` 14,341,937 B (W100_N40); 9.9 s, peak 400 MB; its own decode check passed |
| 4 | Each square cut from the 261024 card extracts with 1° margins, filtered with `USCA_ROUTING_FILTER` | W125_N45 320 MB, W100_N40 132 MB. Extracts took 2.5-6 min each, peak 3.8 GB. |
| 5 | BRouter's three steps, as `build-usca.sh` runs them, once with `no-elevation` and once with `bef3` | table below |

## Results

| Square | `.rd5` without elevation | `.rd5` with elevation | Growth | PosUnifier time / peak, without → with |
|---|---|---|---|---|
| W125_N45 | 54,901,325 | 62,747,167 | +7.85 MB, **+14.3 %** | 20.3 → 26.1 s; 399 → 575 MB |
| W100_N40 | 18,965,774 | 20,860,444 | +1.89 MB, **+10.0 %** | 8.7 → 10.3 s; 200 → 263 MB |

- **The cut is a faithful copy of the weekly build (read).** Both no-elevation squares have exactly
  the byte size of the weekly build's 261024 squares in `out-usca/current/segments`. The growth
  above is therefore the elevation's cost alone.
- **Only PosUnifier changes (read).** The cutter (280 vs 282 s) and WayLinker (67 vs 68 s) times
  are within noise.
- **Routed heights (read):** BRouter 1.7.10 CLI, profile `trekking`, on both versions of each
  square. Without elevation, no track point has `<ele>`. With elevation:
  - Port Angeles to Hurricane Ridge: 880 of 880 points, 64-1,599 m (the visitor centre is at about
    1,598 m), filtered ascent 1,584 m.
  - Coast route, Grays Harbor: 934 of 934 points, 1.75-54.5 m, ascent 143 m. No gaps along the
    shore. The converter's "0 m = no data" didn't show on this route (a route over sea-level ground
    would be the sharper test).
  - Plains, Lincoln NE: 588 of 588 points, 353-419 m, ascent 63 m.
  - In all three, the route geometry and its length are unchanged. The app's profile still has
    `consider_elevation = false`.

## First numbers for the planner (the brief's §3)

- **The `.bef` store at 3″:** 26.6 MB for a mountain square, 14.3 MB for a plains square (read). Over
  the 187 squares, with many of them mostly sea or Arctic: **about 2.5-4 GB (inferred)**. That is inside
  the sizing note's 2-6 GB. It goes on the card.
- **Build time of the store:** 10 s per two squares to convert (read), so minutes for the whole set. The
  1″ hgt step is about 2 s per 1° tile (read), so about 2 h for 3,783 tiles (computed).
- **Download:** 2.46 GB in 14.5 min, about 10 GB/h (read). At that rate, the sizing note's 130 GB takes about
  13 h (computed), not the 2-3 days the plan assumed. MRDEM isn't measured.
- **Whether the weekly unit grows:** only PosUnifier is slower, by 1.6-5.8 s per square (read). Across
  187 squares that is **under about 15 min on a 14.8 h run (inferred, an upper bound)**.
- **Whether the published set grows:** +10-14 % per square, so about +0.2 GB on today's 1.56 GB of
  squares (inferred). That comes out of the NVMe's 6 GB headroom twice at the publish peak. The area
  downloads in the app grow by the same share.
- **Peak memory:** PosUnifier 575 MB at most, with a 4 GB heap (read). Not a concern.

## Not done

- The full download (G7) and the switch in the weekly build (G8) each need their own go.
- The 1″ `.hgt` (1.30 GB for 50 tiles, about 98 GB for 3,783; computed) needs the USB storage drive,
  which still isn't mounted.
- Canada (MRDEM) is untested. 3DEP's Canadian tiles have no stated provenance (the sizing note's
  unknown 2).
- No 1″ `.bef` was made.
