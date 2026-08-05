# Script State Contract

The filesystem owns lesson state:

```text
inbox/<stem>.txt      raw or awaiting refinement
ready/<stem>.txt      approved narration, eligible to build
workspace/<stem>/     claimed production state
published/<stem>.txt  shipped narration record
```

- Named-stem work touches only that stem.
- Program and whole-queue selection require explicit batch scope.
- Never infer a transition from prose or a generated status document.
- Never move a blocked or failed script merely to make the queue look clean.
- Publishing retains current MP4 naming and Wistia ledger behavior.
- Agents read live state with `run.sh status --json`.
