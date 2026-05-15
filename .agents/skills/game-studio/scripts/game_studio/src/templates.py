"""Template materialization for game studio canonical artefacts."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from .constants import IMPLEMENTATION_BRIEF_TEMPLATE, TEMPLATE_MAPPINGS
from .errors import NotFoundError
from .frontmatter import parse_frontmatter, render_frontmatter


def _materialize_template(
    template_path: Path,
    destination_path: Path,
    project_slug: str,
    today: date,
) -> None:
    if not template_path.exists():
        raise NotFoundError(f"Template not found: {template_path}")

    content = template_path.read_text(encoding="utf-8")
    doc = parse_frontmatter(content)
    fm = dict(doc.data)
    if "project" in fm and isinstance(fm["project"], str):
        fm["project"] = project_slug
    if "updated_at" in fm:
        fm["updated_at"] = today.isoformat()

    rendered = render_frontmatter(fm, doc.body)
    rendered = rendered.replace("<project-slug>", project_slug)
    rendered = rendered.replace("<phase>", "01-idea-intake")

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    destination_path.write_text(rendered, encoding="utf-8")


def materialize_project_templates(
    templates_dir: Path,
    project_dir: Path,
    project_slug: str,
    today: date,
    overwrite: bool,
) -> list[Path]:
    created: list[Path] = []
    for mapping in TEMPLATE_MAPPINGS:
        src = templates_dir / mapping.source_template
        dst = project_dir / mapping.target_file
        if dst.exists() and not overwrite:
            continue
        _materialize_template(src, dst, project_slug=project_slug, today=today)
        created.append(dst)
    briefs_dir = project_dir / "08-implementation-briefs"
    briefs_dir.mkdir(parents=True, exist_ok=True)
    return created


def create_implementation_brief(
    templates_dir: Path,
    project_dir: Path,
    project_slug: str,
    slice_name: str,
    today: date,
) -> Path:
    briefs_dir = project_dir / "08-implementation-briefs"
    briefs_dir.mkdir(parents=True, exist_ok=True)

    existing = sorted(briefs_dir.glob("IMP-*.md"))
    next_id = len(existing) + 1
    num = f"{next_id:03d}"
    normalized_slice = "-".join(slice_name.strip().lower().split())
    brief_filename = f"IMP-{num}-{normalized_slice}.md"
    destination_path = briefs_dir / brief_filename

    template_path = templates_dir / IMPLEMENTATION_BRIEF_TEMPLATE
    _materialize_template(
        template_path,
        destination_path,
        project_slug=project_slug,
        today=today,
    )

    content = destination_path.read_text(encoding="utf-8")
    content = content.replace("IMP-<XXX>", f"IMP-{num}")
    content = content.replace("<Slice Name>", slice_name)
    destination_path.write_text(content, encoding="utf-8")

    return destination_path
