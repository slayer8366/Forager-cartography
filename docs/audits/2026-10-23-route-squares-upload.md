# Route squares (261021) uploaded to R2

Written by the planner session `forager-cartography-7b`, 2026-10-23. Times are PDT.

## Go

- **Relayed by Rowan:** asked "For Saturday, the trail route squares need to go up to our storage
  (187 files, ~1.5 GB, ~15 min, private). Which set?", the owner answered "Upload today's set now
  (Recommended)".
- **In the planner's session:** "Yes, upload".
- **The layout:** Rowan's request (RECORD -1553): `routing/<run-id>/segments4/<NAME>.rd5`, with
  `routing/manifest.json` uploaded last, private, and no Worker route.

## Prep (read-only, 2026-10-22 about 23:30)

- **Run:** `usca-20261021T111429Z` (from `status-usca.json`), OSM 2026-10-17T20:20:51Z, sequence
  `us:2415,canada:4945,us/puerto-rico:3281,us/us-virgin-islands:1790`.
- **Squares:** 187 `.rd5` in `out-usca/current/segments`, 1,562,441,923 bytes. Each was re-hashed,
  and all 187 match the build manifest's size and sha256.
- **R2:** `routing/` did not exist on R2.

## Upload

- **Squares, 02:25:40 to 02:28:28:** `rclone copy … r2:forager-maps/routing/usca-20261021T111429Z/segments4/`,
  as single PUTs (`--s3-upload-cutoff 200M`). Exit 0: 187 "Copied (new)" and 0 ERROR. The log is
  `2026-10-23-route-squares-files/upload.log`.
- **Read-back, finished 02:36:57:** each object was read with `rclone cat`, then its sha256 and size
  compared with the manifest. 187 match, 0 mismatch. `lsf` lists 187.
- **Manifest, last, at 02:37:07:** `routing/manifest.json` (Content-Type application/json).
  - The sha256 is `d2ff0d6b484adcb690a1e9d302c8d12a403eafd688d4c290582a168900468f4f`, the same
    locally and read back.
  - A copy is in `2026-10-23-route-squares-files/manifest.json`.
  - Its fields are `{run_id, osm_timestamp, osm_sequence, files: [{path, size, sha256}]}`.
  - `path` is the R2 key relative to `routing/`, for example
    `usca-20261021T111429Z/segments4/E170_N50.rd5`.
- **Private:** the live Worker answers HTTP 404 for `routing/manifest.json` and for a square, both
  cache-busted.

## Next

- Sunday's set replaces this one on a separate go, as a new run folder.
- Old run folders stay until the owner says otherwise (-1553).
- A copy of these squares is also in the USB rollback at `/mnt/storage/rollback/`.
