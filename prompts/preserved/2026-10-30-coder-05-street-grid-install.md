# Dispatch 2026-10-30-coder-05: streets from z10 in the weekly build, for Sunday 11-01

From the Pi planner (session forager-cartography-28, "Aspen") to Willow Quadrat. Written 2026-10-30 at
about 22:20 PDT. Report times in Pacific time.

## The go

- **Your pilots:** Oregon, and New York (largest z10 tile 228,641 B against the 500 KB limit; +0.94 %).
- **The owner, in Aspen's window:** "From Sunday's run (Recommended)". The option read: "Sorrel reviews
  the small build patch Saturday; if mergeable, Willow installs it before Sunday 02:20 PST. Safe for
  today's app: the current v3 style doesn't draw streets below zoom 12, so phones see no change until
  v4 ships. Uploading to R2 stays a separate go."
- **So the go covers:**
  - the patch on `pi-build`;
  - Sorrel's review;
  - if Sorrel says mergeable, the merge, the jar build and `install-map-build.sh` before Sunday's
    timer.
- **It doesn't cover** any R2 upload. If Sorrel finds a blocker, nothing is installed and Sunday runs
  as already set.

## The work

1. **The patch.** On `pi-build` (installed `288ce80cf`), branch `pi-35-street-grid`. Add the z10
   variant as **`0005-minor-roads-z10.patch`**, after 0004 in `BASEMAPS_PATCHES` in `pins.env`.
   - Don't call it 0003: that name is taken by the barriers patch.
   - Rebase the pilot's patch onto 0001-0004 and say whether it applied cleanly.
2. **Tests.** Your RoadsTest cases, plus the map-build suites as at pi-34, all green. Run one revert
   check: drop 0005 from `BASEMAPS_PATCHES` and show the street-zoom test fails.
3. **Before Sunday, show** that the installed run would have the jar with 0005 in it:
   - by the jar's sha256 and the build script's patch list;
   - and by one Oregon z10 tile holding `minor_road`, from the jar the install builds.
4. **Sorrel's review.** I'll dispatch it when you report the branch head. Install only after Sorrel's
   "mergeable".
5. **Install** like pi-34:
   - a `--no-ff` merge into `pi-build`;
   - the jar built and installed, recording its sha256;
   - `install-map-build.sh` from a clean worktree, recording `COMMIT` and `map-build.prev`;
   - the rollback steps written down.
   - **Finish by Sat 10-31 22:00 PST**, well clear of the 02:20 PST timer. If you can't, don't install.

## Order

1. PR #448's low-zoom roads and night rims (the owner is waiting on the S22 check).
2. This.
3. coder-03.
4. coder-04.

If this would push #448 past Saturday midday, tell me.

## Bounds

- If a `build-usca` process is running, stop.
- No R2.
- Leave the scratch archives in place until I say.
- Ask the owner if anything is ambiguous.

## Report

Send the report to Aspen: the branch head, tests, revert, the jar sha256, and after the install,
`COMMIT` and the rollback steps. Claims marked observed, read or inferred.
