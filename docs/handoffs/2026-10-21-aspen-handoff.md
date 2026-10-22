# Handoff from Aspen Meridian (Pi planner), 2026-10-21, about 18:30 PDT

This was written at the owner's request ("Write everything we talked about in a hand off. I'm going
to bring this to another account and I'll pick it up from there"). It is **not committed**: under
the 2026-10-21 ruling ("Go ahead and use coders to commit") the planner commits nothing. If it
should be on record, a Pi coder copies it into `pi-build`.

Everything below was read from the Pi at the time stated. Treat it as a claim about that moment and
re-read the machine before acting on it.

## Who picks this up

The Pi planner, Aspen Meridian. Read `docs/process/pi-planner-profile.md` on `origin/pi-build`
first. The local `pi-build` ref in the bridge worktree is stale (`412fb852`, 2026-10-04).
`origin/pi-build` was at `961a90d3` (dispatch pi-28) when this was written. The planner plans,
asks, records and reviews. Coders edit, run, commit and push, and only on the owner's go.

## 1. The map build finished and is published

- **Unit:** `forager-usca-build-261017-4r` (dispatch pi-23: `build-usca.sh --local 261017`, four
  regions, tracks from z11, paths from z12). It started at 04:14:29 PDT and exited 0 at 17:06:26
  PDT, after 12h52m.
- **`status-usca.json`:** `state: ok`, `stage: done`, `warnings: []`, run `usca-20261021T111429Z`,
  OSM timestamp 2026-10-17T20:20:51Z.
- **Output:** `/srv/forager-build/out-usca/current` →
  `20261017T202051Z-usca-20261021T111429Z`.
  - `forager-usca.pmtiles` is 34,141,705,380 bytes, written 12:54.
  - There are 187 `.rd5` routing squares in `segments/`.
  - Bounds: `-180.0,15.92097,180.0,85.04032`.
  - Regions sequence: `us:2415, canada:4945, us/puerto-rico:3281, us/us-virgin-islands:1790`.
- **Validate stage:** "zooms 0-15, 9 layers, roads carries all six trail keys". All 9 sample points
  were covered: Seattle, Miami, Anchorage, Honolulu, Toronto, Whitehorse, St. John's, San Juan and
  Charlotte Amalie, with 34 to 165 roads each.
- **The full log** is `/srv/forager-build/logs/usca-20261021T111429Z.log`. It is also in
  `journalctl -u forager-usca-build-261017-4r`.

**Planetiler data errors.** These are geometry-repair counters, and validation still passed:

| Counter | Count |
|---|---|
| `render_snap_fix_input` | 18,979,934 |
| `osm_boundary_missing_way` | 26,605 |
| `merge_snap_fix_input` | 1,510 |
| `osm_multipolygon_missing_way` | 1,011 |
| everything else | under 300 each |

**Not compared** against the previous run, so whether these counts are normal for this input is
**not determined**. That comparison belongs in the pi-23 build's audit record.

**An older memory kill.** `dmesg` shows an OOM kill of `osmium` (pid 31182, uid 995, 7.1 GB
resident) at about 18.75 hours of uptime. The Pi has been up more than 3 days, so it is from an
earlier run, not this build. Which run it was is **not traced**.

**The planner was not watching this build.** The bridge session the owner opened did not know the
build existed. It first reported CI status instead, and found the build only when the owner said
"The map build. You're supposed to be watching it". The build was launched from another session
(`cse_016asu…`). Lesson: a handoff or memory entry should name any running unit, so the next
planner session can find it.

## 2. The previous release: the owner's decisions

- **Deleted locally.** The publish step logged `removed old output 20261017T202051Z`, which is the
  build that pi-19 uploaded. The only other basemap on the Pi is
  `/srv/forager-build/kept-usca/usca-20261019T011311Z` (32 GB). That is a failed run: it has a
  `FAILED.txt`.
