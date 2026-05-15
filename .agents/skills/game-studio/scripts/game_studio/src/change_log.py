"""Append a CHG-XXX entry to 07-change-decisions.md."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from .errors import NotFoundError

_ENTRY_TEMPLATE = """
---

### CHG-{num:03d} — {title}

**Date:** {today}
**Requested by:** human
**Status:** `draft`

#### Requested Change
{description}

#### Impacted Artefacts
1.

#### Role Assessments

**Producer** (always):
- Scope impact:
- Sequencing impact:
- Recommendation:

#### Orchestrator Synthesis

#### Recommendation
Recommendation:
Reasoning:

#### Alternatives

Alternative A:
Trade-offs:

#### Decision
Decision:
Decided by:
Conditions (if any):

#### Artefacts Updated
1.

#### Risk Register Updates
1.
"""


def _next_chg_id(content: str) -> int:
    ids = re.findall(r"###\s+CHG-(\d{3})\s+", content)
    if not ids:
        return 1
    return max(int(i) for i in ids) + 1


def append_change_request(
    project_dir: Path,
    title: str,
    description: str,
    today: date,
) -> int:
    change_log = project_dir / "07-change-decisions.md"
    if not change_log.exists():
        raise NotFoundError(
            f"07-change-decisions.md not found in {project_dir}. "
            "Run `init` first or create the artefact."
        )

    content = change_log.read_text(encoding="utf-8")
    chg_id = _next_chg_id(content)
    entry = _ENTRY_TEMPLATE.format(
        num=chg_id,
        title=title,
        today=today.isoformat(),
        description=description,
    )

    updated = content.rstrip() + "\n" + entry.lstrip("\n")
    change_log.write_text(updated, encoding="utf-8")
    return chg_id
