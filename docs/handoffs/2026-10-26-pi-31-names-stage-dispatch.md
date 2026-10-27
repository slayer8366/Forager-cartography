# Dispatch pi-31: trail-names files (FNAM v1) in the weekly build, plus one run on 261024

From Aspen Meridian (Pi planner) to Willow Quadrat (Pi coder), 2026-10-26. Times are PT.

## Why and the go

- **The need:** the app's wrong-turn alert (Forager step 7 PR 4, RECORD -1631) needs trail and road names
  from the same extract as the route squares. The routing data has none.
- **The plan:** `docs/design/2026-10-26-three-builds-plan.md` §2 (`0aef91d`).
- **Owner's answers, relayed by Rowan (RECORD -1695):** "Aspen's compact format (Recommended)". The 261024
  route upload is "Go, when names are ready (Recommended)".
- **Rowan, RECORD -1698:** dropping the per-record bbox is accepted; "Go ahead with Willow's build stage".
- **Measured today:** with the planner's prototype, `/home/bwann83/names-measure/fnam_measure.py`.
  - W75_N40: 1,117,150 named ways, a 38.9 MB file (no bbox), busiest 50 km area 4.3 MB.
  - W120_N45: 139,406 ways, 11.2 MB, busiest area 1.0 MB.

## Where

- Forager repo. Make a worktree off `origin/pi-build` on a new branch `pi-31-names-stage`:
  `git -C ~/Forager worktree add ~/forager-pi31 -b pi-31-names-stage origin/pi-build`.
  Don't touch the `~/Forager` checkout's own branch.
- Code goes under `map-build/`, as in pi-30.
- Push the branch to origin. **Don't merge to `pi-build` and don't install into `/opt/forager-build`.**
  The planner reviews first, then installs.

## Verify before building (report each, with file:line)

1. `$routing_in` is created at `build-usca.sh:728` and deleted at `:753` (installed copy, `COMMIT aa14e6ea`).
   Confirm the same lines on `origin/pi-build`.
2. **Equivalence:** `osmium tags-filter w/highway`, then `w/name w/ref`, gives the same ways and nodes
   whether run on `$routing_in` or on the four raw extracts. `USCA_ROUTING_FILTER` keeps every
   `w/highway` way whole with its nodes (`pins.env:202`).
   - Show it on `us-virgin-islands-261024.osm.pbf` (card, 3 MB): run the build's filter + merge, then
     the names filter, and compare with the names filter on the raw file. `osmium diff` should be empty,
     or the FNAM output byte-identical.
   - If they differ, **stop and report.** The one-off run below depends on it.
3. `osmium export -f geojsonseq` to stdout, with a config keeping only `name`, `ref`, `highway` and `area`
   tags, runs on the full named file without the OOM killer. Measure peak RSS (`tools/peak_rss.py`).
   - Two `osmium extract -s complete_ways` passes at once on this file reached 7.4 GB and were killed
     today at 17:09.
   - The stage must not use `complete_ways` per square. One export pass, streamed into the encoder,
     assigns every piece to its cell and square.

## FNAM v1 (the format; the planner's, don't change it without asking)

One file per route square, named as the `.rd5`: `names1/W75_N40.fnm` beside `segments/W75_N40.rd5`.
Little-endian throughout. `varint` is unsigned LEB128. `zz(n)` is zig-zag, `(n << 1) ^ (n >> 63)`.

**Header, 32 bytes:**

