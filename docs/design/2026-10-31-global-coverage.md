# Global coverage: maps, trails, elevation and routing worldwide

Aspen's record, started 2026-10-31.

## The ask

The owner: "I want global maps with trails and elevation. We have People in Brazil and Qatar
downloading the app so we should be sure it's available to them also".

## Where we are (read by Aspen, 10-31)

- **On R2:**
  - `us.pmtiles` (US + Canada; the 10-21 upload until tonight's run is uploaded);
  - `world-south.pmtiles` (Protomaps planet south of 16°N, z0-8 only, from 10-22);
  - `reference-trails.pmtiles` (USFS/BLM, US only);
  - routing squares for US + Canada only (187).
- **Qatar** (about 25°N, 51°E) is outside both archives: land and water fill only, so a blank map with
  no roads, trails or routing.
- **Brazil** has only the z0-8 world fill: no streets, trails or routing.
- **Pi sizing:** tonight's US + Canada run needs 157.1 of 162.7 GB on the NVMe (7.59 x input +10 %),
  peaks at 5.9 of 8 GB RAM, and takes about 15 h. The laptop is a 10th-gen i7 with 12 GB. Neither is
  comfortable for the planet (inferred: about 1 TB minimum and 2 TB comfortable, plus 32-64 GB RAM).

## The owner's ruling

"Fast fill now, own build later (Recommended)". The option read: "Willow scopes the Protomaps planet +
BRouter world squares as a worldwide fallback (gos for upload/deploy come back to you), and pilots our
own global build to price cloud vs laptop."

- **Phase 1:** a worldwide fallback from ready-made data. Protomaps' daily planet for the tiles, and
  BRouter's world segments4 for routing (elevation is inside the rd5). The Worker serves them wherever
  US + Canada has no data.
- **Phase 2:** Forager's own weekly global build (the patches, heights, names), on a cloud machine or an
  upgraded laptop, priced by a measured pilot. It replaces the fallback.

Dispatched: `prompts/preserved/2026-10-31-coder-08-global-scope.md`.

## Willow's Part A (16:45 PDT)

- **Tiles:** `build.protomaps.com/20261031.pmtiles` is 139.2 GB, z0-15, basemap 4.15.2 (our pin's
  version).
  - **It lacks our patches**, so outside US + Canada:
    - every path draws as "unknown difficulty";
    - tracks start at z12 and paths at z13;
    - streets start at z12;
    - there are no orchards or nurseries, no barriers, and no bare-rock fix.
  - **Upload:** whole, as `world.pmtiles` (about $2.1/month). Streamed with `rclone copyurl` from a cloud
    VM or a GitHub Actions job, not through the Pi.
- **Routing:** brouter.de's segments4 is 1,142 squares, 10.04 GB, weekly. The header version matches
  ours (2/11, 0).
  - The app needs no change. The Worker needs a second manifest (`routing/world-manifest.json`, option
    a).
  - **Flag:** the elevation inside is CGIAR SRTM v4.1. Willow thinks (from memory) that commercial use
    needs CGIAR's agreement. The owner should check before relying on it.
- **Worker:** branch `worker-world-fallback` at `bcaf931a6` (on `pre-main` `b38c1d161`). It falls back
  us -> world -> world-south. Tests-first runs fail and pass as expected. Not deployed.
- **App:** the blockers are the map data, not the code. Grey from z9 up in São Paulo and Doha; offline
  downloads succeed but hold empty tiles. With `world.pmtiles` up and the Worker deployed, the same
  URLs work. Small items: imperial by default, the offline picker centred on the US, the US species
  index, and English month names.
- **The renders** wait until the build finishes.

## The Pi's network (Aspen, 16:30 PDT)

- **Wi-Fi failed at 15:10** (NetworkManager: wlan0 config -> failed, reason "no-secrets"). The default
  route is now the Bluetooth tether to the owner's Tab S8+ (bnep0, about 0.2 MB/s).
- The build is past its downloads, so it's unaffected.
- **The upload watcher now waits for Wi-Fi** (default route via wlan0) before the routing upload and
  again before the tiles, so nothing goes through the tablet's data. It was restarted at 16:30 with the
  guard.
- **The owner, on the SRTM flag:** "We aren't using it commercially." So brouter.de's world squares
  can be used, with the SRTM heights in them, on non-commercial terms.
  - Still owed when world routing ships: a credit for the heights' source (CGIAR-CSI SRTM v4.1) in the
    app's Heights credits, beside the 3DEP and NRCan rows, worded from CGIAR's own terms.
  - If Forager ever becomes commercial, this needs looking at again.
- **Wi-Fi diagnosis (Aspen, about 16:55):** wlan0 scans see only channel 11 (Deschutes, b0490 and a
  hidden one), and the home network isn't heard. rfkill is clear and the region is US.
  - Toggling the radio and reloading `brcmfmac` didn't help.
  - Inferred: Wi-Fi/Bluetooth coexistence on the shared chip while the tether carries traffic.
  - **The owner:** "restart after the build finishes".
- **Timer, so a reboot can't start a second run:** `forager-build.timer` is now **disabled** (not just
  stopped). The earlier resume one-shot is cancelled. `forager-build-timer-resume2` at Sun 11-01
  11:00 UTC touches the stamp and runs `systemctl enable --now forager-build.timer`.
  - That one-shot is transient, so it's lost on a reboot.
