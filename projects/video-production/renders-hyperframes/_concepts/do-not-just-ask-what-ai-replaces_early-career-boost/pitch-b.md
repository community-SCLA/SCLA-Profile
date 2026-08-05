# PITCH B — `do-not-just-ask-what-ai-replaces_early-career-boost`

**Lens: accumulation-first.** The build-up was designed before the object was
named. Working runtime ≈ **190s** (~468 narration words at the pinned voice,
plus the 1.8s final hold) — so the milestone marks below are 0:30 / 1:00 /
1:30 / 2:00 / 2:30 / ~3:10, and the four-frame test lands at ~0:47 / 1:35 /
2:22 / 3:10.

---

## The accumulation ladder

What the frame has physically **gained** at each mark. Every gain is geometry,
not a heading.

**By 0:30 — it has gained edges.** The frame opened as one unbroken solid with
faint dashed scoring drawn across it (the "will AI take my job?" reading: cut
lines on a thing about to be demolished). By 0:30 those dashed lines have been
re-drawn as real joints and the solid has come apart into discrete pieces. The
frame now has many outlines where it had one, and its silhouette is no longer a
rectangle. Nothing has left the frame — that is the point, and it is
load-bearing for the whole runtime.

**By 1:00 — it has gained a sort and a datum.** The loose pieces are no longer
a drift. A single horizontal rule has been drawn across the lower third, and
the pieces have moved to one side of it or the other: below the line, the ones
the narration says get done faster or cheaper; above it, the ones that become
more valuable as a result. The frame also gains its first lettering — only the
four words the script names at this point (judgment, relationships, creativity,
oversight) land on upper pieces.

