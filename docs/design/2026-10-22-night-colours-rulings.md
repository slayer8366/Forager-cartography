# Night colours: owner's rulings on the sage-04 renders

Written by the planner session `forager-cartography-7b` on 2026-10-22. Times are PDT.

## Source

Sage-04 (night tweaks, plus topo hillshade and contours) finished at 00:53. It delivered its report
only as a message to the previous planner window, which did not relay it. The planner recovered the
report from that window's subagent log:
`~/.claude/projects/-home-bwann83-forager-cartography--claude-worktrees-bridge-cse-0162t2dBSU2gd8h4ASadqLVE/cc9dd4b1-c104-5090-8f34-ee8d0dc64e70/subagents/agent-a78503c58e094f393.jsonl`.
The renders are in `/tmp/sage04-scratch/shots/` on the Pi. They are scratch, and are kept off GitHub
because they show place names. The owner reviewed them on a private render page that carried
Sage's recommendations.

Sage's night picks, as reported:
- **Tree glyph:** t50 `#8eca86`. The tested range ran from the plain inversion `#9cd898` (t0) to
  `#81bc74` (t100).
- **Water fill:** A `#7db8ea`, with stream line B `#6eace4`. Today both are `#8ec5f0`.
- **Bare rock:** `#6e7580`.
- **Icons:** trailhead walker, viewpoint binoculars.

## Ruling, 2026-10-22 about 07:45

The owner, verbatim:

> "Darker water fill and darker trees please. The very slight was hardly visible. When the water is
> on my phone against the dark maps, it lights up the display which runs against the point of night
> maps"

The planner's reading, which the owner has not confirmed:
- every water-fill and tree step rendered in sage-04 is too light, including the darkest;
- the goal is that the night map doesn't light up the display;
- the sage-03 condition "not too dark or it blends in" still stands.

Not ruled on yet:
- bare rock;
- the icons;
- the eight topo questions.

## Next

Sage-05 renders clearly darker steps for the water fill (with stream lines that move with it) and
for the tree glyph. The brief is `/tmp/sage05-brief.md`, scratch, quoted in full in
`prompts/preserved/2026-10-22-sage-05.md`. The owner's word that started the round: "Darker water
fill and darker trees please".

## Owner's target colours, 2026-10-22 about 09:55

The owner sent two S22 screenshots of the app's night map, captioned verbatim: "Tree glyph colors
and water colors to aim for". The planner sampled colours from the PNGs (1440×3120), taking the most
common colour in each region:

| what | sampled colour | region |
|---|---|---|
| night water fill | `#163f4b` | Willamette River, screenshot 1 |
| tree glyph core | about `#5d804f` (edges blend toward the forest through `#537644`) | screenshot 2 |
| night forest behind the glyphs | `#446835` | screenshot 2 |

Notes:
- These are screenshot samples: targets, not exact specs.
- The glyph in the screenshot is the app's current double-tree pattern, not Sage's irregular cell.
- The forest colour differs slightly from the `#436d35` Sage used.

The targets were passed to Sage-05, which was still running. It is to place its steps around them.

## Sage-05 result, 2026-10-22 10:01

Sage-05 worked from 09:53 to 10:01. It delivered its report as a message. Its tool refused the
report file, so the planner saved a condensed copy at `/tmp/sage05-scratch/REPORT.md` (scratch). The
renders are in `/tmp/sage05-scratch/shots/`, scratch, and kept off GitHub.

**Sage's finding (read from the repository):** the owner's targets are what the app's night map shows
today. The swatch board, `docs/audits/2026-09-27-marker-swatch-board.md` near line 254, and
`MapPaletteTest.kt` near line 177 measure the app's Street Night as forest `#446835`, glyph
`#5C7D4A`, water `#173E48` and ground `#22201C`. The light values in sage-04 (`#8ec5f0`, `#9cd898`)
come from the new pre-main Street design's day colours run through the night formula.

**Recommended:**
- water A3 `#163f4b`, with streams and rivers the same, at about 8% of `#8ec5f0`'s luminance;
- trees T3 `#5d804f`, the last step that reads as separate marks (T4 `#57784a` reads as texture).

