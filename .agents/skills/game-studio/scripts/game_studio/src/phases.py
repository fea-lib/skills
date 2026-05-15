"""Phase state machine: valid transitions, gate checks, and advancement logic."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .constants import PHASE_VALUES
from .errors import ValidationError
from .frontmatter import parse_frontmatter
from .state import parse_current_state_summary

# ---------------------------------------------------------------------------
# Transition map
# Each phase maps to the one or more phases it may advance into.
# 05-prototype-planning is optional so 04 may skip directly to 06.
# 07-change-control is a standing workflow that may be entered from any active
# phase but not used as a normal sequential target here.
# ---------------------------------------------------------------------------
VALID_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "01-idea-intake": ("02-vision-definition",),
    "02-vision-definition": ("03-concept-stress-test",),
    "03-concept-stress-test": ("04-pre-production-design",),
    "04-pre-production-design": ("05-prototype-planning", "06-production-planning"),
    "05-prototype-planning": ("06-production-planning",),
    "06-production-planning": ("08-implementation-support",),
    "07-change-control": ("08-implementation-support",),
    "08-implementation-support": (),
}

# Artefact that must be present with an approved (or approved-with-conditions)
# status before a phase may advance.  Keyed by the phase being LEFT.
GATE_ARTEFACT: dict[str, str] = {
    "01-idea-intake": "01-idea-brief.md",
    "02-vision-definition": "02-vision-brief.md",
    "03-concept-stress-test": "03-concept-stress-test.md",
    "04-pre-production-design": "04-design-package.md",
    "05-prototype-planning": "05-prototype-plan.md",
    "06-production-planning": "06-production-plan.md",
    "08-implementation-support": "07-change-decisions.md",
}

APPROVED_STATUSES: frozenset[str] = frozenset({"approved", "approved-with-conditions"})


@dataclass(frozen=True)
class PhaseInfo:
    current_phase: str
    valid_next_phases: tuple[str, ...]
    gate_artefact: str | None
    gate_artefact_status: str | None
    gate_met: bool


def _artefact_status(project_dir: Path, artefact_name: str) -> str | None:
    path = project_dir / artefact_name
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8")
    doc = parse_frontmatter(content)
    status = doc.data.get("status")
    return str(status) if status else None


def read_phase_info(project_dir: Path) -> PhaseInfo:
    current_state = project_dir / "00-current-state.md"
    summary = parse_current_state_summary(current_state)
    phase = summary.current_phase

    if phase is None or phase not in PHASE_VALUES:
        raise ValidationError(
            f"Cannot determine current phase from {current_state}. "
            "Run `artefact validate` to diagnose."
        )

    next_phases = VALID_TRANSITIONS.get(phase, ())
    gate_artefact_name = GATE_ARTEFACT.get(phase)
    gate_status: str | None = None
    gate_met = False

    if gate_artefact_name:
        gate_status = _artefact_status(project_dir, gate_artefact_name)
        gate_met = gate_status in APPROVED_STATUSES
    else:
        gate_met = True  # no gate required (e.g. 07-change-control standing workflow)

    return PhaseInfo(
        current_phase=phase,
        valid_next_phases=next_phases,
        gate_artefact=gate_artefact_name,
        gate_artefact_status=gate_status,
        gate_met=gate_met,
    )


def advance_phase(project_dir: Path, target_phase: str) -> str:
    """
    Advance the active phase to *target_phase*.

    Rules enforced:
    1. target_phase must be a valid transition from the current phase.
    2. The gate artefact for the current phase must have an approved status.

    Returns the new phase value on success.
    Raises ValidationError on any constraint violation.
    """
    info = read_phase_info(project_dir)

    if target_phase not in VALID_TRANSITIONS:
        raise ValidationError(
            f"Unknown phase: {target_phase!r}. "
            f"Allowed values: {', '.join(PHASE_VALUES)}"
        )

    if target_phase not in info.valid_next_phases:
        raise ValidationError(
            f"Cannot advance from {info.current_phase!r} to {target_phase!r}. "
            f"Valid next phases: {', '.join(info.valid_next_phases) or 'none (terminal phase)'}"
        )

    if not info.gate_met:
        raise ValidationError(
            f"Phase gate not met for {info.current_phase!r}. "
            f"Artefact {info.gate_artefact!r} must have an approved status "
            f"(current: {info.gate_artefact_status!r}). "
            "Obtain explicit human approval before advancing."
        )

    # Write the new phase into 00-current-state.md
    current_state = project_dir / "00-current-state.md"
    content = current_state.read_text(encoding="utf-8")

    # Replace the Phase: line inside the body
    updated_lines: list[str] = []
    replaced = False
    for line in content.splitlines():
        stripped = line.strip()
        if not replaced and stripped.startswith("Phase:"):
            updated_lines.append(f"Phase: `{target_phase}`")
            replaced = True
        else:
            updated_lines.append(line)

    if not replaced:
        raise ValidationError(
            "Could not locate 'Phase:' line in 00-current-state.md to update."
        )

    current_state.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")

    # Also update frontmatter updated_at
    from datetime import date
    doc = parse_frontmatter(current_state.read_text(encoding="utf-8"))
    fm = dict(doc.data)
    fm["updated_at"] = date.today().isoformat()
    from .frontmatter import render_frontmatter
    current_state.write_text(render_frontmatter(fm, doc.body), encoding="utf-8")

    return target_phase
