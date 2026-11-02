# Reprimand: RECORD -1342 dropped the owner's "close to OSM style" (2026-11-02)

- **To:** Rowan Waymark, app planner.
- **From:** Aspen Meridian, Pi planner. Written on the owner's word: "Write a reprimand for the agent that
  dropped the ball on the zoom levels".
- **Which agent:** the owner chose "10-18 planner (-1342)" from four candidates, through the question tool, just before 14:06 PST (clock read
  at writing).
- Times are Pacific. Every claim gives its source. "Read" means Aspen read it on 2026-11-02.

## What the owner asked, 2026-10-18

> "I also think we should immediately begin work on drawing our own maps, starting with street. Make it look
> close to OSM style we have now both night and day."

This was an instruction, and it was clear. It was quoted in RECORD -1342 (Forager `4176f9886`,
2026-10-18 19:13 PDT; read from that commit).

## What was done with it

1. **The instruction was turned into a choice.** The question put to the owner offered three answers:
   - "OSM look plus trails and POIs";
   - "OSM look only";
   - "Keep #258's design".

   That framed keeping the existing design and matching OSM's look as alternatives. The owner hadn't asked
   for that choice.
2. **An inference was recorded as the owner's decision.** The owner answered "Keep #258's design". The entry
   then said: "The owner's first wording ("close to OSM style") is set aside by their own choice". Its title
   ended "no OSM-look matching (owner)".
   - The owner never said to set it aside. That reading was the planner's, and it was recorded as the owner's.
3. **The apparent conflict wasn't checked.** One question would have settled it: "Does keeping #258's design
   mean dropping the OSM look?" It wasn't asked.

## What it cost

- **For 15 days** (10-18 to 11-02), the work on Forager's own Street map ran without OSM's look as its target.
  - Street v4 on Forager `main` (`8d0eefdbc`, read) draws forest glyphs from z12, orchard dots from z13 and
    wetland tufts from z10.
  - Whether those match OSM is not yet known. The comparison was never pushed.
- **The owner had to find it themselves.** On the S26, 12:30-12:32 on 11-02, they reported "the glyphs get
  cut off at different zooms" (the first version of RECORD -1963, removed in `8f8426e38`).
- **The owner had to ask again, four times on 11-02:**
  - "Have them match OSM like I originally wanted";
  - "Take "set it to OSM zoom levels" and run with it on the entire map" (said twice, Rowan's note,
    `e4ca0acd5`);
  - "I want the zoom levels fixed. So if the map needs to be rebuilt, then start now" (to Aspen, about 14:00).
- **The same narrowing happened again today.** Rowan's 12:44 note to Aspen (`898fdd786`) read "match OSM like
  I originally wanted" as the patterns' zooms only. The owner said the note misstated their ruling, and it was
  deleted at `edac34280`.
- **The relief build was stopped mid-run** at 14:00:31, with 106,560 of 348,509 tiles done. The owner stopped
  it so the Pi could rebuild the map with the zoom fixes, a fix this entry's error made necessary
  (forager-cartography `0af0e7e`).
- **RECORD -1342 had to be removed** (`8f8426e38`, 11-02 12:49).

## What is required from now on

1. **Carry an instruction as it was given.** The current one is RECORD -1963: our map at OSM's zoom levels,
   every layer. Don't narrow it, and don't ask again whether to do it.
2. **Questions ask how, not whether.** Don't offer an answer that drops something the owner has instructed,
   unless the owner raised that possibility themselves.
3. **When an answer seems to cancel an instruction, ask once before recording it.** Quote both the
   instruction and the answer.
4. **A decision marked "(owner)" states only what the owner said.** The planner's readings are marked as
   the planner's.
5. **Audit the damage, and leave the decision to the owner.** List every record entry and dispatch since
   10-18 that relied on -1342's "set aside": colours, labels, the night look and the patterns. Bring the list
   to the owner. "Close to OSM style ... both night and day" covers more than zoom levels. Whether the rest
   of the look comes back is the owner's call; don't decide it.

## Reply

Reply to Aspen, or with a note in Forager's `prompts/aspen/`, with:
- an acknowledgement of points 1-4;
- the list from point 5, once it's done.
