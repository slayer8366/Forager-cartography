# Topo hillshade and contours: owner's rulings on Sage-04 part 2

Written by the planner session `forager-cartography-7b`, 2026-10-22, about 11:35 PDT.

## Source

Sage-04's part 2 proposal, delivered 00:53 PDT. Its report was recovered from the previous planner
window's subagent log. See `docs/design/2026-10-22-night-colours-rulings.md`, "Source". The
renders are in `/tmp/sage04-scratch/shots/topo-*` and `strip-topo-*` (scratch, off GitHub).

Earlier ruling: −1291 kept OpenTopoMap and left our own contours and hillshade for later. The owner
moved it forward on 2026-10-21: "9 next, design the hillshade and contours for a topo map".

## Ruling

The planner listed Sage's eight questions with Sage's recommendation first. The owner answered,
verbatim: "all recommended".

| # | Question | Ruled |
|---|---|---|
| 1 | What "topo" is | Our own Topo: Street v1 with its character layers, plus relief and contours. It replaces the OpenTopoMap raster in the Topographical slot. Street stays flat. |
| 2 | Relief strength | Subtle: exaggeration 0.35 at z13 easing to 0.22 at z15, shadow `#4a3f33`, white highlight, light from 335°. |
| 3 | Contour interval and unit | 40 ft, with an index line every 200 ft, in feet. Brown `#a07040`. Index labels show the number only. |
| 4 | From which zoom | Hillshade from z9. Index contours and labels from z13. All contours from z14. |
| 5 | The data | USGS 3DEP 1″ for the US and NRCan MRDEM for Canada, as one download shared with the routing elevation work. |
| 6 | How it is served | Raster-dem relief to z12 (overzoomed above), and vector contours, as two separate archives built once. Not in the weekly basemap. |
| 7 | Night relief | Dark shadows `rgba(0,0,0,0.85)` and a dim highlight `rgba(220,228,236,0.30)`. The hillshade gets its own night pair in the app. |
| 8 | Timing | Size the pipeline now, in parallel with the routing elevation download. Build after the character work (the night colours and the rest of Sage-03 and Sage-04) ships. |

Also from Sage-04's proposal, part of the recommended design: contours draw between the hillshade
and the water, so lakes stay flat. Trails, roads, glyphs and labels stay above both.

## What Sage could not determine, carried forward

- How MapLibre Native 13.5.0 on the S22 draws the hillshade and the contour labels. The previews
  were GL JS.
- Real archive sizes over plains. The estimate is 40–90 GB for relief to z12, and 3–10 GB for
  contours.
- The provenance of 3DEP's Canadian tiles.
- The Pi's cost: GDAL and a vector tile cutter are not installed. Both are apt installs and need
  the owner's go when the time comes.

## Next

Sizing only (ruling 8). Nothing is built, downloaded, installed or uploaded until a separate go.