**Costs, as Sage reports them:**
- streams nearly vanish on dark meadows (1.08:1) and are faint on bare ground (1.41:1);
- water and wetland are 1.25:1 apart, and the wetland's tufts carry the distinction;
- every step is below the night checker's 2.5:1 floor, so the checker would need an exception.

The owner has not ruled on sage-05 yet. The renders are on the owner's private review page, round 5
section.

## The contrast floor, and the owner's direction, 2026-10-22 about 10:20

The owner asked why the floor is 2.5. The planner's read of Forager `origin/pre-main`:
- `map-style/tools/check-street-night.mjs` line 8 reads: "The thresholds are this check's own
  operating limits, not a standard for maps". Its base is 3:1, the web-accessibility figure for
  non-text UI.
- 2.5:1 was set in -1345 (commit `5b270ac4b`) to fit road colours the owner had accepted (2.65 and
  2.95 on the night forest).
- Night water is held to 3:1 by `NightWaterTest.kt`.
- Informal paths already have a band of 1.9 to 2.3 in place of the floor (-1480).

The owner, verbatim:
- "Blue light is hard to deal with because of how it lights up an area when it displays. The darker
  blues are the only way to deal with that. Lower contrast threshold is probably the answer. Why is
  it 2.5?"
- "I think 2.5 is the same threshold I ran into issues last time. Mapping is a different beast than
  web UI, so this likely needs a rerun of the design research"

Asked whether to send Sage to redo the research from mapping sources, the owner answered, verbatim:
"Option 1, but look at OSM night maps and see their color scheme, then just copy it.b"

Option 1 was: brief Sage; research and a proposal only; the water and tree picks wait for it. The
trailing ".b" is read as a typo.

Next: Sage-06, a survey of OSM-based night styles and a proposal to adopt one scheme. The brief is
in `prompts/preserved/2026-10-22-sage-06.md`.

The owner added, verbatim, at about 10:30: "Unless it's not open to copy, but if it is then let's
just use it, because it's already nice and researched."

So if Sage-06's recommended scheme is open to copy under its licence, the owner adopts it as is.
Forager-specific layers it lacks get the minimum mapping. This was passed to Sage-06 while it ran.

The owner added, verbatim, at about 10:35: "Find the option that we don't need to give credit.
That's not really something to credit over."

So the scheme should need no attribution (CC0 or public domain). One lead was passed to Sage-06 to
check, not assumed: the built archive's manifest records "Protomaps basemap design CC0".

## Sage-06 result, 2026-10-22 10:26

Sage-06 surveyed seven OSM-based night styles, reading the colour values from source. The renders
are in `/tmp/sage06-scratch/shots/` (scratch, off GitHub) and the tables in
`/tmp/sage06-scratch/colours6.out`. The planner holds the report in its session transcript.

**Licence buckets** (Sage, read):

| Bucket | Styles |
|---|---|
| No credit, CC0 | Protomaps dark. VersaTiles Eclipse is stated CC0 but generated from OSM Bright (CC-BY), so its status is uncertain. |
| Credit | CARTO, OpenMapTiles and OpenFreeMap Dark Matter (CC-BY 4.0); Organic Maps (Apache-2.0, plus a visible credit asked for) |
| Not usable | OsmAnd (GPLv3, artwork CC-BY-NC-ND) |
| No values or licence found, dropped | MapTiler, Thunderforest |

**Planner's verification:** the planner re-read the licence itself at about 10:40. `LICENSE.md`
under "Visual Design", https://raw.githubusercontent.com/protomaps/basemaps/main/LICENSE.md: "The
visual design of the Protomaps basemap styles was created by Geraldine Sarmiento for Protomaps LLC
and released under a Creative Commons 0 (CC0) license." The README, lines 64 and 69, says "Map
design is CC0" and that attribution is requested "but you are not required to do so". The OSM data
credit is still required, and Forager already shows it.

**Recommendation:** copy Protomaps dark (`namedFlavor("dark")`, `@protomaps/basemaps` 5.7.2, the same
package Forager builds from). Forager-only layers keep Forager's hues at Protomaps' brightness:

