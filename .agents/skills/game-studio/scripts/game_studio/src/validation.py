"""Validation for project layout and machine-facing frontmatter contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .constants import (
    CANONICAL_ARTEFACT_FILES,
    IMPLEMENTATION_BRIEF_DIR,
    PHASE_VALUES,
    STATUS_VALUES,
)
from .errors import ValidationError
from .frontmatter import parse_frontmatter
from .state import parse_current_state_summary


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    path: Path | None = None


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    issues: list[ValidationIssue]


def _validate_file_exists(project_dir: Path, file_name: str) -> ValidationIssue | None:
    path = project_dir / file_name
    if not path.exists():
        return ValidationIssue(
            code="missing_file",
            message=f"Missing required artefact: {file_name}",
            path=path,
        )
    return None


def _validate_frontmatter_status(path: Path) -> ValidationIssue | None:
    content = path.read_text(encoding="utf-8")
    doc = parse_frontmatter(content)
    status = doc.data.get("status")
    if not isinstance(status, str) or status not in STATUS_VALUES:
        return ValidationIssue(
            code="invalid_status",
            message=(
                f"Invalid status in {path.name}: {status!r}. "
                f"Allowed: {', '.join(STATUS_VALUES)}"
            ),
            path=path,
        )
    return None


def _validate_current_phase(project_dir: Path) -> ValidationIssue | None:
    current_state = project_dir / "00-current-state.md"
    summary = parse_current_state_summary(current_state)
    phase = summary.current_phase
    if phase is None:
        return ValidationIssue(
            code="missing_phase",
            message="Current state does not define an active phase.",
            path=current_state,
        )
    if phase not in PHASE_VALUES:
        return ValidationIssue(
            code="invalid_phase",
            message=(
                f"Invalid active phase {phase!r}. "
                f"Allowed: {', '.join(PHASE_VALUES)}"
            ),
            path=current_state,
        )
    return None


def validate_project(project_dir: Path) -> ValidationResult:
    issues: list[ValidationIssue] = []

    for file_name in CANONICAL_ARTEFACT_FILES:
        issue = _validate_file_exists(project_dir, file_name)
        if issue:
            issues.append(issue)

    briefs_dir = project_dir / IMPLEMENTATION_BRIEF_DIR
    if not briefs_dir.exists() or not briefs_dir.is_dir():
        issues.append(
            ValidationIssue(
                code="missing_dir",
                message=f"Missing required directory: {IMPLEMENTATION_BRIEF_DIR}",
                path=briefs_dir,
            )
        )

    if issues:
        return ValidationResult(ok=False, issues=issues)

    for file_name in CANONICAL_ARTEFACT_FILES:
        file_path = project_dir / file_name
        issue = _validate_frontmatter_status(file_path)
        if issue:
            issues.append(issue)

    phase_issue = _validate_current_phase(project_dir)
    if phase_issue:
        issues.append(phase_issue)

    return ValidationResult(ok=(len(issues) == 0), issues=issues)


def ensure_valid_project(project_dir: Path) -> None:
    result = validate_project(project_dir)
    if result.ok:
        return
    messages = [issue.message for issue in result.issues]
    raise ValidationError("; ".join(messages))
