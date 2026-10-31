# Sprite v6 pattern art behind the 2026-10-31 rulings

Sage's production art (brief sage-10b) for the three patterns sprite v6 adds to v5: orchards, plant nurseries
and vineyards in Street v4. The owner ruled Sage's sage-10 design, "Fill + pattern per kind (Recommended)" with
"Standard night (Recommended)", and "New icon set v6 (Recommended)" for where the patterns go
(`docs/design/2026-10-30-fill-in-rulings.md`, last section).

## What's here

- **day/:** each pattern at 1x (`name.png`) and 2x (`name@2x.png`). Ink `#8ea65c` on transparent, straight alpha
  (every pixel carries the ink's RGB; only alpha varies). No shape touches a cell edge, so each cell repeats
  seamlessly.
- **source/make-patterns.py:** the script that drew them, at 8x and box-filtered down to each scale.
- **SHA256SUMS:** the six files' sums. Forager's `map-style/sprite-v6-items.sha256` holds the same lines, and
  `fetch-assets.sh` checks the extracted files against those.

There's no night/ folder. Night is the app's plain inversion of the day image (ink `#829a50`), as ruled.

## Items

| Item | Cell (1x) | Shapes |
|---|---|---|
| `orchard_dots` | 24 px | round dots r 2.4 on an offset grid |
| `vineyard_rows` | 16 px | bars 1 x 5 px in rows (1 px, not 1.2, so they're crisp at 1x) |
| `nursery_dots` | 12 px | dots r 1.2 on an offset grid |

`nursery_dots@2x.png` is byte-identical to `orchard_dots.png`: the same geometry (r 2.4 on a 24 px cell), not a
copy error. Both names are kept.

## Licence

These drawings are this project's own work and fall under this repository's licence (GPLv3, `LICENSE`). No
third-party art is included.
