# PENDING — the write fence is too tight on Bash. Fix is written and proven.

**Date:** 2026-08-04 · **Status:** ready to apply, BLOCKED on session type ·
**Owner action required:** relaunch Claude Code with `SCLA_SYSTEM_SESSION=1`.

**Third session (2026-08-04, the one that built the Phase 3 pilot) re-probed
and DOWNGRADED the urgency.** The flag is still unset (`SCLA_SYSTEM_SESSION=[]`)
and a `touch` under `scripts/` is still refused as designed, so the fix still
cannot be applied from a build session. But the second session's "shipping-path
block" was **wrong and is withdrawn** — see defect 3. The pilot built and
synthesized end to end with the fence live and unmodified. The fix is unchanged
and still worth applying; it buys back ordinary diagnosis, not the pipeline.

This is BUILD-PLAN step 2.1's open defect, carried out of the session that
installed the fence. The fence works — it blocks every write it should. It also
blocks a class of writes it should not, and it cannot repair itself, because
`scripts/` is one of the paths it fences.

---

## The defect

`scripts/write-fence.sh` grades a Bash call by scanning the RAW command string.
Two consequences, both wrong, both observed live within minutes of install:

1. **Payload text is read as command.** A `git commit` whose MESSAGE merely
   mentions a mutator word near a fenced path is refused, though it writes
   nothing fenced. The commit describing the fence's own probe was blocked —
   and so, later, was the patch that would have fixed this.
2. **Any `>` is read as a redirect into danger.** The check asked *does a
   redirect exist*, not *what does it write to*. So `2>/dev/null` — which
   writes to `/dev/null` — put the whole command into "scan every token" mode,
   and any fenced path mentioned as a READ argument was then refused.
   `env | sed 's/=.*/=<set>/' ; head -20 scripts/with-secrets.sh` was blocked by
   a `>` that was inside a quoted sed replacement and was not a redirect at all.

3. **~~The credential path is fenced~~ — CORRECTED 2026-08-04.** An earlier
   session claimed the fence blocks the shipping path, because
   `scripts/with-secrets.sh` is both the mandatory Infisical entry point and a
   fenced token. **That claim was wrong and is withdrawn.** It rested on a
   command form the procedure does not use: the documented TTS call passes its
   output path as a FLAG, not a shell redirect —

   ```
   bash scripts/with-secrets.sh node <media-skill>/scripts/audio.mjs \
     --request ./audio_request.json --hyperframes . --out ./audio_meta.json \
     --only tts --provider heygen --voice <id>
   ```

   With no `>` anywhere, `DESTRUCTIVE|REDIRECT|SED_INPLACE|GIT_MUTATE` all miss,
   the token scan never runs, and the fence exits 0. Confirmed twice on
   2026-08-04: the payload was graded by the live `write-fence.sh` (exit 0), and
   then the real call ran and synthesized 17 clips with `HEYGEN_API_KEY` from
   Infisical. **The fence has never blocked TTS.**

4. **What IS true: any redirect at all poisons an otherwise read-only command.**
   Two live false positives, both observed while building the Phase 3 pilot,
   both on commands that WRITE NOTHING FENCED:

   ```
   ls .claude/skills/hyperframes-media/ 2>/dev/null
   python3 render-qa/src/preflight.py <ws> > <scratchpad>/pf.txt
   ```

   The first is a bare `ls`. The second redirects into a NON-fenced scratch
   path and is refused purely because `preflight.py` appears as a read
   argument — so **the fence currently refuses to let you capture any gate's
   own output to a file.** That is the strongest case for the fix: not that the
   pipeline cannot run, but that ordinary diagnosis cannot.

This is the "too tight" failure mode, and it is the one that matters: a fence
that refuses ordinary read-only work is a fence somebody switches off. The
existing suite already asserts the fence is not too tight — it just did not
imagine these shapes.

## The fix (written, proven, not applied)

Two changes, both narrowing what is treated as a command:

- **Data is not command.** Strip heredoc bodies and `-m`/`-F`/`--message`
  arguments before any matching.
- **A redirect is graded by WHAT IT WRITES TO.** Extract each redirect's actual
  target and fence-check that, instead of letting the mere presence of `>` widen
  the scan.

Nothing about the fenced set, the default-deny posture, or the
`SCLA_SYSTEM_SESSION` opt-out changes.

## Evidence

