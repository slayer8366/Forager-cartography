# Dispatch 2026-10-30-coder-02: street-grid pilot (minor roads at z10-11), measure only

From the Pi planner (session forager-cartography-28, "Aspen") to Willow Quadrat. Written 2026-10-30 at
about 11:40 PDT. Report times in Pacific time.

## The owner, verbatim

On the S22 with the v4 debug build, comparing it with the OSM layer around Portland at about z10:
"Better, but when zoomed out the detail is still sparse. Is this the rest of the fix?"

Asked whether to revisit the tile change: "I didn't skip it. I asked for the exact same design as
OSM". **So the planner's earlier "skip the tile change" reading is withdrawn.** The goal is OSM's
glance-level detail, and that includes the street grid.

## The gap (read by Aspen from the live archive `usca-20261027T221400Z`, inner Portland)

| Zoom | Tile bytes | Road kinds |
|---|---|---|
| z10 | 196,169 | highway 13, major_road 38 |
| z11 | 136,822 | highway 19, major_road 27, rail 6, path 3 |
| z12 | 122,724 | major_road 161, **minor_road 8** |

There are no minor roads below z12, so no style can draw the grid that OSM shows there. Also
(inferred): the OSM layer is 256 px raster on a high-density screen, so at a given zoom it shows
content from about one zoom deeper.

## The work: a pilot, measure only

1. **The patch.** In a scratch worktree of `pi-build`, add a basemap patch, after the existing
   `map-build/patches/protomaps-basemaps/`. It sets `minor_road` (residential, unclassified, living
   street, and service if you judge it right; say so) to appear from **z11**, with a second variant
   from **z10**.
   - Follow how pi-23 moved tracks to z11 and paths to z12.
   - Keep Protomaps' line simplification and feature merging at those zooms. If they need tuning,
     say what and why.
2. **Build two pilot jars** in scratch. Don't touch `/opt/forager-build/basemap/` or the installed
   map-build.
3. **Run Planetiler on one state extract** (Oregon, from Geofabrik or the card's last extract if one
   is there) three ways: baseline, z11 and z10. For each, record:
   - archive size;
   - bytes per zoom for z9-z13;
   - the largest tiles at z10 and z11, against the 500 KB limit;
   - build time and peak memory.
4. **Estimate the US+Canada cost** from Oregon. Mark it inferred:
   - added archive bytes;
   - added build time;
   - whether Sunday-style runs still fit the NVMe and the card (G8 numbers).
5. **Render** each variant with the v4 style (PR #448's `forager-street-v4.json`) at the same views as
   the S22 check:
   - inner Portland at z10 and z11;
   - Canby-Silverton at z9 and z10;
   - plus Oregon City at z11.

   Keep the renders off GitHub.
6. **Report, then stop.**
   - Nothing goes into the weekly build or the installed jar without the owner's go after they've
     seen the renders and the numbers.
   - If a style change is needed so the new roads draw well (a minor-road width at z10-11), name it.
     Sage designs it; you don't.

## Bounds

- **PR #448 stays as it is.** This is separate work. Don't push to `street-v4`.
- **Sunday's weekly build fires at about Sun 11-01 02:02 PST.**
  - Finish the pilot builds by Sat 10-31 20:00 PDT.
  - If a `build-usca` process is running, stop and say so.
  - Nothing in `/srv/forager-build`, `/opt/forager-build` or the card's build folders changes. Scratch
    goes under `/mnt/storage` or the NVMe, and you check free space first and report it.
- One Planetiler at a time, under `nice -n 10`. Keep the heap within what leaves the Pi at least 2 GB
  free, and report it.
- Run your servers on 127.0.0.1 ports of your own, and stop them by PID. Never use `pkill -f`.

If anything is ambiguous, you find a better way, or something doesn't work how we want it, for any
reason: stop and ask the owner. Don't assume; asking is encouraged.

## Report

Send the report to Aspen, and keep it as your final message:
- every claim marked observed, read or inferred;
- times in PT.
