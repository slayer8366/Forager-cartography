# Dispatch 2026-10-30-coder-04: height notices beside the route files, written by the build

From the Pi planner (session forager-cartography-28, "Aspen") to Willow Quadrat. Written 2026-10-30 at
about 16:15 PDT. Queued: start after coder-03, the heighted fixture. Report times in Pacific time.

## Why

- **Juniper's report:** Forager `juniper-nrcan-credit` at `355933b4d`,
  `docs/research/2026-10-30-nrcan-attribution.md`.
  - Canadian heights come from NRCan MRDEM-30. Outside lidar coverage, MRDEM is built from Copernicus
    WorldDEM-30.
  - Its licence asks anyone passing the data on to carry the OGL-Canada sentence, and the Copernicus
    copyright notice and liability sentence. That this reaches us through NRCan is Juniper's
    inference, not legal advice.
- **Rowan's note:** `prompts/aspen/2026-10-30-08-rowan-to-aspen-copernicus-notice.md` on
  `records-after-173`.
- **The owner, in Aspen's window:** "Build writes them, from next run (Recommended)".

## The work

1. **On `pi-build`,** in a scratch worktree, branch `pi-height-notices`. Change `map-build` so each
   run's published routing set carries:
   - a `NOTICE` file beside `manifest.json`, with Juniper's exact wording: the OGL-Canada sentence,
     the Copernicus notice and liability sentence, and the courtesy line "Elevation: U.S. Geological
     Survey, 3D Elevation Program (3DEP), public domain.";
   - an additive field in `routing/manifest.json`, for example `"notices": [...]` or `"licence"`, with
     the same text or a pointer to `NOTICE`. Say which, and why.
   - The text lives in one place in the repo, so the build and the tests read the same file.
2. **Make sure the upload step sends `NOTICE`** with the set, in the order that keeps the manifest
   last.
   - **No upload now.** The upload is the owner's go for each run, as before.
3. **Tests:** extend the existing map-build suites.
   - `NOTICE` is written.
   - The manifest field is present.
   - Existing manifest readers still parse it. The app ignores unknown fields; confirm that from the
     app's manifest parser.
   - Run one revert check.
4. **Review and install:** a PR or merge into `pi-build` gets Sorrel's review. Installing it
   (`install-map-build.sh`) needs the owner's go.
   - **Not before Sunday 11-01's run.** That run is already set, so don't install while it's
     scheduled or running.

## Bounds

- No change to `/opt/forager-build`, `/srv/forager-build` or R2 without the owner's go.
- If a `build-usca` process is running, stop and say so.

If anything is ambiguous, or Juniper's wording is unclear, stop and ask the owner.

## Report

Send the report to Aspen:
- the commits, the tests and the revert check;
- claims marked observed, read or inferred.
