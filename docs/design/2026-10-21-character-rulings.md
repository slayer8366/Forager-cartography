# Map character: the owner's round-three rulings and the day design they define

Written by the planner session `forager-cartography-7b` on 2026-10-22, about 14:50 PDT, after the
fact. The owner asked for it: "Yes, record it (Recommended)".

**Why now:** the sage-03 report was delivered only as a message to an earlier planner window and was
never filed. Sage-04 confirmed it is on no branch. The owner's rulings were quoted verbatim in the
sage-04 brief (`/tmp/sage04-brief.md`, scratch, and lost on reboot), and the day design exists only
in Sage's scratch code. This record files both.

## Sources

| Source | Status |
|---|---|
| The phase-1 proposal: Forager `origin/pi-build`, `docs/audits/2026-10-21-sage-02-map-character.md`, "Questions for the owner" (lines 166-177) | Committed. Its 1-9 are the topics the owner's 1-9 answer. |
| The owner's words: `/tmp/sage04-brief.md`, lines 6-16 | Scratch, quoted in full below |
| The day design: `/tmp/sage03-scratch/character.mjs` and `make-sprite.py`, and `/tmp/sage04-scratch/sage04-generate.mjs`, the generator with the owner's choices applied (`REC` and the stream widths) | Scratch. The values below are copied from these, and the copies are filed under `assets/sprite-drafts/2026-10-22/source/`. |
| Renders: `/tmp/sage03-scratch/shots/`, `/tmp/sage04-scratch/shots/` | Scratch, off GitHub (they show place names) |

## The owner's rulings, verbatim

Given 2026-10-21 about 10:30 pm PDT, in Aspen's window:

- "1 A. Irregular glyphs are much nicer. Slightly dimmer trees for night maps, but not too dim."
- "2 Option A. Water is a bit too light for the night theme, but that's the right idea. Not too dark or it blends in with the map."
- "3 Option A"
- "4 Option A. Yes"
- "5 Option A"
- "6 Option A"
- "7 Option A"
- "8 Option A"
- "9 next, design the hillshade and contours for a topo map"

## What each ruling decides: the day design

Values are read from the scratch code named above. Night values are in
`docs/design/2026-10-22-night-colours-rulings.md`.

1. **Tree glyphs on forest and wood.**
   - A fill-pattern layer `landuse_forest_glyphs`, minzoom 12, filter `kind in (forest, wood)`.
   - Pattern `tree_dark_irregular`: a 64 px cell holding five conifers, in `#3e7a3a` by day.
   - At night it is `#5d804f`. This was ruled 2026-10-22 and supersedes the first "slightly dimmer"
     wording.
2. **Streams.**
   - `water_stream` from z13. Line width 0.6 px at z13, 1 px at z14, 1.5 px at z15 and 2.5 px at z18.
   - The day colour is `#3fa0c8` (sage-03's deeper line blue).
   - The label zoom equals the line's.
   - Night is `#163f4b`, the same as the water fill (2026-10-22).
3. **Area names, option (a).**
   - A symbol layer `pois_area_names`, minzoom 8, in Noto Sans Italic.
   - Text size 12 at z8, 13.5 at z12 and 15 at z15. Letter spacing 0.08, max width 7.
   - Text colour `#262626` (near-black, "areaNames: black"), with a white halo 1.75 wide.
   - Shown:
     - parks, wildernesses and protected areas (`nature_reserve`, `national_park`,
       `protected_area`) from z8, or from their `min_zoom` if higher;
     - forests named "National Forest", "State Forest", "National Monument", "National Grassland"
       or "Provincial Park" from z8;
     - other forests and parks from z11.
4. **Peak heights, (a) feet, plus (e) huts, shelters and saddles.**
   - A peak with `elevation` shows its name, then the height in feet in a 0.85-scale line (metres
     × 3.28084, rounded).
   - `saddle`, `shelter`, `alpine_hut` and `wilderness_hut` join the outdoor POI list.
5. **Wetland, (a) fill and tufts.**
   - `wetland` joins the `landuse_park` fill in `#c5e3d6` by day and `#2a4f47` at night.
   - A tufts pattern layer, `landuse_wetland_tufts`, from z10, pattern `tufts` in `#3fa0c8`.
   - Scrub dots are not included: they were "recommended not yet" in sage-02.
6. **Six icons, (a).**
   - New sprite icons for trailhead, parking, camp_site, picnic_site, viewpoint and ranger_station,
     shown from z12. They are no longer drawn as dots.
   - The trailhead and viewpoint were then redrawn in sage-04. The owner ruled the redraws on
     2026-10-22: "Rock night color and trailhead/viewpoint icons are good". The ruled names are
     `trailhead_b` (a walker) and `viewpoint_c` (binoculars).
7. **Bare rock, (a) yes.** `bare_rock` joins the `landuse_park` fill in `#c9c4bb` by day, and
   `#6e7580` at night (2026-10-22).
8. **Trail names: unresolved.**
   - sage-02's default was "only if phase 2 shows them lost; default is no change".
   - The owner said "8 Option A", but what (a) meant in the lost sage-03 report can't be read now.
   - Sage-04 kept the base path-label settings.
   - **Ask the owner before dispatching anything for trail labels.**
9. **Hillshade and contours: moved forward.** Ruled in `docs/design/2026-10-22-topo-rulings.md`.

## Status for dispatch

| Item | Status |
|---|---|
| 1-7, day and night | Ruled. Forager `pre-main` has none of these layers yet (Rowan, read: `forager-street.mjs` has no tree-glyph, bare-rock or tufts layer, and draws trailhead and viewpoint as dots in `DOT_KINDS`, line 119). |
| Sprite items | Filed in `assets/sprite-drafts/2026-10-22/` as cut-out PNGs of Sage's own drawings, with no Protomaps art. A shipped sprite v5 means merging them into Forager's sprite build. |
| Night colour of the wetland tufts | Not separately ruled. The night sheet keeps the day `#3fa0c8`. Decide it at dispatch, against the ruled night palette. |
| 8 | Open, as above. |

## Correction, 2026-10-22 about 15:20: the sage-03 report was found

The sage-03 report has been recovered from the earlier planner window's subagent log and filed as
`docs/design/2026-10-21-sage-03-report-recovered.md`. It was delivered 2026-10-21 22:08:59 PDT.
It was asked for by the owner, relayed by Rowan.

Its "Owner's questions, revised (phase-1 order)" define what each "Option A" meant. These
supersede the readings above where they differ:

- **Ruling 8, trail names, is resolved.** Option (a): "Leave the label layer as ruled (−1286, z14)
  and check once on the phone whether Native places more". So there's no style change. The
  follow-up is one phone check of trail-name placement at z14.
  - The other options were (b) `text-max-angle` 90 at z14 and (c) names from z15.
  - The finding behind it: at Forest Park z14 the web engine places no names on winding trails,
    only on straight fire lanes.
- **Ruling 5, wetland:** option (a) "Fill plus tufts, with an app-side night colour `#2a4f47` for
  the fill". This matches the record above.
  - The report's sub-question, (d) tufts from z10 or (e) from z12, was not separately answered.
    The owner answered "5 Option A" without the sub-letter.
  - The renders used (d), z10, so that is what is recorded. Confirm with the owner if it matters.
- **Ruling 1, tree glyph:** option (a), as recorded.
  - Its night sub-question offered (i) the plain inversion or (ii) the dimmer `#81bc74`. The
    owner's "slightly dimmer" was later settled as `#5d804f`.
- **Rulings 2, 3, 4, 6 and 7:** these match the record above. The report's 2(a) gives the stream
  widths z13 0.6, z14 1 and z15 1.5, and the label zoom equal to the line's.
- **Correction to "Night colour of the wetland tufts" above.** The night sheet does not keep the
  day `#3fa0c8`. Its tufts are inverted the app's way, to `#2485ad` (read 2026-10-22 from
  `assets/sprite-drafts/2026-10-22/night/tufts@2x.png`, the most common opaque colour). Whether
  that blue sits with the ruled dark night water `#163f4b` has not been rendered, and the owner has
  not ruled on it.

