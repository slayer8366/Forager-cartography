# Trail Map sprite v5: rebuilt on the Pi and uploaded to R2

Written by the planner session `forager-cartography-7b`, 2026-10-22. Times are PDT.

## Go

- **Relayed by Rowan:** the owner said, in Rowan's window, "Yes: Aspen uploads icons, I deploy
  after your sign-in". The build is Forager PR #379, merged into `pre-main` at `8b6f3572f`
  (RECORD -1561).
- **Confirmed in the planner's session:** "Yes, rebuild and upload".
- **Then, about the rebuild,** after the owner asked "What's being rebuilt?" and was told it was the
  four icon-sheet files, not the map: "Go ahead and rebuild on the Pi".

## Independent rebuild

Done in scratch, `/tmp/claude-1000/.../scratchpad/v5build/` (lost on reboot). The Forager clone was
not modified.

1. `git archive 8b6f3572f map-style`, extracted to scratch.
2. `fetch-assets.sh` from that commit:
   - Protomaps basemaps-assets `028c18f7`: sha256 check OK.
   - Forager-cartography `236957d3`, the archive of this repo: sha256 check OK.
   - The 16 cut-outs checked against `sprite-v5-items.sha256`: all OK.
3. `npm ci --ignore-scripts`, run with Node v22.23.3 from `/opt/forager-build/node-v22.23.3-linux-arm64/`.
   It added 27 packages to scratch only; nothing was installed system-wide.
4. `node tools/build-sprite-v5.mjs`:
   - "light: 256x179, 53 v4 icons unchanged + 8 new = 61";
   - "light@2x: 512x358, 53 v4 icons unchanged + 8 new = 61".

The resulting sha256 are byte-identical to the sums Rowan sent:

| File | sha256 | Bytes |
|---|---|---|
| `light.json` | `5d4f7869f8826454411d5fe02d9746b8cb46b0dfb4ccb634f6ad79c0729173e4` | 6,361 |
| `light.png` | `6a1ddbf336980f4506d0f006072a22cb37ba966feda63fc94d1319731d458622` | 36,968 |
| `light@2x.json` | `073f4064c08a35008afbdb2a0b8c19e1962be4906b905890e35f6e30fca2db9b` | 6,395 |
| `light@2x.png` | `215987d8e70482f03350af734f347704d80a8c5dd553998af8b87b32414fc838` | 66,535 |

## Before upload

- **The Worker** (`server/pmtiles-worker/src/index.ts` at `8b6f3572f`):
  - line 393 reads `SPRITE_PATH = /^\/sprites\/(v4|v5)\/(light(?:@2x)?)\.(json|png)$/`;
  - line 407 maps it to the key `sprites/<v>/<name>.<ext>` and sets the content type itself:
    `image/png` or `application/json`.
- **The v4 objects** carry `image/png` and `application/json` (`rclone lsjson --metadata`).
- **`r2:forager-maps/sprites/v5/`** was empty.

## Upload, 17:56:51 to 17:56:54

The four files went up with `rclone copyto` to `r2:forager-maps/sprites/v5/<file>`: a single PUT
each, with `--header-upload "Content-Type: ..."` (`application/json` for the JSON, `image/png` for
the PNGs). Each logged "Copied (new)".

## Verification

- **Read back:** each object was read back with `rclone cat | sha256sum`, and all four equal the table
  above.
- **On R2:** `lsjson` shows the sizes above and the MIME types `application/json` and `image/png`.
- **v4 is untouched:** `sprites/v4/` still lists its four files.

## Not done

- **The Worker redeploy:** that's the owner's, by hand, after Rowan signs in. Until then nothing reads
  `sprites/v5`.
- **The Trail Map style change** that points at v5 is part of that deploy.
