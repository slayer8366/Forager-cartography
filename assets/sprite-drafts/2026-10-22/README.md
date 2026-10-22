# Sprite drafts behind the 2026-10-22 rulings

Published on the owner's word: "Only our new icons (Recommended)". The question offered publishing
only Sage's own new icons and patterns, plus the scripts and a README, with no third-party art.

## What's here

- **day/ and night/:** each item Sage drew, cut out of its draft sheet, at 1x (`name.png`) and 2x
  (`name@2x.png`).
  - day/ is cut from Sage-04's day sheet.
  - night/ is cut from the night sheet carrying the ruled tree colour `#5d804f`, Sage-05 step T3.
- **source/:** the scripts that drew them:
  - `make-sprite.py`, the drawing functions and sheet assembly;
  - `icons-redraw.py`, the trailhead and viewpoint redraws;
  - `night-sprite4.py`, the night copy;
  - `tree-steps5.py`, the night tree steps.
  - Their paths point at the Pi's scratch folders.
  - `make-sprite.py` pastes these items onto Protomaps' basemaps-assets v4 sprite (MIT,
    "Copyright (c) 2017 Mapzen"). That base art is **not** included here.
    `docs/design/2026-10-21-character-rulings.md` has the details.

## Status of each item

| Item | Status |
|---|---|
| `trailhead_b` | ruled trailhead (walker with pole) |
| `viewpoint_c` | ruled viewpoint (binoculars) |
| `tree_dark_irregular` | ruled tree glyph. Pattern, 64 px cell; `#3e7a3a` by day, `#5d804f` at night. |
| `tufts` | ruled wetland tufts. Pattern, 32 px; `#3fa0c8` by day; the night sheet inverts it to `#2485ad`, which has not been ruled against the dark night water. |
| `parking`, `camp_site`, `picnic_site`, `ranger_station` | ruled icons (ruling 6a) |
| `trailhead`, `trailhead_c`, `viewpoint`, `viewpoint_b` | not chosen: the sage-03 drafts and the alternative redraws |
| `tree_dark_dense`, `tree_dark_sparse`, `tree_light_dense`, `tree_light_sparse` | not chosen: superseded by the irregular cell (ruling 1) |
| `scrub_dots` | not ruled ("not yet") |

## Licence

These drawings are this project's own work and fall under this repository's licence (GPLv3,
`LICENSE`). No third-party art is included.

## Checksums

`SHA256SUMS` lists every PNG and script. To check: `sha256sum -c SHA256SUMS`.

## Records

- `docs/design/2026-10-21-character-rulings.md`
- `docs/design/2026-10-22-night-colours-rulings.md`
