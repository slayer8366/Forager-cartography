# Weekly basemap build timer enabled

Written by the planner session `forager-cartography-7b`, 2026-10-22. Times are PDT.

## Go

- **The owner, in Rowan's window, relayed:** "Turn on weekly (Recommended)". It answered "The weekly
  map build has never been scheduled; builds are run by hand. What should happen?"
- **Confirmed in the planner's session,** after the planner described the schedule, the run length,
  that the build does not upload, and the disk position: "Yes, enable it".

## Done, at about 13:10

- `sudo systemctl enable --now forager-build.timer`: "Created symlink
  /etc/systemd/system/timers.target.wants/forager-build.timer".
- `is-enabled`: enabled. `is-active`: active.
- **The timer, as written** (`/etc/systemd/system/forager-build.timer`):
  - `OnCalendar=Sun *-*-* 10:00:00 UTC`;
  - `RandomizedDelaySec=30min`;
  - `Persistent=true`.
  - The drop-in `forager-build.timer.d/` sets `Unit=forager-build-usca.service`, the US + Canada
    build.
- **Next run** (`systemctl list-timers`): **Sun 2026-10-25 03:24:55 PDT**.
  - It lists a previous trigger at Sun 2026-10-18 03:15:13 PDT, from before the timer was
    disabled.
  - Enabling it started no catch-up run: `forager-build-usca.service` stayed inactive.

## What a run does

Read: `/opt/forager-build/map-build/bin/build-usca.sh` and `pins.env`.

- **No new extract:** if the extracts match `out-usca/current/manifest.json`, the run logs "nothing
  to do" and exits (lines 547-554).
- **Not enough disk:** `run_disk_check` checks free space on the NVMe (Planetiler's need, 157.0 GB
  last run) and on the microSD card `/mnt/archive/forager-build` (download plus merge). It runs
  twice: at line 581, before downloading, and at line 650, before Planetiler.
  - If either check is short, it calls `die "not enough room: ..."`.
  - The exit trap records the status as failed, keeps the run's outputs in `failed-usca/latest`,
    logs "previous outputs untouched", and removes scratch (lines 155-166).
  - So it stops before Planetiler writes anything. The live output and its `current` link are not
    touched. Extracts already downloaded to the card stay there.
- **On success:** it publishes a new `out-usca/<name>`, swaps `current`, and then removes the old
  output (`USCA_KEEP_GOOD_OUTPUTS=1`).
  - It does not upload to R2. `r2:forager-maps/us.pmtiles` changes only on a separate upload with
    the owner's go.
  - **After the first new run, the Pi no longer holds a copy of what is live on R2** (the 261021
    output is removed).
- **Disk at enabling:** 162.94 GB free on the NVMe (need 157.0 GB) and 94 GB free on the card.
  - That's about 6 GB of NVMe headroom.
  - The planner watches it, per the owner's option text.