| Layer | Colour |
|---|---|
| tree glyph | `#2e4227` |
| footpaths | `#6a3a2e` |
| tracks | `#554434` |
| hard trails | `#603f39` |
| informal paths | `#4f382c` |
| wetland | `#1c2421` |
| tufts | `#31353f` |
| bare rock | `#262624` |
| park outline | `#2d422c` |

Icons are unchanged.

**Costs, observed:**
- forest, meadow and ground are near-identical greys;
- water `#31353f` is greyer than the target `#163f4b` and slightly lighter than the land;
- Protomaps' own path grey `#333333` nearly vanishes, which is why Forager's trail colours are kept.

**Proposed checker rules, derived from Protomaps dark:**
- water at least 1.2:1 on land;
- lines at least 1.2:1, roads and trails at least 1.35:1 on forest;
- night luminance ceilings: fills 0.040, lines 0.065, text 0.42;
- blue-dominant colours: blue channel at most 64, luminance at most 0.040.

The owner has not yet ruled on sage-06's four questions. They are on the review page.

## Another water colour from the owner, 2026-10-22 about 10:35

The owner sent an S22 screenshot of the Topographical night map (the OpenTopoMap raster, inverted),
captioned verbatim: "Another color to consider for water. It's both bright and dark".

Sampled by the planner from the PNG (1440×3088):

| What | Colour | Luminance | Notes |
|---|---|---|---|
| stream lines | `#2a58ff` | 0.147 | 28% of today's Street water `#8ec5f0` |
| ground | `#111111` | 0.0056 | |

Contrast between them: 3.54:1.

The planner's note: the blue is saturated, so it stands out while its luminance stays low. At full
blue channel, though, a large fill in it would put a lot of blue light on screen. The planner
suggested that colour for water lines only, with a deep low-saturation fill for areas. The owner has
not ruled.

The owner asked "Are we getting new proposals to look at?" The planner offered a short round to
render the stream blue, and the owner answered, verbatim: "Yes please". Sage-07 brief:
`prompts/preserved/2026-10-22-sage-07.md`.

## Sage-07 result, 2026-10-22 about 10:49

Sage-07 rendered four variants with water lines (`water_stream`, `water_river`) in `#2a58ff`. The
style has no canal layer. 16 renders, no errors. Renders in `/tmp/sage07-scratch/shots/` (scratch,
off GitHub).

| Variant | Base | Water lines | Water fill |
|---|---|---|---|
| V1 | Protomaps dark | `#2a58ff` | `#31353f` |
| V2 | Protomaps dark | `#2a58ff` | `#163f4b` |
| V2b | Protomaps dark | `#3962d9` (same luminance, less saturated) | `#163f4b` |
| V3 | sage-05 base | `#2a58ff` | `#163f4b` |

**Line contrast:** 2.8 to 3.1:1 on every Protomaps surface. In V3 the line is 1.20:1 on the green
forest.

**Crater Lake z12, mean blue channel with the preview controls masked (observed):**

| Render | Mean blue |
|---|---|
| today's `#8ec5f0` | 169.4 |
| V1 | 52.4 |
| V2 | 60.2 |
| V3 | 62.0 |

**Observed:** the Paradise meadow creeks are strong in V1, V2 and V2b, and faint in V3. On wide
rivers the line shows as a centre stripe.

**Sage recommends V2.** The lake-label halo (`#31353f`) should follow the teal fill, after a check
render. Moving the water off Protomaps' own colours is a departure from adopting Protomaps dark
"as is".

The owner has not ruled. The renders are on the review page, round 7.

## The owner's preference, 2026-10-22 about 10:50

The owner sent three phone screenshots of the review page, all from the round-5 section "The
recommended pair, at phone size". They show Sage-05's A3/T3 renders at Crater Lake z12, Ridgefield
z13, Forest Park z14 and Paradise z14. The owner said, verbatim: "These look the best out of all of
them".

The planner reads this as a preference for the round-5 pair over the Protomaps dark copy (round 6)
and the vivid-line variants (round 7). The round-5 pair is:

