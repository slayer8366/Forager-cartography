# G7: the full 3″ elevation store for the route squares

Aspen. Times are PT. The scripts are in `2026-10-26-elevation-g7-files/`; the work is on the card in
`/mnt/archive/aspen-elevation-g7`.

## Go

- The owner, in Aspen's window, 2026-10-26 about 21:05: "Go on G7".
- The owner, in Rowan's window, relayed by Rowan: "Go on the elevation download". G8 is not included.

## What runs (read: `cells.py`, `cell.sh`, `g7.sh`)

- **Cells:** every 1° cell of the 187 `.rd5` squares in `out-usca/current/segments` (261024) that
  touches the build's own `us`, `puerto-rico`, `us-virgin-islands` or `canada` `.poly`
  (`/srv/forager-build/sources/aux`). That is 4,403 cells: US 2,061, Canada 2,532, both 190.
  - 1,441 have a 3DEP tile (3,811 tiles listed in the bucket).
  - The 620 US-polygon cells without a tile are open sea inside the polygon's offshore buffer.
    Checked: off Big Sur, Hatteras and Cape Cod; around Hawaii and Alaska.
- **Per cell (topo ruling 5):**
  - MRDEM-30 first where the cell touches Canada. It is read over HTTP in windows from the one
    83,854,027,098-byte COG and never downloaded whole.
  - Then 3DEP 1″ on top where it touches the US, downloaded, clipped to the US polygons with
    `-cutline`, then deleted.
  - Grid as in the pilot: 3″, 1201², cell centres on whole degrees, Int16, nodata −32768, average.
  - A cell with no valid pixel is written as `<name>.empty`.
- **Then:** `ElevationRasterTileConverter all hgt3 bef3 3`.
- **Run settings:** 3 cells at a time, under `nice -n 10` and `ionice -c3`. A re-run resumes.
  Each cell is skipped while `forager-build-usca.service` is active, and none starts after Sat
  10-31 22:00 PDT.

## Checks before the run (read)

- **Naming:** with a known cell copied to N61W150, N71W157 and N52E173, the converter wrote
  `srtm_07_00`, `srtm_05_-2` and `srtm_71_02`. PosUnifier's point mode read all three back at
  the cell's own height (1,848 m, the same as `gdallocationinfo`).
- **Converter:** it accepts a block with only some of its cells present (one cell gave a 1.5 MB
  `.bef`).
- **Test cells:**

  | Cell | Source | Time | Spot height |
  |---|---|---|---|
  | N49W123 | MRDEM, plus 3DEP clipped | 51 s | 539 m at (−122.5, 49.5); 0 m at Boundary Bay |
  | N53W120 | MRDEM | 15 s | Mt Robson 3,848 m (summit 3,954 m) |
  | N46W122 | 3DEP | 19 s | Rainier 4,376 m (summit 4,392 m) |

  The peaks read low because 3″ averages over about 90 m.

## Not as planned

- **1″ `.hgt` is not kept.** That is about 98 GB (computed). The USB storage drive is not mounted
  (`findmnt /mnt/storage` empty), and the card's 92 GB can't hold it. Keeping 1″ later means
  pulling 3DEP again: about 13 h at the pilot's measured rate.
- **`.bef` goes to `/mnt/archive/aspen-elevation-g7/bef3`, not the plan's
  `/mnt/archive/forager-build/elevation/bef3`.** The build user owns `forager-build`. Where it
  ends up is settled at G8.
- **It runs alongside the names build (`build-names.sh`, 261024) rather than after it:**
  - Disk: the card had 92 GB free. G7 needs about 13 GB at most (3″ `.hgt` about 13 GB, `.bef`
    2.5-4 GB, one COG per worker), and the names build a few GB.
  - Network: the names build uses none.
  - CPU and card I/O: G7 runs at low priority.

## Start

- **Started 21:13:20**, after a first launch at 21:12 was stopped by PID and relaunched detached
  (the tool's background limit is 2 h). 33 cells were already done; `cells.log` keeps every cell.

## Owner rulings on storage (via Rowan, 10-26 evening)

- **Devices (read, nothing written):**
  - The "64GB SSD" is the Lexar USB flash stick: `/dev/sda`, 61.9 GB, ext4, label `forecast-data`,
    empty, on the 5 Gbps port.
  - The micro SD is loose. The Pi's one slot holds the 128 GB archive card, and no reader is
    attached.
  - The 256 GB drive is not connected.
- **1, verbatim:** "Yes: back up heights (Recommended)". After G7 ends, the 3″ `.hgt` and the `.bef`
  (about 17 GB) are copied to the Lexar and verified by sha256. It is not to be reformatted or
  relabelled, and nothing else goes on it (no rollback copy).
- **2, verbatim:** "Wait for the 256 GB drive (Recommended)". No 1″ keep-copies now. A re-pull, even
  with that drive back, needs the owner's word.