- **Question 1, keep the last good release?** The owner: "1 keep it for now. Upload the successful
  one to cloudflare". The planner then pointed out that the only remaining copy of the previous
  release is the live `us.pmtiles` on R2, and asked how to save it before overwriting. The owner
  chose **"Don't keep it"**: overwrite with no backup.
  - The two readings sit uneasily together. "Keep it for now" may have been about future builds'
    rotation policy, which is still unchanged: `build-usca.sh` publish still deletes the previous
    output.
  - **Open:** confirm with the owner whether to change the rotation policy. That would be a coder
    dispatch on `map-build/`.
- **Question 2, delete the failed 2026-10-19 kept basemap (32 GB)?** The owner: "2 hold for now".
  Leave it in place.

## 3. Upload to Cloudflare: drafted, not started, and the owner said stop

The owner then said "Hold on, stop before doing anything". **Nothing was uploaded, started or
changed.** Dispatch pi-29, below, was shown to the owner in chat only. It was not sent to any coder
by the planner. Whether the owner pasted it anywhere is **not known**, so ask.

**State of R2 before any upload,** from pi-19's record, not re-read today:

- Bucket `forager-maps`.
- `us.pmtiles` is 33,973,424,728 bytes. That is the 20261017T202051Z build, uploaded 2026-10-21
  06:04Z.
- The Worker is `forager-pmtiles`. The app reads
  `https://forager-pmtiles.brandonlee1-894.workers.dev/us.json`, so overwriting `us.pmtiles`
  changes what the app gets, with no app change.
- The Worker has no route for `.rd5` squares, so the upload covers the map tiles only.

**Network at about 18:20 PDT.**

- The default route is `wlan0` (metric 600), with the Bluetooth tether `bnep0` (750) behind it.
- A 2-ping test to 1.1.1.1 lost 1 of 2 packets.
- The link logger (`/tmp/pi19-link.sh`, writing `~/pi19-logs/link.log`) logged `route=bnep0` at
  00:51Z and 01:01Z, so Wi-Fi was flaky.
- Earlier the same session, `gh` failed with "no route to host".
- Fix used before: `nmcli radio wifi off`, then `on`, a rescan, then
  `nmcli con up Virusdownloader`. The owner manages the network.

**The draft dispatch pi-29,** as shown to the owner. It needs the owner's go before it reaches a
coder. It reuses pi-19's successful upload command (read from the sudo journal), changing only the
source and the unit name:

