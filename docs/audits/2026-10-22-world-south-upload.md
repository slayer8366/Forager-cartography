# World fill: world-south.pmtiles extracted from the Protomaps planet and uploaded to R2

Written by the planner session `forager-cartography-7b`, 2026-10-22, from its own commands and their
output. Times are UTC, with PDT in brackets.

## Why

The owner's in-app test of the Street build showed a grey band at low zoom, relayed by Rowan. The
read-only check behind it:
- `us.pmtiles` (261021) holds no tiles south of a tile-row edge.
- The edge is 0° at z1-z4, 11.2°N at z5-z6, and just below 15.92°N from z7 up.
- 15.92°N is the archive's bounds south edge, which is `us.poly`'s minimum latitude.
- North of the edge, tiles outside the extracts exist, but they hold land or water fill only.
- The 10-19 archive has the same gaps, so this is not a regression of 261021.

The estimate sent to Rowan recommended Option A: a world fill south of 16°N to z8 as a second archive,
served by a Worker fallback.

## Go

- The owner, relayed by Rowan: "Both now" (Forager RECORD -1554, records-after-173 at 9e05e62).
- Confirmed in this session. The question named the extract (planet 20261022, south of 16°N, z0-8,
  about 100 MB), the key `r2:forager-maps/world-south.pmtiles`, the verification, and that
  us.pmtiles, the Pi build and the route squares stay untouched. The owner's answer: "Yes, extract and
  upload".

## Extract

- Command:
  `pmtiles extract https://build.protomaps.com/20261022.pmtiles world-south.pmtiles --bbox=-180,-85.05,180,16 --maxzoom=8`,
  run in `/home/bwann83/world-south/`.
- Source: 20261022 was the newest dated build that answered (HTTP 206) at about 13:57Z (06:57 PDT).
  Its `planetiler:osm:osmosisreplicationtime` is 2026-10-22T04:00:00Z.
- The extract completed at 13:59:58Z (06:59:58 PDT): 40 requests, 104 MB transferred.
- Result: 99,514,676 bytes. `pmtiles verify` passed.
- Header (`pmtiles show`):
  - spec version 3, tile type mvt, tile compression gzip, internal compression gzip;
  - min zoom 0, max zoom 8;
  - bounds -180, -85.05 to 180, 16;
  - 47,817 addressed tiles, 13,113 tile entries, 10,606 tile contents;
  - version 4.15.2, planetiler 0.10.2. These are the same values as `us.pmtiles`.
- Hashes: sha256 `d95f911e9f7c9ec68b1dfe9271995b96f14158c32eeee2f78eee9f095359f7e4`,
  md5 `5ed7c5173298709ca0699b90ea7e2a73`.
- Six tiles compared with the 20261022 planet build, by the sha256 of the stored bytes: 3/2/4, 4/4/8,
  5/9/15, 6/18/31, 8/75/126 and 8/83/154. All match.

## Upload

- `rclone copyto world-south.pmtiles r2:forager-maps/world-south.pmtiles --s3-no-check-bucket --s3-upload-cutoff 200M --retries 3 --low-level-retries 20 --timeout 2m`.
- A single PUT. Exit 0, `Copied (new)` at 14:01:27Z (07:01:27 PDT), at about 2.2 MiB/s.
- No object existed at that key before.

## Verification

- `rclone lsl`: 99514676 bytes, the same as local.
- `rclone hashsum md5`: `5ed7c5173298709ca0699b90ea7e2a73`, equal to local. Because it was a single
  PUT, this is the md5 R2 stored.
- The whole object streamed back with `rclone cat | sha256sum`: `d95f911e...59f7e4`, equal to local.
  So the R2 copy is byte-identical, and every tile in it is too.
- Three 16 KiB ranges (offsets 0, 49757338 and 99498292) match local.
- `list-multipart-uploads` returned `{"forager-maps": []}`.
- `us.pmtiles` is untouched: 34141705380 bytes, 2026-10-21 12:54:52.

## Check tiles sent for the Worker dispatch

Each is non-empty in world-south and absent from us.pmtiles, so serving it requires the fallback.
Sizes are stored (gzip) bytes, each followed by the sha256 of those bytes.

| place | tile | bytes | sha256 |
|---|---|---|---|
| Bogotá | 8/75/124 | 76230 | d9db4c8aa932e6ac2d1d023264863783644e34f5effc622cf2ccea64122e6914 |
| Guatemala City | 8/63/117 | 46167 | d411640926a6aa7a29a15b3fe1adc7ea9704cc9d0fd9ad69845edc1084a7d66d |
| Lima | 6/18/34 | 21387 | de3920cfefc618f3b583127f71bcd81b6f19c20b1591c1881ac49d49d7dcdce0 |
| South America | 3/2/4 | 71783 | bc7c700dd7eabb883c768fd390d241a6dcf5fd774e471f2da5572022429021e9 |

## Not done

- **Worker change:** Hazel writes it in the Forager repo, and the owner deploys it by hand. Until then
  nothing serves world-south, and the grey band remains.
- **Known caveats**, from the estimate:
  - the planet tiles carry roads and labels for Central and South America, while us.pmtiles has the
    land north of the line as plain fill, so a seam will show at the line;
  - tiles south of the line stay 204 above z8;
  - cached 204s can persist for up to a day after the deploy.
- **R2 storage** rises by about 0.1 GB, from about 34.1 GB.
- **Local copy:** `/home/bwann83/world-south/world-south.pmtiles` is kept for now. Deleting it is the
  owner's call.

## Local copy deleted (supersedes "kept for now" above)

The owner, 2026-10-22, verbatim: "Delete it." The planner deleted
`/home/bwann83/world-south/world-south.pmtiles` (99,514,676 bytes) at about 14:20Z (07:20 PDT). The
only copy is now `r2:forager-maps/world-south.pmtiles`. A new copy can be extracted again, but only
while Protomaps keeps the 20261022 build online. The small `extract.log` and `upload.log` stay in
`/home/bwann83/world-south/`.

Rowan confirmed receipt of the key, header and check tiles, as the owner relayed it: "Rowan got your
message".
