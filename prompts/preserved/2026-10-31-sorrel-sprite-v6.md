# Review dispatch 2026-10-31-sorrel-v6: sprite v6 with the orchard, vineyard and nursery patterns

From Aspen to Sorrel Tally. Written 2026-10-31 at about 12:10 PDT. There's no deadline. Nothing is
uploaded, deployed or merged until the owner gives a go after your verdict.

## The go and the background

- **The owner:** "New icon set v6 (Recommended)", then "Sorrel reviews first (Recommended)".
- **The spec:** `docs/design/2026-10-30-fill-in-rulings.md`, the last two sections (Sage's sage-10
  design as ruled), and `prompts/preserved/2026-10-31-coder-07-orchard-style.md`.

## Baseline

- **The art:** Forager-cartography `2bdd3342`, merged into main today. Six PNGs, SHA256SUMS and
  `make-patterns.py`. `nursery_dots@2x` is byte-identical to `orchard_dots` on purpose.
- **The style and the app:** Forager `street-v4-sprite-v6` at `b1a373f45`, on `street-v4`
  `11c31a9e0`. Full CI is green (41229557604).
- **The Worker:** `worker-sprite-v6` at `220094639` (41228391862).
- **The selector revert:** throwaway `street-v4-revert-sprite-choice` (`eed189bd1`, run 41229594666).
- **The v6 sums to upload:** `light.json c1f9b912…`, `light.png 220679a6…`, `light@2x.json 64ad928a…`
  and `light@2x.png 428573d1…`, as `NightSpriteTest` pins them.

## Questions

1. **v6 = v5 plus three.** Does every v5 entry keep its index entry and pixels? Are sprite v5's four
   files and `forager-street-v3.json` (plus the Worker copy) byte-identical?
2. **The pattern layer.** Do the place, minzoom 13, filter and `fill-pattern` match the spec? Is the
   "" fallback truly unreachable, and harmless if it were reached?
3. **The app.** Does `nightSpriteAssetDirFor` pick v6 only for `/sprites/v6/light`, and v5 for every
   committed style? Is the cache keyed so v5 and v6 sheets can't mix? Is `night-sprite/v6` exactly
   v5 plus the three, inverted to `#829a50`?
4. **The Worker.** Does it allow only v4, v5 and v6? Is the cache unchanged? Does it make no change to
   v4 or v5?
5. **The order.** Confirm the order is the R2 upload, then the Worker deploy, then the merge into
   `street-v4`, and what a phone draws at each step. Can an offline region of v3 or v4 ever end up
   with a mismatched sprite?
6. **The pin.** Does `fetch-assets.sh` fail closed if the archive or any sum differs?
7. Run one revert check of your own.

## Bounds and verdict

- Read-only. No R2 or Worker calls except read-only GETs, and no deploys.
- Write the review on a new branch `sorrel-sprite-v6`, as
  `docs/reviews/2026-10-31-sorrel-sprite-v6.md`.
- After 01:30 PST, run nothing heavy on the Pi until Sunday's build finishes.
- **The verdict:** blocking / should-fix / notes, ending with "Is sprite v6 ready for the R2 upload,
  Worker deploy and merge, in that order?" Send it to Aspen.