- **After the reboot** (by Aspen, or by the owner if Aspen's session isn't back):
  1. `sudo touch /var/lib/systemd/timers/stamp-forager-build.timer && sudo systemctl enable --now forager-build.timer`.
     The next run is then Sun 11-08.
  2. `cd /mnt/archive/aspen-upload-next && setsid nohup ./upload-after-build.sh >> nohup.out 2>&1 < /dev/null &`.
     It checks the run finished OK, waits for Wi-Fi, then uploads.
- **Wi-Fi back (about 21:30 PDT):** wlan0 has 10.0.0.115 on Virusdownloader, and the default route is
  via wlan0 (metric 600, ahead of bnep0's 750). **The owner:** "skip the restart then".
  - The watcher uploads over Wi-Fi after the build.
  - `forager-build-timer-resume2` still re-enables the weekly timer at Sun 11-01 03:00 PST, so the
    after-reboot steps above aren't needed.

## The early run failed: Planetiler out of heap (Sun 11-01, read at 04:00 PST)

- **`usca-20261031T193102Z` failed at stage `planetiler`** at 23:29 PDT, 10-31, after 8.4 h.
  - `java.lang.OutOfMemoryError: Java heap space` in `WriteablePmtiles$DeduplicatingTileWriter.write`,
    during the archive write.
  - At the time: features 747M (48 %), tiles 213M, heap 4.2G/4.2G, GC 98 %; peak RSS 6.24 GB.
  - The heap is `USCA_PLANETILER_XMX=4g` (`pins.env:178`).
- **Last week's run (10-27) was already at the edge:** heap 3.9G/4.2G post-GC near its end, with 651M
  tiles and 1.5B features in the end. This week's tiles carry 0005 (streets from z10) and 0006 (orchard
  kinds) and filled the heap earlier.
  - Inferred: 0005's extra z10-11 roads are the main growth. Willow's Oregon pilot measured the archive,
    not the heap at US scale.
- **Nothing was published or uploaded:**
  - The build left the previous outputs untouched; this run's partial output is kept in
    `/srv/forager-build/failed-usca/latest`.
  - The watcher stopped at 23:31 ("STOP: the run failed …") before any upload.
  - R2 still has the 10-21 `us.pmtiles` and routing `usca-20261027T221400Z`.
- **The timer:** `forager-build-timer-resume2` fired at 03:00:06 PST. `forager-build.timer` is enabled
  again, and its next run is Sun 11-08 02:08 PST. **That run will fail the same way unless the heap is
  fixed.**
