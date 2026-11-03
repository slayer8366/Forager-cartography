# The renders

Each image shows the same view three times: OpenStreetMap as the app draws it (a 256 px raster), Street v5 on the
patched Molalla test archive, and Street v4 on the control (today's installed jar).

- `0008b-as-installed/`: patch 0008 with option (b), jar sha256 5f9a8bcd…c754. That is upstream's landuse floor
  below z11 and the quarter pixel from z11. Shot with v5 at Forager `osm-zooms-style` `d7c57375c` (the peak fix:
  icons from 9.5, names from 11.5). This is what the full build will draw.
- `0008a-quarter-pixel-every-zoom/`: the first set, shot 17:44-17:46 PST (the files' times). Patch 0008 with the quarter-pixel floor at every
  zoom (jar 3b90772f, superseded), and v5 at `50242c74c`, before the peak fix, so peak names show from 9.5. Kept for
  comparison (Aspen).

Molalla at 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5 and 14; Liberal at 11.5, 12.5 and 13.5. The OSM and v4 panels are
the same shots in both sets.
