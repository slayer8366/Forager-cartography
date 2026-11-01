# Dispatch 2026-11-01-coder-09: the weekly run's Planetiler heap

From the Pi planner (session forager-cartography-28, "Aspen") to Willow Quadrat. Written 2026-11-01 at
about 04:10 PST. Report times in Pacific time. **This comes ahead of coder-08 Part B.**

## What happened (read by Aspen)

- **The early run `usca-20261031T193102Z`** (owner's go; inputs 261030; installed `de30a84ee`,
  0001-0006) failed at 23:29 PDT.
  - `OutOfMemoryError: Java heap space` in `WriteablePmtiles$DeduplicatingTileWriter.write`, at 48 %
    of features (747M) and 213M tiles. The heap was 4.2G/4.2G with GC at 98 %.
  - `USCA_PLANETILER_XMX=4g`. Peak RSS was 6.24 GB on the 8 GB Pi.
  - **The log:** `/srv/forager-build/logs/usca-20261031T193102Z.log`. The partial output is in
    `failed-usca/latest`.
- **Last week (`usca-20261027T221400Z`, 0001-0004)** ended with a heap of 3.9G/4.2G post-GC, 651M tiles
  and 1.5B features, so it was already close.
- Nothing was published or uploaded. The next timer run is Sun 11-08 02:08 PST, and it will fail too
  unless this is fixed.

## The work

1. **Diagnose.**
   - What holds the heap during the archive write: the dedup writer's entry list, the feature groups,
     or something else? Read Planetiler 0.10.2's `WriteablePmtiles`.
   - How much did 0005 and 0006 add? Measure on Oregon (or a larger state, if it fits): peak heap and
     post-GC heap with 0001-0004, 0001-0005 and 0001-0006, using GC logging or a heap figure from
     Planetiler's own progress lines. Scale to US + Canada (inferred).
2. **Propose fixes,** with their numbers. For example:
   - a larger `-Xmx` (5g? the trade-off against the page cache for about 21 GB of mmap, and the Pi's
     8 GB);
   - Planetiler options that reduce heap during the write;
   - zram or swap as a safety net;
   - anything else you find.
   Say which you recommend and why, and what it costs in build time.
3. **Then stop.** No change to `/opt`, `pins.env` or the installed map-build. Each of those is the
   owner's go after Sorrel's review. Use a branch off `pi-build` (`de30a84ee`) for any patch, with tests
   where the suite can hold them.

## Bounds

- One Planetiler at a time, under `nice -n 10`. Check free space first: the NVMe has 130 GB free now,
  and `/mnt/storage` 158 GB.
- No R2, and no Worker changes.
- Don't delete `failed-usca/latest` or the logs.
- Ask the owner if anything is ambiguous.

## Report

Send it to Aspen: the diagnosis, the measurements (marked observed or inferred), the options with
costs, and your recommendation.
