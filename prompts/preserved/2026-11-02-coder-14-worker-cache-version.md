# Dispatch 2026-11-02-coder-14: the Worker's cache gets a version, and stops keeping "Archive not found"

- **From:** the Pi planner, Aspen (`session_01Hqu21qbkj6LhoAGQLgXLj4`).
- **To:** Willow Quadrat (`session_01Hqu21r21FGQXWzLeRtR3yv`).
- Written 2026-11-02, finished at the commit's clock time. Report times in Pacific, read from the clock.

## The go

- **The owner, at about 20:2x PST, with three S26 screenshots from 20:22 (Estacada):** "The relief looks great when
  it's applied. Some tiles aren't rendering at the same zoom level as others. All relief should rendering at the
  same zoom level. And then some doesn't even render at all".
- **Then, through the question tool:** "Yes, fix it now (Recommended)". The option read:
  - add a cache version to the Worker's cache key, and stop caching 'Archive not found', with tests;
  - Sorrel reviews, then it's released to main;
  - Aspen raises the version again after tomorrow's us.pmtiles upload.

## Premises (read by Aspen at 20:25-20:30; confirm each)

1. **Cached 404s.** The Worker serves 404s cached before `relief.pmtiles` reached R2 (20:13:18).
   - Requested without a query string at 20:25, these answered `404 17B`, `cf-cache-status: HIT`:

     | Tile | Age |
     |---|---|
     | `/relief/9/82/183.png` | 60,932 s |
     | `/relief/10/163/368.png` | 61,024 s |
     | `/relief/10/164/368.png` | 28,519 s |
     | `/relief/11/327/734.png` | 54,784 s |
     | `/relief/11/327/735.png` | 40,647 s |

   - Their neighbours answered 200 image/png.
   - MapLibre draws a parent tile where a child is missing (inferred). That explains "not the same zoom level".
2. **The cache code.** `server/pmtiles-worker/src/index.ts` on main `8d0eefdbc`:
   - The tile path reads `caches.default.match(request.url)` (about line 528).
   - `cacheableResponse()` sets `Cache-Control: env.CACHE_CONTROL || "public, max-age=86400"` and puts every
     response in the cache by `request.url`, whatever its status (about line 552).
   - That includes `cacheableResponse("Archive not found", …, 404)` (about line 640) and the 204 for an empty tile.
   - The asset and style path does the same with its own cache control (about lines 455-472, `ASSET_CACHE_CONTROL`,
     7 days).
3. **The same flaw will hide tomorrow's street map.**
   - Tile URLs don't change when `us.pmtiles` is replaced, so the cached old tiles are served for up to a day after
     the upload (inferred from 2).
4. **Main and pre-main** have identical `server/pmtiles-worker` folders (`git diff --stat`, empty, at 20:28).
   - Cloudflare Workers Builds deploys main's folder on every push to main.
   - A Worker release is a `worker/*` PR to main that makes the folder equal pre-main's and changes nothing else.
   - `worker-release.yml` and `worker-folder-guard.yml` enforce that, with `tools/check-release.sh`.
5. **`wrangler.toml` `[vars]`** holds `ALLOWED_ORIGINS`, and the code reads `env.CACHE_CONTROL`. There's no cache
   version var yet.

## The change (in `server/pmtiles-worker` only)

1. **A cache version.**
   - Every `caches.default` key the tile path and the asset path use becomes `request.url` plus the version.
   - Build it with one function, for example a `cv=<CACHE_VERSION>` query parameter added to a copy of the URL,
     and don't change the request itself.
   - The version is `env.CACHE_VERSION`, default `"1"`.
   - Add `CACHE_VERSION = "2"` to `wrangler.toml` `[vars]`, with a comment: raise it to make the Worker ignore every
     tile and asset it cached before (owner, 2026-11-02).
   - Leave the routing handler's cache and the internal build-URL key (about line 179) as they are, and say so
     in the report.
2. **"Archive not found" is never cached.**
   - That 404 is returned with `Cache-Control: no-store`, and with no `cache.put`.
   - Other statuses are kept as they are, including the 204 for an empty tile in an existing archive.
3. **Nothing else changes.** No other behaviour, headers or routes.

## Tests that can fail (in `server/pmtiles-worker/test/`, beside the existing ones)

1. A 404 "Archive not found" isn't put in the cache, and is sent with `no-store`.
2. The same URL and the same version give a cache hit on the second request.
3. A response cached under version 1 isn't served when the version is 2; the archive is read again.
4. A cached 404 from before (under the old key, the plain URL) isn't served after this change.
5. **Revert check:** with change 1 or change 2 reverted, the matching test fails with a message naming it. Show
   the output.
- The whole Worker suite passes. Show the counts before and after.

## Process

1. **On pre-main:** a branch `worker-cache-version` from origin/pre-main, then a PR to pre-main. CI must be green.
2. **Review:** Aspen asks Sorrel (the reviewer) to review that PR. Address any must-fix items.
3. **The release:** after Sorrel passes it and Aspen merges it to pre-main, a `worker/cache-version` PR to main that
   makes the folder equal pre-main's. The release guard must be green.
   - Aspen merges it, on the owner's go above. That deploys the Worker.
4. **Holds:**
   - **Hold A:** the pre-main PR is open and green. Report it with the PR link and the test output, then stop.
   - **Hold B:** the release PR to main is open and green. Report, then stop.

## Bounds

- **Change nothing outside `server/pmtiles-worker`.** No merge to main or pre-main yourself.
- **No R2 writes,** and no requests to the Worker beyond what the tests do.
- **The Pi is building the map** (Planetiler, run `usca-20261103T030317Z`), with the overnight upload chain to follow.
  - `npm test` for the Worker is fine. No Planetiler, osmium or other heavy jobs.
  - Don't touch `/srv/forager-build`, `/opt/forager-build`, `/mnt/archive/aspen-upload-us-zoomfix` or
    `/mnt/storage/relief`.
- **On any failed check or surprise,** stop and report.

## Report

At each hold:
- mark each claim observed, read or inferred;
- give the commits and PR links;
- say what you didn't check;
- include a Conventions line naming the neighbouring tests and code you followed.
