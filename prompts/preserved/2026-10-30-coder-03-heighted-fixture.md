# Dispatch 2026-10-30-coder-03: a heighted rd5 test fixture for the app

From the Pi planner (session forager-cartography-28, "Aspen") to Willow Quadrat. Written 2026-10-30 at
about 15:45 PDT. Start it **after** PR #448's current round is reported. Report times in Pacific time.

## The ask and the go

- **The ask:** Rowan's `prompts/aspen/2026-10-30-03-rowan-to-aspen-heighted-fixture.md`, on Forager
  `records-after-173`.
- **The owner's words behind it:** "Yes, ask Aspen (Recommended)" (Forager RECORD -1838).
- **Aspen's reply** is `prompts/aspen/2026-10-30-06-aspen-to-rowan-heighted-fixture.md` on the same
  branch.
- **What the go covers:** a small file made from data that's already built. No rebuild, no R2
  upload, no change to the live run.

## The work

1. **Branch:** `fixture-rd5-heights` from Forager `origin/pre-main`. It touches only
   `server/pmtiles-worker/test/fixtures/rd5/`.
2. **Make a heighted `W75_N40.rd5`** covering the same place as today's fixture (Harriman / Bear
   Mountain; `routes.json`'s rectangle and margin). Choose the method and say why:
   - cut it from the live run's `W75_N40.rd5` (`usca-20261027T221400Z`, under
     `/srv/forager-build/out-usca/current/segments/`, read-only);
   - or rerun `make-fixture.sh` with PosUnifier pointed at the pinned store
     `/mnt/archive/forager-build/elevation/bef3-20261027`, read-only.

   Keep `routes.json`'s routes valid, and regenerate any expected output its tests need.
3. **Show the heights are there:**
   - every route in `routes.json` returns a height on its points with BRouter 1.7.10 and the stock
     `hiking-mountain.brf`;
   - give the min and max.
4. **README:**
   - the run id and sha256 of the source square (or the store's SHA256SUMS sha256), and the new file's
     size and sha256;
   - the courtesy line "Elevation: U.S. Geological Survey, 3D Elevation Program (3DEP), public
     domain.";
   - keep the OSM/ODbL notice.
5. **Tests:** the existing rd5 tests still pass on the new file in CI. Push the branch. A PR into
   `pre-main` is fine, with CI green. Don't merge without the owner's go.

## Bounds

- Read-only on `/srv/forager-build`, `/opt/forager-build`, the card store and R2.
- **Sunday's weekly build** fires at about Sun 11-01 02:02 PST. If a `build-usca` process is running,
  stop and say so.
- Run your servers on 127.0.0.1 ports of your own, and stop them by PID. Never use `pkill -f`.

If anything is ambiguous, stop and ask the owner.

## Report

Send the report to Aspen:
- the file size and sha256, the method used, the heights shown, and the CI run;
- claims marked observed, read or inferred.
