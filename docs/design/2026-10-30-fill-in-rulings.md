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

## Area borders (about 14:30)

- **The owner, with an S22 screenshot of Oregon City at about z15:** "Things without a border blends
  together, and is hard to see where one ends and another begins until you really look at it. Can we
  have a border around forests, parks, bodies of water, etc.?"
- **Sent to Sage** for options: outlines for each fill type, with colour, width, zooms and night.
  Then the owner picks, and Willow builds it into v4.
- **The owner, with a matching pair (v4 against the OSM layer, same place at z16):** "OSM does this
  faintly". **The aim is faint, OSM-style edges.** Aspen's read of the pair:
  - the golf course has a thin edge a shade darker than its fill;
  - industrial is OSM's lilac-pink, not our pale blue, so it parts from the earth by hue;
  - buildings are a warm tan with a darker outline;
  - the parking lot has a thin outline.

## Night tertiary and rail (about 14:45)

- **Sage's options** (renders in `/tmp/sage10-work/strips/nightforest-*`, off GitHub; also on the
  owner's private study page).
- **The owner, in Aspen's window:**
  - Tertiary: "Dark grey #333333 (Recommended)".
  - Rail: "Plain inversion (Recommended)".
- **The spec:**
  - **Tertiary centre at night is `#333333`.** It's a per-class rule on `roads_major` and
    `roads_bridges_major`: day `#ffffff` (tertiary and tertiary_link) → `#333333` at night. The other
    classes still invert, and the tertiary casing stays the inversion `#70685a`. This brings back the
    owner's 09:20 choice, "App rule (Recommended)", for per-class road nights.
  - **Night-checker band for it (Aspen's call):**
    - forest: 1.7 to 2.3:1, and below the night footpath;
    - grass and ground: at most the night footpath's figure.
  - **Rail:** drop `roads_rail` from v4's night-layers, so it inverts to `#636c6f`.
- **Trails** are the strongest line at night on forest, grass and ground with this set. Calculated by
  Sage.

## Borders, industrial and buildings (about 14:55)

- **Sage's options:** the sage-10 borders renders, in `/tmp/sage10-work/strips/borders-*`, off
  GitHub. They're also on the owner's private study page.
- **The owner, in Aspen's window:**
  - "Faint (Recommended)";
  - "No edge at night (Recommended)";
  - "Lilac, like OSM (Recommended)";
  - "Tan, like OSM". **This replaces RECORD -1733's grey buildings.**
- **The spec (Sage's FAINT):**
  - **Layers:** `landuse_edges` (source-layer landuse) and `water_edges` (water polygons), after
    `landuse_pier`.
  - **Width:** linear, 0.5 at z13, 0.75 at z15, 1.0 at z17. Minzoom 13. Residential, commercial and
    railway land start at z14.
  - **Edge colours** (day; night is the plain inversion):

    | Area | Edge |
    |---|---|
    | Forest and wood | `#94b988` |
    | Grass kinds | `#c2cdaa` |
    | Parks | `#b4caa8` |
    | Urban green | `#88b99d` |
    | Wetland | `#adc8bc` |
    | Bare rock | `#b0aba4` |
    | Residential | `#c3bfba` |
    | Commercial | `#d0bdb9` |
    | Railway land | `#c4bfc2` |
    | Farmland | `#ccceb4` |
    | School and similar | `#c9c3bd` |
    | Hospital | `#c9c0bf` |
    | Water | `#71c3ce` (no edge at night; accepted) |
    | Industrial | `#cfc1cc` (it goes with the lilac) |

  - **Industrial fill** `#d1dde1` → `#ebdbe8`.
  - **Buildings** from z14: fill `#d9d0c9`, outline `#c4b6ab`.
  - **To confirm:** Sage recalled the lilac and tan values from OSM Carto's own files. Willow confirms
    them against Carto.
  - **Unchanged:** `landuse_park_outline`.
  - **Not possible from these tiles:** parking-lot outlines, because parking isn't in the landuse
    layer.
- **Willow's check against Carto** (gravitystorm/openstreetmap-carto master `9295745d`):
  - Matches: `@industrial: #ebdbe8` (`landcover.mss:22`) and `@building-fill: #d9d0c9`
    (`buildings.mss:1`).
  - Differs: `@building-line` is `darken(@building-fill, 15%)`, which is `#b9a99c`, not `#c4b6ab`.
  - Carto's `@industrial-line` is `#c6b3c3` (`landcover.mss:23`).
- **The owner, in Aspen's window (about 15:10):**
  - "OSM's #b9a99c (Recommended)";
  - "Keep OSM's steps (Recommended)": tan with Carto's darker step at z14, which is
    `darken(#d9d0c9, 4%)`, and the outline from z15;
  - "Accept the inversion (Recommended)": v4's night buildings are the plain inversion of tan (fill
    `#372e27`). This replaces -1733's night greys for v4 only. v1-v3 are unchanged.
  - "OSM's #c6b3c3 (Recommended)" for the industrial edge.
- **The z14 building step, as darkened by Carto:** `#d1c6bd` inverts to 1.001:1 on night water, which
  fails the 1.05 floor. Willow computed this.
  - **The owner:** "One step darker #ccc0b7 (Recommended)" (night `#493d34`, 1.083). This is the same
    remedy as -1733.
  - **Below z14:** tan `#d9d0c9` at 0.5 opacity.

## Street grid, Sorrel's re-look, night edges (about 21:10)

- **The Oregon pilot** (Willow, about 20:45; renders on the owner's study page; branch
  `street-grid-pilot` at `3877c9558`):
  - streets from z11: +0.40 % on Oregon;
  - streets from z10: +0.68 % on Oregon, about +0.23 GB for US+Canada (inferred);
  - largest tiles well under 500 KB.
- **The owner, in Aspen's window:**
  - "Zoom 10, with Sage styling";
  - "Yes, measure California (Recommended)".
- **The owner, in Willow's window:** "Z10 is good, whichever is the one OSM uses…" and "yes do a test
  measurement".
  - Willow read that Carto draws residential streets from its z12. In the app, OSM's 256 px raster
    shows that from about map zoom 10.5, so z10 is the match.
  - Willow is measuring **New York**, not California. Either covers the dense-city risk.
  - **Installing the street-grid patch in the weekly build needs its own go.**
- **Sorrel's re-look** (Forager `sorrel-street-v4` at `6ea1c9290`): PR #448 at `e9be0bcdd` is mergeable
  as plumbing. No blockers.
  - The new should-fix 3: the night-tertiary band test should read the app's table value, not a
    hard-coded `0x333333`.
  - Note: `pre-main` moved to `1ac67f12b` (PR #451, the Heights credits). No overlap.
- **The owner, on Sorrel's note** that the inverted land edges read firmer at night (forest 3.50:1 at
  night against 1.65:1 by day): "Faint at night too (Recommended)". This goes to Sage for night edge
  colours.
- **Also to Sage:** a minor-road style for z10-z11, by day and night.
- **The owner, with a v4 and OSM pair of inner Portland at about z10.5 (21:15):** "When zoomed out,
  the streets are more noise than signal. OSM fixed this by making their borders faint".
  - **Aspen's read of the pair:**
    - v4 draws every main road with a dark amber casing, and tertiary roads with grey casings, so at
      z10-z11 the network becomes a dense outlined mesh.
    - OSM's roads at that zoom are thin lines with little or no casing, and the small streets are a
      faint grey texture.
  - **Sent to Sage,** folded into the z10-z12 minor-road ask: faint or no road casings at low zoom,
    thinner roads at z9-z12, and OSM Carto's low-zoom road colours where Carto has them.

## Low-zoom roads, night borders, notices route (about 21:45)

- **Sage's sage-11 specs** (renders in `/tmp/sage11-work/strips/`, off GitHub; also on the owner's
  study page; night-edge tables in `/tmp/sage11-work/night-edges.json`).