| Offset | Type | Field |
|---|---|---|
| 0 | 4 bytes | magic `FNAM` |
| 4 | u16 | version = 1 |
| 6 | i16 | west: the square's west edge, whole degrees (W75 → -75) |
| 8 | i16 | south: the square's south edge, whole degrees |
| 10 | u8 | cells per side = 40, so 1/8° cells |
| 11 | u8 | reserved = 0 |
| 12 | i64 | OSM timestamp, Unix seconds (the extract's replication timestamp) |
| 20 | u32 | tables offset |
| 24 | u32 | directory offset |
| 28 | u32 | records offset |

**Tables, at the tables offset:**
- Strings: `varint N`, then N × (`varint byte length`, UTF-8 bytes). Records refer to strings 1…N, and
  0 means none. Names and refs share the table.
- Highway values: `varint M`, then M × (`varint length`, bytes). Records refer to them 0…M-1 in one byte,
  so M ≤ 256.

**Directory, at the directory offset:**
- 1600 × (`u32 offset`, `u32 length`). Offsets are relative to the records offset.
- The index is `row * 40 + col`, with `row = floor((lat - south) * 8)` and `col = floor((lon - west) * 8)`,
  so row 0 is the south.
- An empty cell has length 0.

**Cell body:** `varint` record count, then each record:
- `varint` name: 0, or a 1-based string index;
- `varint` ref: the same;
- `u8` highway: an index into the highway table;
- `varint` point count, at least 2;
- points: the first is `zz(x) zz(y)` relative to the cell's south-west corner, the rest `zz(dx) zz(dy)` from
  the previous point. Units are 1e-6°. The corner is `round((west + col/8) * 1e6)`, `round((south + row/8) * 1e6)`,
  and points are `round(lon * 1e6)`, `round(lat * 1e6)`.

**No bbox in records** (RECORD -1698). The reader computes it.

**Content:**
- Ways with `highway=*` and a `name` or a `ref`, exported as LineStrings.
- Dropped: polygons from closed ways; `area=yes`; and `highway` values `proposed`, `construction`,
  `abandoned`, `razed`, `disused` and `platform`.
- **Simplified** by Douglas-Peucker at 2 m (a local equirectangular frame per line) before splitting.
- **Split at cell edges exactly:** a segment that crosses an edge gets an interpolated point on the edge,
  and each piece lies inside one cell. A point on an edge belongs to the cell to its north and east,
  following the floor rule above.
- Pieces in cells of squares that have no `.rd5` are dropped. Every `.rd5` square gets a file, even one
  with no records.
- Pieces in a cell may be in any order.

**Area cut (Hazel's Worker, later, for reference):** the same format and the same square origin. Only the
area's cells carry data, and the others have length 0. The string table may be re-indexed. A reader must
not assume indices are stable across files.

## Build integration

1. **The encoder:** `map-build/tools/fnam_build.py`, Python stdlib only, like the other tools. Input is
   geojsonseq on stdin; outputs are the square files in an output folder, for a given list of square
   names (the `.rd5` set).
   - Holding encoded cells in memory is fine if peak RSS stays under 2 GB on the full input. Measure it.
   - Parallelism is optional.
2. **The stage in `build-usca.sh`, `set_stage names`:** between the band cut and `rm -f -- "$routing_in"`
   (`:753`).
   - Run the two tags-filters on `$routing_in` to a temporary file in `$run`, then `osmium export | fnam_build.py`
     into `$run/out/names1/`.
   - Run it after the `.rd5` squares exist (after the brouter stage), so the square list is known. If
     `$routing_in` must live longer for that, keep its named cut instead and delete `$routing_in` where it
     is deleted today.
   - Nothing about the `.rd5` squares may change.
3. **Validation, section 7:**
   - every `.rd5` has a `.fnm`;
   - each `.fnm` has the right magic, version and edges for its name, and its offsets and lengths are
     inside the file;
   - log the count, the total bytes and the largest file.
4. **Manifest:** add the `.fnm` files to `run_record.py`'s `--outputs`, so the build manifest lists their
   size and sha256 as it does for the squares.
5. **Disk check:** the names output, about 0.6-0.75 GB a set (inferred), stays in the output. If you can
   see where the check should count it, say where. Don't change `pins.env` ratios without asking.
6. **One-off script, `map-build/bin/build-names.sh <extract-dir> <osm-timestamp> <square-list-dir> <out-dir>`:**
   the same filter, export and encoder, on raw extracts. Its temporary files go on the card under
   `/mnt/archive/forager-build/work/`, not the NVMe; the NVMe has about 6 GB above the weekly start check.
   Step 2 of "Verify before building" is what makes this equal to the stage.

## Tests (map-build/tools/test_fnam_build.py, `python3 -m unittest`)

- Round trip: a small geojsonseq fixture → files → decode with a test decoder → the same names, refs,
  highway values, and points to the 1e-6 grid.
- Cell edges:
  - a line crossing a cell edge splits there, with the interpolated point on the edge in both pieces;
  - a line crossing a square edge lands in both squares;
  - a point exactly on an edge goes north/east.
- Dropped values and polygons are absent.
- Douglas-Peucker: no kept line moves more than 2 m from its source.
- Directory offsets and lengths cover the records exactly, without overlap.
- **Revert check:** break the edge interpolation (assign by midpoint, as the planner's prototype did) and
  show which test fails, with its message.
- The existing suites still pass: `tools/test_build_usca_functions.sh`, `test_run_record.py`, and the rest
  under `tools/`.

## One run on 261024, to scratch (after tests pass)

- Inputs: `/mnt/archive/forager-build/sources-osm/*-261024.osm.pbf` (OSM 2026-10-24T20:20:51Z) and the
  square list from `/srv/forager-build/out-usca/current/segments/` (187 `.rd5`). Read only; don't modify
  either.
- Output: `/srv/forager-build/names-261024/names1/`, plus a log. Temporary files on the card.
- **Report:**
  - wall time and peak RSS per step;
  - the file count, which must be 187;
  - total bytes and the largest file;
  - W75_N40 and W120_N45 against the planner's prototype figures (38.9 MB and 11.2 MB; within ±15%
    expected, explain any bigger gap);
  - free space on the NVMe and the card before and after.
- It must finish before **Sun 11-01 02:13 PST**, when the weekly build starts and deletes these extracts at
  publish. Don't run anything while `forager-build-usca.service` is active.

## Don't

- No uploads to R2 and no Worker or app changes. Don't touch `/mnt/storage`, which isn't mounted.
- No apt installs. If the encoder seems to need pyosmium or shapely, stop and say why.
- Don't edit `/opt/forager-build`, the systemd units or the timer.
- Don't delete anything outside your worktree and your own scratch and temporary folders.

## Report back

Commits (hashes) on `pi-31-names-stage`, the verification answers with file:line, test output with
counts, the revert check, the 261024 run's figures above, and anything not done or not tested, said
plainly.
