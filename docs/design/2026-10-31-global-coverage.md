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
- **Wi-Fi diagnosis (Aspen, about 16:55):** wlan0 scans see only channel 11 (Deschutes, b0490 and a
  hidden one), and the home network isn't heard. rfkill is clear and the region is US.
  - Toggling the radio and reloading `brcmfmac` didn't help.
  - Inferred: Wi-Fi/Bluetooth coexistence on the shared chip while the tether carries traffic.
  - **The owner:** "restart after the build finishes".
- **Timer, so a reboot can't start a second run:** `forager-build.timer` is now **disabled** (not just
  stopped). The earlier resume one-shot is cancelled. `forager-build-timer-resume2` at Sun 11-01
  11:00 UTC touches the stamp and runs `systemctl enable --now forager-build.timer`.
  - That one-shot is transient, so it's lost on a reboot.
- **After the reboot** (by Aspen, or by the owner if Aspen's session isn't back):
  1. `sudo touch /var/lib/systemd/timers/stamp-forager-build.timer && sudo systemctl enable --now forager-build.timer`.
     The next run is then Sun 11-08.
  2. `cd /mnt/archive/aspen-upload-next && setsid nohup ./upload-after-build.sh >> nohup.out 2>&1 < /dev/null &`.
     It checks the run finished OK, waits for Wi-Fi, then uploads.
- **Wi-Fi back (about 21:30 PDT):** wlan0 has 10.0.0.115 on Virusdownloader, and the default route is
  via wlan0 (metric 600, ahead of bnep0's 750). **The owner:** "skip the restart then".
  - The watcher uploads over Wi-Fi after the build.
  - `forager-build-timer-resume2` still re-enables the weekly timer at Sun 11-01 03:00 PST, so the
    after-reboot steps above aren't needed.

## The early run failed: Planetiler out of heap (Sun 11-01, read at 04:00 PST)

- **`usca-20261031T193102Z` failed at stage `planetiler`** at 23:29 PDT, 10-31, after 8.4 h.
  - `java.lang.OutOfMemoryError: Java heap space` in `WriteablePmtiles$DeduplicatingTileWriter.write`,
    during the archive write.
  - At the time: features 747M (48 %), tiles 213M, heap 4.2G/4.2G, GC 98 %; peak RSS 6.24 GB.
  - The heap is `USCA_PLANETILER_XMX=4g` (`pins.env:178`).
- **Last week's run (10-27) was already at the edge:** heap 3.9G/4.2G post-GC near its end, with 651M
  tiles and 1.5B features in the end. This week's tiles carry 0005 (streets from z10) and 0006 (orchard
  kinds) and filled the heap earlier.
  - Inferred: 0005's extra z10-11 roads are the main growth. Willow's Oregon pilot measured the archive,
    not the heap at US scale.
- **Nothing was published or uploaded:**
  - The build left the previous outputs untouched; this run's partial output is kept in
    `/srv/forager-build/failed-usca/latest`.
  - The watcher stopped at 23:31 ("STOP: the run failed …") before any upload.
  - R2 still has the 10-21 `us.pmtiles` and routing `usca-20261027T221400Z`.
- **The timer:** `forager-build-timer-resume2` fired at 03:00:06 PST. `forager-build.timer` is enabled
  again, and its next run is Sun 11-08 02:08 PST. **That run will fail the same way unless the heap is
  fixed.**
- **Wi-Fi** is up (the default route is via wlan0).
- **Dispatched:** Willow, coder-09 (diagnose and fix the heap, with Sorrel's review). A rerun is the
  owner's go.
- **Willow, coder-09 (06:45 PST): the cause is 0004, not 0005 or 0006.** This corrects Aspen's
  inference above.
  - 0004's per-tile corner mark is a **point**. Planetiler only deduplicates tiles made purely of fills
    and edges, so no z15 tile dedupes, and every all-water, all-forest or all-farmland tile gets its
    own entry in the heap-resident entry list (about 44 B each).
  - Last week's run started before 0003 and 0004 were installed (10-28), so 10-31 was the first US +
    Canada build with the mark.
  - **Oregon measurements:**
    - 0001-0003: 418,172 entries;
    - 0001-0004: 613,976 (+46.8 %);
    - 0005: +0;
    - 0006: +3.
  - Scaled to US + Canada: about +27.6M entries, about +1.2 GB of heap.
- **The fix:** Forager `pi-37-barrier-mark-fill` at `63a3649e5`, patch **0007**.
  - The mark becomes one fill polygon covering the tile, still on every z15 tile, so "fences checked"
    still holds.
  - Oregon is back to 418,177 entries, and the archive is about 5 % smaller.
  - mvn 513 tests, 0 failures. The gate needs 9 BarriersTest cases; the revert check gives 8 and is
    refused.
  - The app's reader (#439, unmerged) keeps only lines, so the mark is ignored either way.
- **Willow also recommends** raising `USCA_PLANETILER_XMX` from 4g to 5g (or 4.5g) for headroom: last
  week was already at 4.0 of 4.2G post-GC.
  - Zram is optional; swap wouldn't have helped.
- Sorrel is dispatched for review. The install, the -Xmx change and a rerun are each the owner's go.
