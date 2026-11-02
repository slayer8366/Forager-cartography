# coder-13 Z1: OSM first zooms against ours — DRAFT, withdrawn before completion

Willow (coder-13, `session_01Hqu21r21FGQXWzLeRtR3yv`), 2026-11-02, 14:15–14:26 PST. Times are Pacific, from the clock.

**Status: withdrawn, incomplete.** Aspen withdrew Z1 at about 14:25. The owner pointed the comparison at Juniper (Forager
dispatch 2026-11-02-03, `session_01Hqu21oansrXBVEfzvrbt17`). This draft keeps what was read and decoded up to then.

- **There is no OSM-side column.** The openstreetmap-carto reading was under way and was stopped before it reported.
- **No row has a fix decided.**
- **Use it only as input:** our style's layers and our tiles' first zooms at Molalla, both observed.

## Premises (read 14:15–14:17; reported to Aspen at about 14:17)

1. **map-build: wrong in part.**
   - `~/forager-pi34` is at `288ce80cf` and holds patches 0001–0004 only.
   - The installed `/opt/forager-build/map-build/COMMIT` is `53a7283417` (Forager "Merge pi-37-barrier-mark-fill", 11-01
     09:08, on origin/pi-build), with patches 0001–0007.
   - Aspen's word: Z2's patch branch is cut from `53a728341`.
2. **The basemaps source: confirmed.**
   - `/srv/forager-build/src/basemaps`, owned by forager-build, at ca93fc06.
   - The working tree carries the patches: Basemap, Buildings, Landuse, Roads and Water are modified, and Barriers.java
     is new.
3. **The jar: differs.**
   - Installed: `/opt/forager-build/basemap/protomaps-basemap-HEAD-with-deps.jar`, 11-01 09:40, sha256
     `25e5b8db69a85f1181c5a01b121aa5dd3e73cbb217a9555af013ed9412773a83`.
   - `1d892172…` is the rollback copy in `basemap.prev-20261030`.
4. **The tiles: confirmed.**
   - `/srv/forager-build/out-usca/current` → `20261030T212451Z`, z0–15, mvt, 58,893,441 tile entries.
   - Its manifest has map_build_commit `53a7283`, built_at 2026-11-02T07:53:36Z.
   - Written by run `usca-20261101T174337Z`.
   - Inferred, not checked: it's the same file as R2's us.pmtiles.
5. **The Pi wasn't idle at 14:16.**
   - The relief build had resumed at 14:16:10.
   - forager-build-usca.service had been activating since 13:59:35. Aspen stopped it at 14:18:52, on the owner's word.
6. **The tools: confirmed.** `~/pi29-logs/resume/tiles` (mvt.py, kinds.py) and `~/street-preview-scratch`.

## The reference

openstreetmap-carto **v5.9.0**: the newest `v5*` tag by `git ls-remote` at 14:17, commit `491bd4a4` (2024-10-17). It's
cloned read-only at `~/scratch/coder13/carto-v5.9.0`. Not tabulated (see Status).

## The styles the app draws our tiles with (read)

| Style | Served from | Used when | Zoom changes in the app |
|---|---|---|---|
| Street v4, `/style/street-v4.json` | Forager `server/pmtiles-worker/src/street-style-v4.json` (main `8d0eefdbc`), served unchanged (`index.ts:438-445`, `:503-505`), cache 86400 s | the own Street map, and offline when a v4 region is downloaded (`StreetStyle.kt:23`, `:83-84`) | none found: the night code sets icon images only (`NightImageApply.kt:93-102`) |
| Street v3, v2, v1 | `street-style-v3/v2/v1.json`, served the same way (`index.ts:491-501`) | offline, for regions downloaded against them (`StreetStyle.kt:46`, `:83-84`) | none found |
| offline, `/style/offline.json` | `server/pmtiles-worker/src/offline-style.json`: 57 layers, no labels (`index.ts:487-489`; `MapLibreOfflineMapRepository.kt:63-67`) | "use offline tiles" with no Street region (`StreetStyle.kt:84`) | — |

