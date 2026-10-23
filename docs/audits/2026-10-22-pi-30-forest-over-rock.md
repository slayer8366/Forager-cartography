# pi-30: forest wins over bare rock in the map build

Written by the planner session `forager-cartography-7b`. Times are PDT.
Dispatch: `prompts/preserved/2026-10-22-pi-30.md`.

## Why

The owner's S22 check of Trail Map, relayed by Rowan, found a large flat grey area east of
Seaside, OR. It is OSM relation 14965119, tagged `landuse=forest` + `natural=bare_rock`. The
profile's last-matching-rule-wins logic makes it kind `bare_rock`.

## Go

- **Relayed by Rowan:** the owner chose "A: build prefers forest (Recommended)", described as
  "Aspen changes the map build so forest wins when both tags are present; live after Sunday's
  weekly build. Aspen first counts how many areas it affects."
- **In the planner's session,** after the count: "Still change the build".

## Count, read-only, 2026-10-22 20:36-20:51

`osmium tags-filter wr/natural=bare_rock` on each 261017 extract, then the tags of each element
were checked for `landuse=forest|wood`.

| Extract | Ways and relations with `natural=bare_rock` | Also `landuse=forest` or `wood` |
|---|---|---|
| us | 151,039 | 1: r14965119, about 170 km² (inferred from its tile coverage) |
| canada | 22,982 | 0 |
| puerto-rico | 113 | 0 |
| us-virgin-islands | 57 | 0 |

The first count read 0 because the pattern missed OPL's `T` prefix on the first tag. It was
corrected, and r14965119 was confirmed in the output by id.

## Upload

The weekly build does not upload. A Sunday run publishes on the Pi only, and the R2 upload stays a
separate step needing the owner's go.

## Status

Dispatched to a coder, about 21:10. Results follow below when the coder reports.

**The owner on editing OSM,** about 21:20, verbatim: "OSM has the area covered in their maps properly, so we shouldn't need to edit it on their end". So no OSM edit; the fix is the build change only. The planner's note: OSM Carto draws the relation as forest, which is why it looks right there; the tags themselves still carry `natural=bare_rock`.

**Coder stop at step B, and Amendment 1, about 21:40.** The coder found that upstream's landuse rule has no `wood`, so decision 1 would have dropped wood + bare_rock areas entirely. The planner verified it, and found no such element in the data. Amendment 1 (in the preserved dispatch) excludes `landuse=forest` only and leaves wood + bare_rock as bare_rock. This is a planner's call, recorded here. The jar before is `7f9c4aef942b3688980bfe91a67e455eb1bc59115a4b5a37ddee41d7ed98f8db` (coder, observed).

**The coder's name.** The owner: "Willow is your coder I believe". Asked how to handle coder work, they chose "Helpers, called Willow". pi-30's coder is a helper started from the planner session; this record names that role Willow Quadrat, Pi coder, from here on.

## Result: done, about 21:27 (Willow Quadrat, coder; checked by the planner at about 21:45)

Willow's report: steps A to D, all observed by Willow. The planner re-checked the items marked
**checked**.

- **Code:** Forager `pi-build` `aa14e6eaa752fe830f8354574671cc0eda736246`, "map-build: forest wins
  over bare rock in the landuse layer (dispatch pi-30)". It is a fast-forward from 961a90d36.
  - It adds `map-build/patches/protomaps-basemaps/0002-landuse-forest-over-bare-rock.patch`. 0001 is
    unchanged.
  - **checked:** pins.env now reads `BASEMAPS_PATCHES` = 0001 then 0002.
  - build-basemap-jar.sh applies both and adds the LanduseTest gate.
  - The new rule, per Amendment 1: `rule(with("natural", "bare_rock"), without("landuse", "forest"),
    use("kind", "bare_rock"))`.
- **Tests:**
  - 485 run, 0 failures, BUILD SUCCESS.
  - **checked:** the log has "Forager tests ran: 29 cases, 0 failures" and "Forager landuse tests ran:
    4 cases, 0 failures".
  - Willow's extra pre-check: with Landuse.java reverted, case 1 fails "expected forest but was
    bare_rock". So the test distinguishes the behaviours.
- **Installed:**
  - **checked:** `/opt/forager-build/map-build/COMMIT` = aa14e6ea, and the previous copy (e5f5add6) is
    in `map-build.prev`.
  - **checked:** the jar went from `7f9c4aef942b3688980bfe91a67e455eb1bc59115a4b5a37ddee41d7ed98f8db`
    to `32126b8c9543d301b3bd288c4c063694a657b792b9f26f38020c418717d90fcc`.
  - The rollback jar is in `/opt/forager-build/basemap.prev-20261022/`.
- **Seaside test build** (osmium extract `-b -123.98,45.90,-123.80,46.05 -s smart`, Planetiler
  `--maxzoom=14`, with each jar):
  - In tile 13/1276/2915, feature 52776573098367 (r14965119) is `forest` with the new jar and
    `bare_rock` with the rollback jar. The other 8 landuse (id, kind) pairs are identical.
    **checked:** `diff tile-old.txt tile-new.txt` shows only that line.
  - The genuine bare-rock relation r7138014 (no landuse tag) is bare_rock under both jars at z12-z14,
    and so are r7138023 and r21189590.
  - Logs are in `/home/bwann83/pi30-logs/`.
  - The test needed a scratch copy of the daylight-landcover gpkg, because SQLite needs a writable
    journal. The sources were not touched.
- **Untouched:** **checked:** the timer's next run is still Sun 2026-10-25 03:24:55 PDT. R2,
  out-usca and the cards were not touched, and nothing was uploaded.
- **Left in place:** the worktree `/tmp/pi30-wt` and scratch clones.

## Live

Sunday's weekly build uses the new jar. Getting it to phones needs the separate R2 upload of
us.pmtiles, with the owner's go.

**Rollback:**
1. Copy `basemap.prev-20261022/protomaps-basemap-HEAD-with-deps.jar` back over the installed jar.
2. Reinstall map-build from e5f5add6, which is the `map-build.prev` copy.
