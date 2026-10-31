# Review dispatch 2026-10-30-sorrel-pi35: streets from z10 in the weekly build (pi-35)

From Aspen to Sorrel Tally. Written 2026-10-30 at about 22:35 PDT.

## The go and the deadline

- **The owner, in Aspen's window:** "From Sunday's run (Recommended)". Sorrel reviews. If you say
  mergeable, Willow installs it by **Sat 10-31 22:00 PDT**, clear of Sunday's 02:20 PST timer. If
  not, nothing is installed and Sunday runs as already set.
- **Willow's dispatch:** `prompts/preserved/2026-10-30-coder-05-street-grid-install.md`.

## Baseline (confirm first)

- **The branch:** Forager `pi-35-street-grid` at `064d70542`. It's based on the **installed**
  map-build `288ce80cf` (`/opt/forager-build/map-build/COMMIT`), from `pi-34-barrier-mark`, which
  holds patches 0001-0004.
- **Note:** `origin/pi-build` is at `532f70fd6`, with patches 0001-0002 only. pi-33 and pi-34 were
  installed but never merged into it. So merging pi-35 into `pi-build` also brings pi-33 and pi-34.
  - Aspen accepts that, because it makes `pi-build` match what's installed.
  - **Review the delta `288ce80cf..064d70542`.** For pi-33 and pi-34, only confirm that the merge
    brings in exactly the installed tree.
- **Willow's evidence:**
  - `mvn package` with 0001-0005: 506 tests, 0 failures. Scratch jar sha256 `ca9201f7…a4408`.
  - The map-build suites are green.
  - Revert: with 0005 dropped, the jar script dies on "foragerStreets cases … 0 (expected 7)".
- **The pilots:** Oregon (+0.68 %) and New York (+0.94 %; largest z10 tile 228,641 B, limit 500 KB),
  scratch in `~/scratch/willow-grid`.

## Questions

1. Does 0005 do only what's ruled? Residential, unclassified and road start at z10. Service roads,
   living_street and private or no-access ways are unchanged. min_zoom, sort keys, merging and
   simplification are upstream's.
2. Does the jar script's new street-count gate stop a jar without 0005, and nothing else?
3. **Size and safety for the full US+Canada run,** recomputed from the pilot archives:
   - the largest-tile margin, including the New Jersey caveat on Hudson tiles;
   - the NVMe and card checks, read from build-usca's disk logic;
   - build time.
4. **The v3 app today:** confirm that v3 (`street-v3.json`) draws no `minor_road` below z12, so
   phones see no change from these tiles until v4.
5. Is the merge into `pi-build` safe? It should give exactly the installed `288ce80cf` tree plus the
   0005 change.
6. Run one revert check of your own.

## Bounds and verdict

- Read-only. Write the review on a new branch `sorrel-pi35`, as
  `docs/reviews/2026-10-30-sorrel-pi35-street-grid.md`.
- No installs. Leave `/opt` and `/srv` alone. If `build-usca` is running, no heavy work.
- **The verdict:** blocking / should-fix / notes, ending with "Is pi-35 mergeable for install before
  Sunday 11-01's run?" Send it to Aspen by Sat 10-31 18:00 PDT if you can.
