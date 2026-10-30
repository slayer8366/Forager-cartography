# Review dispatch 2026-10-30-sorrel: PR #448, Street v4 (fill-in)

From the Pi planner (session forager-cartography-28, "Aspen") to Sorrel Tally. Written 2026-10-30 at
about 11:10 PDT. Report times in Pacific time.

You are **Sorrel Tally**, the independent reviewer. Read Forager `origin/pre-main`
`docs/process/reviewer-profile.md` before your first action, and work under it. You run on a
different model from the coder (Willow Quadrat, Opus).

## The owner, verbatim

- **The reviewer:** "Sorrel can review for now", in Willow's window, about 11:00. In Aspen's window the
  owner also chose "Sorrel (Recommended)".
- **Willow's three calls beyond the dispatch:** "Accept all three (Recommended)". They are:
  1. v4's night tables are picked when the URI's last path part is `street-v4.json` or
     `forager-street-v4.json`;
  2. a new branch `street-v4`, with Sage's `street-v4-fill-in` superseded;
  3. the throwaway branches are deleted after the S22 check.

## What to review

- **The PR:** PR #448, https://github.com/slayer8366/Forager/pull/448, `street-v4` → `pre-main`.
- **The design:** `slayer8366/Forager-cartography` main, `docs/design/2026-10-30-fill-in-rulings.md`.
  It covers the day design, the night table, the ramps section and the draft script in
  `docs/design/2026-10-30-fill-in-files/mkdraft.py`.
- **The coder's brief:** `prompts/preserved/2026-10-30-coder-01-street-v4.md`, the same repo.

## Baseline (confirm first; any mismatch is a stop)

- **Heads:** `street-v4` is `f228f9281`. `pre-main` is `b493cffeb`. The PR's head is `f228f9281`.
- **CI runs:**
  - full CI on the head: 41097273828;
  - the test-first run: 41095849138;
  - revert checks: 41097417352 (a fill dropped) and 41097421525 (v4 on v3's tables);
  - the S22 debug APK: 41099952632, artifact sha256
    `6079649c23530ceb49dc6751d6a26f044da4dbe933d3769a8ef92f00927f734b`.
- **v3 sha256, which must be unchanged from pre-main:**
  - `map-style/forager-street-v3.json` and `server/pmtiles-worker/src/street-style-v3.json`:
    `e2a259820bd1dda6bccfd7e05d5132adea6254002540cfbfdcfc04747de16b7f`;
  - `forager-street-v3.preview.json`:
    `beb40e3a0e5624da44f52e98f0e85c52e3065cc87af5987396fbf983a8d71c97`.

## Questions, in order

1. **Does v4 equal the ruled design, and nothing else?**
   - Rebuild it yourself: `mkdraft.py` on v3, plus the ruled ramp match.
   - Compare layers and paint, and the night metadata against the rulings table.
   - Name any difference.
2. **Is v1-v3 unchanged by day and by night?**
   - Check the style files by sha256.
   - Check the app: what every pre-v4 URI and StreetWithTopoOver get from the new selector and
     `StreetNightTables.kt`.
   - Look for any path where v3 could get v4's tables, or the reverse.
3. **The selector.**
   - Is matching on the last path part (`street-v4.json` / `forager-street-v4.json`) sound?
   - Could any other style URI match by accident, such as a downloaded region's URI or a query string?
4. **The tests.**
   - Does `NightExceptionsV4Test` test the design's values rather than restate the code?
   - Do the two revert runs fail on the edit they name, and only that?
   - Run one revert check of your own.
5. **Willow's observation:** `usesStreetSprite` (`BasemapStyles.kt:278`) gives Street night only to
   URIs in `STREET_STYLE_URLS`, so v4's tables can't take effect in this PR. Is that right? Is it
   safe to merge as plumbing ahead of the switch PR?
6. **Look at the output.**
   - Render v4 by day and night at:
     - z9 Canby-Silverton (-122.62,45.12);
     - z11 Oregon City (-122.6,45.33);
     - z13.5 Silver Falls (-122.64,44.875);
     - z12 inner Portland (-122.66,45.52).
   - Describe the renders in words. They show place names, so keep them off GitHub.
   - Say whether trails stay the strongest line.

## Bounds

- **Read-only on the PR.** Don't push to `street-v4`, merge, comment on GitHub, deploy, or change the
  Worker.
- **The review file** goes on a new branch `sorrel-street-v4` in Forager:
  `docs/reviews/2026-10-30-sorrel-street-v4.md`, committed and pushed.
- Run one browser at a time, under `nice -n 10`, on 127.0.0.1 ports of your own, and stop it by PID.
  Never use `pkill -f`.
- Don't touch 127.0.0.1:8081 or 127.0.0.1:8765, `/srv/forager-build`, `/opt/forager-build` or the
  cards.
- **Sunday's weekly build** fires at about Sun 11-01 02:02 PST. If a `build-usca` process is running,
  don't start heavy work.

If anything is ambiguous, stop and ask the owner.

## The verdict

Give it in three parts, as the profile asks: **blocking**, **should-fix**, **notes**. Mark each claim
read, computed or inferred. End with one line: "Is PR #448 mergeable as plumbing ahead of the switch,
and under what conditions?" Merging is the owner's go, never the reviewer's.

Send the report to Aspen (session "raspberrypi-radiant-parasol") and keep it as your final message.
