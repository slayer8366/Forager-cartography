<!--
Recovered by the planner session forager-cartography-7b on 2026-10-22, about 15:20 PDT, at the
owner's request relayed by Rowan.
Source: the SubagentHandback message in
/home/bwann83/.claude/projects/-home-bwann83-forager-cartography--claude-worktrees-bridge-cse-0162t2dBSU2gd8h4ASadqLVE/cc9dd4b1-c104-5090-8f34-ee8d0dc64e70/subagents/agent-a7ffd82d1f2d3cfa4.jsonl
(a subagent of the earlier planner window cc9dd4b1). The log's timestamp for the message is
2026-10-22T05:08:59.895Z, which is 2026-10-21 22:08:59 PDT. The subagent's first prompt is at
2026-10-22T04:49:30Z.
The text below is the message exactly as delivered (18,024 characters, unedited). It was never
filed before.
-->

# Sage Wayfinder: map character, phase 2, previews on real tiles (brief 2026-10-22-sage-03)

Scratch only. Everything is under `/tmp/sage03-scratch/`; the brief is `/tmp/sage03-brief.md`. Nothing was written to any repository (all three checkouts report clean), nothing committed, pushed or uploaded. The owner's preview servers (pids 272560 and 272561, ports 8081 and 8765) and the rclone process (pid 409903) were not touched and are still running; `~/street-preview-scratch/` has no file newer than the brief (observed, `find -newer`). My two servers (pmtiles serve on 127.0.0.1:8181, http.server on 127.0.0.1:8766) are stopped and no Firefox is left (observed, `ss` and `ps`). Memory: one Firefox at a time under `nice -n 10`, RSS about 530 MB; available memory never went below 5.7 GB (observed, the driver logged `free -m` after each shot). No builds, no installs: `node_modules` is the street-preview worktree's, linked read-only.

Claims are marked **observed** (a named render I looked at, or a tile I decoded by z/x/y), **read** (file:line) or **inferred**. 44 renders were written; I looked at 27 by eye, named below. The others were rendered and are listed at the end but not viewed.

## What I built from

- Style source: `map-style/overrides/forager-street.mjs` at `origin/pre-main` `7101e9096`, blob `e487d9fc` (read; identical blob on `origin/street-cloudflare`, so there is one newest Street-with-trails). Generated through the pinned `@protomaps/basemaps` 5.7.2 and `applyStreetDesign`, then my scratch `character.mjs` on top, each idea switchable. Night styles the app's way (pi-18 `make-styles.mjs` logic: water to `nightWater`, line exceptions, V1 of everything else), plus one scratch exception the app does not have: the wetland fill's night colour.
- Archive: `/srv/forager-build/out-usca/20261017T202051Z-usca-20261021T111429Z/forager-usca.pmtiles` (the resolved `current`), served from my own `pmtiles serve`. Max zoom 15 (observed, `pmtiles show`).
- Sprite: a scratch v5 = the pinned 53-icon light sprite plus 13 drafts (`/tmp/sage03-scratch/sprite/`), night copy by the pi-18 `night-sprite.py` method (`sprite-night/`), and a second night copy with a dimmer tree glyph (`sprite-night-dim/`). Correction to phase 1: the pinned local sprite has 53 icons, not 70 (observed, `assets/sprites/v4/light.json`); 70 was the upstream commit's count.
- Method: Part A exactly, Firefox 142 headless over WebDriver BiDi, 412x800 at devicePixelRatio 2, port 9223, own profile. One failure mode seen and fixed: Chromium not tried.

## Premises corrected by the tiles (new archive)

