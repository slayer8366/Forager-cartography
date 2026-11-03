# coder-13 Z2: OSM's first zooms, the fixes and their tests (Hold B)

Willow (`session_01Hqu21r21FGQXWzLeRtR3yv`), 2026-11-02. Times are Pacific, read from the clock. Each claim is marked
**observed**, **read**, or **inferred**. Dispatch: `prompts/preserved/2026-11-02-coder-13-osm-zoom-levels.md` (updates
of 14:53 and later). Table: Juniper's comparison, Forager `osm-zoom-levels` `026c7748f` (rows unchanged from
`53c5d6801`). Target: a style minzoom of camera N - 1.5, with the data in the tiles from level N - 2, where N is
openstreetmap-carto v6.1.0's first zoom.

## What was written

| Part | Where | Commit |
|---|---|---|
| Basemap patch 0008, its tests and the jar gate | Forager `osm-zooms-map-build`, from `53a728341` | `96e4c0305` |
| Street v5 (`map-style/forager-street-v5.json`) and `overrides/forager-osm-zooms.mjs` | Forager `osm-zooms-style`, from pre-main `04746d8f0` | `50242c74c` |
| The offline style's zooms (`map-style/forager-offline-v2.json`, `tools/build-offline-v2.mjs`) | the same branch | `5d8653721` |
| This report, the style diff, the test scripts and logs, the renders | forager-cartography `willow-osm-zooms` | this commit |

Neither style is wired into the Worker or the app. Nothing was pushed to `main` or `pre-main`.

### The data: patch 0008 (read: the patch; observed: the tests)

- **What it changes:** every line, name, shield, place, POI and label goes into the tiles at carto's N - 2, and
  polygons are kept from a quarter pixel. The values and their carto file:line are in the patch's header and code.
- **Roads:**
  - lines: motorway and trunk 4, primary 6, secondary 7, tertiary and links 8, residential and unclassified 10,
    road 8, raceway 10, living street 11, service 12 (driveways, parking aisles and drive-throughs 14), pedestrian,
    path, footway and steps 12, track, cycleway and bridleway 11;
  - names: trunk to secondary 11, tertiary 12, streets, living and pedestrian streets and tracks 13;
  - shields: motorway 8, trunk and primary 9, secondary 10, tertiary 11;
  - bridges 11 (motorway to secondary; others 12), tunnels 10 (motorway to tertiary) and 11 (streets);
  - links are kept from 8 (LinkSimplify only below 8);
  - access=private or no keeps the class's zoom, except paths and tracks carto's int_access calls "no" (13);
  - rail 6 (preserved, tram and subway 10, spurs, sidings and yards 11, disused 13), piers 10, taxiways 9.
- **Water:** rivers 6, streams 10 (intermittent or seasonal 11), water polygons from a quarter pixel, and lake
  labels at carto's first level over 3000 px minus 2 (from 3).
- **Landuse:** polygons from a quarter pixel, by size and by bounding box.
- **Boundaries:** admin 5 from 6, admin 7 from 9.
- **Places:** carto's population score for cities, and its zooms for towns down to neighbourhoods.
- **POIs:** peaks 9, huts 11, camp and picnic sites, viewpoints and shelters 14, parking by size; area names by
  carto's tag groups and 3000 px rule.
- **Islands:** carto's 3000 px rule.
- **Unit tests** (observed, `mvn test` in a scratch clone, about 15:33; the time is estimated, not read from the clock): 590 tests, 0 failures.
  - 72 earlier cases are updated to the new zooms, each marked "Forager patch 0008".
  - 77 new `foragerOsm*` cases, gated per class in `build-basemap-jar.sh`.
  - The patched jar is sha256 `3b90772f218ab4fd…`.

### The style: Street v5 (read: the override; observed: the generator and the validator)

- **The minzooms:** each layer's minzoom is set to carto's N - 1.5. A layer whose kinds start at different zooms is
  split by kind.
- **Rules by size or population** get one layer per level of the tiles' `min_zoom`: lake labels, area names, cities,
  stream intermittency and parking. A filter's `["zoom"]` is the tile's whole level, so only `minzoom` can say
  N - 1.5.
- **The layers:** 181 (104 + 77 clones). Each clone gets its original's night-table entries, and the clones are listed
  in `forager:layer-clones`.
- **Validation:** v5 is valid (`@maplibre/maplibre-gl-style-spec` `validateStyleMin`, observed). v3 and v4 regenerate
  byte for byte (observed, sha256 before and after).
- **The change by layer:** `style-diff-v4-v5.md`. 55 of v4's 104 layers change.
- **The offline style:** `forager-offline-v2.json` takes the same zooms for its 57 layers: 78 layers, 21 clones, no
  labels. `offline-style.json` stays byte for byte (-1294; Aspen).

## The tests (observed; scripts and logs in `test/`)

