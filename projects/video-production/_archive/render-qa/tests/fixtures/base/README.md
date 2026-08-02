# tests/fixtures/base/scenes.json

The 20-scene 2026-07-29 `better-decisions-come-from-better-criteria` plan — the
only real full-length gate-clean plan that exists.

**Status: `gate-clean, pending owner sign-off`. NEVER "approved."** No
owner-approved plan exists to use here: all six published videos predate
`build_index.py` and had no `scenes.json` at all. This fixture is the base for
`tests/test_mutations.py`, and that use does not require sign-off — the
assertions are differential (rule R fires on the mutant AND does not fire on
this baseline), so what matters is that the baseline is gate-clean, not that a
human liked it.

**The plan is stored; the workspace is not.** `build_index.py` compiles this
against the LIVE `design-system/` on every run. A frozen *workspace* would
hard-fail `composition_freshness` within 24h and would be graded against a
snapshot of `design-contract.md`; a frozen *plan* tracks live templates by construction,
so a template edit that breaks this plan shows up as a red test rather than as
a fixture that quietly diverges from the system it is meant to represent.