1. Paths at z13 carry no names, at z14 they do: Forest Park z13/1302/2928 has 16 paths, 0 named; z14/2605/5857 has 14 paths, 13 named, including Wildwood, Maple, Tye, Nature, Chestnut Trails (observed). Same as phase 1.
2. "Mount Rainier National Park" is kind `nature_reserve`, min_zoom 8; "Gifford Pinchot National Forest" is kind `forest`, min_zoom 9; wildernesses are `nature_reserve` min_zoom 9-10 (observed, z8/41/90 and z10/165/360). So phase 1's "forest kind from z11" would have hidden a national forest at z9-10. Revised below.
3. Wetland is dense where it matters: Everglades z10/281/436 has 184 wetland of 194 landuse; Ridgefield z13/1302/2919 has 21 of 51; Paradise z13 has 2 (observed).
4. Bare rock is in the tiles as `bare_rock` only: Snow Lake z12/666/1432 has 11 of 27 landuse, z13/1332/2865 12 of 30 (observed).
5. Peaks carry `elevation` in metres: Alta Vista 1817, Avalanche Mountain 1634, two unnamed peaks at Snow Lake (observed).
6. Street v1 today labels creeks it does not draw: `water_waterway_label` has minzoom 13 and filter river/stream, `water_stream` has minzoom 14 (read, generated `base.json`); Balch Creek is kind `stream` (observed, z13/1302/2929); the render with streams at z14 shows the label "Balch Creek" on no line (observed, `forest-park-z13-day-rec-streams14.png`). That is a thing on the shipped map today that reads as broken.

## What the renders showed, per idea

### 1. Tree glyphs
- Day, dark glyph `#3e7a3a`, one tree per 32 px cell: reads as "forest" at z12-z15 and leaves trails, streams and labels readable (observed, `forest-park-z12-day-rec.png`, `-z13-`, `-z14-`, `-z15-`; `paradise-z14-day-rec.png`). But the cell shows as a lattice of rows, wallpaper-like (observed, all of those).
- An irregular 64 px cell with five trees removes the rows and reads as scattered trees (observed, `forest-park-z14-day-rec-irregular.png`, `-z12-`). **This is my revised recommendation.**
- Two trees per 32 px cell is an even texture but busier (observed, `forest-park-z14-day-rec-dense.png`). The light glyph `#5f9a52` is faint by day (swatch, observed).
- Night: the app's inversion makes the glyph `#9cd898`, brighter at night than by day; the forest reads as a lit field of trees, still as trees (observed, `forest-park-z12-night-rec.png`, `-z14-night-rec.png`, `paradise-z14-night-rec.png`). A dimmer night glyph `#81bc74` is calmer and still reads (observed, `forest-park-z14-night-rec-dim.png`). A dimmer glyph needs an app-side night exception for that image, like the icon rings (inferred); the plain inversion needs only the image name in the inversion list.
- Without glyphs: today's flat green, for comparison (observed, `forest-park-z14-day-rec-noglyph.png`, `forest-park-z14-day-base.png`).

### 2. Wetland fill and tufts
- Fill `#c5e3d6` with blue tufts reads as marsh beside lakes, the river and grass, and does not read as a mis-coloured pond, so no outline is needed (observed, `ridgefield-z13-day-rec.png`, `paradise-z14-day-rec.png`). The fill alone is close to grass in the swatch (observed, `swatch-day.png`); the tufts carry it.
- At z10 the Everglades is a sheet of tufts on a regular lattice; conventional, honest, but dense (observed, `everglades-z10-day-rec.png`).
- Night: the plain inversion `#1b392c` is near the night ground (swatch night, observed). The scratch exception `#2a4f47` with the inverted tufts reads as marsh beside the bright night water (observed, `ridgefield-z12-night-rec.png`, `everglades-z10-night-rec.png`, `paradise-z14-night-rec.png`). A fill-colour night exception is an app change: today's exceptions cover line colours and icon rings only (read, `forager-street.mjs:66-83`, `NIGHT_LAYER_COLOURS`; inferred for the app).

