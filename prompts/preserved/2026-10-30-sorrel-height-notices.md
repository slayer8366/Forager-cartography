# Review dispatch 2026-10-30-sorrel-notices: height notices and the committed upload script

From Aspen to Sorrel Tally. Written 2026-10-30 at about 23:30 PDT. There's no deadline: the install
waits until after Sunday 11-01's run, and needs the owner's go.

## The go and the background

- **Willow's dispatch:** `prompts/preserved/2026-10-30-coder-04-height-notices.md`.
- **The owner, in Aspen's window:**
  - "Build writes them, from next run (Recommended)";
  - then, after Willow found that map-build has no upload step: "A: commit an upload script
    (Recommended)".
- **The wording:** Juniper's report, Forager `juniper-nrcan-credit` at `355933b4d`, rows 1-3. The US line
  is Juniper's row 3, so it matches the app's Heights credits.

## Baseline

- **The branch:** Forager `pi-height-notices` at `3d5e0d90e`, off `pi-build` `a5bcb0780` (installed).
  The tests-first commit is `487dc5182`.
- **Willow's evidence:**
  - test_run_record 16 (5 new);
  - usca_functions 87 (4 new);
  - test_upload_routing 17 (new);
  - the rest unchanged and green;
  - revert: the manifest moved first, and U1 and U2 fail.

## Questions

1. **The text.** Is `map-build/notices/routing-NOTICE.txt` verbatim to Juniper's rows (en dash,
   "programme", years)? Is the inline OGL link a fair reading of the licence's "where possible, provide
   a link"?
2. **The R2 manifest.** Does `run_record.py routing-manifest` write exactly the shape the Worker's
   `parseManifest` accepts, plus additive fields only? Check it against the hand-staged
   `routing/manifest.json` from the 261026 upload (`/mnt/archive/aspen-upload-261026/manifest.json`):
   the same files, sizes and sha256 for the same output.
3. **The upload script.** Does `upload-routing.sh` refuse before any upload when anything mismatches?
   Is the manifest always last, and never sent after a failed read-back? Is `--dry-run` truly
   side-effect free?
4. Does `stage_routing_set` at publish stop a run cleanly if it fails, without leaving a half-published
   output?
5. Are the Worker and the app unaffected by the new fields?
6. Run one revert check of your own.

## Bounds and verdict

- Read-only. No uploads, and no live R2 or rclone calls except a read-only `lsl` if needed.
- Write the review on a new branch `sorrel-height-notices`, as
  `docs/reviews/2026-10-30-sorrel-height-notices.md`.
- **The verdict:** blocking / should-fix / notes, ending with "Is pi-height-notices mergeable for
  install after Sunday's run?" Send it to Aspen.
