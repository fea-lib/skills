"""Path resolution helpers for skill-local templates and target workspace projects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .constants import repo_root_from_file


@dataclass(frozen=True)
class StudioPaths:
    repo_root: Path
    templates_dir: Path
    docs_dir_in_workspace: Path
    project_dir: Path
    implementation_briefs_dir: Path


def resolve_paths(workspace: str, docs_dir: str, project_slug: str) -> StudioPaths:
    repo_root = repo_root_from_file()
    workspace_path = Path(workspace).expanduser().resolve()
    docs_dir_path = workspace_path / docs_dir
    project_dir = docs_dir_path / "game-studio" / "projects" / project_slug
    briefs_dir = project_dir / "08-implementation-briefs"
    templates_dir = repo_root / "references" / "templates"

    return StudioPaths(
        repo_root=repo_root,
        templates_dir=templates_dir,
        docs_dir_in_workspace=docs_dir_path,
        project_dir=project_dir,
        implementation_briefs_dir=briefs_dir,
    )
