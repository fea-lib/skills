"""Minimal YAML-frontmatter parsing and serialization for markdown artefacts."""

from __future__ import annotations

import re
from dataclasses import dataclass

FRONTMATTER_BOUNDARY = "---"


@dataclass(frozen=True)
class FrontmatterDoc:
    data: dict[str, object]
    body: str


def _parse_scalar(value: str) -> object:
    text = value.strip()
    if text == "":
        return ""
    if text in {"[]"}:
        return []
    if text in {"{}"}:
        return {}
    if text in {"true", "false"}:
        return text == "true"
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return text


def parse_frontmatter(content: str) -> FrontmatterDoc:
    lines = content.splitlines()
    if len(lines) < 3 or lines[0].strip() != FRONTMATTER_BOUNDARY:
        return FrontmatterDoc(data={}, body=content)

    try:
        end_idx = lines.index(FRONTMATTER_BOUNDARY, 1)
    except ValueError:
        return FrontmatterDoc(data={}, body=content)

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])

    data: dict[str, object] = {}
    current_key: str | None = None
    for raw_line in fm_lines:
        line = raw_line.rstrip()
        if not line:
            continue
        if line.lstrip().startswith("#"):
            continue

        if line.startswith("  - ") and current_key:
            existing = data.setdefault(current_key, [])
            if isinstance(existing, list):
                existing.append(_parse_scalar(line[4:]))
            else:
                data[current_key] = [_parse_scalar(line[4:])]
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.rstrip()
        current_key = key
        parsed_value = _parse_scalar(value)
        data[key] = parsed_value

    return FrontmatterDoc(data=data, body=body)


def _serialize_value(value: object, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, list):
        if not value:
            return [f"{prefix}[]"]
        lines: list[str] = []
        for item in value:
            if isinstance(item, (list, dict)):
                raise ValueError("Nested lists or dicts are not supported in frontmatter")
            lines.append(f"{prefix}- {item}")
        return lines
    if isinstance(value, dict):
        if not value:
            return [f"{prefix}{{}}"]
        raise ValueError("Dict frontmatter values are not supported in this parser")
    if value is None:
        return [prefix]
    return [f"{prefix}{value}"]


def render_frontmatter(data: dict[str, object], body: str) -> str:
    lines: list[str] = [FRONTMATTER_BOUNDARY]
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            list_lines = _serialize_value(value, indent=2)
            lines.extend(list_lines)
        else:
            scalar = _serialize_value(value)[0]
            lines.append(f"{key}: {scalar}".rstrip())
    lines.append(FRONTMATTER_BOUNDARY)
    if body:
        lines.append(body)
    return "\n".join(lines).rstrip() + "\n"
