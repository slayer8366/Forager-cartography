# Dispatch: way-to-waypoint route ends across houses (10-28)

From Aspen (planner) to Willow Quadrat, Pi coder. The owner asked for this on 10-28 at about 12:05 PDT.

## What the owner saw

On 10-28 at 11:43 PDT, the S26 (SM-S948U, Android 17) was running app build `1.0.4123+g4113c078`, which is
`~/Forager` commit `4113c0780`. The way-to-waypoint route to Waypoint 6 ran south first. It then came back up
a lane west of the pin and ended at that lane's far end. From there the app drew a dashed straight line to the
pin, across houses. The card said "0.3 mi … by trail".

The owner says this is wrong: there is a road route that gets closer to the pin without crossing houses.

## What the planner checked (evidence)

Everything is in `~/pi-handoffs/wayto-houses-261028/`, on the Pi only, because the points are the owner's home.

- **Inputs from the phone:**
  - The route square is `files/offline_routes/4/W125_N45.rd5`. Download #4 was saved 11:40:45 from run
    `usca-20261027T221400Z`. It is 530,232 B with sha256 `7f5485d3…694b`.
  - The profile files are `files/routing/profiles2/hiking-mountain.brf` and `lookups.dat`.
  - The start and target are in `points.txt`. The start is the fused GPS position from `dumpsys location`. The
    target is `waypoint_navigation.target_id`, which is Waypoint 6.
- **Reference run:** `rerun.sh` uses BRouter 1.7.10 on the Pi with exactly those files. It finds a 395 m route
  at cost 550: a service lane onto a secondary road, then a residential street. The route ends 69 m from the
  pin, on the road, and crosses no houses (`testtrack0.geojson`).
