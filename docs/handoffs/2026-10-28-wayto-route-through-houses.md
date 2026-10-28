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
