# Dispatch 2026-10-31-coder-07: orchards, nurseries and vineyards in Street v4 (fill, edges, patterns)

From the Pi planner (session forager-cartography-28, "Aspen") to Willow Quadrat. Written 2026-10-31 at
about 09:55 PDT. Report times in Pacific time. Start after coder-06's install.

## The go

The owner ruled Sage's sage-10 design: "Fill + pattern per kind (Recommended)", `#c8dd98`, and
"Standard night (Recommended)". The full spec is the last section of
`docs/design/2026-10-30-fill-in-rulings.md` in this repo. Build exactly what it says. Sage's
scratch art is in `/tmp/sage13-work/pat/` (2x, day and night). It's a reference, not production art.

## The work, in two parts with a stop

1. **Fill and edges on #448** (`street-v4`):
   - the fill layer after `landuse_settled`;
   - the three kinds in `landuse_edges`, with the night rim in `forager:night-line-colours`;
   - a check in `check-street-night.mjs` (or the right checker) that asserts the values and the order,
     plus a revert check;
   - v3 byte-identical, and the usual style checks green.

   These need no sprite, so they can go in now.
2. **Patterns: propose first, then stop.** The three are new sprite items (`orchard_dots`,
   `vineyard_rows`, `nursery_dots`). Before building any sprite, report:
   - whether to add them to v5 or cut a v6;
   - what each choice does to offline regions that already stored v5 by URL, the Worker, the app's
     bundled night sprite (`app/src/main/assets/night-sprite/v5`), and `sprite-v5-items.sha256`;
   - what v4 draws if a pattern image is missing (MapLibre's behaviour with a missing `fill-pattern`
     image).

   I'll take it to the owner. No sprite changes and no Worker deploy until then.

## Bounds

- No R2 and no Worker deploy. Nothing is merged.
- Use a debug APK for the S22 only once part 1 is in, and say so.
- Ask the owner if anything is ambiguous.

## Report

Send it to Aspen: the head, checks, revert check, the APK if built, and the sprite proposal. Mark
every claim observed, read or inferred.
