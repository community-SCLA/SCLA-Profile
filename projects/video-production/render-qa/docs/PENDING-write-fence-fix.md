# PENDING — the write fence is too tight on Bash. Fix is written and proven.

**Date:** 2026-08-04 · **Status:** ready to apply, BLOCKED on session type ·
**Owner action required:** relaunch Claude Code with `SCLA_SYSTEM_SESSION=1`.

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

This is the "too tight" failure mode, and it is the one that matters: a fence
that refuses ordinary read-only work is a fence somebody switches off. The
existing suite already asserts the fence is not too tight — it just did not
imagine these three shapes.

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

`verify_fence_fix.py` runs 21 cases against the LIVE fence and the FIXED one
side by side. Result: the 4 false positives become ALLOW, and **every** safety
case still BLOCKs — real redirects into fenced paths, `rm`/`mv`/`tee`/`sed -i`,
`git checkout`, `cp` INTO a fenced path, `mv` OUT of one, and all three
Write/Edit cases.

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
```

## Then delete this hand-off

`write-fence.fixed.sh`, `verify_fence_fix.py` and this file are a hand-off, not
a second source of truth. Once the fix is in `scripts/` and the cases are in
`test_write_fence.py`, `git rm` all three — a stale copy of a guard beside the
real one is exactly the drift this repo deletes rather than archives.
