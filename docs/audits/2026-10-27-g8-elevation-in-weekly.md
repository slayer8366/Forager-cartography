# G8: the weekly build makes route squares with 3″ heights, from 2026-11-01

Aspen, 2026-10-27, about 06:50 PDT. Times are PT.

## Go

The owner, via Rowan, verbatim: "G8 from Sunday, app later". The weekly build from Sunday 11-01
builds `.rd5` with G7's 3″ `.bef`. The app keeps `consider_elevation` off; its change is its own
report and go.

## Branch (Forager `pi-32-elevation`, `6b991fac5`, on `pi-build` `20f75d063`; not merged)

- **PosUnifier's last argument:** `"$USCA_BEF_DIR"` in place of the empty `no-elevation` folder.
- **Pins:**
  - `USCA_BEF_DIR=/mnt/archive/forager-build/elevation/bef3-20261027`
  - `USCA_BEF_SUMS_SHA256=36b05da7cee10340f8ccec1249255d97e7b096564323c71f7101fee443102292`, the
    sha256 of the store's `SHA256SUMS`
  - `USCA_BEF_FILES=182`
- **`bef_store_ok DIR SUMS FILES [full]`** checks that the folder and `SHA256SUMS` exist, that the
  list's sha256 and line count match the pins, and that the folder has that many non-empty `.bef`.
  With `full`, every file is also hashed against the list.
  - **Called in full at the state stage,** after the disk check and before any download, so a
    missing or changed store fails in about a minute.
  - **Called quickly at the start of the brouter stage,** in case the card went away mid-run.
  - Either failure `die`s.

## Where the build reads heights from: the card, not /mnt/storage

- **The card** (`/mnt/archive`) is already a hard requirement: `card_ready` stops a run if it isn't
  mounted.
- **`/mnt/storage`** is mounted `nofail` and doesn't remount on a replug (the 10-22 lesson). The
  owner has moved drives during runs before.
- `/mnt/storage/elevation/bef3` stays as the verified backup (G7 record).
- **Behaviour change:** a `--basemap` run used not to need the card. It now does, for the store,
  and stops at `state` without it.

## Tests (read, on the Pi)

| Suite | Result |
|---|---|
| `test_build_usca_functions.sh` | **76** (9 new for the store) |
| `test_build_usca_run.sh` | **65**, exit 0 (R9 new: missing store, changed `.bef`) |
| `test_build_names.sh` | 23 |
| `test_build_usca_disk.sh` | 95 |
| `test_build_functions.sh` | 14 |
| `test_fnam_build.py` | 21 OK |

