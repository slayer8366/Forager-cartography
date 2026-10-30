# Dispatch 2026-10-30-coder-01: Street v4 (fill-in), style and app night, to a PR into pre-main

From the Pi planner (session forager-cartography-28, "Aspen") to the coder. Written 2026-10-30 at about
10:30 PDT. Report times in Pacific time.

## Read first

- **Rulings:** `slayer8366/Forager-cartography` main, `docs/design/2026-10-30-fill-in-rulings.md`, all
  of it. It holds the day design, the ruled night, and the owner's words.
- **Sage's design brief:** `prompts/preserved/2026-10-30-sage-09.md`, the same repo. Its phase 2 is
  what you are doing now.
- **In Forager:**
  - `map-style/README.md`;
  - `app/src/main/java/com/zynergylabs/forager/app/map/StreetStyle.kt`;
  - `NightColour.kt` (`STREET_NIGHT_LAYER_COLOURS`, `STREET_NIGHT_FILL_COLOURS`);
  - `MapStyleReload.kt` (`applyOfflineNightRecolour`);
  - `NightExceptionsTest`, `StreetStyleTest`, `BasemapNightStyleTest`.

## The go

The owner said "Yes, ship it" to the OSM-like night and to phase 2, as Sage quoted at about 09:46.
In Aspen's window the owner then chose "New coder session" for this work. The go covers what is
below, up to a PR into `pre-main` and the S22 check. It doesn't cover:
- putting `street-v4.json` on the Worker;
- changing `STREET_STYLE_URL` or `STREET_STYLE_URLS`;
- anything that changes what v1-v3 regions show, by day or by night.

Each of those is its own go.

## Where it starts

Sage wrote style-side code on branch `street-v4-fill-in` before the owner limited Sage to design. It
is commit `55ed979af`, from `origin/pre-main` `b493cffeb`, and has no PR.
- **What it holds:**
  - `map-style/overrides/forager-fill-in.mjs`;
  - `generate-street.mjs` writing v4 beside v3;
  - optional `v4` arguments on `check-street-night.mjs` and `check-street-trails.mjs`;
  - `npm run check:street:v4`.
- **Review it as your own.** Keep it, fix it or redo it, and say which. The coder owns this code from
  here.
- **Sage's checks (observed, by Sage):**
  - v3's three copies are byte-identical before and after;
  - v4 equals the ruled draft;
  - the night checker exits 0 on v4;
  - the trails checker passes 6,643 cases;
  - dropping parks' night colour fails the night checker.
- **Not run by Sage:** `build-sprite-v5 --check`, because pngjs was missing. Run it.

## The work

1. **The style:**
   - v4 carries the ruled day design and the ruled night (the rulings table).
   - v3 (all copies) stays byte-for-byte unchanged. Show the sha256 before and after.
   - v4 isn't added to `server/pmtiles-worker`.
2. **Ramps and slip roads at night.** The owner ruled them "Invert them too", so each ramp matches
   the road it joins. Motorway ramps stay amber.
   - Today `roads_link` and `roads_bridges_link` are one layer with one night colour (`#e0ad4f`).
   - **Sage specifies the values.** Aspen has asked Sage for them; use Sage's spec.
   - If the night mechanism can set only one colour per layer, and the ruling needs a split by
     `kind_detail`, propose the smallest change and ask before building it.
3. **The app: per-version night tables.**
   - Today the night tables are one global table for every Trail Map version. v4 differs from v3 in:
     - `roads_major` and `roads_bridges_major`: no entry in v4, `#e0ad4f` in v3;
     - `roads_rail`: `#a3acae` in v4, `#b4bec0` in v3;
     - the five new night-fills;
     - the ramps, after step 2.
   - **Suggested by Sage:**
     - v1-v3 and StreetWithTopoOver keep today's tables exactly;
     - v4's tables are chosen when the loaded style URI ends in `/street-v4.json` (`MapStyleReload.kt`
       has `source.uri` where `applyOfflineNightRecolour` runs).

     Choose the design yourself. If you find a better way, say why.
4. **Tests:**
   - A v4 twin of `NightExceptionsTest` reading `map-style/forager-street-v4.json`.
   - The v3 tests stay unchanged and green.
   - **Revert checks,** each run once:
     - drop one new fill's night colour in v4 and show both the style night checker and the app
       test fail;
     - point v4 at the v3 tables and show the twin fails.
   - The Pi has no Android SDK platforms, so CI builds and runs the app tests.
5. **The S22 check:**
   - Make a **never-merged** debug branch that loads
     `https://raw.githubusercontent.com/slayer8366/Forager/<your branch>/map-style/forager-street-v4.json`.
     Fonts, sprite and tiles stay on the Worker.
   - Use CI's app-debug-apk.
   - The owner checks day and night at:
     - z9 Canby-Silverton (-122.62,45.12);
     - z11 Oregon City (-122.6,45.33);
     - z13.5 Silver Falls (-122.64,44.875);
     - z12 inner Portland (-122.66,45.52).

     Ask the owner for the screenshots, or for their word.
6. **The PR** into `pre-main`, with CI green. The PR body lists what is and isn't in it (the go's
   limits above).
   - Ask for Sorrel's review if Sorrel is available. If not, ask the owner who reviews.
   - Don't merge without the owner's go.

## Bounds

- **Sunday's weekly build** fires at about Sun 11-01 02:02 PST. If a `build-usca` process is running,
  don't start heavy work, and say so.
- Run local servers on 127.0.0.1 ports of your own, and stop them by PID. Never use `pkill -f`.
- Don't touch 127.0.0.1:8081 or 127.0.0.1:8765.
- **Leave alone:** `/srv/forager-build`, `/opt/forager-build`, the cards and R2.

If anything is ambiguous, you find a better way, or something doesn't work how we want it, for any
reason: stop and ask the owner. Don't assume; asking is encouraged.

## Report

Send the report to Aspen (session forager-cartography-28), and keep it as your final message:
- every claim marked observed, read or inferred;
- commits, CI runs and the PR named;
- times in PT.