| What | Colour |
|---|---|
| water fill, and stream and river lines | `#163f4b` |
| tree glyph | `#5d804f` |
| forest | `#446835` |
| everything else | today's app night formula |

The owner has not yet confirmed what follows from it: whether the copied scheme is dropped, how
streams are drawn, and what replaces the checker floors.

## Rulings, 2026-10-22 about 11:20

Asked in the planner's session, the owner chose, verbatim:

| Question | The owner's answer |
|---|---|
| The scheme | "Yes, drop the copy". Night stays on the app's own palette (green forest), with water `#163f4b` and trees `#5d804f`. Protomaps dark is not used. |
| Streams | "Same as water (Recommended)". Stream and river lines are `#163f4b`, as in the round-5 renders. Meadow creeks stay faint. |
| The checker | "Rules from your colours (Recommended)". The floors and a night brightness ceiling, with a tighter limit for blue, are set so the round-5 colours pass and today's `#8ec5f0` water fails. |

This supersedes the sage-06 adoption of Protomaps dark (the owner's "just use it" was conditional,
and round 5 was then preferred). It also closes sage-07: the vivid stream blue is not used.

### The planner's call: the checker numbers

These are technical. The owner ruled the rule; the numbers are the planner's. They are derived from
Sage-05's figures for the ruled colours, for the coder to confirm against the app's real colours:

1. **Night ceiling for water fills and lines:** relative luminance at most 0.050, and blue channel at
   most 96.
   - The ruled `#163f4b` has L 0.042 and blue 75, so it passes.
   - Today's `#8ec5f0` has L 0.52 and blue 240, so it fails.
2. **Water against land:** at least 1.05:1 on every night land fill. The ruled water's lowest is
   1.08, on night grass/meadow.
3. **Tree glyph against the night forest:** at least 1.35:1.
   - `#5d804f` is 1.42:1, so it passes.
   - Sage-05 observed that the next step down, T4 at 1.28:1, reads as texture.
4. **Every other layer** keeps its current floor, until a later ruling.

Still open: bare rock's night colour, the trailhead and viewpoint icons, and the eight topo
questions.

## Rock and icons, 2026-10-22 about 11:30

The owner, verbatim: "Rock night color and trailhead/viewpoint icons are good".

This is read as accepting Sage-04's recommendations:
- **Bare rock at night:** rock3, cool slate `#6e7580`
  (`/tmp/sage04-scratch/shots/snow-lake-z12-night-rock3.png`).
- **Trailhead:** B, a walker with a pole.
- **Viewpoint:** C, binoculars.
  - The drafts are in the scratch sprite `/tmp/sage04-scratch/sprite/light@2x.png` and its night copy.
  - They have only been judged on the 6× proof sheets. No trailhead or viewpoint fell in a rendered
    map view.

Still open: the eight topo questions.

## Sent to Rowan, 2026-10-22 about 11:40

On the owner's word, "Send Rowan the full set now", the planner sent Rowan (session
`bridge:session_01EYWpbjwcxidzc6rvny9rgK`) the full set: the night colours, the checker rule and its
numbers, rock, icons and topo. The message pointed to this record and to
`docs/design/2026-10-22-topo-rulings.md`. Delivery is accepted by the server, not confirmed read.

## Observed on the phone: night mode doesn't recolour icons or shields, 2026-10-22 about 18:40

The owner sent S22 screenshots of the live Trail Map, by day and by night, at Guy W. Talbot State
Park, captioned verbatim: "See how these icons stay white during the switch? Including the highway
icon".

The planner sampled the PNGs. The icons and shields keep their day pixels at night:

| Image | Day and night |
|---|---|
| picnic_site, viewpoint_c | `#d6f2e3` fill, `#4fa074` ring |
| toilets (v4 base) | `#dcebfa` |
| US 30 shield | `#ffffff` |

The fills, lines and tree glyph did switch.

This doesn't match the design's assumption: the icons are inverted at night, per sage-03 ruling 6 and
the build-sprite-v5.mjs header.

Reported to Rowan for Hazel. Whether road shields should change at night has not been ruled.
