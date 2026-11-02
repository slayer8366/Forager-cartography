# Willow's handoff: the Pi coder's work as of Sun 2026-11-01, 22:10 PST

From Willow Quadrat (Pi coder) to the next coder. Planner: Aspen. Aspen's own handoff is
`docs/handoffs/2026-11-01-aspen-handoff.md`. Read that one first for the planner's view and the owner's rulings; this one
is the coder's state of play. Claims are marked observed, read or inferred.

## How to work (read)

- **The profile** is `docs/process/pi-coder-profile.md` on Forager `pi-build`:
  - tests first, and one revert check per behaviour;
  - stop and ask when something is ambiguous;
  - commit and push often.
- **Reports** go to Aspen with `send_message`, with times in PT and each claim marked observed, read or inferred.
- **Merges:** the coder doesn't merge.
  - Aspen merges after Sorrel's "mergeable", or the owner does.
  - This session's permission check refuses `gh pr merge`, writes to `/opt`, deleting files, and starting services. When
    a step is refused, stop and report it with the exact command for the owner. Don't work around it.
- **Throwaway branches:** delete only on the owner's word. List them in reports.

### Tools on the Pi (observed)

- **Node:** `export PATH=~/tools/node-v22.23.3-linux-arm64/bin:$PATH`. `map-style/` needs its `node_modules`; symlink one
  from another worktree.
- **Java and Maven:** `/opt/forager-build/jdk`, `/opt/forager-build/maven/bin/mvn`. Read-only to you.
- **Gradle:** there's no Android SDK here. App tests run in CI:
  - `gh workflow run ci.yml --ref <branch> [-f tests='*SomeTest;*Other']`;
  - read failures with `gh run view <id> --log-failed`.
- **The Worker's tests** need wrangler's build, which only CI has. Run the folder's pure tests locally:
  `node --test test/self-contained.test.mjs test/check-release.test.mjs test/cross-folder.test.mjs`.
- **Style checks**, in `map-style/`:
  - `npm run -s generate:street` regenerates v3 and v4 and copies both into `server/pmtiles-worker/src/`;
  - then `npm run check:street` and `npm run check:street:v4`.
  - `assets/` (sprites and cut-outs) is gitignored: `./fetch-assets.sh`, then `node tools/build-sprite-v5.mjs` and `... v6`.
- **Local servers:** run them on `127.0.0.1` ports of your own, and stop them by PID. Never use `pkill -f`. Don't touch
  `:8081` or `:8765`.
- **Background tasks:** they have a 2-hour limit. For anything longer (downloads, builds), use `nohup setsid` with its own
  log and a PID file.
- **Wrangler** (`/home/bwann83/Forager/server/pmtiles-worker/node_modules/.bin/wrangler`) isn't logged in. The Worker deploys
  only through `main` (below).

## Running right now (observed, 22:06 PST)

- **The US + Canada rerun** `usca-20261101T174337Z`: transient unit `forager-build-usca-rerun-261030`, from the saved 261030
  inputs, with the installed 0001-0007 and a 4608m heap.
  - Planetiler finished: 651M tiles, post-GC 3.9G of 4.8G. So 0007 fixed the out-of-memory.
  - It's now in the `brouter` stage.
  - Aspen's upload watcher is armed for it.
  - **No heavy Pi work until it finishes:** no Planetiler, Gradle, mvn or big downloads.
- **CI for S-1** (see open item 1): the revert check failed, as it should; full CI was still running.

## Open items, in order

1. **Sorrel's S-1 on #462**, branch `night-tables-by-source`, head eafc26a5e, on pre-main 2bc8913f4.
   - `streetNightTablesForSource(source)` is the one place the night pass picks its Street tables, through `streetUriOf`.
     `NightTablesBySourceTest` tests what it chooses and holds `MapStyleReload` to calling it.
   - Tests first: 094256be3.
   - Revert check: throwaway `night-tables-revert-check` (80bbc697e), run 41395977468, failed as it should. Read the
     failing test's name from the log before reporting.
   - Full CI: run 41395980243.
   - **To do:** confirm both runs, open the PR to `pre-main`, and report to Aspen for Sorrel.
2. **The relief build** (coder-11 step 2), on Aspen's go after the rerun and its R2 upload finish.
   - On `/mnt/storage/relief/` (writable now), from `/mnt/storage/elevation/hgt3`: 3,631 cells.
   - z5-11 Terrarium PNG 256 px, Aspen's `/mnt/archive/aspen-hillshade-trial/make-relief.py` generalised. My sample copy is
     `~/scratch/willow-relief/make-relief-sample.py`.
   - Up to 4 processes under `nice -n 10`. Then MBTiles, then `pmtiles convert` to `relief.pmtiles`, with the attribution
     "Heights: USGS 3DEP; NRCan MRDEM". Skip WebP.
   - **Sorrel's check:** `pmtiles show relief.pmtiles` must read "tile type: png".
   - Expected (inferred from samples): about 348,509 tiles, 16-34 GB (about 22 GB likely), 1-2.3 h on 4 processes.
   - Record the time and size, and report.
   - It must be on R2 **before any v4 APK reaches phones**. Aspen plans the upload for Monday. New v4 downloads include
     relief tiles, which answer 404 until then.
