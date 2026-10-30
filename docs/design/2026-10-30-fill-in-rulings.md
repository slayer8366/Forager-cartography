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

## Night and the go for phase 2 (from Sage's sage-09 report, about 10:15)

**The owner, as Sage quoted:**
- ~09:33: "Closer to the OSM style".
- ~09:44: "Undo that last change. Keep it osm-like".
- ~09:46: "Yes, ship it". This was the answer to "OSM-like, with motorways staying amber, and the go
  for phase 2?"
- ~09:55: "You're only allowed to design and style. Coding is for coders" and "Pass the report to
  Aspen who will instruct the coders".

**The ruled v4 night:**

| Feature | Night | Mechanism |
|---|---|---|
| Residential | `#2d2a25` | night-fills, new key |
| Commercial | `#362824` | night-fills, new key |
| Railway land | `#2b2829` | night-fills, new key |
| Farmland | `#2e2a10` | night-fills, new key |
| Parks | `#2c461e` | night-fills, new key |
| Trunk, primary, secondary, tertiary | `#845104`, `#674400`, `#463100`, `#000000` | inversion; no night-layers entry for `roads_major` or `roads_bridges_major` in v4 |
| Tertiary casing | `#70685a` | inversion |
| Other major casings | `#a7853f` | inversion |
| Rail | `#a3acae` | night-layers |
| Motorways | v3's amber `#f0c060` | unchanged |

**Asked in Aspen's window (~10:20):**
- **Ramps and slip roads** at night: "Invert them too (Recommended)". The option read: "Each ramp
  takes its road's OSM-like night colour, so a ramp matches the road it joins." Motorway ramps stay
  amber with the motorways. Sage specifies the values.
- **Coding:** "New coder session (Recommended)". The owner named the new coder Willow (the earlier Willow session is gone). The coder brief is
  `prompts/preserved/2026-10-30-coder-01-street-v4.md`.

## Ramps: Sage's spec and the owner's OK (about 11:00)

- **Sage's finding.** These were read from the tiles and from v4.
  - `roads_major` draws trunk-to-tertiary ramps (`is_link` with kind `major_road`).
  - `roads_link` and `roads_bridges_link` show only motorway ramps.
  - The draft's colour match covered `trunk_link`, but not `primary_link`, `secondary_link` or
    `tertiary_link`. Those fell to v3's amber `#f6d68f`.
- **The owner, in Aspen's window:** "Approve the fix (Recommended)".
  - **Day:** the `line-color` match for `roads_major` and `roads_bridges_major` becomes:
    - `["trunk","trunk_link"]` `#f2bf72`;
    - `["primary","primary_link"]` `#f5d28c`;
    - `["secondary","secondary_link"]` `#f8e3ae`;
    - `["tertiary","tertiary_link"]` `#ffffff`;
    - fallback `#f6d68f`.
  - **Night:** this follows by inversion, with no table change.
- **Night-layers: no change.** `roads_link` and `roads_bridges_link` keep `#e0ad4f`, so motorway
  ramps stay amber. Casings are unchanged.

## PR #448 and the review (about 11:10)

- **Willow's report** came in at about 10:57.
  - PR #448, `street-v4` at `f228f9281` → `pre-main` at `b493cffeb`. Full CI is green (run 41097273828).
  - The S22 debug APK is CI run 41099952632, branch `street-v4-s22-debug` (never merge).
- **The owner, in Aspen's window:**
  - Reviewer: "Sorrel (Recommended)". In Willow's window: "Sorrel can review for now".
  - Willow's three calls: "Accept all three (Recommended)". They are:
    1. the selector also matches `forager-street-v4.json`;
    2. a new branch `street-v4`, with `street-v4-fill-in` superseded;
    3. the throwaway branches are deleted after the S22 check.
- **The review dispatch** is `prompts/preserved/2026-10-30-sorrel-street-v4.md`.
- **Still to come:**
  - the owner's S22 check;
  - Sorrel's verdict;
  - the owner's go to merge.

  The Worker deploy and the app switch, which adds v4 to `STREET_STYLE_URLS`, are each their own go.

## S22 first look, and "the exact same design as OSM" (about 11:20-11:40)

- **The owner, on the S22 with the v4 debug build beside the OSM layer near Portland at about z10:**
  "Better, but when zoomed out the detail is still sparse. Is this the rest of the fix?"
- **Aspen read the live tiles:** there are no minor roads below z12 (inner Portland: z10 and z11 have
  none; z12 has 8).
- **The owner, asked about the tile change:** "I didn't skip it. I asked for the exact same design as
  OSM".
  - **Ruling 3 above ("No tile-build change") is withdrawn.** It was the planner's reading of "skip
    the tile change", and it was offered as a recommendation.
  - **The aim is OSM's glance-level look,** including the street grid.
- **Next:**
  - **Willow:** a measure-only pilot of minor roads from z11 and from z10 on Oregon
    (`prompts/preserved/2026-10-30-coder-02-street-grid-pilot.md`). Nothing goes into the weekly
    build without the owner's go.
  - **Motorways** (`#f0b95c`) read almost the same as trunk (`#f2bf72`). The owner chose "Ask Sage
    for options (Recommended)", aiming for OSM's look. The night amber for motorways stays as ruled
    unless the owner changes it.

## Motorways (about 11:55)

- **Sage's options** (sage-10 renders in `/tmp/sage10-work/strips/`, off GitHub; also on the owner's
  private study page): A, OSM Carto pink; B, brick; C, deep orange.
- **The owner, in Aspen's window:**
  - Day: "A: OSM pink (Recommended)".
  - Night: "Invert like OSM (Recommended)". **This replaces "motorways stay amber".**
- **The spec:**
  - **Centre `#e892a2`:** `roads_highway`, `roads_bridges_highway`, `roads_link`, `roads_bridges_link`.
  - **Casing `#dc2a67`:** `roads_highway_casing_early`, `roads_highway_casing_late`,
    `roads_bridges_highway_casing`, `roads_link_casing`, `roads_bridges_link_casing`.
  - **Tunnels** keep their grey.
  - **Night:** drop `roads_highway`, `roads_bridges_highway`, `roads_link` and `roads_bridges_link`
    from v4's night-layers, so they invert. The centre becomes `#7f2939` and the casing `#e83673`.
  - **Confirm** the two values against OSM Carto's road colour file. Sage quoted them from memory.

## Sorrel's verdict on PR #448 (about 11:50)

- **The review:** Forager `sorrel-street-v4` at `11959e944`,
  `docs/reviews/2026-10-30-sorrel-street-v4.md`.
- **The verdict:** mergeable as plumbing ahead of the switch. No blockers.
  - v4 equals the ruled design to the byte.
  - v1-v3 are unchanged by file and by every app path.
- **Should-fix:**
  1. **For the switch PR:** pass `source.streetUri` for StreetWithTopoOver into the selector, and test
     it.
  2. The style night checker should require a night-fills entry for every fill-in day colour. Today
     it catches only parks; Sorrel's revert of residential passed it.
  3. The rail comment in `forager-fill-in.mjs` is wrong. The value stands.
  4. CI runs no map-style checker. This was already the case before this PR.
- **Design note for the owner:** at night in forest at z13 and above, the black tertiary (3.28:1,
  2.26 px) outranks the night footpath (2.58:1, 1.35 px). The rail is slightly above the footpath.
  This follows from the OSM-like ruling.
- **The owner, on the night-forest catch:** "Sage fixes it (Recommended)". Sage will propose night
  tertiary and rail colours that stay OSM-like but sit under the trails in forest, for the owner to
  pick. Willow adds the pick to PR #448.