- **The owner, in Aspen's window:**
  - Low-zoom roads: "A: OSM's treatment (Recommended)".
  - Night borders: "Darker rims (Recommended)".
- **Option A, low-zoom roads:**
  - **Casings:** off below z11. Early casings 0 at 10.9, 0.3 at z11, 0.5 at z12. Late and bridge
    casings as Sage specified.
  - **Major widths by class:** trunk / primary / secondary / tertiary / other at z8 0.9/0.9/0.5/0/0.5,
    z9 1.1/1.1/0.7/0.4/0.7, z10 1.3/1.3/0.9/0.6/0.9, z11 1.6/1.6/1.2/0.9/1.2, z12 1.9/1.9/1.7/1.5/1.7.
    The ruled z15 and z18 values follow.
  - **Motorway widths:** 0.8 at z6, 1.0 at z8, 1.3 at z9, 1.7 at z10, 2.0 at z11, 2.4 at z12, 5 at
    z15, 15 at z18.
  - **Low-zoom colours,** cross-fading 10.5 → 11.5 into the ruled colours:
    - motorway `#e66e89` (Carto's own), with casing `#c24e6b` fading 11.5 → 12.5 into `#dc2a67`;
    - trunk `#eeab4f`, primary `#efc46c`, secondary `#ecd58c`, tertiary `#bdb7ad`, other `#efc46c`.
  - **roads_minor:**
    - width 0.4 at z10, 0.6 at z11, 0.8 at z12, 2 at z15, 11 at z18;
    - colour `#c4beb4` until 11.5, then `#ffffff` by z12;
    - opacity 0.7 at z10, 1 at z11;
    - casing width 0 at 11.5, 0.5 at z12.
  - **Night:**
    - the low-zoom colours invert;
    - `roads_minor` gets `{"#ffffff": "#333333"}` in night-line-colours, with the tertiary band.
- **Darker rims at night:**
  - per-kind night edges for `landuse_edges` in night-line-colours, keyed by the day edge, taken from
    Sage's REC table;
  - recorded, not gated;
  - water edges stay off at night.
- **To check:** Sage reads v4 at `e9be0bcdd` as drawing settled-land edges from z13. Willow's report
  says z14, through an opacity step. Willow confirms which.
- **Sorrel's should-fix 3** is done: `307d3c2ac`, CI 41168327133.
- **coder-04's premise was wrong** (found by Willow). map-build has no upload step, and
  `routing/manifest.json` is staged by hand for each run.
  - **The owner:** "A: commit an upload script (Recommended)".
  - map-build writes `NOTICE` and stages the R2 manifest itself.
  - A tested `upload-routing.sh` sends the squares, names1, `NOTICE`, then the manifest last. Each
    upload still needs the owner's go.

## Street grid into Sunday's run (about 22:20)

- **The New York pilot** (Willow, 22:10): z10 adds 0.94 %. The largest z10 tile is 228,641 B
  (Manhattan and Brooklyn), against the 500 KB limit. US+Canada would grow about 0.23-0.32 GB
  (inferred). Build time shows no measurable change.
- **Settled-land edges** are confirmed to start at z14, through the opacity step. Sage had read the
  layer's minzoom.
- **The owner:** "From Sunday's run (Recommended)". The patch goes on `pi-build` as 0005, then Sorrel
  reviews it. If mergeable, Willow installs it before Sun 11-01 02:20 PST. R2 is a separate go.
  The dispatch is `prompts/preserved/2026-10-30-coder-05-street-grid-install.md`.

## Sorrel on pi-35 (about 22:50)

- **The review:** Forager `sorrel-pi35` at `1924a90dc`. Mergeable for install before Sunday. No
  blockers.
  - The merge into `pi-build` gives exactly the installed `288ce80cf` tree plus 0005.
  - Sorrel's own New Jersey build puts the worst Hudson z10 tile at about 275 KB, under 500 KB.
- **Install go:** the owner's "From Sunday's run (Recommended)" was conditional on this verdict, so
  Willow installs now, folding in Sorrel's should-fix 2 (the README count).
- **Correction to Aspen's option text.** "phones see no change until v4 ships" was not exact.
  - v3's `roads_minor` has no minzoom; its width ramps from 0 at z11 to 0.5 at z12.5.
  - With 0005, v3 phones would draw faint white hairline streets between z11 and z12 (2.85-3.23 % of
    pixels at Oregon City).
  - This only happens after the **R2 upload go**, so it goes to the owner before that go.
- **The owner, told of the correction:** "Accept the hairlines (Recommended)". When the upload go is
  given, v3 phones show faint streets at z11-12 until v4 ships. Sorrel's should-fix 1 is closed by
  that decision. The upload itself is still its own go.
- **Noted by Sorrel:** one pull_request CI run on #448's head (41172037381) is red on an unrelated,
  likely flaky test (AvailabilityScreenCrowdedIconsSettingTest). The dispatched run on the same SHA
  passed. Sorrel's second re-look covers it.

## pi-35 installed (Fri 10-30, 23:10 PDT)

- **The merge:** `a5bcb0780` (`--no-ff`, `pi-35-street-grid` into `pi-build`). It brings `pi-build` up
  to the installed pi-33 and pi-34, plus 0005.
- **Installed:** `COMMIT` is `a5bcb0780`, and `map-build.prev` is `288ce80cf`.
  - The jar sha256 is `8dd2a0f2…6cc5b`. The prior jar was backed up at
    `/opt/forager-build/basemap.prev-20261030/` (`1d892172…`).
  - Aspen read this back at about 23:15: `COMMIT`, prev, the jar sha prefix, 0005 in `pins.env`, the
    timer at Sun 11-01 02:20:42 PST, and the service inactive.
- **The proof:** the installed jar on Oregon. Inner Portland 10/163/366 holds `minor_road` residential
  and unclassified (206,049 B, against 130,403 B without 0005).
- **Rollback:** Willow's 10-30 23:10 report, steps 1-5 (`mv` the prev tree back, restore the jar).
- **Not done:** R2. The upload is the owner's go after Sunday's run.

## Sorrel's second re-look on #448 (about 23:10)

- **The review:** Forager `sorrel-street-v4` at `106de157e`. #448 at `97a26e8c7` is mergeable as
  plumbing once the PR's own pull_request check is green. No blockers.
  - v4 equals every ruled value.
  - v1-v3 and StreetWithTopoOver are unreachable by the new table.
  - Trails are the strongest line at z13 forest, day and night.
- **Should-fix 1:** the pull_request run 41172037381 is red on an unrelated, likely flaky test. Willow
  re-runs the failed job.
- **Should-fix 2:** three of the 13 "darker" night rims are lighter than their fills (school,
  hospital, industrial).
  - **Aspen:** this was stated in Sage's 21:25 spec. Those night fills are too dark to darken by 1.3
    without going near-black, so they take a lighter rim of the same faintness. It's a deliberate
    exception, but it wasn't on the owner's options page, so Aspen told the owner.
