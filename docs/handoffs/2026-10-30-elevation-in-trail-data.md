# The trail data already carries elevation: a correction for the Forager planner

Aspen, 2026-10-30, about 07:20 PDT. Times are PT. For Rowan to pass to the Forager planner (Juniper / Sorrel).

## Why this note

The owner asked to "get elevation on along with trail data", saying Juniper had done the research.
Forager RECORD -1822, -1824 (plan `docs/plans/2026-10-29-waypoint-route-plotting-plan.md`,
Addenda 1 and 2) and the header of `domain/wayhome/WayHomeHeights.kt` say **"the route files carry
no elevation"**. **That is out of date.** The Pi side of Juniper's sizing (RECORD -1501, 3″ first) was
built as G7/G8. The route squares the app downloads today carry 3″ heights.

## What is live (from the G8 record, `docs/audits/2026-10-27-g8-elevation-in-weekly.md`)

- **Run `usca-20261027T221400Z`** (the early run, finished 10-28 05:59) built all 187 `.rd5` from the
  pinned 3″ `.bef` store. Only the squares pinned in `USCA_BEF_NONE` have no heights: W170_N20,
  W180_N25, W80_N25, W95_N15, W95_N20.
- **R2:** live since 10-28 10:09. `routing/manifest.json` names that run.
- **Sunday 11-01** and later weekly runs build heights the same way.

## Checked today (07:00-07:20, read-only on the Pi)

**1. BRouter returns heights on the live squares.** BRouter 1.7.10 (the app's version), stock
`hiking-mountain.brf` (the app's profile), local RouteServer on
`/srv/forager-build/out-usca/current/segments`, GeoJSON output:

| Route | Length | Filtered ascend | Points with height | Low / high |
|---|---|---|---|---|
| Boise foothills, -116.1935,43.6360 → -116.1725,43.6555 | 3,668 m | 139 m | 182 of 182 | 875.75 / 992.0 m |
| Rainier, Paradise → toward Panorama Point, -121.7356,46.7865 → -121.7300,46.8022 | 2,855 m | 377 m | 206 of 206 | 1,656.5 / 2,033.5 m |
| Miami, -80.1918,25.7617 → -80.1300,25.7900 | 9,446 m | 2 m | 530 of 530 | 0.75 / 3.0 m |
| San Juan, -66.1057,18.4655 → -66.0700,18.4500 | 4,778 m | 10 m | 197 of 197 | 1.0 / 13.0 m |

The heights make sense: Paradise is about 1,646 m and the Rainier route starts at 1,656 m. Miami
sits near sea level. (Miami is in W85_N25, not the pinned W80_N25.) No route was run in a pinned
no-heights square.

**2. The squares on R2 are the files tested.**
- R2 `routing/manifest.json` sha256 `7ac9341a…f81ef` equals the local copy, and its run_id is
  `usca-20261027T221400Z`.
- **W120_N40** (Boise) and **W125_N45** (Rainier) were read from R2 and hashed. Each equals the local
  file and the manifest's sha256: `507c6034…09d0` and `710c71b1…8d3b`.

**3. Not checked:**
- **Downloading through the Worker.** The app key isn't on the Pi. Without it,
  `/routing/area.json` answers 403, as designed. The bytes behind the Worker are the R2 objects
  checked above.
- **A route on the phone.** Not done.

## What's left, all app side (not Aspen's)

1. **Step 4a can start now.** It doesn't have to wait for "the Pi's elevation build". In
   `routing/BRouterTrailRouter.kt`, keep the engine's per-point elevation where it maps nodes to
   positions, and add a heights field to `TrailRoute` (the RECORD -1689 note, and the climbing-allowance
   doc's "For the elevation work").
   - **For the route card:** the climb, graph, high/low and per-leg rows can then use trail-data heights.
     Open-Meteo is then needed only for straight legs with no trail data, and for the five pinned squares.
   - **For the way home:** `WayHomeHeights`' trail-part stand-in can be replaced too.
   - **A phone with route data downloaded before 10-28 still has squares without heights.** The app
     should treat missing heights as missing, not as zero.
2. **Fix the out-of-date text:** the "route files carry no elevation" claim in `WayHomeHeights.kt` and
   the RECORD -1822/-1824 Observed lines.
3. **`consider_elevation`** stays off (G8 go: "app later"). Turning it on changes which way a route
   goes, not just what the card shows, so it needs its own report and go.
4. **Device check:** one route on the S22 after a fresh route-data download, to confirm heights arrive
   through the Worker.

Nothing was installed, uploaded or changed on the Pi or R2. The test server was stopped afterwards.