- **Wi-Fi** is up (the default route is via wlan0).
- **Dispatched:** Willow, coder-09 (diagnose and fix the heap, with Sorrel's review). A rerun is the
  owner's go.
- **Willow, coder-09 (06:45 PST): the cause is 0004, not 0005 or 0006.** This corrects Aspen's
  inference above.
  - 0004's per-tile corner mark is a **point**. Planetiler only deduplicates tiles made purely of fills
    and edges, so no z15 tile dedupes, and every all-water, all-forest or all-farmland tile gets its
    own entry in the heap-resident entry list (about 44 B each).
  - Last week's run started before 0003 and 0004 were installed (10-28), so 10-31 was the first US +
    Canada build with the mark.
  - **Oregon measurements:**
    - 0001-0003: 418,172 entries;
    - 0001-0004: 613,976 (+46.8 %);
    - 0005: +0;
    - 0006: +3.
  - Scaled to US + Canada: about +27.6M entries, about +1.2 GB of heap.
- **The fix:** Forager `pi-37-barrier-mark-fill` at `63a3649e5`, patch **0007**.
  - The mark becomes one fill polygon covering the tile, still on every z15 tile, so "fences checked"
    still holds.
  - Oregon is back to 418,177 entries, and the archive is about 5 % smaller.
  - mvn 513 tests, 0 failures. The gate needs 9 BarriersTest cases; the revert check gives 8 and is
    refused.
  - The app's reader (#439, unmerged) keeps only lines, so the mark is ignored either way.
- **Willow also recommends** raising `USCA_PLANETILER_XMX` from 4g to 5g (or 4.5g) for headroom: last
  week was already at 4.0 of 4.2G post-GC.
  - Zram is optional; swap wouldn't have helped.
- Sorrel is dispatched for review. The install, the -Xmx change and a rerun are each the owner's go.
- **Sorrel (about 05:30 PST):** `pi-37-barrier-mark-fill` at `63a3649e5` is mergeable for install, with
  no blockers. The review is Forager `sorrel-pi37-barrier-mark-fill` at `a497077be`.
  - Sorrel confirmed the mechanism from the 0.10.2 sources. The clean build passes 513 tests, and the
    revert check fails exactly the two shape assertions.
  - **Should-fix 1:** the -Xmx change rides on the same branch, as its own commit, with the comment at
    `pins.env:174-177` rewritten.
  - **Should-fix 2 (for #439):** the fixture and text describe the mark as a point.
  - **Heap:** 4.5g recommended. With the sessions open, 4 / 4.5 / 5g leave about 1.2 / 0.7 / 0.2 GB of
    page cache. 5g only if the Pi runs the build alone.
- **The owner:** "0007 + 4.5 GB (Recommended)" and "Rerun as soon as installed (Recommended)".
  - Asked why it failed and whether it could be salvaged, Aspen read `failed-usca/latest`: one 24.0 GB
    `forager-usca.pmtiles` written to 48 % with no directory, so it's unreadable ("never publishable").
    Planetiler's 108 GB of intermediate features was removed on exit.
  - What can be salvaged is the downloaded 261030 extracts on the card, so the rerun uses
    `--local 261030` and skips the download.
  - Then: "Yes, delete both and rerun (Recommended)". That means deleting the partial pmtiles (23 GB)
    and Willow's pilot and test scratch (about 19 GB) to get the NVMe back to the 157.1 GB the build
    needs (113 GB free at 07:10 PST). Willow pauses the South America pilot.
- **Willow's renders** (São Paulo and Doha with v4 over the planet) are done, at
  `~/scratch/willow-global/shots/`. They show nothing broken, with the expected gaps.
  - **The global DEM:** Copernicus GLO-90, 71.1 GB, a free licence that allows commercial use.

## Hill shading trial first (Sun 11-01)

- **The owner:** "Do the hill shading first. That is due even sooner". Then "Quick trial, and prepare
  for full rollout if I like it". The go is Rowan's RECORD -1926.
- **Aspen built the tiles (09:07):** Terrarium raster-dem, 256 px PNG, z5-z11, for Mount Hood and the
  Columbia Gorge (45-46 N, 123-121 W), from the 3″ grid.
  - 156 tiles, 16.0 MB; `png256.pmtiles` is 15.9 MB. The highest reads 3,392 m (Hood is 3,429 m).
  - Built in `/mnt/archive/aspen-hillshade-trial/`. The 512 px lossless WebP set is slow to encode and
    still running.
- **Hosted** on Forager throwaway branch `hillshade-trial-tiles` (raw URL returns 200 image/png).
- **Sage (sage-11):** the hillshade look. **Willow (coder-10):** the throwaway APK, then the rollout
  scope.
- The rerun is on hold until the trial. The install is still waiting on the owner (Willow's session was
  refused at `/opt`). `pi-build` is at `53a728341` (0007, plus `USCA_PLANETILER_XMX=4608m`: Java
  refuses "4.5g").
- **Sage, sage-11:** the hillshade layer goes directly before `water_stream`.
  - Illumination 335 with anchor "map"; day shadow `#4a3f33`, highlight white, accent
    `rgba(74,63,51,0.5)`.
  - **ALT** (recommended for the trial): exaggeration 9→0.28, 11→0.32, 13→0.24, 15→0.16, 17→0.10.
    Night shadow 0.7, highlight `rgba(220,228,236,0.20)`, accent 0.35.
  - **REC-faint** (the fallback): 0.18 / 0.22 / 0.16 / 0.10 / 0.06.
  - Both are fainter than Topo's ruled values.
  - The night tables can't carry hillshade (NightColour.kt walks only background, fill, line and symbol
    colours), so the app needs its own night pair, as Topo ruling 7 said.
  - The renders are at `/tmp/sage14-work/strips/`. Aspen sent ALT to Willow for the trial APK; the
    owner judges strength on the phone.
- **Aspen's session container restarted (about 09:30).** The WebP encode stopped at 142 of 156 tiles.
  The PNG set, the pmtiles and the hosted branch are complete.
- **0007 installed (Willow, 09:42 PST)**, on the owner's "Go on the modified shared resources" in
  Willow's window.
  - `COMMIT` is `53a728341`, and `map-build.prev` is `de30a84ee`. `USCA_PLANETILER_XMX=4608m`.
  - The jar sha256 is `25e5b8db…773a83`: 513 tests, 0 failures, BarriersTest 9. The prior jar is backed
    up at `basemap.prev-20261101/` (`d3210b86…`).
  - Aspen read all of this back at 09:50.
- **Space freed by Aspen**, on the owner's "Yes, delete both and rerun":
  - deleted `failed-usca/latest/out/forager-usca.pmtiles` (24.0 GB, partial) and
    `~/scratch/willow-pilot`, `willow-heap` and `willow-grid` (Willow's session was refused, "Irreversible
    Local Destruction");
  - kept the failed run's log, FAILED.txt, metrics and versions.
  - `/` now has 165.0 GB free (the build needs 157.1).
- **The rerun is released** (`--local 261030`). The hill shading's Pi work is done, and its APK builds in
  CI.
- **The rerun started at 09:43 PST as `usca-20261101T174337Z`.** Willow's session was refused, so Aspen
  started it under the owner's earlier "I allow the commands in this session" and today's "Rerun as
  soon as installed".
  - It runs as a transient unit, `forager-build-usca-rerun-261030`, with every setting of
    `forager-build-usca.service`, plus `build-usca.sh --local 261030`.
  - Inputs: local, 0 to download. NVMe: 165.0 GB free against 157.1 needed.
  - `forager-build.timer` is untouched (next run Sun 11-08); the script's flock prevents overlapping
    runs.
- **The upload watcher was restarted for this run** (09:44): Wi-Fi only, routing then `us.pmtiles`.
- **The hill shading trial APK (Willow, 10:30):** run 41332802392, artifact 13094875304, branch
  `hillshade-trial-s22` at `cae711fff` (never merge).
  - v4 with Sage's ALT. The style is fetched live, so the look can be changed with no new APK.
  - The night pair comes from `HillshadeTrialNight.kt` (MapLibre 13.5.0 takes shadow and highlight as
    colour arrays).
- **The rollout scope (Willow, 10:40):**
  - US + Canada z5-11 is 348,509 tiles (75 % of them at z11), about 22 GB (16-34 GB), 1-2.3 h on four
    processes, about $0.33/month on R2.
  - **The Worker needs a change first:** overflow and maxzoom advertising for the Street archive only,
    or relief z12+ requests would pull vector tiles into R2. The style also gives the relief source an
    inline tiles URL with maxzoom 11.
  - **The app:** v4's dem source and hillshade layer through `forager-fill-in.mjs`. A
    `forager:night-hillshade` night table replaces the trial's code. Credits rows for USGS 3DEP and NRCan
    MRDEM.
  - Relief joins offline downloads automatically (about 1.5-3 MB per region). Hide it under Topographical
    (OpenTopoMap shades already).
  - **The order:** the build (USB drive, outside the weekly run), then the Worker, then the R2 upload,
    then the v4 merge.
  - The WebP encode stopped when Aspen's container restarted, so it's untested.
- **Waiting for the owner's verdict on the trial.**
- **The owner, on the trial:** "It's good. It actively defines the trail map from a street or topo map,
  which is ideal. Let's keep this". Then "Go for all four, in order (Recommended)".
  - The four steps: the tiles (after tonight's run and upload), the Worker fix (Sorrel, then deploy),
    the R2 upload, and style, night and credits into #448.
  - **Aspen's note:** `pre-main` is 330 commits ahead of `main`, so the Worker deploy is a Worker-only
    PR to `main`, not a promotion. Sprite v6 stays on `pre-main` only, as ruled.
  - `/mnt/storage/relief/` was made writable for the build. Dispatched: coder-11.
- **Correction (Willow, 11:20):** the live Worker is **not** built from `main`. It serves `street-v3`,
  `reference-trails` and sprite v5, which only `pre-main` has.
  - It was deployed by hand with wrangler from `pre-main` (the v5 audit: Rowan, from `8b6f3572f`). A
    `main`-based deploy would drop street-v3 from every phone, so Aspen's "Worker-only PR to main" is
    withdrawn.
  - **The Worker fix:** `worker-overflow-street-only` (`0e3306d3d` tests first, then `f8fa10db2`), on
    `pre-main` `9ef5c9385`. Overflow and maxzoom advertising apply to `us` only; other archives answer
    204 above their maxzoom. Tests-first and fix runs are green as expected.
  - **The owner:** "pre-main as it stands (Recommended)". The deploy is wrangler from `pre-main` after the
    fix merges. That includes #453's v6 route, which is harmless: the files are on R2, and no style names
    v6 yet. It supersedes the earlier "pre-main only" for v6.
  - Who runs wrangler (needs a Cloudflare login) is settled before the deploy.
- **Wrangler on the Pi (Willow, 11:55):** 4.124.0 is installed but **not logged in** (no auth, no
  `CLOUDFLARE_API_TOKEN`), so the live version can't be read from the Pi. The `main` branch was dropped,
  never pushed.
  - **The deploy needs** Rowan's session (if it still has the login), the owner's machine, or an API
    token with Workers edit rights, made by the owner for the Pi. Asked of the owner when the fix is on
    `pre-main`.
- **Sorrel (12:35):** `worker-overflow-street-only` (`f8fa10db2`) is correct, with no blockers. A
  `pre-main` deploy changes nothing else live except the v6 route. The review is Forager
  `sorrel-worker-overflow` at `3baa5bf16`.
  - Sorrel's half-revert checks each fail exactly one test.
  - **The bug is live today for `world-south`:** it advertises 15, and a z9 request returned a Protomaps
    vector tile through the overflow.
  - R2 has one stray object, `overflow/world-south/9/81/183.mvt` (219,298 B, 10:54 PST, Sorrel's own
    probe). It should be removed once the deploy is done; that goes to the owner.
- Willow opens the PR to `pre-main`. **The deploy (wrangler) is waiting on the owner's choice:** Rowan,
  the owner, or an API token for the Pi.
- **The owner, on who deploys the Worker:** "Wait on this." The deploy is on hold, so the relief R2
  upload (which must follow it) waits too.
  - The relief build (after tonight's run) and the #448 style work go ahead.
  - **The stray tile:** "Yes, delete it (Recommended)", to be done after the deploy.
- **The owner:** "Find a way to deploy it. I did the API token already and I won't do it again". Aspen's
  two searches for where the token lives (Pi config files, then the records and workflows) were refused
  by Aspen's session as "Credential Exploration", so Aspen stopped.
- **The owner:** "Workers deploy from Main so no need for it".
  - **Aspen:** Cloudflare Workers Builds deploys from `main` (root `server/pmtiles-worker`), but `main`'s
    Worker folder lacks street-v3 and reference-trails, which are live. Deploying `main` as it stands
    would break every phone's Trail Map.
- **The owner:** "Yes, Worker folder only (Recommended)".
  - A PR to `main` that changes only `server/pmtiles-worker`, made equal to `pre-main`'s after the overflow
    fix merges (the fix plus v6).
  - Sorrel glances at it, then it merges, then Cloudflare deploys.
  - Aspen checks the live routes (street-v3/v2, reference-trails, sprites v4/v5/v6, a Street tile,
    world-south above z8 = 204), then deletes the stray world-south tile.
- **The owner:** "We are close to merging to main anyway, but may as well get it modular to work around
  these situations in the future".
  - **Aspen's plan, no dashboard change needed:** the Worker ships on its own track, still deployed by
    Workers Builds from `main`.
    - A Worker release is a PR to `main` from a `worker/<topic>` branch whose diff is confined to
      `server/pmtiles-worker`, its folder equal to `pre-main`'s.
    - A CI guard fails a `worker/*` PR that touches anything else, and checks the folder against
      `pre-main`.
    - The README's deploy section says this, and that `main`'s Worker folder is always what's live.
  - **Optional later** (the owner's dashboard, once): a dedicated production branch for the Worker
    (e.g. `worker-live`) plus build watch paths, so app merges to `main` never redeploy the Worker.
  - Willow does it after this deploy is live.
- **The merges:** Willow's session refused `gh pr merge 455` ("Merge Without Review"). The owner chose
  "Aspen merges both (Recommended)".
  - **Aspen merged #455 into `pre-main`** with a merge commit, `b535bc025`, matched to the reviewed head
    `f8fa10db2`, with all 6 checks green.
  - `worker/overflow-street-only` (`4fa944c01`, on `main` `177215135`): its folder equals the new
    `pre-main`'s, with 0 files outside `server/pmtiles-worker` (Aspen checked).
  - Its PR to `main` follows. Aspen merges it after Sorrel's OK; Cloudflare then deploys from `main`.
- **#448, hill shading (Willow, 13:00):** `00aaf7753`, then `a578ecd56`, which dropped the hillshade's
  own credits rows to avoid duplicating `pre-main`'s Heights section (68b9a2120). A test merge into
  `pre-main` is clean.
  - **PR #456** (`worker/overflow-street-only` -> `main`, `4fa944c01`) is open, with CI running.
  - **The owner, on the Heights credits wording:** "Leave as is. Full Topo will likely need it also." The
    current rows stay, and the wording gets revisited with own Topo.
- **#456's Worker job fails on `main`** (run 41349304735): `test/worker.test.mjs` imports
  `map-style/overrides/forager-reference.mjs` and hashes `map-style` files outside the folder, and
  `main`'s `map-style` is behind.
  - **Aspen, within the owner's go and "modular" ask:** option (a). Make the Worker's tests
    self-contained on `pre-main`: a reference-names copy with a cross-check, and the cross-folder
    assertions in their own test file, run only when `map-style` exists. Fold in the `worker/*` CI guard
    and the README.
  - Then Sorrel reviews, Aspen merges, and #456 is refreshed. #456 stays unmerged until then.
- **#448** at `a578ecd56`: every PR check passes, and it's mergeable. The merge is the owner's call.
- **The owner:** "I approve of your plan. Go".
- **PR #457** (`worker-self-contained-tests` -> `pre-main`; `d98d3980e` tests first, then `a43a41a05`)
  is green. It has the self-contained Worker tests, the cross-folder tests that skip on a folder-only
  `main`, and `tools/check-release.sh` with `worker-release.yml` (the `worker/*` guard), plus the README.
  Sorrel is dispatched.
  - **Risk (Willow):** Workers Builds redeploys `main`'s Worker folder on every push to `main`, and that
    folder is older than live. **Until #456 lands, nothing may be merged to `main`.** Any push would drop
    street-v3 and official trails.
- **The owner:** "I'll leave the merging to you for the time being. Let Rowan know also". Aspen merges for
  now. Rowan has been told by `prompts/aspen/2026-11-01-05-aspen-to-rowan-main-merges-held.md`
  (records-after-173 `deaa04b7d`) and a direct message: no merges to `main` until #456 is live.
- **The owner noticed #448's app still loads v3:** `STREET_STYLE_URL` is the Worker's `street-v3.json`,
  and the Worker serves no `street-v4.json` (404). v4 has only shown in S22 debug builds.
  - **The owner:** "Yes, queue it (Recommended)". After #456 is live, in order, each with Sorrel's review
    and merged by Aspen:
    1. v6 into #448;
    2. #448 into `pre-main`;
    3. a `worker/*` release serving `/style/street-v4.json`;
    4. the app-switch PR to v4.
- **Sorrel on #457 (13:45):** mergeable. 67/67 tests on `pre-main`, 65 plus 2 skipped on a folder-only
  `main`; the guard was checked on proper and broken releases.
  - **Should-fix 1:** guard PRs to `main` from non-`worker/*` branches that touch the folder. That's a
    follow-up.
  - **Aspen merged #457:** `pre-main` is at `08c1c3363`. Willow refreshes #456.
- **Sorrel confirmed #456 (14:05):** the folder tree is identical to `pre-main` `08c1c3363` (tree
  `28896dee`), confined to the folder. The live effect is v6 served plus the overflow fix.
- **Aspen merged #456 into `main` at about 14:30 PST: `33d2caa22`.** Cloudflare Workers Builds deployed it
  within about 45 s; v6 went from 404 to 200.
- **Aspen's live check after the deploy:**
  - Unchanged and answering 200: street-v3, reference-trails, reference-trails-manifest, street-v2,
    sprites v5, `us.json`.
  - The served street-v3 is JSON-equal to the bundled copy.
  - `us` maxzoom 15; a Portland z12 tile answers 200 (102,850 B).
  - **The fix is live:** `world-south.json` advertises maxzoom 8, and a z9 request answers 204.
  - Sprite v6's four files match the build sums (`c1f9b912`, `220679a6`, `64ad928a`, `428573d1`).
- **The stray tile is deleted** (`overflow/world-south/9/81/183.mvt`, on the owner's "Yes, delete it");
  `overflow/world-south/` is now empty.
- **`main` is safe for merges again.** Rowan has been told.
- **Sorrel (14:35):** #458 and #459 are mergeable.
  - **Aspen merged #458** (the path-based Worker folder guard) into `pre-main`: `40e9e4d3b`.
  - **Aspen merged #459** (v6 patterns into Street v4) into `street-v4`: `75bd32e17`. v4 now names sprite
    v6, with the orchard patterns, the hill shading, and 104 layers. v3 and sprite v5 are byte-identical.
- **Next, step (b):** a catch-up merge of `pre-main` into `street-v4`, then Sorrel reviews #448's delta
  since `97a26e8c7`, then Aspen merges #448 into `pre-main`. Then (c), the Worker serving
  `street-v4.json`, and (d), the app switch.
- **Sorrel's final review of #448** at `ae647aaf4` (sent 20:00): mergeable, with nothing new to fix.
  - Each piece equals its ruling. Phones still load v3. The catch-up merge needed no hand resolution.
  - **Carried to the switch PR:** pass `source.streetUri` for StreetWithTopoOver into the selector, and a
    CI job for the map-style checkers.
  - **Aspen merged #448 into `pre-main` at about 20:05 PST: `5679eabac`.** Step (c), the Worker serving
    `street-v4.json`, is with Willow.
- **The rerun cleared Planetiler:** the archive finished with 1.5B features, 651M tiles, heap 4.0G of 4.8G,
  post-GC 3.9G, so no out-of-memory error, and 0007 plus 4608m worked. It's in `routing-bands` at
  20:05.
- **Release path (the owner):** "Current play release doesn't have trail maps, so this will all be very
  new." "I think Main does automatic Play build releases so all I have to do is upload it to Play once
  it lands".
  - Asked whether Aspen should line up the promotion with Rowan and bring one release go: **"Yes
    please"**.
  - Rowan has been asked by `prompts/aspen/2026-11-01-07-aspen-to-rowan-release-promotion.md`
    (records-after-173): what on `pre-main` is ready, and the timing.
  - **The order:** the Worker v4 route, then the app switch PR, then the promotion, then the automatic
    Play build, then the owner's upload.
- **Rowan's reply (-08):** what's ready to ship isn't known yet. `pre-main` (363 ahead) needs sorting
  into ready / needs polish / must hide, and Rowan has asked the owner for a go on that.
  - #449 and #440 aren't on `pre-main`.
  - **The promotion gate:** CI, the UX auditor's report (a fresh session, on a different model), and the
    owner's approval. Rowan's hold (-1933) stands until the owner lifts it.
  - Aspen answered (-09): the trial is done, and #448 carries the rollout. The release go comes only after
    the sort and the audit.
- **Sorrel on #460:** mergeable, nothing to fix. The bundled v4 is byte-identical to map-style's
  (sha256 `6ce7271e…`), 71/71 tests, and revert checks fail as expected. Note for later: check that
  relief.pmtiles's header tile type is PNG.
  - **Aspen merged #460 into `pre-main`: `13bcd0ebf`.** The `worker/*` release to `main` comes next.
- **Rowan's hold on `pre-main` merges** (the owner's word in Rowan's window) still stands. The owner
  said they'd tell Rowan when it's safe.
