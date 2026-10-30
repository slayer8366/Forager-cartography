# Street fill-in: the owner's rulings, 2026-10-30

Aspen, 2026-10-30, about 08:40 PDT. Times are PT.

## The ask

The owner, verbatim: "it looks a bit cartoony … some extra coloring could help readability … OSM
seems more detailed at glance level than Trail maps. Can we get the filling in done with our maps
similar to that style OSM uses?" The owner's phone screenshots compared Street v3 with the OSM layer
at about z9 and z6 around Canby.

## What the tiles already hold (read 08:00, live archive `usca-20261027T221400Z`)

- **Landuse kinds** in 12 sample tiles at z9 and z11 (Portland, Canby, Salem, Rainier, Boise):
  - residential 5,175; farmland 2,528; industrial 688; park 338; commercial 322;
  - also railway, recreation_ground, garden, pitch and dog_park.
  - There is no orchard, vineyard or retail.
- **Roads:** major_road carries `kind_detail` (trunk, primary, secondary, tertiary) from z9. Minor roads
  start at z12. Rail starts at z11.
- **Street v3** (Worker `style/street-v3.json`, sha256 prefix `0dd89cfee27edbb1`) draws none of
  residential, farmland, commercial, railway or park. It draws every major road in one amber, about
  0.8 px wide at z9.

## The draft (style only)

The draft is `docs/design/2026-10-30-fill-in-files/mkdraft.py`, applied to street-v3. The renders are
on the owner's private page (https://claude.ai/artifact/KjM74XJWvM9nBRHx6SwCAq). They were made with
GL JS on the Pi. They show place names, so they are not in this repo.

- **`landuse_settled`,** after `landcover`:
  - residential `#d5d1cb`, commercial `#e3cfca`, railway `#d6d1d4`, farmland `#e8eacd`;
  - opacity 0.6 at z6, 1 by z9.
- **`landuse_parks_fill`:** park, recreation_ground, garden, dog_park and pitch, in `#cde5bf`.
- **`roads_major` and `roads_bridges_major`:**
  - colour by `kind_detail`: trunk `#f2bf72`, primary `#f5d28c`, secondary `#f8e3ae`, tertiary
    `#ffffff`;
  - width 0 at z6, 0.8 at z8, 1.3 at z10, 1.9 at z12, 3 at z15 and 13 at z18;
  - the casings' gap matches.
- **Casings:** tertiary `#a39b8d`, the others keep `#b4924c`. The early casing is 0.6 px at z8.5 and
  1 px at z12.
- **`roads_minor`:** 0.3 at z11 and 0.7 at z12. Its casing is 0.6 px from z12.
- **`roads_rail`:** `#8e979a`, opacity 0.85.

## Rulings, verbatim

"Go with the draft, white tertiary, skip the tile change. I like the faint hillshade idea"

1. **The fill-in:** adopt the draft as rendered.
2. **Tertiary roads:** white with the grey casing, as drafted.
3. **No tile-build change.** Minor roads at z10-11 stay out, and the Pi build is untouched.
4. **A faint hillshade on Street.** This reopens topo ruling 1 (2026-10-22), "Street stays flat".
   - **Data:** Street would read the same relief archive that Topo is planned to use: 3DEP 1″ and
     MRDEM, raster-dem to z12 (topo rulings 5 and 6).
   - **Strength:** fainter than Topo's 0.35 to 0.22, with values and renders proposed for a ruling.
   - **Timing:** the relief archive isn't built. It waits on the topo plan's steps after Sunday's
     11-01 build: the GDAL install and the two-square measurement, each with its own go. **So the
     hillshade follows the fill-in. It does not ship with it.**

## Still to do before the fill-in ships

- **Night colours** for the five new fills and the road classes, in the style of the 10-22 night
  rulings. They go to the owner for a ruling.
- **MapLibre Native check** on the S22, by day and by night, at z9, z11 and z13.
- **Coder work in Forager:** in `overrides/forager-street.mjs` (or a new override), generate the next
  Street style version. The app reads `style/street-v3.json` by URL, so publishing it on the Worker
  needs the owner's go.

Nothing is dispatched, published or installed yet.