`verify_fence_fix.py` runs 24 cases against the LIVE fence and the FIXED one
side by side. Result: the 5 false positives become ALLOW, and **every** safety
case still BLOCKs — real redirects into fenced paths, `rm`/`mv`/`tee`/`sed -i`,
`git checkout`, `cp` INTO a fenced path, `mv` OUT of one, all three Write/Edit
cases, and the direct counterpart to FP4 (`with-secrets.sh env > scripts/…`,
which must stay blocked and does).

```
PASS — every case correct after the fix, and no safety case regressed
```

## To apply (needs a flagged session)

```bash
# 1. Relaunch Claude Code (or a shell) with the system flag:
export SCLA_SYSTEM_SESSION=1

# 2. Put the proven script in place:
cp projects/video-production/render-qa/docs/write-fence.fixed.sh \
   scripts/write-fence.sh
chmod +x scripts/write-fence.sh

# 3. Re-prove it, then confirm the existing suite is still green:
python3 projects/video-production/render-qa/docs/verify_fence_fix.py
python3 projects/video-production/render-qa/tests/run_tests.py
bash scripts/lint-refs.sh

# 4. Fold the regressions into the permanent suite so they cannot come back.
#    render-qa/tests/ is NOT fenced, but these cases FAIL against the unfixed
#    fence, so they belong in the same commit as the fix — never before it.
```

Add to `render-qa/tests/test_write_fence.py`:

```python
print("== data is not command, and a redirect is graded by its TARGET ==")
check("a commit whose MESSAGE names a fenced path is ALLOWED",
      allowed("Bash", {"command":
              "git commit -F - <<'MSG'\n"
              "a probe write under scripts/ was blocked\n"
              "we ran touch scripts/__fence_probe to verify\n"
              "MSG"}))
check("`2>/dev/null` on a read-only command naming a fenced path is ALLOWED",
      allowed("Bash", {"command":
              "python3 projects/video-production/render-qa/src/check_ink.py "
              "frames 2>/dev/null"}))
check("a '>' inside a quoted sed replacement is not a redirect",
      allowed("Bash", {"command":
              "env | sed 's/=.*/=<set>/' ; head -20 scripts/with-secrets.sh"}))
check("but a REAL redirect into a fenced path is still blocked",
      blocked("Bash", {"command": "echo x > scripts/batch-ship.sh"}))
check("...and a redirect into a WORKSPACE file is still allowed",
      allowed("Bash", {"command":
              "echo x > projects/video-production/renders-hyperframes/"
              "m2_demo/timing.json"}))

print("== the credential path: with-secrets.sh is fenced AND mandatory ==")
check("TTS via with-secrets, redirecting into the build's OWN workspace",
      allowed("Bash", {"command":
              "bash scripts/with-secrets.sh node audio.mjs --provider heygen "
              "> projects/video-production/renders-hyperframes/"
              "m2_demo/audio_meta.json"}))
check("a credentialed publish with 2>/dev/null is ALLOWED",
      allowed("Bash", {"command":
              "bash scripts/with-secrets.sh bash scripts/wistia-upload.sh "
              "out.mp4 2>/dev/null"}))
check("but leaking the injected env INTO a fenced path is still blocked",
      blocked("Bash", {"command":
              "bash scripts/with-secrets.sh env > scripts/leaked.env"}))

print("== FP6/FP7: read-only commands, observed live on 2026-08-04 ==")
check("a bare `ls` of a fenced dir with 2>/dev/null is ALLOWED",
      allowed("Bash", {"command":
              "ls .claude/skills/hyperframes-media/ 2>/dev/null"}))
check("capturing a GATE's own output to a non-fenced scratch path is ALLOWED",
      allowed("Bash", {"command":
              "python3 projects/video-production/render-qa/src/preflight.py "
              "projects/video-production/renders-hyperframes/m2_demo "
              "> /tmp/pf.txt"}))
check("...but writing INTO the gate directory is still blocked",
      blocked("Bash", {"command":
              "echo x > projects/video-production/render-qa/src/preflight.py"}))

print("== the documented TTS form has no redirect and must stay ALLOWED ==")
check("audio.mjs --out (a flag, not a redirect) through with-secrets",
      allowed("Bash", {"command":
              "bash scripts/with-secrets.sh node m/scripts/audio.mjs "
              "--request ./audio_request.json --hyperframes . "
              "--out ./audio_meta.json --only tts --provider heygen"}))
```

## Then delete this hand-off

`write-fence.fixed.sh`, `verify_fence_fix.py` and this file are a hand-off, not
a second source of truth. Once the fix is in `scripts/` and the cases are in
`test_write_fence.py`, `git rm` all three — a stale copy of a guard beside the
real one is exactly the drift this repo deletes rather than archives.