3. **After relief is on R2:** check hill shading on the S22 with a v4 debug build. The Worker already serves
   `/relief/{z}/{x}/{y}.png` through the generic path; #455 stops the overflow for non-Street archives.

## What shipped today (observed)

### The map build (installed on the Pi)

- 0006 (orchards, nurseries and vineyards as farmland with `kind_detail`) is on `pi-build`.
- 0007 is on `pi-build` as 53a728341, installed:
  - the 0004 barrier mark became a whole-tile fill, so Planetiler deduplicates z15 tiles again (it ran out of memory on
    10-31);
  - heap 4608m;
  - jar sha256 `25e5b8db…a83`;
  - rollback: `basemap.prev-20261101`, and `map-build.prev` (de30a84ee).

### Street v4 (on `pre-main`)

- **#448**, merged at 5679eabac. It carries:
  - the fill-in;
  - orchards (fill, edges, sprite v6 patterns);
  - the hill shading (`dem` source, `hillshade` layer, `forager:night-hillshade`, night pass, hidden under Topographical);
  - creeks under water.
- **#462**, at 2bc8913f4: the app loads and downloads `/style/street-v4.json`.
  - v3 is kept as `STREET_STYLE_V3_URL`.
  - `streetUriOf` covers Street under Topographical.
  - New CI job: **map-style**. It regenerates the styles and fails on any difference from what's committed, then runs both
    checker suites.

### The Worker (live, deployed from `main`)

- **#456** and **#461** carried `pre-main`'s folder to `main`:
  - Street-only overflow and maxzoom;
  - sprite v6;
  - `/style/street-v4.json`.
- **#463** put the two guard workflows on `main`.

### How Worker releases work (read: `server/pmtiles-worker/README.md`, "Deploying")

- Cloudflare Workers Builds deploys **main's** `server/pmtiles-worker` on every push to `main`, whatever the push touches.
- A Worker release is a `worker/*` branch off `main`, made with `git checkout origin/pre-main -- server/pmtiles-worker`,
  with nothing outside the folder.
- Run the guard before the PR: `bash server/pmtiles-worker/tools/check-release.sh origin/main HEAD origin/pre-main`.
- The folder's tests must read nothing outside it (`self-contained.test.mjs`). Cross-folder checks live only in
  `cross-folder.test.mjs`, which skips on `main`.

### Global coverage (coder-08) and hill shading scope (coder-10)

- **Coder-08, Part A:** reported. Branch `worker-world-fallback` (planet first, then world-south; not merged).
- **Coder-08, Part B (the South America pilot):** paused by Aspen.
- **Renders:** `~/scratch/willow-global/shots/`.
- **The hill shading trial:** branches `hillshade-trial-s22` and `hillshade-trial-tiles`. Delete them on the owner's word,
  now that #448 has the real thing.

## Branches waiting for the owner's word to delete (throwaways, observed on origin)

| Branch | Why it was made |
|---|---|
| `street-v4-revert-hillshade-night` | revert check |
| `app-switch-revert-check` | revert check |
| `night-tables-revert-check` | revert check |
| `hillshade-trial-s22`, `hillshade-trial-tiles` | the hill shading trial |
| `street-v4-sprite-v6`, `street-v4-merge-sprite-v6` | merged into #448 |
| `worker-sprite-v6` | the pre-`pre-main` Worker branch |
| `worker-overflow-street-only` | merged as #455 |
| `street-grid-pilot` | Aspen kept it |
| `street-v4-s22-debug` | the S22 debug build; keep while S22 checks continue |

The `revert-check/*` branches on origin are other coders'. Leave them.

## Gotchas learned the hard way (observed)

- **Java's `-Xmx`** takes whole numbers only: `4.5g` stops the JVM ("Invalid maximum heap size"). Use `4608m`.
  `test_build_usca_functions.sh` checks this now.
- **Planetiler 0.10.2** deduplicates a tile only if every feature in it is a fill or an edge. Any point or line added to
  every tile undoes that.
- **MapLibre Native 13.5.0 hillshade colours:** `hillshadeShadowColor` and `hillshadeHighlightColor` take colour
  **arrays** (`arrayOf("rgba(…)")`). `hillshadeAccentColor` takes one colour.
- **The Worker's overflow** reads Protomaps' live **vector** build. #455 limits it to the Street archive, so never undo that
  for a raster archive.
- **A PR with a merge conflict** gets no `pull_request` CI run. If a PR shows no checks, test-merge it into its base.
- **`/mnt/storage`:** my user couldn't write to it before; `/mnt/storage/relief/` is writable now.
- **`raw.githubusercontent.com`** caches for 5 minutes. A debug build that loads a style from a branch sees pushes late.
