# Review dispatch 2026-11-01-sorrel-pi37: the barrier mark as a fill (0007), and the heap

From Aspen to Sorrel Tally. Written 2026-11-01 at about 07:00 PST. The target is before Sun 11-08 02:08
PST, and sooner if the owner wants a rerun this week.

## Background

- The 10-31 early run ran out of heap. Willow's diagnosis is in
  `docs/design/2026-10-31-global-coverage.md`, the last section, and
  `prompts/preserved/2026-11-01-coder-09-planetiler-heap.md`.
- **The cause:** 0004's point mark stops z15 deduplication, about +1.2 GB of heap at US + Canada scale.

## Baseline

- **The branch:** Forager `pi-37-barrier-mark-fill` at `63a3649e5`, one commit on `pi-build`
  `de30a84ee` (installed).
- **Willow's evidence:**
  - Oregon entries: 418,172 (0001-0003), 613,976 (0001-0004), 613,979 (0001-0006), 418,177
    (0001-0007);
  - mvn 513 tests, 0 failures; BarriersTest has 9 forager cases;
  - the gate refuses a build with 8;
  - the GC logs are in `~/scratch/willow-heap`.
- **Also proposed:** `USCA_PLANETILER_XMX` 4g -> 5g (or 4.5g), as headroom.

## Questions

1. **The mechanism.** Does Planetiler 0.10.2 skip deduplication for a tile with any non-fill feature
   (`VectorTile.likelyToBeDuplicated`, `TileArchiveWriter`)? Does a full-tile fill keep the dedup?
2. **The patch.** Is 0007 correct and minimal? Is the mark still on every z15 tile, with no id and no
   fields? Is it the same coverage as 0004 intended?
3. **The meaning.** Does "barriers layer present = fences checked" still hold for every reader? Check
   PR #439 (MapFeatures.kt:84 keeps only LINESTRING) and its tests and wording, which describe a point.
   Do any style or Worker paths read the mark?
4. **The tests and gate.** Do the two new BarriersTest cases guard it? Run one revert check of your
   own.
5. **The heap.** Is 4g -> 5g (or 4.5g) safe on the 8 GB Pi, given about 21 GB of mmap and peak RSS of
   6.24 GB at 4g? Which do you recommend, and is zram worth it?
6. **The install** follows pi-36's steps and rollback.

## Bounds and verdict

- Read-only. No installs, nothing in `/opt` or `/srv` changes, and no R2.
- One Planetiler at a time, under `nice -n 10`.
- Write the review on a new branch `sorrel-pi37-barrier-mark-fill`, as
  `docs/reviews/2026-11-01-sorrel-pi37-barrier-mark-fill.md`.
- **The verdict:** blocking / should-fix / notes, ending with "Is pi-37-barrier-mark-fill mergeable
  for install, and which -Xmx?" Send it to Aspen.
