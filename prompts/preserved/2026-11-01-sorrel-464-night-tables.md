# Review dispatch 2026-11-01-sorrel-464: the night pass picks Street tables in one place (PR #464)

From Aspen to Sorrel. Written 2026-11-01 at about 23:10 PST. There's no deadline. Aspen merges only after
your "mergeable", matching the head you reviewed (owner: "I'll leave the merging to you for the time being").

## Background

- You (the previous Sorrel session, now gone) reviewed #462, the app switch to Street v4, and asked for
  S-1: a test that the night pass really uses `streetUriOf`, or a pure `nightTablesFor(source)`. #462 is
  merged into `pre-main` as `2bc8913f4`.
- Willow answered S-1 as **Forager PR #464 -> `pre-main`**, branch `night-tables-by-source`, head
  `eafc26a5e`.

## What Willow reports (confirm each yourself; don't take it as read)

- `streetNightTablesForSource(source)` in `StreetNightTables.kt` is the one place the night pass picks its
  Street tables, through `streetUriOf`. `MapStyleReload` calls it.
- `NightTablesBySourceTest`, 3 tests: what each source chooses; v4 under the night topo; and a source check
  that `MapStyleReload` calls it once and never calls `streetNightTablesFor(`.
- Tests first at `094256be3`. Full CI run 41395980243, all jobs green.
- Revert check run 41395977468 on `night-tables-revert-check` (`80bbc697e`; branch since deleted from
  origin, SHA in `~/scratch/willow-deleted-branches-20261101.txt`) failed at `NightTablesBySourceTest.kt:37`,
  3 run, 1 failed.
- Written on `2bc8913f4`; merges clean into `pre-main` `6522e5d1e`. Not tested on a device.

## Questions

1. Is every night-table choice on the night path now routed through `streetNightTablesForSource`? Grep for
   any other caller of `streetNightTablesFor(` or a direct table pick.
2. Does it choose the same tables as before #464 for every source (v3, v4, Topographical, satellite,
   none)? Any behaviour change at all?
3. Is the source-text check robust (comments, renames, a second call through a helper), or easy to fool?
   Say whether a behavioural test would be better and whether that's blocking.
4. Run one revert check of your own (a fresh throwaway branch, CI only) and name the failing test line.
5. Is the diff confined to what S-1 needs?

## Bounds and verdict

- Read-only on the code under review. Work in a new worktree, e.g.
  `~/Forager/.claude/worktrees/sorrel-464`. Git over SSH was dropping tonight; use HTTPS or `gh`.
- **No heavy work on the Pi** (no local Gradle builds): the weekly rerun is running. Use CI for evidence.
- No merges, deploys, R2 calls or branch deletions. Name any throwaway branch you push in your verdict.
- Write the review on a new branch `sorrel-464-night-tables` in Forager, as
  `docs/reviews/2026-11-01-sorrel-464-night-tables.md`.
- **The verdict:** blocking / should-fix / notes, ending with "Is #464 mergeable into `pre-main` at
  <the head SHA you reviewed>?" Send it to Aspen with `mcp__claude-code-remote__send_message`
  (session `session_01Hqu21ntTjr3Lo2Pf81mxzk`).
