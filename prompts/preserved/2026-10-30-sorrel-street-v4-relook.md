# Review dispatch 2026-10-30-sorrel-relook: PR #448 at e9be0bcdd

From Aspen to Sorrel Tally. Written 2026-10-30 at about 20:35 PDT. It follows
`2026-10-30-sorrel-street-v4.md`; your first review is Forager `sorrel-street-v4` at `11959e944`.

## What changed since your review (f228f9281 → e9be0bcdd)

These are the owner's rulings, in `docs/design/2026-10-30-fill-in-rulings.md` (Forager-cartography
main), sections "Motorways", "Night tertiary and rail" and "Borders, industrial and buildings":
- **Motorways:** OSM Carto pink (`#e892a2` / `#dc2a67`), inverted at night.
- **Night tertiary** `#333333`, through a new per-layer "night colour by day colour" table:
  - in the style, `forager:night-line-colours` in v4's metadata;
  - in the app, `StreetNightTables.lineColours`;
  - a band in the night checker.
- **Rail** is inverted at night.
- **Your should-fix 2 and 3.**
- **Faint borders:** `landuse_edges` and `water_edges`.
- **Industrial** is lilac `#ebdbe8` (edge `#c6b3c3`).
- **Tan buildings:** `#d9d0c9`, z14 step `#ccc0b7`, outline `#b9a99c`. The night is the inversion, v4
  only.

## The baseline (confirm first)

- **Heads:** `street-v4` is `e9be0bcdd`; `pre-main` is `b493cffeb`.
- **CI:** full CI is run 41162267089. The test-first runs are 41133078333 and 41135796965. The revert
  runs are 41162544051 (rail) and 41162546044 (outline).
- **The S22 APK** is run 41162594972 (branch `street-v4-s22-debug` at `975cdea0b`).
- **v3's sha256** must be unchanged: `e2a259820bd1dda6…` and `beb40e3a0e5624da…`.

## Questions, in order

1. Does v4 equal the rulings, every value, now including the four sections above? Rebuild it
   yourself.
2. **The new night-line-colours mechanism:**
   - Can it reach v1-v3 or StreetWithTopoOver?
   - Does every non-named colour in the match still invert?
   - Is it tested against the design rather than restating the code?
3. **Do the trails stay the strongest line,** day and night, with borders and pink motorways? Use your
   own renders at the four views plus Oregon City z15 (-122.595,45.355).
4. **Your earlier should-fixes:** are 2 and 3 closed? Are 1 and 4 still correctly left for the switch
   PR?
5. Run one revert check of your own.

## Bounds and verdict

- **As before:** read-only on the PR. Your review file goes on `sorrel-street-v4`, as
  `docs/reviews/2026-10-30-sorrel-street-v4-relook.md`.
- Render off GitHub, with no GitHub comments.
- If a `build-usca` process is running, don't start heavy work.
- **The verdict:** blocking / should-fix / notes, ending with "Is PR #448 at e9be0bcdd mergeable as
  plumbing ahead of the switch?" Send it to Aspen.