Not checked: v1–v3's layer zooms (only v4's and offline's were listed).

## Our style: Street v4 layers (observed)

All 104 layers, with source layer, minzoom, maxzoom and filter (truncated at 400 characters), are in
`our-style-layers.tsv`. These have zoom-dependent filters or visibility:

- **`pois`, no minzoom.**
  - Trailhead, parking, camp_site, picnic_site, viewpoint, peak, toilets, drinking_water, ranger_station, saddle,
    shelter, alpine_hut and wilderness_hut: from z12.
  - Restaurant, fast_food, cafe, bar, supermarket, convenience, books, clothes, beauty and electronics: from
    max(16, min_zoom).
  - Every other kind: not drawn.
- **`pois_area_names`, minzoom 8.**
  - nature_reserve, national_park and protected_area: from max(8, min_zoom).
  - forest named "National Forest", "State Forest", "National Monument", "National Grassland" or "Provincial Park":
    from z8.
  - Other forest and park: from z11.
- **`places_locality`:** the town-spot icon only below z8; text at every zoom the data has.
- **Minzooms named in the dispatch:**
  - `landuse_forest_glyphs` 12;
  - `landuse_orchards_pattern` 13;
  - `landuse_wetland_tufts` 10;
  - `water_river` 9;
  - `water_stream` 13;
  - `water_waterway_label` 13;
  - `roads_labels_major` 11;
  - `roads_labels_minor` 14;
  - `roads_oneway` 16;
  - `address_label` 18 (drawn only at z18, the app's maximum zoom, `StreetStyle.kt:59`);
  - `buildings_outline` 15;
  - `roads_taxiway` 13;
  - `landuse_edges` and `water_edges` 13.
- **`roads_shields`:** no minzoom; it draws wherever the tiles carry a ref.

## Our tiles: first zoom at Molalla and Liberal (observed, decoded 14:19:40–14:20:02)

- **How:** `first_zooms.py -122.66 45.10 -122.50 45.20` decoded all 313 tiles of z0–15 over that box from the local
  `current` archive, read-only, with `pmtiles tile`. Full output in `first_zooms.txt` and `first_zooms.json`: per layer
  and kind/kind_detail, the first zoom, the first zoom with a name and with a ref, min_zoom values, and counts per zoom.
- **Caveat:** below about z9 one tile covers far more than Molalla, so low first zooms aren't local.

| Seen in your screenshots | Our tiles: first zoom here | Our style: first zoom drawn |
|---|---|---|
| "Molalla" (place, town) | z7 (`places`, locality) | any zoom with data |
| "Liberal" | z12 (locality) | any zoom with data |
| OR 213 shield | z7, on I-205 (ref "I 205;OR 213") | `roads_shields`: no minzoom |
| OR 211 shield | z10 (primary, ref "OR 211") | `roads_shields`: no minzoom |
| "Molalla River" name | z9 (`water` river line, named) | `water_waterway_label` z13 |
| creek names (streams) | z13 (stream lines, named) | `water_waterway_label` z13 |
| primary/secondary road names | z12 | `roads_labels_major` z11, but no names in the tiles until z12 |
| tertiary road names | z13 | `roads_labels_major` z11 |
| residential/unclassified/service names | z14 | `roads_labels_minor` z14 |
| orchards (farmland, kind_detail orchard) | z6 here | fill: no minzoom; pattern: z13 |
| forest / wood | z2 (one tile then; 401 polygons at z7) | fill: no minzoom; glyphs: z12 |
| streams (lines) | z13 | `water_stream` z13 |
| buildings | z11 (1 here), 9,095 at z15 | `buildings` no minzoom |
| fences | z15 (patch 0003) | — |

## Not done (withdrawn)

- The OSM first zoom for each row: openstreetmap-carto `project.mml` and `.mss`, with file and line.
- The profile's file and line for each kind, from `layers/*.java`.
- The fix column (style, data or none), and the lists of things one map draws and the other doesn't.
- v1–v3's layers.