**Revert checks**, each run once:
- With PosUnifier back on `no-elevation`, the functions test fails ("PosUnifier reads the pinned
  store…").
- Without the state-stage check, both R9 checks fail ("…at the state stage"). The run still dies
  later, at the brouter-stage check.

## Does Sunday still fit? (read 06:44 PDT, last week from `logs/usca-20261025T101217Z.log`)

- **NVMe:**
  - 160,750,977,024 bytes free now. Last week's start had 162.5 GB free and needed 157.2 GB, from
    18.82 GB of inputs × 7.59 + 10 %.
  - With similar inputs, **about 3.5 GB in hand** (inferred), 1.7 GB less than last week.
  - About 1.2 GB of that is my own scratch: `~/reference-trails-build` 210 MB, `~/pi31-scratch`
    752 MB, `~/names-measure` 202 MB. Moving or deleting it restores about 5 GB; it waits for the
    owner's word.
  - The names stage and the heights don't touch the start check. They sit inside the routing stage,
    after Planetiler's temp is removed. They add about 0.8 GB per kept set from the week after
    (names 0.6 GB, `.rd5` +10-14 % of 1.56 GB).
- **Card:**
  - 79,451,602,944 bytes free now. The run needs 42.6 GB there (download + merged extract + 5 GB).
  - The store copy adds 1.93 GB. **About 35 GB in hand.**
  - `forager-build/work/pi31-willow` (2.2 GB, the pi-31 helper's) isn't removed by the build;
    suggested for removal.
- **Time:**
  - Last week: 10:12:17Z to 01:01:23Z, 14.8 h.
  - Added: the store's full check (1.93 GB hashed on the card, about 1 min, inferred); PosUnifier
    with heights at +1.6-5.8 s per square, so under 15 min (G6); the names stage, about 30 min
    (the 261024 `build-names.sh` run took 27 min from raw extracts).
  - **About 15.5 h in all (inferred), so a 02:13 PST start ends about 17:45 PST Sunday.**
- **Memory:** unchanged. PosUnifier with heights peaked at 575 MB in G6; the names pipeline at about
  5.6 GB after BRouter.

## Install, after Sorrel's review (needs the owner's word typed in Aspen's window)

1. Copy `/mnt/archive/aspen-elevation-g7/bef3/*.bef` and its `SHA256SUMS` to `USCA_BEF_DIR`,
   root-owned and readable. Check `sha256sum -c` there and the list's sha256 against the pin.
2. Merge `pi-32-elevation` into `pi-build`, then run `install-map-build.sh` from a clean worktree.
   `map-build.prev` becomes `20f75d063`.
3. Check `COMMIT`, and run `bef_store_ok … full` on the installed path.

## Sorrel's review and the fixes (10-27 morning)

- **Review:** Forager `sorrel-pi32-elevation` `c3c914b70`, `docs/reviews/2026-10-27-sorrel-pi32-elevation.md`.
  Mergeable, nothing blocking.
- **The owner, verbatim:** "Fix the gap, then install (Recommended)".
- **Fixes in `ea67332db` on `pi-32-elevation`:**
  - **S1:** `heights_read_ok` runs after each band's PosUnifier. It stops the run if a node tile is
    left `<SQUARE>.u5d` (no heights read) for a square not in the new pin
    `USCA_BEF_NONE="W170_N20 W180_N25 W80_N25 W95_N15 W95_N20"`.
    - **The marker was read on the Pi first,** with BRouter 1.7.10 on the 261024 USVI extract:
      with the store, `W65_N15.u5d_3` and `W70_N15.u5d_3`; with an empty folder, `W65_N15.u5d` and
      `W70_N15.u5d`.
  - **N1:** the state-stage check is skipped on `--fetch-only`.
  - **N3:** a failed full check names the files.
  - **N4:** the quick check compares names, not only counts.
  - **N5:** a missing store says when the card isn't mounted.
  - **N2:** R10 is now a behavioural test for the brouter stage.
- **Tests:**

  | Suite | Result |
  |---|---|
  | functions | 83 (7 new) |
  | run | 69 |
  | names | 23 |
  | disk | 95 |
  | build_functions | 14 |
  | fnam | 21 |

  The run suite's new scenarios:
  - **R10:** with the store there, the run reaches WayLinker and logs the pinned squares. With the
    store gone after the cutter, it fails at brouter, naming W125_N45, before WayLinker.
  - **R11:** `--fetch-only` isn't stopped by a missing store.
- **Revert checks,** each run once: without the heights check R10 fails; without the gate R11
  fails; without the name comparison the quick-check name test fails.
- **Side note:** BRouter's cutter takes about 2 min to start even on a 0.9 MB input (121 s, 4 GB
  heap); a 120 s timeout cut off the first try.

## Scratch moved to the 256 GB drive (10-27)

- **The owner, via Rowan, verbatim:** "Move them to the 256 GB drive (Recommended)".
  - The removal was first refused by this session's permission check as irreversible.
  - The owner said "Go" in Aspen's window, at about 07:25 PDT.
- **Copied** (06:48-06:50; drive read `/dev/sda1` on USB 3 before and after) with `rsync -a` to
  `/mnt/storage/moved-20261027/`:

  | Folder | Files | Links |
  |---|---|---|
  | `reference-trails-build` | 10 | 2, into `/mnt/archive/aspen-reference-trails-20261026`, unchanged |
  | `pi31-scratch` | 23 | 0 |
  | `names-measure` | 13 | 0 |
  | the card's `forager-build/work/pi31-willow` | 5 | 0 |

  Each folder has a `.sha256` and a `.links` list beside it.
- **Verified** from the drive after `drop_caches`: at 06:50 and again at 07:25, every file OK and
  every link identical.
- **Originals removed** at 07:26.
- **Free space at 07:26:24 (read):**

  | Disk | Bytes free | Change |
  |---|---|---|
  | NVMe | 161,965,445,120 | +1.21 GB; about 4.8 GB in hand against last week's 157.2 GB need |
  | card | 81,753,735,168 | +2.30 GB |
  | `/mnt/storage` | 183,807,627,264 | |

## The owner's install go, conditional (10-27 about 07:35 PDT, in Aspen's window)

- The owner said "Go". Asked whether that meant now or after Sorrel's quick look at `ea67332db`
  (not posted yet; `sorrel-pi32-elevation` is still `c3c914b70`, 06:59), the owner chose: **"Wait for
  Sorrel, then install (Recommended)"**.
- **So the install has its go.** It runs once Sorrel's quick look says mergeable:
  1. Merge `pi-32-elevation` into `pi-build` (`--no-ff`).
  2. Copy the store to `USCA_BEF_DIR` on the card and check `SHA256SUMS` there.
  3. `install-map-build.sh` from a clean worktree.
  4. Check `COMMIT`, and run `bef_store_ok … full` on the installed path.
- **If Sorrel's look finds something to fix,** the go doesn't cover the changed commit until the owner
  is asked again.

## Sorrel's quick look: B1 found and fixed (10-27, about 09:30 PDT)

- **Quick look:** `sorrel-pi32-elevation` `25ecfe7cd` at `ea67332db`. It found one **blocker, B1**.
  - The line that logs a band's pinned squares listed them with `ls -- *.u5d`. **In a band with no
    unsuffixed tile, the normal case, `ls` exits 2, and `pipefail` with `errexit` ends the run at
    brouter with nothing logged.** Sunday's run would have stopped at band two.
  - My R10 stub always wrote `W80_N25.u5d`, so the tests never saw a band without one.
  - **Reproduced in a clean bash on the Pi:** the old line exits 2 with only `.u5d_3` tiles. My
    first attempt in this session's shell didn't fail, because its profile changes how globs
    expand; the build runs under plain bash.
- **Under the owner's condition, their install go doesn't cover the new commit.** No merge, no
  install.
- **Fixes in `8a9331fa6`:**
  - **B1:** `find -maxdepth 1 -name '*.u5d'`.
  - R10 gains an all-heights case: the run reaches WayLinker and logs no pinned squares.
  - **N6:** R11 now asserts rc 0 and ok at fetch-only.
- **N7, read 09:28 PDT:** `bef_store_ok` from this head was run against `/mnt/storage/elevation/bef3`,
  the verified copy of what the install will put at `USCA_BEF_DIR` (that path doesn't exist yet).
  - The `SHA256SUMS` sha256 equals the pin; 0 lines off the form `<sha>  srtm_X_Y.bef`.
  - Quick check OK; full check OK in 13 s.
- **N8, noted:** a node tile outside the 187 squares would also stop the run, naming the square.
- **Tests:** functions 83, run 70, names 23, disk 95.
- **Revert check:** with the `ls` line back, the new R10 case fails.
- **Next:** Sorrel's quick look at `8a9331fa6`, then the owner is asked again for the install go.

## G8 installed (10-27, 09:40-09:44 PDT)

- **Re-check:** Sorrel `4208a9e03` at `8a9331fa6`: mergeable for the 2026-11-01 run.
- **The owner, in Aspen's window, asked again:** "Go, install now (Recommended)".
- **1. Merge:** `532f70fd6` ("Merge pi-32-elevation (G8) …", `--no-ff`) on `pi-build` `20f75d063`,
  in a fresh worktree, pushed. Suites at the merge head:

  | Suite | Result |
  |---|---|
  | functions | 83 |
  | run | 70 |
  | names | 23 |
  | disk | 95 |
  | build_functions | 14 |
  | fnam | 21 |

  Worktree removed.
- **2. Store on the card (09:41-09:43):**
  - Service inactive; `/mnt/archive` is `/dev/mmcblk0p1`; no `elevation/` beforehand.
  - Created `/mnt/archive/forager-build/elevation/bef3-20261027`, root:root 0755. Copied the 182
    `.bef` (0644) from `/mnt/archive/aspen-elevation-g7/bef3`, plus `SHA256SUMS` (from
    `bef3.sha256`); 1,926,613,676 bytes with the list.
  - The `SHA256SUMS` sha256 is `36b05da7…102292`, equal to the pin.
  - After `drop_caches`, `sha256sum -c` **as forager-build**: all 182 OK.
- **3. Install:** `install-map-build.sh` from the clean merge worktree.
  - **`COMMIT` = `532f70fd691a32a755fe99d2727e9df9428c4fdc`.**
  - **Rollback:** `map-build.prev` = `20f75d063`; the older `aa14e6eaa` is `map-build.prev.1793119401`.
- **4. Step 4** (Sorrel's N7 directory half), from the installed script and pins, as forager-build,
  in a clean bash, after `drop_caches`:
  - `USCA_BEF_DIR=/mnt/archive/forager-build/elevation/bef3-20261027`, 182 files.
  - **Quick OK; full OK (21 s).**
- **Also checked:**
  - The installed `build-usca.sh` has the `heights_read_ok … "$USCA_BEF_NONE"` call and no
    `no-elevation`.
  - The installed file list matches `git archive 532f70fd6`.
  - The functions suite from the installed copy: 83.
  - forager-build can run the script.
  - Timer: Sun 11-01 02:13 PST.
- **Rollback steps:** `sudo mv -T /opt/forager-build/map-build /opt/forager-build/map-build.bad &&
  sudo mv -T /opt/forager-build/map-build.prev /opt/forager-build/map-build`. The store on the card
  can stay; 20f75d063 doesn't read it.
- **Sunday's run** builds route squares with 3″ heights and names files. The app keeps
  `consider_elevation` off. Read after the run: the log's "elevation store:" line, the per-band
  "no heights, as pinned" lines, and the `.rd5` growth (+10-14 % expected).

## The owner's plan for an early run (10-27, about 10:30 PDT)

- **Verbatim:** "When the fixes are in place and verified, I'm going to have you run the build early.
  And then we can run it on Sunday, and keep the schedule as planned."
- **"The fixes"** are the buildings outline and the night tree glyphs (handoff `51d6358`). Both are
  app-side style changes; the Pi build doesn't carry them. The early run tests names + heights (G8)
  on real data before Sunday.
- **Constraints, to be re-read before starting:**
  - About 15.5 h (inferred), so it must start by about **Sat 10-31 10:00 PST**. `build-usca.lock`
    stops the 02:13 timer run if it's still going.
  - Its publish replaces the 261024 set on the Pi (`USCA_KEEP_GOOD_OUTPUTS=1`); R2 is untouched.
  - Its set is about 0.8 GB bigger, so Sunday's start check has about 4 GB in hand (inferred; read
    `df` before each run).
  - Sunday builds only if Geofabrik has newer extracts.
- **Starting it needs the owner's word typed in Aspen's window.**

## The owner's files off the NVMe (10-27, 14:07-14:21 PDT)

- **The owner, in Aspen's window:** "Go ahead and move the 14gb to the flash drive". That's
  `~/imx` and `~/archive`, the NVMe stopgap from the NVMe answer to Rowan.
- **Before (read 14:07):**
  - Nothing had them open (`lsof`); nothing in cron, systemd, fstab or the shell profile names them.
  - The drive was `/dev/sda1` on USB 3.
  - `imx`: a Python project with a virtualenv, 12,143,947,386 B, 4,566 files, 4 links.
  - `archive`: bracket captures, 2,513,384,852 B, 253 files.
- **Copied** with `rsync -a` to `/mnt/storage/moved-20261027/{imx,archive}`, with `.sha256` and
  `.links` lists beside them.
- **Verified** from the drive after `drop_caches`: all files OK, links identical. Originals removed
  14:20.
- **Note for the owner:** `imx/venv` records its old absolute path, so it needs re-creating before
  it's used from the new place, or a link `~/imx` → the copy. Neither was done.
- **Free (read 14:20:52):**
  - **NVMe 176,621,113,344 B** (+14.67 GB). About 18.5 GB over Sunday's ~157.3 GB start need
    after the early run's +0.8 GB (inferred), so roughly 2 years at the measured growth (inferred,
    one interval).
  - `/mnt/storage` 169.1 GB.

## Early run started (10-27 15:14 PDT)

- **Cue met** (Forager RECORD -1755): the buildings are verified (-1748), and the night-glyph fix is
  verified on #429's build (-1754). The owner, in Aspen's window: "Go ahead and begin the run".
- **Before starting (read 15:13):**
  - **The Pi had rebooted at 15:11** (the owner, via Rowan: power unplugged, now fixed). `/mnt/archive` and `/mnt/storage` were both back from fstab;
    the 256 GB drive is on USB 3 (now device 2); NTP synced.
  - Service inactive; COMMIT `532f70fd6`; 182 `.bef` on the card.
  - NVMe 177.9 GB free, card 79.8 GB.
  - The timer's next fire is now Sun 11-01 02:29:45 PST, from its 30 min RandomizedDelay, re-drawn
    at boot.
- **Started:** `sudo systemctl start --no-block forager-build-usca.service` at **15:14:00 PDT**. Run
  `usca-20261027T221400Z`, extracts 261026 (OSM 2026-10-26T21:24:46Z), inputs 18,825,253,619 B.
- **State checks (read from the log):**
  - NVMe 177.9 GB free against 157.2 GB needed.
  - Card 79.8 GB free against 42.7 GB needed.
  - **Elevation store: 182 `.bef` matching SHA256SUMS (`36b05da7…`)**, the full check, 15:14:10-15:14:31.
- **Then:** fetch-extracts from 15:14:32. Expected end about 06:45 PDT Wed 10-28 (inferred, 15.5 h).

## Early run finished (10-28 05:59 PDT): ok

Read 08:01 PDT from `/srv/forager-build/status-usca.json` and `logs/usca-20261027T221400Z.log`.

- **End state:** `state ok`, `stage done`, no warnings. Published
  `/srv/forager-build/out-usca/20261026T212446Z` at 12:59:23Z (05:59 PDT), 14 h 45 min after the start.
- **Stage times (log):**
  - downloads 15:14-17:23; merge to 17:46;
  - Planetiler 17:46-01:32 (27,940 s, 7 h 46 min; last week 8 h 42 min);
  - routing input 01:32-02:02 (829,409,865 nodes, 77,320,127 ways); bands 02:02-02:48;
  - BRouter 02:48-05:48; names 05:48-05:54; validate 05:54; publish 05:54-05:59.
- **Heights (G8), first full run:**
  - No `read no heights` failure (0 matches in the log).
  - `no heights, as pinned` lines, all only squares in `USCA_BEF_NONE`:
    - -180:-125: W170_N20 W180_N25
    - -100:-95, -95:-90, -90:-85: W95_N15 W95_N20. The squares sit on these bands' widened extracts.
    - -85:-80, -80:-75: W80_N25
    - The other bands printed none, so every square there read heights.
  - Squares kept per band: 48, 9, 19, 20, 11, 13, 11, 12, 11, 33 = **187**.
- **Names check:** `187 .fnm files, one per .rd5; 603705657 bytes; largest W75_N40.fnm, 38054680 bytes`.
- **Validate:** archive z0-15, 9 layers, roads with all six trail keys; 9 sample points covered; 187 `.rd5`, 187 `.fnm`.
- **Route squares:** 187 `.rd5`, **1,748,674,894 B**, against 261024's 1,563,722,864 B: **+11.8 %** (expected
  +10-14 %; most of it is the heights). Archive `forager-usca.pmtiles` 34,137,101,257 B.
- **Rotation:** publish removed the old output 20261024T202051Z and the 261024 extracts (NVMe and card). The
  261024 set on R2 is untouched and still live.
- **Free afterwards (read 08:01 PDT):** NVMe 177,126,944,768 B (177.1 GB); card 79,824,650,240 B (79.8 GB);
  `/mnt/storage` 169.1 GB.
- **Not done:** no R2 upload. That needs the owner's go. Sunday 11-01's run is unchanged.
