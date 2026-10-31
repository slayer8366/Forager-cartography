# Review dispatch 2026-10-30-sorrel-relook2: PR #448 at 97a26e8c7 (after pi-35)

From Aspen to Sorrel Tally. Written 2026-10-30 at about 22:50 PDT.

**Priority:** do this after pi-35, which has a Saturday deadline.

## What's new since your re-look at e9be0bcdd

- **307d3c2ac:** your should-fix 3.
- **5a5cbd1b6:** tests first.
- **97a26e8c7:** the owner's low-zoom roads "A: OSM's treatment" and night borders "Darker rims".
  - casings off below z11, and majors thinner by class;
  - Carto low-zoom colours cross-fading 10.5→11.5;
  - roads_minor as a faint texture from z10;
  - night-line-colours gains roads_minor {#ffffff→#333333} and landuse_edges, with Sage's 13 rims.

The spec is in the rulings doc, section "Low-zoom roads, night borders, notices route", plus Sage's
`/tmp/sage11-work/night-edges.json`.

## Baseline

- **street-v4** is at `97a26e8c7`.
- **CI:** full CI 41172033453; test-first 41171469222; the revert 41172097097.
- **The S22 APK:** run 41172099022, debug branch at `fb987fe13`.
- **v3's sha256** is unchanged.

## Questions

1. Does v4 equal the rulings, every value, including the cross-fades and the night rims?
2. Can the extended night-line-colours reach v1-v3 or StreetWithTopoOver? Does each named day colour
   map only within its own layer?
3. Do trails stay the strongest line, day and night? Check the four views, plus z13 forest, where
   roads_minor now goes dark grey.
4. Run one revert check of your own.

**The verdict:** blocking / should-fix / notes, ending with "Is PR #448 at 97a26e8c7 mergeable as
plumbing ahead of the switch?" Read-only. The review file goes on `sorrel-street-v4`.
