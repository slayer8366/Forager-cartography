# Street v4 to v5: first zooms by layer (generated from forager-street-v4.json and forager-street-v5.json)

Forager `osm-zooms-style` 50242c74c (map-style/overrides/forager-osm-zooms.mjs). A layer's minzoom is a camera zoom;
v5 sets it to openstreetmap-carto v6.1.0's first zoom N minus 1.5. Clones are `<layer>__<group>`; the original keeps
what no clone takes. Unchanged layers are not listed. `-` is no minzoom (the layer draws from the tiles' first level).

| v4 layer | v4 minzoom | v5: the original | v5 clones (minzoom) | width changed |
|---|---|---|---|---|
| `landuse_settled` | - | 3.5 | `urban` 6.5, `railway` 8.5 |  |
| `landuse_orchards` | - | 3.5 | `nursery` 8.5 |  |
| `landuse_orchards_pattern` | 13 | 11.5 |  |  |
| `landuse_parks_fill` | - | 8.5 |  |  |
| `landuse_park` | - | 3.5 | `military` 6.5, `cemetery_golf` 8.5 |  |
| `landuse_forest_glyphs` | 12 | 11.5 |  |  |
| `landuse_wetland_tufts` | 10 | 8.5 |  |  |
| `landuse_park_outline` | 6 | 6.5 |  |  |
| `landuse_urban_green` | - | 8.5 | `village_green` 3.5, `playground` 11.5 |  |
| `landuse_hospital` | - | 8.5 |  |  |
| `landuse_industrial` | - | 6.5 |  |  |
| `landuse_school` | - | 8.5 |  |  |
| `landuse_beach` | - | 8.5 |  |  |
| `landuse_aerodrome` | - | 8.5 |  |  |
| `roads_runway` | - | 9.5 |  | yes |
| `roads_taxiway` | 13 | 9.5 |  | yes |
| `landuse_runway` | - | 12.5 |  |  |
| `water_stream` | 13 | 10.5 | `z11` 11.5 |  |
| `water_river` | 9 | 6.5 |  | yes |
| `landuse_pedestrian` | - | 13.5 | `dam` 11.5 |  |
| `landuse_pier` | - | 10.5 |  |  |
| `landuse_edges` | 13 | 13 | `institutions` 11.5, `settled` 14.5, `sport` 13.5 |  |
| `buildings` | - | 12.5 |  |  |
| `buildings_outline` | 15 | 13.5 |  |  |
| `roads_pier` | - | 10.5 |  | yes |
| `roads_other` | - | 12.5 | `living_street` 11.5 |  |
| `roads_path_track` | 12 | 11.5 |  |  |
| `roads_path_informal_z13` | 13 | 12.5 | `cycle_bridle` 11.5 |  |
| `roads_path_steps` | 13 | 12.5 |  |  |
| `roads_path_unknown_z13` | 13 | 12.5 | `cycle_bridle` 11.5 |  |
| `roads_path_hard_z13` | 13 | 12.5 | `cycle_bridle` 11.5 |  |
| `roads_link` | - | 8.5 |  | yes |
| `roads_minor_service` | - | 12.5 |  | yes |
| `roads_minor` | - | 10.5 | `road` 8.5 |  |
| `roads_major` | - | 4.5 | `primary` 6.5, `secondary` 7.5, `tertiary` 8.5, `links` 8.5 |  |
| `roads_highway_casing_early` | - | 4.5 |  |  |
| `roads_highway` | - | 4.5 |  |  |
| `roads_rail` | - | 6.5 | `service` 11.5, `urban` 10.5, `disused` 13.5 |  |
| `boundaries_country` | - | 2.5 |  |  |
| `boundaries` | - | 2.5 | `admin5` 6.5, `admin6` 8.5, `admin7` 9.5, `admin8` 10.5 |  |
| `address_label` | 18 | 15.5 |  |  |
| `water_waterway_label` | 13 | 13.5 | `river` 11.5 |  |
| `roads_oneway` | 16 | 14.5 |  |  |
| `roads_labels_minor` | 14 | 13.5 | `service_paths` 14.5 |  |
| `water_label_ocean` | - | - | `bays` 12.5 |  |
| `earth_label_islands` | - | 2.5 |  |  |
| `water_label_lakes` | - | 15.5 | `z14` 14.5, `z13` 13.5, `z12` 12.5, `z11` 11.5, `z10` 10.5, `z9` 9.5, `z8` 8.5, `z7` 7.5, `z6` 6.5, `z5` 5.5, `z4` 4.5, `z3` 3.5 |  |
| `roads_shields` | - | 8.5 | `trunk_primary` 9.5, `secondary` 10.5, `tertiary` 11.5 |  |
| `roads_labels_major` | 11 | 11.5 | `tertiary` 12.5 |  |
| `pois_area_names` | 8 | 15.5 | `z14` 14.5, `z13` 13.5, `z12` 12.5, `z11` 11.5, `z10` 10.5, `z9` 9.5, `z8` 8.5, `z7` 7.5, `z6` 6.5 |  |
| `pois` | - | 12 | `toilets` 16.5, `food` 15.5, `shops` 15.5, `drinking_water` 15.5, `parking_small` 15.5, `supermarket` 14.5, `camp` 14.5, `parking_large` 12.5, `huts` 11.5, `peak` 9.5 |  |
| `places_subplace` | - | 13.5 | `suburb` 10.5, `quarter` 12.5 |  |
| `places_region` | - | 3.5 |  |  |
| `places_locality` | - | - | `city_z5` 5.5, `city_z4` 4.5, `city_z3` 3.5, `city_z2` 2.5, `town` 7.5, `village` 10.5, `hamlet` 12.5, `dwelling` 13.5, `locality` 14.5 |  |
| `places_country` | - | 1.5 |  |  |

55 of 104 v4 layers changed; v5 has 181 layers (77 clones).
