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
