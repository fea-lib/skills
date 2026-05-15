"""Shared constants for the game studio CLI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

STATUS_VALUES: tuple[str, ...] = (
    "draft",
    "approved",
    "approved-with-conditions",
    "rework-required",
    "rejected",
    "parked",
)

PHASE_VALUES: tuple[str, ...] = (
    "01-idea-intake",
    "02-vision-definition",
    "03-concept-stress-test",
    "04-pre-production-design",
    "05-prototype-planning",
    "06-production-planning",
    "07-change-control",
    "08-implementation-support",
)

CANONICAL_ARTEFACT_FILES: tuple[str, ...] = (
    "00-current-state.md",
    "00-risk-register.md",
    "01-idea-brief.md",
    "02-vision-brief.md",
    "03-concept-stress-test.md",
    "04-design-package.md",
    "05-prototype-plan.md",
    "06-production-plan.md",
    "07-change-decisions.md",
)


@dataclass(frozen=True)
class TemplateMapping:
    source_template: str
    target_file: str


TEMPLATE_MAPPINGS: tuple[TemplateMapping, ...] = (
    TemplateMapping("00-current-state.md", "00-current-state.md"),
    TemplateMapping("00-risk-register.md", "00-risk-register.md"),
    TemplateMapping("01-idea-brief.md", "01-idea-brief.md"),
    TemplateMapping("02-vision-brief.md", "02-vision-brief.md"),
    TemplateMapping("03-concept-stress-test.md", "03-concept-stress-test.md"),
    TemplateMapping("04-design-package.md", "04-design-package.md"),
    TemplateMapping("05-prototype-plan.md", "05-prototype-plan.md"),
    TemplateMapping("06-production-plan.md", "06-production-plan.md"),
    TemplateMapping("07-change-decisions.md", "07-change-decisions.md"),
)

IMPLEMENTATION_BRIEF_TEMPLATE = "08-implementation-brief.md"
IMPLEMENTATION_BRIEF_DIR = "08-implementation-briefs"


def repo_root_from_file() -> Path:
    # constants.py lives at:
    # .agents/skills/game-studio/scripts/game_studio/src/constants.py
    # We want the skill root:
    # .agents/skills/game-studio/
    return Path(__file__).resolve().parents[3]
