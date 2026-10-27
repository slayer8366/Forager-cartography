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