1. **The test area:**
   - The extract: `osmium extract -b -122.95,44.95,-122.25,45.40` from `us-261030.osm.pbf`, 16,317,785 bytes.
   - Built in `~/scratch/coder13/molalla` with the patched jar and with the installed one (`25e5b8db`, the control).
   - patched: 22,249,412 bytes in 4 m 29 s; control: 20,565,241 bytes in 4 m 17 s.
   - The first try failed: the landcover GeoPackage can't write a journal through a link to the build user's
     folder, so it is copied.
2. **First zooms** (`zoomcheck.log`):
   - **The data rows:** 33 classes found in the area pass at carto's N - 2. In every one 0008 moves, the control
     differs. Four classes aren't in the area: tertiary shields, huts, admin 5 and admin 7.
   - **Two fail, both for size, not zoom:**
     - **highway=road** (want 8, first 12): the only two pieces in the area are 14 m and 33 m long. Roads'
       post-process drops lines under 0.5 px (27 m at 11). The zoom rule is pinned by a unit test.
     - **Major tunnels** (want 10, first 11): one 44 m trunk tunnel, under 0.5 px at 10 (54 m). On carto at 12, 44 m
       is about 1 px, so this one is slightly late.
   - **"Control same" on spurs and hamlets is the script's mistake.** Upstream already had spurs at 11 and these
     hamlets at 12.
   - **Per feature:** 3 of the 4 "inconsistent" labels are two features sharing a name (Clackamas River, Stella Olsen
     Park, Wildwood Open Space; the script keys on the name). The fourth, Mount Hood National Forest, first shows a
     level after its `min_zoom` says (10, not 9). Inferred: POI thinning (one per 8 px cell below 14) or the label
     point lying outside the box at 9; not checked.
   - **Named examples:** Molalla River from level 6 (control 9).
3. **Nothing else changes:** z15 feature counts are equal in every layer but water.
   - Water: 486 against 474. All 12 extra are stream lines: intermittent streams now carry another `min_zoom`, so
     Planetiler merges them separately. The geometry is the same.
4. **Size:**
   - The archive is +8.2%. No tile in the test is over 500 KB; the busiest is 193 KB gzipped (9/81/183), against
     77 KB in the control.
   - The landuse layer grows most: about 10x at 7, 5x at 8, 3.3x at 9 and 2x at 10. That's the quarter-pixel floor.
   - Water grows about 3x at 10-12, and roads 2x at 12.
   - See "Projection" for what this means at full scale.
5. **Renders:** `renders/`, one image per view: OSM as the app draws it (256 px raster), v5 on the patched test
   archive, and v4 on the control.
   - Molalla at 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5 and 14; Liberal at 11.5, 12.5 and 13.5.
   - Headless Firefox over WebDriver BiDi (headless Chromium stops at navigate on this Pi, as Hazel found).
   - No request to the Worker's `/relief`. Hill shading and the reference-trail band are left out (ours alone).

## Projection for the full build (inferred)

- **Size:** +8% (the test) to +20% (if the 2-5x growth at z7-12 holds where landuse is denser): 38-42 GB, against
  35.26 GB.
- **Time:** Planetiler +5% (the test), about 9 h 30 m against 9 h 02 m; the whole run about 14.5-15 h.
- **The risk is tile size, not total size.**
  - The last full build's largest tile is 352 KB gzipped (8/70/97, West Virginia; landuse 513 KB uncompressed,
    `usca-20261101T174337Z.log`).
  - With landuse 3-5x at 8-9, the densest tiles would reach about 1-1.5 MB gzipped.
  - Before the full build, either:
    - (a) test the floor on a dense landuse tile such as 8/70/97; or
    - (b) keep upstream's 2 px floor below 11 and the quarter pixel from 11. Small fills would then come in 1-2
      zooms after OSM at low zoom, where sub-pixel fills hardly show.

## Asked for by the dispatch

### Things that move later (ours was earlier than OSM; Juniper's negative Δ, now N - 1.5)

- **Fills:**
  - forest, wood, scrub, grass, meadow, sand, bare rock and wetland 2 → 3.5;
  - farmland, orchard and vineyard 2 → 3.5; plant nurseries 2 → 8.5;
  - residential and commercial 2 → 6.5, industrial → 6.5, railway land → 8.5;
  - parks, cemetery, golf, garden, pitch, recreation ground and allotments → 8.5; playground → 11.5;
  - hospital, school, university, beach and aerodrome → 8.5, military → 6.5, glacier → 3.5;
  - runway areas → 12.5, piers → 10.5, pedestrian areas → 13.5;
  - buildings 11 → 12.5.
