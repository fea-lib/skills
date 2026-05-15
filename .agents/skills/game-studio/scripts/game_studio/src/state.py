"""Project state reading helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import NotFoundError
from .frontmatter import FrontmatterDoc, parse_frontmatter


@dataclass(frozen=True)
class StateSummary:
    current_phase: str | None
    blocking_questions: list[str]
    accepted_risks: list[str]
    next_decision_required: str | None
    recommended_next_step: str | None


def read_markdown_frontmatter(path: Path) -> FrontmatterDoc:
    if not path.exists():
        raise NotFoundError(f"Required file not found: {path}")
    content = path.read_text(encoding="utf-8")
    return parse_frontmatter(content)


def _extract_after_label(body: str, label: str) -> str | None:
    marker = f"{label}:"
    for line in body.splitlines():
        if line.strip().startswith(marker):
            value = line.split(marker, 1)[1].strip().strip("`")
            return value or None
    return None


def _extract_under_heading(body: str, heading: str) -> str | None:
    lines = body.splitlines()
    wanted = f"## {heading}".strip()
    in_section = False
    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("## "):
            if in_section:
                break
            in_section = stripped == wanted
            continue
        if not in_section:
            continue
        if not stripped or stripped.startswith("<!--"):
            continue
        return stripped
    return None


def _extract_numbered_section_lines(body: str, heading: str) -> list[str]:
    lines = body.splitlines()
    wanted = f"## {heading}".strip()
    in_section = False
    collected: list[str] = []
    for raw in lines:
        line = raw.rstrip()
        if line.startswith("## "):
            if in_section:
                break
            in_section = line.strip() == wanted
            continue
        if not in_section:
            continue
        stripped = line.strip()
        if stripped.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
            value = stripped.split(".", 1)[1].strip()
            if value:
                collected.append(value)
    return collected


def parse_current_state_summary(path: Path) -> StateSummary:
    doc = read_markdown_frontmatter(path)
    body = doc.body
    current_phase = _extract_after_label(body, "Phase")
    blocking_questions = _extract_numbered_section_lines(body, "Blocking Questions")
    accepted_risks = _extract_numbered_section_lines(body, "Accepted Risks")
    next_decision_required = _extract_under_heading(body, "Next Decision Required")

    recommended_next_step = None
    lines = body.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == "## Recommended Next Step":
            for next_line in lines[idx + 1 :]:
                stripped = next_line.strip()
                if not stripped or stripped.startswith("<!--"):
                    continue
                if stripped.startswith("## "):
                    break
                recommended_next_step = stripped
                break
            break

    return StateSummary(
        current_phase=current_phase,
        blocking_questions=blocking_questions,
        accepted_risks=accepted_risks,
        next_decision_required=next_decision_required,
        recommended_next_step=recommended_next_step,
    )