- **Logged on the phone:** before download #4, three attempts logged `FindWayToWaypoint … straight line
  (NO_TRAIL_ROUTES): no downloaded area covers either end`. After the download, the app logged nothing about
  routing, and there were no crashes.
- **Ruled out:** two private driveways next to the pin (OSM ways 749703663 and 749703664) are closed to the
  profile. That explains why the route can't reach the pin itself. It does not explain the route the phone
  chose, because the reference run avoids them and ends much closer.
- **Not yet checked:** what start, target and parameters the app actually passes to BRouter. Whether the app
  filters or restricts ways, for example to trails only. How the app picks the point where the routed part
  ends and the straight line begins.

## Task

1. **Find the cause before changing anything.** In `4113c0780`, follow
   `domain/wayto/FindWayToWaypointUseCase.kt` and what it calls. Reproduce the phone's route from the inputs
   above, through the app's own code path (a JVM test with the `.rd5` is fine). Report, with file and line:
   what is sent to the engine, what comes back, and where the app's route stops matching the reference run.
2. **Stop and report to the planner** with that evidence. Propose a fix and say what it changes. Do not push
   a fix before the planner and the owner have seen the cause.
3. **Later, for the fix:** add a test built from these inputs. It must fail on `4113c0780`. It must pass only
   when the routed part ends within about 70 m of the pin on a public way, with no straight leg longer than
   that leg.

## Constraints

- Do not change the Pi build, the `.rd5` and `.fnm` formats, BRouter 1.7.10 on the Pi, or R2.
- Do not edit `hiking-mountain.brf` to fix this. The profile already produces the right route.
- Keep the owner's coordinates out of anything pushed. Use the files in the handoff folder, or a shifted copy.

## Outcome of steps 1 and 2 (Willow, 10-28 ~12:25 PDT). This supersedes "What the planner checked"

- **The planner's premise was wrong.** The phone's route *is* the reference route. Willow called the engine
  exactly as `BRouterTrailRouter.kt:146-163` does, on the handoff files, and got the same 12 points, 395 m
  and cost 550. The route ends at the dead end of Legato Drive, 69 m from the pin. The planner checked the end
  against the 10-26 extract (Legato Drive, 7 m). The reference's 69 m straight leg is the same leg across the
  houses. The planner's "routes correctly, crosses no houses" was not checked against the buildings and is
  withdrawn.
- **Why it looked different:** the map was rotated, with a bearing of roughly 140–150°. That is fitted from
  the road angles, because the bearing was not logged.
- **Cause:** the routed part ends where BRouter matches the waypoint to its *nearest routable* way
  (`FindWayToWaypointUseCase.kt:70,79-85`). The app adds no end-point logic. The approach the owner wants is
  Parrish Road at the mouth of the private driveway, which is 73 m away, 4 m farther than Legato. So it is
  never picked.
- **Proposals, waiting on the owner:** A. End the route where a nearer closed way (private or no access)
  meets a routable way, then a second engine run to that junction. B. Show the map's bearing during a
  way-to while the map is rotated.
- **Step 3's test is withdrawn as written.** It already passes on `4113c0780`. A replacement test asserts
  that the route ends within about 10 m of the closed way's junction. It needs a public stand-in place, or it
  stays Pi-local.

## Owner's ruling (10-28 ~14:10 PDT). Replaces proposals A and B, which were both declined

The owner said: "The route didn't take me to the house. It took me to the house behind it. That's the
difference between one side of a ravine and the other. The trail can't be good enough, it has to be precise."

1. **Drop-off at the street in front of the pin, the way Google does it.** The route ends on the public street
   the pin's property faces. In this case that is Parrish Road, where the driveway to the pin starts. It is
   **not** the nearest way in a straight line. The route must not go up private ways, including the pin's
   own driveway. That was the planner's suggestion, and the owner said no.
2. **The distance from the drop-off to the pin can vary.** The line from the drop-off to the pin must not cross
   buildings, private property or rivers.
3. **Use elevation to detect sharp drops** (a ravine, a bluff) between the drop-off and the pin, and reject any
   drop-off that has one.
4. Still applies from the planner, and the owner did not reject it: if no drop-off meets 2 and 3, the app says
   so plainly. It does not draw a confident line or say "by trail".

**Data limits to resolve before building:**
- OSM rarely has property lines.
- Where do "private property", rivers and elevation come from on the phone, offline?

**Owner, 10-28 (follow-up):** use **building footprints and fences** (`barrier=fence` and related) as the
property lines for rule 2. No parcel data is needed.

**Owner, 10-28 (follow-up 2):** "For trails, the legs can stay so long as they pass our determined gates to
be useful."
- **Planner's reading:** on trails, the straight off-trail legs stay. That means the lead-in from the walker
  and the final leg to the pin. Each is kept only if it passes the same gates: no building, no fence, no river,
  no sharp drop.
- The street-in-front drop-off applies where the pin is served by streets.
- A leg that fails a gate is handled by rule 4.
- **Open:** Willow is to propose how the app tells a trail case from a street case.

## Willow's design report (10-28 ~15:00 PDT): design only, nothing changed

**What exists offline today:**
- Building and water polygons are in the downloaded z10–15 map tiles, but the app has no code that reads them.
- Fences are not on the phone at all.
- Around the pin, the 10-26 extract has 0 barrier lines. The planner checked this too: 620 buildings and 0 barrier ways in the small box.
- The route square's heights are from a 3-arc-second grid, about 92 × 65 m, sampled only at road nodes. That is
  too coarse to see a ravine.
- The pin's private driveways are in the route square.

**Choosing the drop-off:**
1. Find where the pin building's private access way comes out onto a public road.
2. Then, if the build ever ships it, the address street.
3. Then frontage: the shortest leg that passes the gates.

Here this picks Parrish Road at the driveway mouth: a 73.4 m leg that crosses 0 buildings. The Legato leg
crosses 2 buildings and fails.

**Street end or trail end** is decided by buildings within 15 m, or built-up landuse. A trail end keeps the
straight leg, subject to the gates.

**Size:** about 5–7 PRs. Elevation is a separate project: a 1/3-arc-second USGS grid per downloaded area.

**Calls waiting on the owner:**
1. Elevation: block street drop-offs until it ships, or show "drop not checked".
2. Fences: ship them in the build, or leave that gate off with a note.
3. The address street in the basemap.
4. Decode closed ways from the route square, or use a derived profile.
5. What counts as a river.
6. The thresholds.
7. Test fixtures: Boise (a stranger's home), or synthetic only.

The full report is in the planner's session; its scratch scripts are in the session scratchpad.

## Owner's go (10-28 ~15:10 PDT)

1. **Elevation:** ship without the drop gate, and **show no note** about it. The 10 m elevation data is a
   separate project for later. Not dispatched now.
2. **Fences go into the weekly build.** Per the planner's recommendation, which the owner accepted under "the
   rest is good", the address **street name** goes in with them.

**The rest of the design is approved as proposed:**
- closed ways are decoded from the route square, and the profile is not edited;
- "river" means river, stream, ditch, canal and wetland, and culverts pass;
- thresholds are 15, 25, 150 and 300 m;
- tests use synthetic fixtures only in the repo, and the real case and Boise stay Pi-local.

**Dispatched to Willow:**
- the app work, in Willow's order of 5–7 PRs, with fixtures first;
- the build change for fences and address streets.

**Build change, procedure:**
- Test on one band, report, and keep a rollback.
- Installing it on the Pi before Sunday 11-01's 02:29 PST run needs the planner's check of the one-band
  result first.
- No R2 change. The new data arrives with Sunday's run through the normal upload, which needs the owner's go
  as usual.

## Progress (10-28 16:40 PDT, planner checked)

**PR 1, the fixtures:**
- Branch `wayto-dropoff-fixtures` at `8a8326af1`, based on pre-main.
- The planner's dispatch said main. That was wrong: the repo's `CLAUDE.md` names pre-main as the target.
- The fixture is a made-up street block drawn in the open Atlantic. Cases: A, the owner's trap; B, a fence;
  C, a stream with a culvert; D, a trail pin; D2, a trail pin with a stream.
- CI run `40784532287`, started by `workflow_dispatch`: 5 of 5 jobs green, 5,897 tests, 0 failures.
- PR 1 to be opened against pre-main.

**pi-33, the build change:**
- Branch `pi-33-fences-addr` at `5cbb559df`. Basemap patch 0003 adds a `barriers` layer at z15 (fence, wall,
  hedge, retaining_wall), keeps `addr_street` at z15, and puts `tunnel` on water lines from z14.
- Boise one-box proof: 111,993 of 111,994 address points carry a street, 128 barrier lines, 405 tunnel tags.
  z15 is +3.1 %, the whole archive +1.9 %. The full US is estimated at +0.6–1.1 GB.
- Approved by the planner: tunnel (needed for culverts), retaining_wall included, and area hedges left out as
  a known gap.
- Install approved before Sunday 11-01.
- **Rollback:** map-build `532f70fd6` plus the jar `32126b8c…` in
  `/mnt/storage/rollback/basemap-jar-before-pi33/`, which the planner checked with `sha256sum -c`.
- NVMe had 175.8 GB free at 16:40.

**Known limit:** areas downloaded before Sunday's upload have no `barriers` layer. The reader PR is to read the
tile metadata, and say "fences not checked" instead of passing the gate.
