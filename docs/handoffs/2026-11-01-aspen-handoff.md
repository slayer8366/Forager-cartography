# Aspen handoff, 2026-11-01 (about 22:00 PST)

Written by the planner session forager-cartography-28 ("Aspen") at the owner's request: "Session limit
is about to hit, so wrap up and write a handoff for the next Aspen". The full record is
`docs/design/2026-10-30-fill-in-rulings.md` and `docs/design/2026-10-31-global-coverage.md` (read their
last sections first). Dispatches are in `prompts/preserved/`.

## Standing owner rules from today

- **"I'll leave the merging to you for the time being."** Aspen merges PRs after Sorrel's OK, with
  `gh pr merge N --merge --match-head-commit <reviewed sha>`.
  - Willow's session can't merge ("Merge Without Review"), touch `/opt`, delete, or start builds.
  - Aspen's session can (the owner allowed the build-start commands).
  - Credential searches are refused; don't try them.
- **Rowan** holds `pre-main` merges on the owner's word ("when she tells me it's safe I'll let you know").
  Only the owner lifts that. Rowan's coders don't merge.
- **The Worker** deploys by Cloudflare Workers Builds from **`main`**, folder `server/pmtiles-worker`,
  on **every push to `main`**.
  - Releases are `worker/*` PRs confined to that folder, equal to `pre-main`'s (`tools/check-release.sh`;
    the Worker README's "Deploying" section).
  - `main`'s folder now equals `pre-main` `13bcd0ebf`.
- **The release path:** `pre-main` -> `main` promotion builds the Play release automatically, and the
  owner uploads it.
  - Gate (Rowan, -08): Rowan's sort of `pre-main` into ready / needs polish / must hide, the UX auditor's
    report, CI, then the owner's approval.
  - **Bring the owner ONE release go**, only after the sort and the audit. The owner said "Yes please" to
    Aspen lining it up with Rowan.

## In flight right now

1. **The weekly rerun `usca-20261101T174337Z`:** unit `forager-build-usca-rerun-261030`, `--local
   261030`, 0001-0007, 4608m.
   - Planetiler finished with no out-of-memory error (651M tiles, heap 4.0G of 4.8G).
   - At 22:00 it's in stage `brouter`; expect it done around 23:00-00:00.
   - **The upload watcher** `/mnt/archive/aspen-upload-next/upload-after-build.sh` (pid 221905,
     detached) waits for that run.
     - On success with no warnings, it uploads routing (segments4, names1, then the manifest last), then
       `us.pmtiles`.
     - **Wi-Fi only: it waits while the default route is the tablet's Bluetooth link (bnep0).** At 22:00
       Wi-Fi had dropped again (default via bnep0), so the owner may need to reconnect the Pi's Wi-Fi
       ("Virusdownloader"). On 10-31 it rejoined by itself after a while.
     - Log: `/mnt/archive/aspen-upload-next/upload.log`. On any STOP, read the log; nothing is uploaded.
   - **Check in the morning:** the log ends with "DONE". Then tell the owner the orchards and z10 streets
     are live, and have them check the S22.
   - The weekly timer is enabled again (next run Sun 11-08 02:08 PST).
2. **PR #462 (the app switch to Street v4, -> `pre-main`):** every PR check is green, including the new
   map-style checker job. It's waiting on Sorrel's verdict (Sorrel was running revert checks).
   - **The owner pre-approved the merge:** "Go ahead with 462 merge when ready". Merge it after Sorrel's
     OK, matching the head (`2d939a19b`).
3. **PR #463 (the two guard workflows -> `main`):** Sorrel says mergeable (`sorrel-worker-guards-to-main`).
   Its APK job was pending at 22:00.
   - Merge it once that's green, matching head `51541c286`. It's a no-op Worker redeploy.
   - The next `worker/*` release is the first time the guards run, so glance at its check list.
4. **Hill shading rollout** (the owner: "Go for all four, in order").
   - Done: step 1, the Worker overflow fix, live; step 4, #448 with hillshade, now on `pre-main`.
   - **Step 2:** the relief build for US + Canada, z5-11 Terrarium PNG 256 px, from
     `/mnt/storage/elevation/hgt3`, into `/mnt/storage/relief/` (writable).
     - Aspen's trial script is `/mnt/archive/aspen-hillshade-trial/make-relief.py`; generalise it to all
       cells (Willow, coder-11).
     - Start it ONLY after the rerun's upload finishes. About 1-2.5 h; about 22 GB (inferred).
     - Then `pmtiles convert`; check that `pmtiles show` says tile type png (Sorrel's note).
   - **Step 3:** Aspen uploads `relief.pmtiles` to `r2:forager-maps/relief.pmtiles`, using
     content-type octet-stream, the same way as `us.pmtiles` (see `upload-after-build.sh`).
     - Then check `/relief.json` (maxzoom 11) and a z11 tile over Mount Hood.
     - Until then v4's hill shading draws nothing, and new v4 offline downloads would hit 404s for
       relief. Upload it before any release.
5. **Global coverage** (the owner: "Fast fill now, own build later").
   - Willow's coder-08 Part A scope is recorded.
   - The worldwide fallback needs gos: the `world.pmtiles` upload (139 GB, streamed from Protomaps by a
     cloud VM or GitHub job, not the Pi), the Worker fallback (`worker-world-fallback`, on old
     `pre-main`; needs rebasing as a fresh branch), and BRouter's world squares (needs a second routing
     manifest).
   - Part B (the South America pilot) is paused; its scratch was deleted.
   - The owner said they're non-commercial (SRTM in the BRouter squares is OK; a CGIAR credit is owed when
     world routing ships).
   - The global DEM is Copernicus GLO-90 (71 GB, commercial use allowed).
6. **Rowan's hill shading trial** (-1926) is done. Answered in -09.

## Owner's word still owed or pending

- Deleting the throwaway branches `hillshade-trial-s22`, `hillshade-trial-tiles`,
  `street-v4-revert-hillshade-night`, `app-switch-revert-check` and `worker-sprite-v6` (the old one) needs
  the owner's word.
- 0006's should-fix (a null guard in `Landuse.java`) is for a next pass; not done.

## People and channels

- **Willow** (coder): `session_019DQwoeyANjh9Kcz7mhdfbL`.
- **Sorrel** (reviewer): `session_019DQwod3PaWQYeR9FJLNn1m`.
- **Sage** (designer, design only): `session_019DQwodPVJkcqtk7AF9tQvJ`.
- **Rowan** (app planner): `session_019DQwod2KaJbvEBsgRtumiq`, and files in Forager `records-after-173`
  `prompts/aspen/`. The last is -09 (Aspen).
- Send messages with `mcp__claude-code-remote__send_message`.