**By 1:30 — it has gained thickness, and a worked example inside itself.** The
lower course flattens: those pieces lose height and stretch wide into thin
strips (the script's "less scarce"). The upper pieces grow taller and pick up a
second stroke. Then the drafting example is built out of the *same* masonry
rather than beside it — a "first draft" piece is drawn arriving and settling
into the thin lower strip, while three pieces rise out of that same example
into the thick upper course: what is worth saying, whether the work is good,
and who owns the relationship with the audience. The frame now reads at two
distinct weights.

**By 2:00 — it has gained a full inventory, and reaches maximum ink.** The
upper course, which held four labels at 1:00, now carries the whole durable set
the narration names — judgment, trust, communication, collaboration, ethical
choices, understanding what actually matters — and the thin lower strip gains
its own lettering: speed, repetition, summarizing, first drafts. Both courses
are fully lettered. This is the densest the frame ever is; every later gain is
structural, not textual.

**By 2:30 — it has gained connections.** For the first time in the runtime a
line crosses between the two courses. A four-stop path is drawn leaving the
upper course (a human question), dropping to the thin lower strip (an AI
draft), returning up (a human review) and closing at the top (a better result
than either would produce alone). Until this beat the two courses were a
comparison; after it they are one working thing.

**By ~3:10 — it has gained an opening, and the largest silhouette of the whole
video.** The upper pieces move outward and re-lay as two piers; the three
closing pieces the script names — judgment, range, tool fluency — become a
lintel across the top; the thin lower strip becomes the threshold; the
connecting path now runs around the doorframe. Between the piers is a clear
rectangular void. The frame is wider and taller than it has ever been, and
every piece that was in the opening solid is still visibly on screen, just
re-laid.

---

## The carrying object

**A single masonry slab labelled with one role, taken apart into its
task-bricks and re-laid, over the runtime, into a doorframe with an opening in
it.**

Drawn as flat rectangles only: each brick is a 4px-radius rectangle with a 2px
stroke and a near-transparent fill, height between roughly 28px and 72px, width
between roughly 90px and 260px, separated by a uniform 6px mortar gap; the
opening slab is one large rectangle with 2px dashed internal scoring; the datum
is a single 2px rule spanning most of the frame width; the connecting path is a
3px polyline with four small square nodes. Weight is the only encoding that
matters — a thin wide strip versus a tall double-stroked brick — so the two
courses stay legible as pure silhouette with the lettering covered. No
gradients, no shadows, no icons, no illustration beside the object: the masonry
*is* the illustration, and it uses the full canvas from 0:30 onward.

Per the motion rule, a brick moves exactly once per beat — one lay, one
migration, one thickening — and is pixel-static afterwards. That gives the
build a natural beat atom (one brick action = one idea), which is what carries
the ~8+ beats/min without splitting anything.

---

## Four frames

**25% (~0:47) — a scatter above an empty line.** No stacking anywhere. Fifteen-
to-twenty loose bricks drift across the upper two-thirds at mixed angles,
unlabeled, one of them held clearly apart from the rest. A single thin
horizontal rule is being drawn across the lower third with nothing on it yet.
The original slab is gone as a shape but present as its pieces.

**50% (~1:35) — a low flat strip, a short thick row, and one traveller.** Along
the bottom, a wide flat band of thin strips with a couple of labels. Above it,
a short but tall row of double-stroked bricks carrying four labels. Dead centre,
one brick mid-migration between the two — the only thing on the frame not yet
settled. The two courses are obviously different heights and obviously the same
material.

**75% (~2:22) — a dense two-tone wall with a line beginning to cross it.** The
upper course is at full height and fully lettered, edge to edge; the lower strip
is fully lettered and unmistakably thinner than anything above it. The first leg
of the connecting path has left the top course and is descending through the
mortar gap toward the strip. Maximum ink of the runtime; the eye has words to
read everywhere.

**100% (~3:10) — an aperture, not a wall.** Two piers, a three-brick lintel, a
threshold, the closed path running around the doorframe, and a clear void in the
middle where the wall used to be densest. The picture is now an opening you
could walk through, and it is the widest and tallest silhouette in the video.

Four silhouettes: rectangle → scatter → stratified wall → aperture. The shuffle
test is trivially passable from the pictures alone.

---

## The payoff beat

**The beat on "look for the openings instead of the threats" (~2:55).** The
upper course splits and moves outward into piers, the lintel drops in, and the
void appears. The re-read is the whole argument in one move: no brick left the
frame, so the opening was not made by anything being deleted — it was made by
the same pieces being re-laid. That is the script's "most roles are not deleted
— they are reshaped" restated as geometry, and it is only legible *because* the
viewer watched every brick arrive. The final beat (curiosity beats dread) holds
that completed doorframe still.

A second, smaller re-read runs underneath it: the "judgment" brick is laid at
1:00, thickened at 2:00, and ends up in the lintel at 3:10 — one piece with a
three-act life the viewer can trace backwards.

---

## Why this is not lazy

A builder cannot satisfy this with heading swaps against a static prop, for five
mechanical reasons:

1. **The silhouette is contracted at four different shapes.** Rectangle, scatter,
   stratified wall, aperture. A static prop has exactly one silhouette, so a
   heading-swap build fails the four-frame test on the first pair compared.
2. **Brick conservation is a per-beat constraint on element identity, not on
   copy.** Every brick that leaves a position must be visible in a new one, and
   the closing frame must contain everything the opening slab contained. That
   constraint cannot be met by adding text; it forces the builder to track and
   move real elements.
3. **Three milestones change no copy at all.** The thickness differential
   (1:30), the example brick's migration (1:35) and the connecting path (2:30)
   are geometry-only gains. If the builder leaves the masonry alone and swaps
   headings, the 1:30 and 2:00 frames are the same picture and the flatness is
   immediately visible on the contact sheet.
4. **The copy budget is fixed by the narration, so there are no spare headings
   to swap.** Every label on every brick is a word the script actually says
   (judgment / relationships / creativity / oversight; speed / repetition /
   summarizing / first drafts; judgment / trust / communication / collaboration
   / ethical choices / what actually matters; judgment / range / tool fluency;
   the four stops of the loop). Nothing on frame states a count, a total, or an
   ordering the narration does not state. With the text locked, the only degree
   of freedom left to the builder is the masonry itself.
5. **The payoff requires a void.** You cannot produce an aperture by relabeling
   a wall — you have to physically move the piers apart. The last milestone is
   unfakeable by construction.

Risk to watch: the brick field must read as masonry texture, never as an
enumeration — no on-frame count, no numbering, irregular widths — or it starts
implying "a role has N tasks", which the script never says.