```
Dispatch pi-29: upload the 261021 US + Canada map to Cloudflare R2 (from Aspen Meridian, Pi planner)

The owner, 2026-10-21, verbatim: "Upload the successful one to cloudflare". On keeping the
previous release first: "Don't keep it". The live us.pmtiles is overwritten with no backup.

Work on branch pi-build. Records go in docs/audits/2026-10-20-cloudflare-upload-prep.md as a new
appended section; preserve this dispatch at prompts/preserved/2026-10-21-pi-29.md.

PREP (read-only), then report and ask the owner before any non-read action:
1. Confirm the file: /srv/forager-build/out-usca/current/forager-usca.pmtiles, expected
   34,141,705,380 bytes, run usca-20261021T111429Z (status-usca.json: state ok, stage done).
   Record its sha256 and that `current` resolves to
   20261017T202051Z-usca-20261021T111429Z.
2. Read the live object: `rclone lsl r2:forager-maps/us.pmtiles` (expected 33,973,424,728
   bytes, from pi-19) and `rclone backend list-multipart-uploads r2:forager-maps` (expected []).
3. Network: `ip route show default`, a 10-ping to 1.1.1.1, and wlan0 bitrate/signal. Report them.
   Do not change the Pi's network.
4. Confirm no other heavy job is running (no planetiler/osmium/brouter/rclone process).
5. Report all of this, then ask the owner for the go to start the unit below.

ON THE OWNER'S GO, start a fresh transient unit, using the command pi-19's successful run used,
with only the source and the unit name changed:
  systemd-run --unit=forager-pi29-us-upload --description='Forager pi-29: copyto 261021
  forager-usca.pmtiles -> r2:forager-maps/us.pmtiles (owner, 2026-10-21)' --uid=bwann83
  --gid=bwann83 -p RemainAfterExit=yes -p Nice=10 --setenv=HOME=/home/bwann83
  --setenv=RCLONE_CONFIG=/home/bwann83/.config/rclone/rclone.conf
  /usr/bin/rclone copyto /srv/forager-build/out-usca/current/forager-usca.pmtiles
  r2:forager-maps/us.pmtiles --s3-no-check-bucket --s3-chunk-size 16M --s3-upload-concurrency 2
  --retries 1 --low-level-retries 20 --timeout 2m --log-file /home/bwann83/pi29-logs/us-upload.log
  --log-level INFO --stats 60s --stats-log-level NOTICE --stats-one-line

WATCHING: the unit stays "active (exited)" after a clean exit (RemainAfterExit=yes), so read
ExecMainStatus and the main PID, not is-active. Also watch the log for ERROR lines.

IF IT FAILS: report and do nothing. Do not restart, retry, stop or delete anything without the
owner's go. Record the error lines, the network at that moment, and list-multipart-uploads.

AFTER A CLEAN EXIT, check and record (every HTTP request cache-busted with a query string):
- R2 size equals the local size (rclone lsl against stat).
- list-multipart-uploads returns [].
- https://forager-pmtiles.brandonlee1-894.workers.dev/us.json?cb=<unique>: 200, z0-15, `roads`
  lists the six trail keys.
- One trail tile at z15, e.g. 15/5303/11553: 200, x-forager-origin r2, and identical to the local
  archive's tile once both are decompressed.
- A z11 tile with a track and a z12 tile with a path appear (the pi-23 zoom change), each
  matching the local archive.
State plainly anything not checked (edge caches may serve old tiles for up to a day).

Then write the record section, commit and push to pi-build.

If anything is ambiguous, you find a better way, or something doesn't work how we want it, for
any reason: stop and ask the owner. Don't assume; asking is encouraged. No building of any kind.
```

**Notes for the next planner on this draft:**

- **`pi29-logs/` may not exist.** The coder should create it before starting the unit, or rclone
  may fail to open the log file. This was not checked in the draft.
- **The z11 and z12 tile checks name no tiles yet.** The coder has to pick tiles that are known to
  hold a track and a path.
- **Pi-19's upload took about 6 to 8 hours over Wi-Fi.** It survived one Wi-Fi drop because its
  connections moved interfaces. It reported 33.6 GiB sent for a 31.6 GiB file, and the cause of the
  extra was not determined.
- **What happens if the upload dies partway** was not verified. pi-19 inferred that
  `rclone copyto` writes the object only when the multipart upload completes, so the old
  `us.pmtiles` stays live until the new one is whole.

## 4. Other things seen, not acted on

- **CI on `pre-main`** is green through the PR #372 merge (run 39664469294, success). `main` was
  last seen at `381515c6` (the PR #357 merge). The newer `pre-main` work has not been promoted.
  Whether `main` CI is green is **not checked**, because the network was down.
- **The basemap jar build at 03:01 today** (`/tmp/pi23-jarbuild.log`) ran 29 tests with 0 failures.
  It installed `/opt/forager-build/basemap/protomaps-basemap-HEAD-with-deps.jar`, sha256
  `7f9c4aef942b3688980bfe91a67e455eb1bc59115a4b5a37ddee41d7ed98f8db`.
- **The audit record for the pi-23 build's finish has not been written.** It should cover the result
  above, the data-error comparison, and the deleted previous output. It is a coder dispatch.

## Open questions for the owner

1. Was the pi-29 draft sent anywhere? Is the go still on to upload, and is "don't keep" still the
   ruling?
2. Should the build keep its previous published output from now on? That means a change to
   `build-usca.sh` publish, on `pi-build`.
3. The failed 2026-10-19 kept basemap (32 GB): it is on hold, to be ruled on later.
4. Should this handoff be committed to `pi-build` by a coder?