### 3. Area names
- Italic, letter-spaced, near-black with halo. At z8 only "Mount Rainier National Park" shows in the Rainier view, no parcels, no clutter (observed, `rainier-region-z8-day-rec.png`). At z10 the wildernesses join it and the names sit well on the mountain (observed, `rainier-region-z10-day-rec.png`). At Ridgefield and the Everglades the refuge, natural area, wilderness and park names place (observed, `ridgefield-z12-night-rec.png`, `everglades-z10-day-rec.png`).
- Revised filter, rendered: `nature_reserve`, `national_park`, `protected_area` from their tile min_zoom (floor 8); `forest` whose name contains "National Forest", "State Forest", "National Monument", "National Grassland" or "Provincial Park" likewise; other `forest` and `park` from z11. The string test is a style `in` on the name (inferred that Native supports it as GL JS does).
- One duplicate: at Forest Park z12 the italic area name "Forest Park" and the existing locality label "FOREST PARK" both show, in different places (observed, `forest-park-z12-day-rec.png`). A style cannot de-duplicate across layers; it is honest, two different features, but the owner should see it.
- Green `#3e7a3a` text is softer than near-black and still readable day and night (swatch, observed). Near-black is what −1286 ruled.

### 4. Streams
- From z13 at 1 px `#3fa0c8`: creeks are now visible on forest by day (observed everywhere; swatch shows today's 0.5 px `#80deea` barely visible on forest). Night is the app's `#8ec5f0`, fine (observed).
- The cost, seen: Forest Park at z13 and z14 is a dense drainage web of equal weight to the trail dashes; the trails still read by colour but the picture is busy (observed, `forest-park-z13-day-rec.png`, `-z14-`). Paradise and Snow Lake at z13 are moderate (observed, `paradise-z13-day-rec.png`, `snow-lake-z13-day-rec.png`).
- Streams from z14 instead: Forest Park z13 is calm, but the "Balch Creek" label sits on nothing, which is today's map (premise 6; observed, `forest-park-z13-day-rec-streams14.png`).
- **Revised recommendation:** z13 at 0.6 px, 1 px at z14, 1.5 px at z15, in `#3fa0c8`, so z13 creeks are present but under the trails; and whatever the choice, the waterway label's zoom must equal the stream line's. Not rendered at 0.6 px (inferred from the 0.5 and 1 px cells of the swatch).

### 5. Peak heights
- "Alta Vista / 5,961 ft" under the peak icon, smaller than the name; unnamed peaks show "1,155 ft" alone (observed, `paradise-z14-day-rec.png`, `paradise-z13-day-rec.png`, `snow-lake-z13-day-rec.png`, `forest-park-z13-day-rec.png`). Panorama Point 6,909 ft, Chair Peak 6,240 ft, Wright Mountain 5,430 ft (observed). Reads at once; nothing to think about. Done with `number-format` and a `format` expression (inferred that Native 13.5.0 supports both as the spec says).
- Huts, shelters and saddles were added to the outdoor list as dot-and-name; none fell inside any rendered view, so not seen.

### 6. Six icons
- Drafts in the pinned style (19 px, green ring `#4fa074` on `#d6f2e3`, the peak's colours, observed from the sprite pixels). On the map: picnic at Paradise and Forest Park z15, camp at Snow Lake, beside names (observed, `paradise-z14-day-rec.png`, `forest-park-z15-day-rec.png`, `snow-lake-z13-day-rec.png`). Night: the plain inversion gives a light ring on a dark fill, like the peak icon, no ring exception needed (observed, `swatch-night.png`, `paradise-z14-night-rec.png`).
- Two drafts need redrawing before anyone ships them: the trailhead signpost reads close to a flag, and the viewpoint reads a little like a sunrise (observed, `swatch-day.png`). Drafts are at `/tmp/sage03-scratch/new-sprite-items-x2.png`.
- Trailhead, viewpoint, toilets and ranger station are z15-only in the tiles (phase 1), and no z15 view here held one, so those icons are seen only in the swatch.

### 7. Trail names at Forest Park z14: they do not show
- With Street v1's label layer as it is, the z14 view centred on the Wildwood Trail places one minor-road label ("Northwest Forest Lane") and no trail name, although the three tiles under the view carry 13, 8 and 8 named paths (observed, `forest-park-z14-day-rec.png` and the driver's placed-label count of 1; tiles z14/2605/5857, 2605/5858, 2604/5857). Paradise z14 likewise shows none of its 19 named paths, while "Edith Creek" places along a winding stream (observed, `paradise-z14-day-rec.png`).
- The layer and data are right: filter `kind in minor_road, other, path`, minzoom 14, 14 px (read, generated `rec.json`). The cause is placement: with `text-max-angle` 60 and 12 px text, 3 labels place; with 90 and 14 px, 5 place, all of them the straighter fire lanes and Leif Erikson Drive, never Wildwood or Maple Trail (observed, `forest-park-z14-day-rec-labelsA.png`, `-labelsB.png`). At z15 "Northwest Firelane 1 Road" places (observed, `forest-park-z15-day-rec.png`).
- So the owner's screenshot with no trail names was most likely z14 or z15 on winding trails, and the web engine cannot place a 14 px name on them; whether Native does better is not determined (inferred). This changes question 8 below.

### 8. Bare rock
- Day `#c9c4bb` makes Paradise, Snow Lake and the Rainier massif read as mountain, and the hard-trail colour sits on it (observed, `paradise-z13-day-rec.png`, `snow-lake-z13-day-rec.png`, `rainier-region-z10-day-rec.png`). `#d9d4cc` is too close to the ground, `#bcb7ae` heavy (swatch, observed).
- Night: its inversion `#433e35` is darker than the night forest, and the rock reads as dark holes in the forest (observed, `snow-lake-z12-night-rec.png`). So rock needs its own night colour too (the same app-side fill exception as wetland), or stays day-only, or is accepted as dark. Not rendered with a night exception.

### Scrub dots
Rendered in the swatch only: visible, noisy (observed, `swatch-day.png`). Recommendation unchanged: not now.

## Owner's questions, revised (phase-1 order)

1. **Tree marks.** (a) Dark glyph `#3e7a3a` in an irregular 64 px cell from z12, via sprite v5, **recommended**: it reads as scattered trees, and fails to today's green. (b) The same glyph on the regular 32 px cell (rows show). (c) No glyphs, today's flat green. Sub-question, night: (i) plain inversion `#9cd898`, bright, no app change, **recommended for now**; (ii) a dimmer night glyph `#81bc74`, calmer, an app-side exception for one image.
2. **Streams.** (a) From z13 at 0.6 px, 1 px at z14, 1.5 px at z15, blue `#3fa0c8`, and the creek-name label moved to the same zoom, **recommended**. (b) From z14 at 1 px, label moved to z14 (fixes today's label on nothing). (c) As today, with the label-on-nothing left as is.
3. **Area names.** (a) Parks, wildernesses, protected areas and the big named forests from the zoom the tiles give them (z8-10), other forests and city parks from z11, italic near-black, **recommended**; the "Forest Park" doubling at z12 is accepted. (b) The same in dark green `#3e7a3a`, softer. (c) None.
4. **Peak heights.** (a) Feet, fixed in the style, as rendered, **recommended**. (b) Metres. (c) None. Plus (d) huts, shelters and saddles as dot-and-name, **recommended yes**, unseen in any view.
5. **Wetland.** (a) Fill plus tufts, with an app-side night colour `#2a4f47` for the fill, **recommended**: without the night colour the marsh vanishes at night. (b) Fill plus tufts, night as the plain inversion (tufts alone carry it). (c) Nothing. Sub-question: (d) tufts from z10 as rendered, or (e) from z12, fill only below, to calm the Everglades at z10 (not rendered).
6. **Icons.** (a) All six in sprite v5, with the trailhead and viewpoint redrawn first, **recommended**. (b) Keep the dots. (c) Three (trailhead, parking, viewpoint).
7. **Bare rock.** (a) `#c9c4bb` by day with its own night colour (an app-side fill exception, colour to be chosen on a render), **recommended**. (b) `#c9c4bb` by day, dark at night as rendered. (c) No.
8. **Trail names.** Names at z14 do not place on winding trails in the web engine whatever the angle limit; only straight fire lanes do. (a) Leave the label layer as ruled (−1286, z14) and check once on the phone whether Native places more, **recommended**. (b) Allow `text-max-angle` 90 at z14 for a few more straight ones (seen: 5 instead of 1). (c) Start trail names at z15 and say so.
9. **Hillshade and contours.** Unchanged: hold to −1291.
10. **Leaf type.** Unchanged: no data.

Two of the recommended options (5a, 7a) and the night sub-option 1(ii) need an app change beyond the style: a night colour for a named fill layer, or for a named sprite image. Everything else is style plus sprite v5.

## Could not render, and why

- Bare rock and the dim glyph with their own night colours on a map: not built (the exception mechanism is an app change; the swatch and `-rec-dim` show the colours).
- Streams at 0.6 px at z13: not rendered; inferred from the 0.5 and 1 px swatch cells.
- Trailhead, viewpoint, toilets, ranger-station, hut, shelter and saddle icons on a map: none fell in a rendered view (z15-only kinds, and no hut nearby); seen in the swatch only.
- Tufts from z12 only (5e): not rendered.
- Anything on the phone's engine: the preview is GL JS 6.12.0; label placement in particular can differ (read, `preview/index.html` note).

## Render paths (all under `/tmp/sage03-scratch/shots/`)

Viewed by eye: `swatch-day.png`, `swatch-night.png` (night strip viewed in its first version; the re-render only adds captions), `forest-park-z12-day-rec.png`, `forest-park-z12-day-rec-irregular.png`, `forest-park-z12-night-rec.png`, `forest-park-z13-day-rec.png`, `forest-park-z13-day-rec-streams14.png`, `forest-park-z14-day-rec.png`, `forest-park-z14-day-rec-noglyph.png`, `forest-park-z14-day-rec-dense.png`, `forest-park-z14-day-rec-irregular.png`, `forest-park-z14-day-rec-labelsA.png`, `forest-park-z14-day-rec-labelsB.png`, `forest-park-z14-night-rec.png`, `forest-park-z14-night-rec-dim.png`, `forest-park-z15-day-rec.png`, `paradise-z13-day-rec.png`, `paradise-z14-day-rec.png`, `paradise-z14-night-rec.png`, `snow-lake-z12-night-rec.png`, `snow-lake-z13-day-rec.png`, `ridgefield-z12-night-rec.png`, `ridgefield-z13-day-rec.png`, `rainier-region-z8-day-rec.png`, `rainier-region-z10-day-rec.png`, `everglades-z10-day-rec.png`, `everglades-z10-night-rec.png`.

Rendered, not viewed: `forest-park-z12-day-rec-noglyph.png`, `forest-park-z12-night-rec-noglyph.png`, `forest-park-z13-day-rec-noglyph.png`, `forest-park-z13-night-rec.png`, `forest-park-z13-night-rec-noglyph.png`, `forest-park-z14-day-base.png`, `forest-park-z14-day-rec-light.png`, `forest-park-z14-night-rec-noglyph.png`, `forest-park-z14-night-rec-irregular.png`, `forest-park-z15-day-rec-noglyph.png`, `forest-park-z15-night-rec.png`, `forest-park-z15-night-rec-noglyph.png`, `paradise-z13-night-rec.png`, `snow-lake-z12-day-rec.png`, `snow-lake-z13-night-rec.png`, `ridgefield-z12-day-rec.png`, `ridgefield-z13-night-rec.png`.

Styles are in `/tmp/sage03-scratch/styles/` (`base`, `rec`, `rec-noglyph`, `rec-dense`, `rec-light`, `rec-irregular`, `rec-streams14`, `rec-labelsA`, `rec-labelsB`, each with a `-night` twin, plus `rec-night-dim`, `rec-irregular-night-dim`). `rec` = irregular not yet: `rec` uses the regular sparse cell; `rec-irregular` is the recommended look. Scripts: `make-sprite.py`, `character.mjs`, `map-style/sage03-generate.mjs`, `night.mjs`, `night-sprite.py`, `render.mjs`, `www/swatch.html`, job lists `jobs-*.json`, logs `render-maps.log`, `render-followup.log`. Renders show place names, so they stay off GitHub, as the brief says.

Centres used: Forest Park 45.556,−122.745; Paradise 46.786,−121.735; Snow Lake 47.4615,−121.4525; Ridgefield 45.83,−122.755; Rainier region 46.85,−121.75; Everglades 25.5,−80.95.