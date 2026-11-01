# Dispatch 2026-11-01-coder-11: hill shading in Street v4 for US + Canada

From the Pi planner (session forager-cartography-28, "Aspen") to Willow Quadrat. Written 2026-11-01 at
about 10:50 PST. Report times in Pacific time.

## The go

- **The owner, on the S22 trial:** "It's good. It actively defines the trail map from a street or topo
  map, which is ideal. Let's keep this".
- **Then:** "Go for all four, in order (Recommended)". The option read: "Build tiles (after tonight's map
  build + upload), Worker fix reviewed by Sorrel then deployed via pre-main→main, R2 upload, style +
  night + credits into #448. I report each step; I stop and ask if anything goes wrong."
- **The spec:** Sage's sage-11 **ALT** as on the trial (the last sections of
  `docs/design/2026-10-31-global-coverage.md`), and your Part 2 scope.

## A deploy constraint Aspen found (read)

- `pre-main` is 330 commits ahead of `main` (`177215135`), and the live Worker deploys from `main`. So
  "pre-main→main" can't mean promoting all of `pre-main`; that would be an app release nobody has
  ruled on.
- **The Worker change goes to `main` as Worker-only commits** (a PR of cherry-picks, as
  `worker-sprite-v6-pre-main` did for `pre-main`), and into `pre-main` too, so the trunk keeps it.
- **Leave out the sprite v6 Worker change** (#453): the owner ruled "pre-main only" for it.

## The work, in order

1. **The Worker** (branch off `pre-main`, with tests first and a revert check):
   - overflow and maxzoom advertising for the Street archive only;
   - every other archive advertises its own maxzoom and answers 204 above it.
   - **Sorrel reviews.** Then a PR to `pre-main`, and a Worker-only PR to `main`, which deploys.
   - Check it live afterwards: `/relief.json` 404 until the upload; `us.json` and a Street tile
     unchanged.
2. **The relief build,** only after tonight's run `usca-20261101T174337Z` and its R2 upload have
   finished (Aspen will say go).
   - On `/mnt/storage/relief/` (now writable), from `/mnt/storage/elevation/hgt3`.
   - z5-11 Terrarium PNG 256 px (Aspen's `make-relief.py`, generalised to all 3,631 cells), up to 4
     processes under `nice -n 10`. Record the time and size.
   - Make the MBTiles, then `pmtiles convert` to `relief.pmtiles`, with the attribution "Heights: USGS
     3DEP; NRCan MRDEM".
   - Skip WebP.
3. **The R2 upload of `relief.pmtiles`:** Aspen does it, after step 1 is live.
4. **On #448** (`street-v4`):
   - the dem source (inline tiles URL from the Worker, maxzoom 11) and the hillshade layer, through
     `forager-fill-in.mjs`;
   - `forager:night-hillshade` in v4's metadata, plus `STREET_V4_NIGHT_TABLES` and the night pass,
     replacing the trial's `HillshadeTrialNight.kt`;
   - Credits rows for USGS 3DEP and NRCan MRDEM (OGL-Canada wording, from the licence text);
   - hidden under Topographical (check with Sage if it's unclear).
   - A check-street-night block with a revert check; v3 byte-identical.
   - Sorrel reviews it with the rest of #448. #448's merge stays the owner's call, as before.

## Bounds

- Nothing heavy on the Pi until Aspen says tonight's run and upload are done.
- No `pre-main` → `main` promotion. Don't touch `us.pmtiles`, routing or the sprites on R2.
- Delete `hillshade-trial-s22` and `hillshade-trial-tiles` only on the owner's word, after #448 has the
  real thing.
- If anything is refused or goes wrong, stop and report it.

## Report

Send a report to Aspen after each step. Mark claims observed, read or inferred.