## Wetland tufts: zoom and night colour, 2026-10-22 about 15:30

The owner, verbatim: "Keep tufts at z10, darker night tufts".

- **Tufts from z10:** the sub-question's (d), as rendered. That settles the recovered report's
  5(d)/(e).
- **Night tufts darker than the inverted `#2485ad`.** The exact colour is not yet chosen.

**Night tufts colour, ruled about 15:35.** The planner offered three candidates, with brightness
and contrast against the night wetland `#2a4f47`:

| Candidate | Luminance | Contrast on the wetland |
|---|---|---|
| `#2485ad` (today's inversion) | 0.202 | 2.18:1 |
| `#1d6a8a` | 0.124 | 1.51:1 |
| `#163f4b` (matching the night water) | 0.042 | 1.25:1 |

The owner chose "Middle step #1d6a8a".

So the night tufts are **`#1d6a8a`**. Not rendered. This is a named night exception for the tufts
pattern image, like the tree glyph's.

The planner's note: `#1d6a8a` is above the ruled water ceiling (luminance 0.050, blue channel 96).
That ceiling was set for water fills and lines; tufts are a pattern on the wetland, not water. The
checker dispatch should exempt the tufts image or give it its own limit.

**Night tufts colour, superseded about 15:45.** The owner sent a phone screenshot of the round-5
Ridgefield render, the approved A3/T3 set, captioned verbatim: "This is what I approved earlier .
Whatever that was".

That render's style uses the sprite `sprite-night-steps/T3`. Its `tufts` image is `#2485ad`, the
plain inversion (read). The planner asked which the owner wanted. The owner chose "Keep #2485ad".

So the night tufts are **`#2485ad`**, the app's plain inversion of the day `#3fa0c8`, as rendered.
- This supersedes the `#1d6a8a` pick above.
- No night exception is needed for the tufts image.
- The checker note above about a tufts limit no longer applies.

**Night tufts, a trial render, about 15:50.** The owner said, verbatim: "Let's try the #1d6a8a and see how it looks". So Sage-08 renders `#1d6a8a` beside `#2485ad`. Brief: `prompts/preserved/2026-10-22-sage-08.md`. The ruling stays `#2485ad` until the owner chooses.

**Sage-08 result.** Renders are in `/tmp/sage08-scratch/shots/` (scratch). The `#2485ad` render is pixel-identical to the approved round-5 Ridgefield render. Contrast on the night wetland: `#2485ad` 2.18:1, `#1d6a8a` 1.51:1. Sage observed that `#1d6a8a` still reads at Ridgefield but recedes into texture in the Everglades z10. Sage recommends keeping `#2485ad`. The owner has not chosen; the ruling stays `#2485ad`.

**Night tufts, final, about 16:00.** Having seen the sage-08 renders, the owner said, verbatim: "Keep #2485ad". The night tufts stay the plain inversion `#2485ad`. This closes the tufts question.
