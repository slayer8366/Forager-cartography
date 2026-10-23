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
