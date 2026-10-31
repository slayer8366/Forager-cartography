# Dispatch 2026-10-31-coder-06: orchards, plant nurseries and vineyards in the tiles, for Sunday 11-01

From the Pi planner (session forager-cartography-28, "Aspen") to Willow Quadrat. Written 2026-10-31 at
about 09:05 PDT. Report times in Pacific time.

## The go

- **The owner, in Aspen's window:** "Orchards, Plant nurseries, Vineyards", and "Rush for Sunday". That
  option read: "Willow patches and installs today before 02:20 PST. Less review time on a build that's
  already been checked."
- **The background** is in `slayer8366/Forager-cartography` main,
  `docs/design/2026-10-30-fill-in-rulings.md`, last section.
- **So the go covers:**
  - a build patch on `pi-build`;
  - Sorrel's review;
  - if Sorrel says mergeable, the merge, the jar build and `install-map-build.sh`.
- **It doesn't cover:** any R2 upload, or any style change. The v4 layer waits on Sage's design and the
  owner's ruling.

## What the tiles hold today (read by Aspen from `Landuse.java` at pi-35)

- `landuse=orchard` and `farmyard` are written as kind `farmland`.
- `landuse=plant_nursery` and `vineyard` match no rule, so nothing is written.

## The work

1. **The patch.** On `pi-build` (installed `a5bcb0780`), branch `pi-36-orchard-kinds`. Add
   **`0006-orchard-nursery-vineyard.patch`**, after 0005 in `BASEMAPS_PATCHES`.
   - Write orchard, plant nursery and vineyard into `landuse` so the style can tell each one apart.
   - **Aspen's lean (yours to judge):** keep kind `farmland` and add `kind_detail` = `orchard` /
     `plant_nursery` / `vineyard`.
     - v3 phones then keep drawing orchards as farmland, as they do today.
     - Nurseries and vineyards would newly take v3's pale farmland fill.
     - New kinds are the other way, but then v3 would lose orchards' farmland fill.
   - Whichever you choose, **say exactly how v3 and the v4 at #448's head would draw each of the three
     differently**, so I can tell the owner before the R2 go.
   - Leave `farmyard` as it is.
   - Say whether `kind_detail` stops these polygons merging with neighbouring farmland at low zooms, and
     whether that costs anything.
2. **Tests.** A LanduseTest case for each of the three, plus the map-build suites as at pi-35, all
   green. Run one revert check: drop 0006 and show the new tests fail.
3. **Before the install, show:**
   - the jar's sha256 and the patch list;
   - one Oregon tile holding each of the three. Orchards near S Haines Rd / S Bremer Rd, about
     45.278 N 122.650 W, z13-14.
   - Give the bytes for that tile with and without 0006, and the largest Oregon z10 tile against
     500 KB.
4. **Sorrel's review.** I'll dispatch it when you report the branch head. Install only after Sorrel's
   "mergeable".
5. **Install** like pi-35:
   - a `--no-ff` merge into `pi-build`;
   - the jar built and installed, with its sha256 recorded;
   - `install-map-build.sh` from a clean worktree, recording `COMMIT` and `map-build.prev`;
   - the rollback steps written down.
   - **Finish by Sat 10-31 22:00 PDT.** The timer is Sun 11-01 02:20 PST. If you can't, don't install,
     and Sunday runs as already installed.

## Order

This comes first, ahead of coder-03 and coder-04. #448 waits on the owner's S22 check, so nothing is
due there. Report the branch head by about 15:00 PDT so Sorrel has time.

## Bounds

- If a `build-usca` process is running, stop.
- No R2. Don't push to `street-v4`.
- The 10 throwaway branches stay until the owner's word.
- One Planetiler at a time, under `nice -n 10`, leaving 2 GB free.
- Ask the owner if anything is ambiguous.

## Report

Send the report to Aspen:
- the branch head, tests and revert check;
- the v3/v4 differences;
- the tile proof;
- the jar sha256;
- after the install, `COMMIT` and the rollback steps.

Mark every claim observed, read or inferred.
