# Buildings with an outline, and the night tree glyphs at full zoom

Aspen (cartography planner), 2026-10-27, for Rowan (app planner). Times are PT.

## Source

The owner, from the S22 at about 10:01-10:05 on 2026-10-27, with five screenshots (Seaside area,
10T ER 28696 19256):

> "The buildings and houses are soft against the background, and the forest also overlaps them. Can
> we have a border around the buildings and houses to separate them from the rest of the map?"
>
> "Also, in night mode, the tree glyphs disappear when all the way zoomed in, but reappear when full
> zoom is broken."

The owner said "Yes please" to: Aspen writes the buildings spec, and both items go to Rowan.

Marks: **read** (a file at a commit, or a command), **computed**, **inferred**.

## 1. Buildings: opaque, with an outline (a spec)

### What it does today (read, Forager `origin/pre-main`, `map-style/forager-street-v3.json`)

- Layer 32, `buildings`: `fill` on source-layer `buildings`, filter `kind in building, building_part`.
  Paint is `fill-color #cccccc`, **`fill-opacity 0.5`**, with no minzoom.
- **There is no outline layer.**
- Layer 4, `landuse_forest_glyphs` (`fill-pattern tree_dark_irregular`, minzoom 12), and layer 3,
  `landuse_park` (forest `#a9d39b`), draw **below** it. At 0.5 opacity they show through every
  building: the "forest overlaps them" in the screenshots.
- No Forager override touches buildings (`git grep building` in `map-style/overrides/*.mjs` and
  `generate-street.mjs`: no hits). They come from the Protomaps base as generated.
- **Night:** the app's V1 transform (`NightColour.kt`, `nightColorOf`:
  `c + 255 − 2·mean(r,g,b)` per channel) gives `#cccccc` → **`#333333`** (computed), still at 0.5,
  over night forest `#446835` (`forager:night-fills`).

### Prior art (read: openstreetmap-carto `style/buildings.mss`, master, 2026-10-27)

```
@building-fill: #d9d0c9;
@building-line: darken(@building-fill, 15%);
@building-low-zoom: darken(@building-fill, 4%);
#buildings { [zoom >= 14] { polygon-fill: @building-low-zoom;
  [zoom >= 15] { polygon-fill: @building-fill; line-color: @building-line; line-width: .75; } } }
```

- Buildings are opaque (Carto sets no polygon-opacity).
- They're a shade darker at z14, and get a 0.75 px outline 15 % darker than the fill from z15.

### The spec: copy Carto's structure onto our grey

| | Today | Proposed | Night by the existing V1 rule (computed) |
|---|---|---|---|
| `buildings` fill, z14 | `#cccccc`, 0.5 | `#c2c2c2` (Carto's darken 4 %), **opacity 1** | `#3d3d3d` |
| `buildings` fill, z ≥ 15 | `#cccccc`, 0.5 | `#cccccc`, **opacity 1** | `#333333` |
| **new** `buildings_outline` line, z ≥ 15 | none | `#a6a6a6` (darken 15 % of `#cccccc`), **`line-width 0.75`** | `#595959` |

- **The new layer goes directly above `buildings`,** same source-layer and filter. As a line it
  follows the building edges; MapLibre draws a fill polygon's outline as a line layer.
- **Colours:**
  - The grey stays: it's our base's, and the owner asked for a border, not a new colour.
  - **Alternative, not recommended unprompted:** Carto's own warm `#d9d0c9` with outline `#b9a99c`
    (computed).
- **Night:**
  - No night exception is proposed. The V1 rule inverts lightness, so the outline comes out lighter
    than the fill: `#595959` round `#333333`, on `#446835` forest. That still separates the
    building from the ground.
  - It is **not** pushed over the web-UI 2.5:1 or 3:1 floors; per the owner (10-22), night colours
    follow mapping practice, not those floors.
  - If the owner finds the night outline weak on the phone, the fix is a night exception copied from
    an established OSM night style, not a contrast bump.
- **Zoom range:** from z14 (Carto's start; Protomaps carries buildings from about z14 there,
  inferred) to the app's max of 18 (`Basemap.kt:141`).
- **Why this answers both complaints:**
  - The opaque fill hides the forest glyphs under buildings.
  - The outline separates the building from the ground.

### For the coder (Forager map-style)

- Put it in the generator (`generate-street.mjs` with an override, as for the other Forager
  changes), not by hand in the JSON. Then regenerate `forager-street-v3.json`.
- Run `tools/check-style.mjs`, `check-street-night.mjs` and `diff-style.mjs`. The app's style tests
  (`StreetStyleTest`) may count layers, so expect to update the count by one, with the new layer named.
- The diff should show exactly:
  - `buildings`: opacity 0.5 → 1, plus a z14→15 fill step;
  - one new `buildings_outline` layer.
- **Device check (owner's S22), day and night, at the screenshots' place (10T ER 28696 19256) at
  z15, z17 and z18.** Pass: each building has a visible edge, and no tree glyph shows inside it.
  The owner's eye decides; no ratio gate.

## 2. Night: tree glyphs gone at full zoom (a bug report, not a fix)

### Observed (the owner's screenshots, 10-27)

| Screenshot | Mode | Glyphs |
|---|---|---|
| 1-3, 10:01-10:02 | day | present, including at full zoom (screenshot 3, the "14900" building) |
| 4, 10:03 | night, the same place, full zoom | **none**; plain night green |
| 5, 10:05 | night, slightly zoomed out (10T ER 28691 19251) | present (dim) |

### What the style says (read, v3 at `origin/pre-main`)

- `landuse_forest_glyphs` has `minzoom 12` and **no maxzoom**. The source is `protomaps` (TileJSON
  `us.json`, z15 data; MapLibre overzooms above it).
- The only night rule naming its image is `forager:night-patterns`:
  `{"tree_dark_irregular": "#5d804f"}`. The app paints that image one colour at night.
- `forager:night-bands` and `forager:night-layers` don't mention the forest glyph layer.

So **the style has no zoom where the glyphs stop.** Day shows them at z18, which points at the app's
night path. There, the night pattern is a bitmap the app adds itself (`NightImageSwitch.kt` /
`NightImageApply.kt` `addImages`, then the layer's `fill-pattern` switched to the night image's
name), not a sprite image.

### Hypotheses for the coder to test (inferred; none confirmed)

1. **MapLibre's cross-fade of `fill-pattern` at the integer max zoom.** Pattern properties are
   evaluated cross-faded between z and z+1. At the camera's max zoom (18), the z+1 side may resolve
   to a missing or unregistered image for the runtime-added night bitmap. The sprite's image works.
2. **The runtime bitmap's pixel ratio or size,** as added by `style.addImages`, behaves differently
   from the sprite's @2x image at that zoom.
3. **Something re-applies the night switch on a zoom change** and drops the image at the cap.

### Asked of the coder: reproduce first, then root-cause, then fix

- On the S22, night on, at 10T ER 28696 19256: zoom to the cap (glyphs gone?), then pinch out
  slightly (back?). Note the exact camera zoom of each, from a debug log line.
- Same steps in day, as the control.
- Log what `fill-pattern` reads on `landuse_forest_glyphs` at each, and whether the night image is
  present (`style.getImage(name)`).
- A fix only once the cause is shown, with a test or device evidence that fails before it and passes
  after.

## Not touched

- Nothing on the Pi.
- Sunday's 11-01 run (route squares, names, heights) doesn't involve the style.

The owner's five screenshots are in `2026-10-27-buildings-files/` (1-3 day, 4 night at full zoom, 5 night slightly zoomed out).
