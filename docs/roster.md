# Forager roster

Who does what, where work goes, and which session holds each role. Times are PT.

Drafted 2026-11-03 14:25 PST from the 11-01 Aspen handoff, the records on `main`, and the session list
read at 14:25. **Owner to confirm** marks a line that no ruling in this repo covers.

## Roles

| Name | Role | Reports to |
|---|---|---|
| Aspen Meridian | Pi planner (this repo) | the owner |
| Willow Quadrat | Pi coder | Aspen |
| Rowan Waymark | app planner (Forager repo) | the owner |
| Sorrel Tally | reviewer | whoever sent the review |
| Sage Wayfinder | designer, design only | Aspen |
| Juniper | research and comparisons | owner to confirm |
| Hazel | Forager coder (app, Worker) | Rowan |
| Alder | owner to confirm | owner to confirm |

- **Aspen** plans Pi work, writes dispatches, and writes this repo's record (owner, 10-22). Merges Forager
  PRs after Sorrel's OK (owner, 11-01: "I'll leave the merging to you for the time being"). Starts builds.
  Doesn't code.
- **Willow** runs dispatches: build steps, tests, uploads with a go. Doesn't merge or write the record.
  The 11-01 Willow session couldn't touch `/opt` or start builds; Aspen did those.
- **Rowan** plans the app and keeps Forager's record (`records-after-173`), including every merge into
  `pre-main` and `main`. Holds `pre-main` merges until the owner lifts that. Per the 11-01 handoff, Rowan's
  coders don't merge.
- **Sorrel** reviews PRs and says mergeable or not, with revert checks. Doesn't merge.
- **Sage** does design only: map character, colours, previews on real tiles.
- **Juniper** did the elevation sizing (RECORD -1501) and the zoom comparison (coder-13 Z1). The 10-30
  handoff says "the Forager planner (Juniper / Sorrel)". Owner to confirm the role.
- **Hazel** writes Worker and app changes in the Forager repo, through Rowan.
- **Alder** isn't in this repo's records. Its one session (10-25) was waiting on a height-data sign-up on
  the laptop. Owner to confirm the role.

## Where work goes

- Pi builds, tiles, uploads, R2, routing squares: Aspen plans, Willow runs.
- App code, releases, Forager's record: Rowan. Worker and app code goes through Rowan to Hazel.
- PR reviews: Sorrel. With no Sorrel session, a helper briefed as Sorrel (as on 11-03 01:15).
- Design and style: Sage. Design helpers are briefed as Sage Wayfinder.
- Research and comparisons: Juniper.
- Before any merge into Forager `pre-main` or `main`: one line to Rowan first (11-03).
- Uploads, installs, build starts, deletions and merges: the owner's go first.

## Sessions (read 2026-11-03 14:25 PST)

Send with `mcp__claude-code-remote__send_message` to the session id.

- **Aspen:** `session_01Hqu21qbkj6LhoAGQLgXLj4`, running (opened 11-02 12:55).
- **Willow:** `session_01Hqu21r21FGQXWzLeRtR3yv`, idle, the most recently active Willow (last 11-03
  10:16). Two older Willow sessions are idle too, `session_01Hqu21n3VSBieRY3s57PyLD` and
  `session_01Hqu21qBFb5b4scLRXKqSQs`. Owner to confirm which is current.
- **Rowan:** `session_01Hqu21q3Gcwz48bSJpYkUEp`, waiting on the owner (last 11-03 14:23). The 10-26
  Rowan, `session_01G24bZzkbEC1T4tzDQisDds`, has failed; don't send there.
- **Sorrel:** `session_01Hqu21obr8SqgUyvBhiTw6o`, idle (last 11-02 21:00). At 11-03 01:15 it couldn't
  be reached, and a helper did the review.
- **Juniper:** `session_01Hqu21oansrXBVEfzvrbt17`, idle (last 11-02 14:55).
- **Sage, Hazel:** no session by either name among the 33 most recent. Sage runs as a helper; Hazel
  works through Rowan.
- **Alder:** `session_01ExhkVf2ZVytf4RtvGdugNs`, idle (last 10-26 10:23 PDT).

Not roles: the owner's side chats from the phone, like the one that drafted this file.

## Keeping it current

- Before a dispatch, check the session list. If it differs from this file, fix the file first.
- When a role moves to a new session, change its line above and add a dated line below.
- Session pointers in memory defer to this file.

## Changes

- 2026-11-03 14:25 PST: drafted in the owner's side chat; waiting on the owner's OK.
