# Review dispatch 2026-10-31-sorrel-pi36: orchard, nursery and vineyard kind_detail (patch 0006)

From Aspen to Sorrel Tally. Written 2026-10-31 at about 09:35 PDT.

**The timing:** the target is Sunday 11-01's run. Willow installs only after your "mergeable", and only
by Sat 22:00 PDT. The owner: "I'm not in a rush, but it's such a small change that if anything goes
wrong, we can trace it easily still". So don't cut anything to make it. If it isn't mergeable in time,
it goes in the next run.

## The go and the background

- **Willow's dispatch:** `prompts/preserved/2026-10-31-coder-06-orchard-kinds.md`.
- **The rulings:** `docs/design/2026-10-30-fill-in-rulings.md`, last section (both in this repo).

## Baseline

- **The branch:** Forager `pi-36-orchard-kinds` at `4decb59ea`, one commit on `pi-build` `a5bcb0780`
  (installed).
- **The approach:** kind stays `farmland`, and `kind_detail` is `orchard` / `plant_nursery` /
  `vineyard`, set only where the final kind is still farmland.
- **Willow's evidence:**
  - mvn 512 tests, 0 failures (LanduseTest 30, 6 new); map-build suites green;
  - revert: the new tests fail 3 of 3 and the jar gate refuses;
  - Oregon tile 13/1305/2937 gains only `kind_detail`, with the archive +0.14 %;
  - largest z10 tile 229,832 B;
  - scratch jar `8ab7a1be…5041b`.
- **Willow's claim:** v1-v3 and light draw no landuse farmland, so no change on today's phones.
  - v4 at `c2e06dff6` newly draws nurseries and vineyards in the farmland fill and rim.

## Questions

1. **The patch.** Is it correct and minimal? Does `kind_detail` appear only on farmland, and never on a
   feature whose kind was overridden (park, national_park, forest)? Are farmyard and plain farmland
   untouched?
2. **The tests and the gate.** Do the 6 cases and the jar gate's count really guard the change? Run one
   revert check of your own.
3. **Today's phones.** Confirm, from the styles on `street-v4` and the app's bundled styles, that
   v1-v3 and light draw nothing different.
4. **v4.** Is the v4 effect exactly what Willow states?
5. **Merging.** Willow says merging happens only at z ≤ 6 (z6 +25 B in Oregon). Is that right, and
   harmless?
6. **The install.** Is the steps-and-rollback plan the same as pi-35's?

## Bounds and verdict

- Read-only. No installs, no R2, and nothing in `/opt` or `/srv` changes.
- One Planetiler at a time, under `nice -n 10`. If a `build-usca` process is running, wait.
- Write the review on a new branch `sorrel-pi36-orchard-kinds`, as
  `docs/reviews/2026-10-31-sorrel-pi36-orchard-kinds.md`.
- **The verdict:** blocking / should-fix / notes, ending with "Is pi-36-orchard-kinds mergeable for
  install before Sunday's run?" Send it to Aspen.
