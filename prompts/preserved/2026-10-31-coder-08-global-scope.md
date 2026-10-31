# Dispatch 2026-10-31-coder-08: global coverage, scope and measure (no uploads)

From the Pi planner (session forager-cartography-28, "Aspen") to Willow Quadrat. Written 2026-10-31 at
about 16:10 PDT. Report times in Pacific time. There's no deadline, but Brazil and Qatar have users
today.

## The go

The owner: "I want global maps with trails and elevation. We have People in Brazil and Qatar
downloading the app so we should be sure it's available to them also". Then "Fast fill now, own build
later (Recommended)". The background is `docs/design/2026-10-31-global-coverage.md` in this repo.

This dispatch covers scoping, measuring and branches only. Every R2 upload, Worker deploy, merge and
purchase is a separate go from the owner.

## Part A: the worldwide fallback (phase 1)

1. **Tiles.**
   - Read the current Protomaps daily planet's header with `pmtiles show` on the URL, without
     downloading it: size, maxzoom, basemap version.
   - Compare its schema with what v3 and v4 need: layers and kinds, our 0001/0005/0006 attributes, and
     what v4 loses where they're absent (trail attributes, z10 streets, orchards).
   - Say whether to upload it whole as `world.pmtiles` or to cut out US + Canada. Give the transfer
     path: the Pi's network and card, or `pmtiles extract`, or another way. Estimate the hours.
2. **Routing.**
   - BRouter's world segments4: the source and its licence, the count and total size.
   - Is its rd5 format the same version the app's BRouter reads? Elevation is inside.
   - How do the app and the Worker's `routing/manifest.json` handle squares outside the 187? What
     changes? Names (FNAM) won't exist outside US + Canada: what does the app do without them?
3. **The Worker.** Design the fallback: us.pmtiles first, world elsewhere (as `world-south` does today,
   generalised). Cover tile JSON, bounds, caching, and what happens at the seam. A branch with tests is
   fine; no deploy.
4. **The app.**
   - What blocks a user in Brazil or Qatar today? Offline region downloads outside the US, routing
     squares, StreetStyle and topo bounds, and any US-only assumptions.
   - List them with file:line. Fix on a branch only where it's small and obvious; report the rest.
5. **Check:** renders of São Paulo and Doha at z10, z13 and z15 with v4 over the planet (read straight
   from Protomaps' URL, not R2), day and night. Keep them off GitHub.

## Part B: our own global build (phase 2), measure only

1. **After tonight's run finishes** (about 03:00 PST): a measured pilot on one large region (Europe
   from Geofabrik, or South America if Europe won't fit), with the installed jar (0001-0006). Record
   NVMe peak, RAM peak, time, archive size, and routing and names time.
   - Not on the NVMe while the run or the R2 upload is going. Check free space first; use `/mnt/storage`
     if it fits.
2. **Scale it to the planet** (inferred) for:
   - a cloud machine (name one or two concrete instance types with RAM, disk and hourly price);
   - the owner's laptop (10th-gen i7, 12 GB) as it is, and with 32 GB plus a 2 TB drive.
3. **Elevation:** the global source for 3" heights (the US + Canada store is bef3, 1.8 GB), its size
   and licence. The topo relief is out of scope.

## Bounds

- **Until the run and its upload finish** (the watcher in `/mnt/archive/aspen-upload-next/`):
  - no Planetiler, no Gradle, no large downloads on the Pi;
  - nothing large on the NVMe;
  - CI and reading headers are fine.
- No R2 writes. Don't touch `us.pmtiles`, `world-south.pmtiles`, the routing set or the Worker.
- One Planetiler at a time, under `nice -n 10`, leaving 2 GB of RAM free.
- Ask the owner if anything is ambiguous.

## Report

Send Part A first, then Part B, to Aspen. Mark every claim observed, read or inferred, with sizes,
times and costs.
