# Global coverage: maps, trails, elevation and routing worldwide

Aspen's record, started 2026-10-31.

## The ask

The owner: "I want global maps with trails and elevation. We have People in Brazil and Qatar
downloading the app so we should be sure it's available to them also".

## Where we are (read by Aspen, 10-31)

- **On R2:**
  - `us.pmtiles` (US + Canada; the 10-21 upload until tonight's run is uploaded);
  - `world-south.pmtiles` (Protomaps planet south of 16°N, z0-8 only, from 10-22);
  - `reference-trails.pmtiles` (USFS/BLM, US only);
  - routing squares for US + Canada only (187).
- **Qatar** (about 25°N, 51°E) is outside both archives: land and water fill only, so a blank map with
  no roads, trails or routing.
- **Brazil** has only the z0-8 world fill: no streets, trails or routing.
- **Pi sizing:** tonight's US + Canada run needs 157.1 of 162.7 GB on the NVMe (7.59 x input +10 %),
  peaks at 5.9 of 8 GB RAM, and takes about 15 h. The laptop is a 10th-gen i7 with 12 GB. Neither is
  comfortable for the planet (inferred: about 1 TB minimum and 2 TB comfortable, plus 32-64 GB RAM).

## The owner's ruling

"Fast fill now, own build later (Recommended)". The option read: "Willow scopes the Protomaps planet +
BRouter world squares as a worldwide fallback (gos for upload/deploy come back to you), and pilots our
own global build to price cloud vs laptop."

- **Phase 1:** a worldwide fallback from ready-made data. Protomaps' daily planet for the tiles, and
  BRouter's world segments4 for routing (elevation is inside the rd5). The Worker serves them wherever
  US + Canada has no data.
- **Phase 2:** Forager's own weekly global build (the patches, heights, names), on a cloud machine or an
  upgraded laptop, priced by a measured pilot. It replaces the fallback.

Dispatched: `prompts/preserved/2026-10-31-coder-08-global-scope.md`.

## Willow's Part A (16:45 PDT)

- **Tiles:** `build.protomaps.com/20261031.pmtiles` is 139.2 GB, z0-15, basemap 4.15.2 (our pin's
  version).
  - **It lacks our patches**, so outside US + Canada:
    - every path draws as "unknown difficulty";
    - tracks start at z12 and paths at z13;
    - streets start at z12;
    - there are no orchards or nurseries, no barriers, and no bare-rock fix.
  - **Upload:** whole, as `world.pmtiles` (about $2.1/month). Streamed with `rclone copyurl` from a cloud
    VM or a GitHub Actions job, not through the Pi.
- **Routing:** brouter.de's segments4 is 1,142 squares, 10.04 GB, weekly. The header version matches
  ours (2/11, 0).
  - The app needs no change. The Worker needs a second manifest (`routing/world-manifest.json`, option
    a).
  - **Flag:** the elevation inside is CGIAR SRTM v4.1. Willow thinks (from memory) that commercial use
    needs CGIAR's agreement. The owner should check before relying on it.
- **Worker:** branch `worker-world-fallback` at `bcaf931a6` (on `pre-main` `b38c1d161`). It falls back
  us -> world -> world-south. Tests-first runs fail and pass as expected. Not deployed.
- **App:** the blockers are the map data, not the code. Grey from z9 up in São Paulo and Doha; offline
  downloads succeed but hold empty tiles. With `world.pmtiles` up and the Worker deployed, the same
  URLs work. Small items: imperial by default, the offline picker centred on the US, the US species
  index, and English month names.
- **The renders** wait until the build finishes.

## The Pi's network (Aspen, 16:30 PDT)

- **Wi-Fi failed at 15:10** (NetworkManager: wlan0 config -> failed, reason "no-secrets"). The default
  route is now the Bluetooth tether to the owner's Tab S8+ (bnep0, about 0.2 MB/s).
- The build is past its downloads, so it's unaffected.
- **The upload watcher now waits for Wi-Fi** (default route via wlan0) before the routing upload and
  again before the tiles, so nothing goes through the tablet's data. It was restarted at 16:30 with the
  guard.
- **The owner, on the SRTM flag:** "We aren't using it commercially." So brouter.de's world squares
  can be used, with the SRTM heights in them, on non-commercial terms.
  - Still owed when world routing ships: a credit for the heights' source (CGIAR-CSI SRTM v4.1) in the
    app's Heights credits, beside the 3DEP and NRCan rows, worded from CGIAR's own terms.
  - If Forager ever becomes commercial, this needs looking at again.
