# Run Folder Contract

Every `/research` run writes to one local folder and execution writes only inside
that folder.

Default path:
- `<workspace-root>/docs/research/<run-slug>/`

## Required Artifacts

| File | Purpose |
|---|---|
| `brief.md` | Normalized brief, defaults, assumptions, source/tool policy |
| `state.json` | Machine-readable graph state, node statuses, dependencies |
| `source-inventory.md` | Source list with metadata and quality notes |
| `notes/` | Per-source notes and extracted evidence |
| `evaluation.md` | Quality-gate outcomes and unresolved quality issues |
| `final-report.md` | Final report for the user |
| `run-log.md` | Timeline of major steps, checkpoints, and completion status |
| `deferred-decisions.md` | Required only in AFK mode |

## `state.json` Minimum Shape

```json
{
  "run_id": "2026-05-29-my-topic",
  "question": "...",
  "depth": "standard",
  "checkpoint_mode": "default",
  "status": "running",
  "created_at": "2026-05-29T12:00:00Z",
  "updated_at": "2026-05-29T12:34:00Z",
  "nodes": [
    {
      "id": "n-001",
      "type": "discovery",
      "title": "Discover primary sources for subquestion A",
      "status": "complete",
      "depends_on": [],
      "artifacts": ["notes/s1.md"],
      "blocked_reason": null
    }
  ]
}
```

Status values:
- `pending`
- `running`
- `blocked`
- `skipped`
- `complete`

## Resume Rules

- Completed nodes remain complete unless explicitly invalidated.
- Blocked nodes keep their `blocked_reason`.
- Resume from the frontier of `pending`/`blocked` nodes.
- Keep `run-log.md` append-only.

## `run-log.md` Event Pattern

Use concise chronological entries:

```markdown
- 2026-05-29T12:00:00Z: Run initialized (depth=standard, mode=default)
- 2026-05-29T12:01:20Z: Discovery branch A started
- 2026-05-29T12:03:54Z: Checkpoint opened: material scope expansion
- 2026-05-29T12:08:10Z: Checkpoint resolved: approved
- 2026-05-29T12:22:44Z: Quality gates completed (1 warning)
- 2026-05-29T12:25:00Z: Run completed
```