- **Outlines:** protected areas 6 → 6.5, residential etc. outlines → 14.5, pitch outlines → 13.5.
- **Roads:** Interstates 3 → 4.5, streets 10 → 10.5, pedestrian streets 12 → 12.5, driveways 13 → 14 (data).
- **Boundaries:** countries and states 0 → 2.5, counties 8 → 8.5, city limits 10 → 10.5.
- **Names and labels:**
  - motorway names 11 → 11.5, service and path names 14 → 14.5;
  - motorway shields 7 → 8.5, trunk 8 → 9.5;
  - stream names 13 → 13.5, small lakes 15 → 15.5, bays and straits → 12.5;
  - countries 1 → 1.5, states 3 → 3.5;
  - towns 7 → 7.5, villages 10 → 10.5, hamlets 11-12 → 12.5, dwellings and farms → 13.5, localities → 14.5;
  - quarters 10 → 12.5, neighbourhoods 12 → 13.5;
  - parking nodes and drinking water 15 → 15.5, toilets 15 → 16.5.

### Earlier rulings this supersedes (read in the overrides and docs)

- **RECORD -1737** (buildings' change "only from zoom 14"): buildings now start at 12.5, where v4 drew them from 11.
- **The character rulings** (`docs/design/2026-10-21-character-rulings.md`; RECORD -1561):
  - ruling 1, tree glyphs from 12 → 11.5;
  - ruling 5, tufts from 10 → 8.5;
  - ruling 3, area names (reserves from 8, named forests from 8, the rest from 11) → carto's tag groups and 3000 px,
    per level.
  - The dispatch's "-27197" wasn't found in either repo.
- **sage-03 ruling 2(a)** (streams from 13): streams 10.5, intermittent 11.5.
- **RECORD -1506** ("names from zoom 14"; tracks a zoom before footpaths): street and track names 13.5, path names
  14.5; tracks 11.5, paths 12.5.
- **Patch 0005** (streets from 10, "Streets only"): residential and unclassified unchanged at 10 (style 10.5); road 8;
  service 13 → 12.
- **Patch 0001** (private and no-access paths at 15): 13, for paths and tracks carto's int_access calls "no"; every
  other class keeps its zoom.

### Only one map draws these (Juniper's B2; left as they are)

- **OSM only:**
  - heath fill;
  - canal, ditch and drain lines and their names;
  - wetland subtype patterns, and the other patterns (scrub, cemetery, allotments, garden, rock, scree, beach,
    military);
  - glacier outline; landuse names other than parks and forests; railway names; junction refs; ferries; aerialways;
  - barriers; cliffs, ridges and aretes; springs, waterfalls, caves, trees, fuel and information boards;
  - county names and boundary names; building names; islet names;
  - bridge decks, breakwaters and the folded landuse kinds;
  - **and saddles:** found here, they aren't in our tiles at all (no `natural=saddle` in Pois.java), though v4's
    filter lists them. Juniper's row 108 said "ours 15".
- **Ours only:** the Daylight land cover at 0-7; the national-park fill; outlines on forest and other natural fills
  and on water; trailheads and ranger stations; sea and ocean names; state abbreviations; the FS and BLM bands; link
  shields; the military naval-base and airfield fills; hill shading.

### Still off by half a zoom (inferred; the style can't tell these apart in the tiles)

- **Bridges and tunnels** come in at their data level, N - 2 (-0.5). A later minzoom would leave them undrawn, since
  the plain road layer lets them go at that level.
- **Driveways and parking aisles:** 14, not 14.5. The `service` value isn't in our tiles.
- **Paths and tracks with access=no:** 13, not 13.5.
- **Preserved main-line rail:** 10, not 10.5.
- **Islands other than the largest:** their tiles carry no `min_zoom`.
- **Small lakes:** 15, not 15.5.

### Seen in the renders, and not a zoom matter

- **Rail:** it is in the tiles here from level 6 (18 main-line pieces at 11, observed), and v5 draws it from 6.5. But
  v5's rail is a 0.45 px grey dashed line at 11 (its width runs exponentially from 0.15 at 6), so it is hard to see.
  OSM draws a main line at about 1.5 px.
- So on the renders, rail reads as later than OSM's because of how it is drawn. Look is outside this dispatch; the
  owner's call.

## Not checked

- The full build. Tile sizes in dense landuse (see Projection).
- The phone: MapLibre Native 13.5 against GL JS 6.12 in the renders.
- v1-v3 (frozen).
- The app wiring of v5 (its night tables are keyed by layer id; the clones are listed).
- Whether "-27197" names another ruling.

## Conventions

- **The patch:** 0001-0007's patch-header style and `foragerX` test naming, and the jar gate pattern in
  `build-basemap-jar.sh`.
- **The style:** `generate-street.mjs`'s version table and the override pattern (`forager-fill-in.mjs`).
- **The tests:** `~/pi29-logs/resume/tiles/mvt.py` for decoding; Hazel's `render-ff.mjs` for the renders; Planetiler's
  invocation from `build-usca.sh`.
