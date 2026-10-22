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
