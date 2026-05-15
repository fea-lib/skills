"""Deterministic v1 game-studio CLI entrypoint."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from .change_log import append_change_request
from .constants import CANONICAL_ARTEFACT_FILES, IMPLEMENTATION_BRIEF_DIR, PHASE_VALUES
from .errors import GameStudioError
from .paths import resolve_paths
from .phases import VALID_TRANSITIONS, read_phase_info, advance_phase
from .state import parse_current_state_summary, read_markdown_frontmatter
from .templates import create_implementation_brief, materialize_project_templates
from .validation import validate_project


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _json_out(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, indent=2) + "\n")


def _human_ok(message: str) -> None:
    sys.stdout.write(f"OK: {message}\n")


def _today() -> date:
    return date.today()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> int:
    paths = resolve_paths(args.workspace, args.docs_dir, args.project)
    created = materialize_project_templates(
        templates_dir=paths.templates_dir,
        project_dir=paths.project_dir,
        project_slug=args.project,
        today=_today(),
        overwrite=args.overwrite,
    )

    if args.json:
        _json_out(
            {
                "ok": True,
                "project_dir": str(paths.project_dir),
                "created": [str(p) for p in created],
                "implementation_briefs_dir": str(paths.implementation_briefs_dir),
            }
        )
    else:
        _human_ok(f"Initialized project at {paths.project_dir}")
        sys.stdout.write(f"Created {len(created)} artefact files\n")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    paths = resolve_paths(args.workspace, args.docs_dir, args.project)
    current_state_path = paths.project_dir / "00-current-state.md"
    summary = parse_current_state_summary(current_state_path)

    if args.json:
        _json_out(
            {
                "ok": True,
                "project_dir": str(paths.project_dir),
                "summary": asdict(summary),
            }
        )
    else:
        _human_ok(f"Loaded state from {current_state_path}")
        sys.stdout.write(f"Phase:                 {summary.current_phase or 'unknown'}\n")
        sys.stdout.write(f"Recommended next step: {summary.recommended_next_step or 'not set'}\n")
        if summary.blocking_questions:
            sys.stdout.write("Blocking questions:\n")
            for item in summary.blocking_questions:
                sys.stdout.write(f"  - {item}\n")
        else:
            sys.stdout.write("Blocking questions:    none\n")
        if summary.next_decision_required:
            sys.stdout.write(f"Next decision:         {summary.next_decision_required}\n")
    return 0


def cmd_phase_show(args: argparse.Namespace) -> int:
    paths = resolve_paths(args.workspace, args.docs_dir, args.project)
    info = read_phase_info(paths.project_dir)

    if args.json:
        _json_out(
            {
                "ok": True,
                "current_phase": info.current_phase,
                "valid_next_phases": list(info.valid_next_phases),
                "gate_artefact": info.gate_artefact,
                "gate_artefact_status": info.gate_artefact_status,
                "gate_met": info.gate_met,
            }
        )
    else:
        _human_ok(f"Current phase: {info.current_phase}")
        if info.valid_next_phases:
            sys.stdout.write(f"Valid next phases: {', '.join(info.valid_next_phases)}\n")
        else:
            sys.stdout.write("Valid next phases: none (terminal phase)\n")
        if info.gate_artefact:
            gate_status = info.gate_artefact_status or "missing"
            gate_flag = "PASS" if info.gate_met else "FAIL"
            sys.stdout.write(
                f"Gate: {info.gate_artefact} "
                f"[status={gate_status}] [{gate_flag}]\n"
            )
        else:
            sys.stdout.write("Gate: none required\n")
    return 0


def cmd_phase_advance(args: argparse.Namespace) -> int:
    paths = resolve_paths(args.workspace, args.docs_dir, args.project)
    new_phase = advance_phase(paths.project_dir, args.to)

    if args.json:
        _json_out({"ok": True, "new_phase": new_phase})
    else:
        _human_ok(f"Advanced to phase: {new_phase}")
    return 0


def cmd_artefact_validate(args: argparse.Namespace) -> int:
    paths = resolve_paths(args.workspace, args.docs_dir, args.project)
    result = validate_project(paths.project_dir)

    if args.json:
        _json_out(
            {
                "ok": result.ok,
                "project_dir": str(paths.project_dir),
                "issues": [
                    {
                        "code": issue.code,
                        "message": issue.message,
                        "path": str(issue.path) if issue.path else None,
                    }
                    for issue in result.issues
                ],
            }
        )
    else:
        if result.ok:
            _human_ok(f"Project is valid: {paths.project_dir}")
        else:
            sys.stdout.write(f"Validation failed for {paths.project_dir}\n")
            for issue in result.issues:
                sys.stdout.write(f"  - [{issue.code}] {issue.message}\n")

    return 0 if result.ok else 1


def cmd_artefact_create(args: argparse.Namespace) -> int:
    paths = resolve_paths(args.workspace, args.docs_dir, args.project)
    from .templates import _materialize_template

    target_file = args.artefact
    template_src = paths.templates_dir / target_file
    destination = paths.project_dir / target_file

    if destination.exists() and not args.overwrite:
        if args.json:
            _json_out({"ok": False, "error": f"{target_file} already exists. Use --overwrite to replace."})
        else:
            sys.stderr.write(f"ERROR: {target_file} already exists. Use --overwrite to replace.\n")
        return 1

    _materialize_template(template_src, destination, project_slug=args.project, today=_today())

    if args.json:
        _json_out({"ok": True, "created": str(destination)})
    else:
        _human_ok(f"Created artefact: {destination}")
    return 0


def cmd_change_request(args: argparse.Namespace) -> int:
    paths = resolve_paths(args.workspace, args.docs_dir, args.project)
    chg_id = append_change_request(
        project_dir=paths.project_dir,
        title=args.title,
        description=args.description,
        today=_today(),
    )

    if args.json:
        _json_out({"ok": True, "chg_id": f"CHG-{chg_id:03d}", "title": args.title})
    else:
        _human_ok(f"Appended CHG-{chg_id:03d} — {args.title}")
    return 0


def cmd_brief_create(args: argparse.Namespace) -> int:
    paths = resolve_paths(args.workspace, args.docs_dir, args.project)
    brief_path = create_implementation_brief(
        templates_dir=paths.templates_dir,
        project_dir=paths.project_dir,
        project_slug=args.project,
        slice_name=args.slice_name,
        today=_today(),
    )

    if args.json:
        _json_out({"ok": True, "brief_path": str(brief_path)})
    else:
        _human_ok(f"Created implementation brief: {brief_path}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    paths = resolve_paths(args.workspace, args.docs_dir, args.project)
    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    # 1. Templates dir exists
    if not paths.templates_dir.exists():
        issues.append({
            "code": "missing_templates_dir",
            "message": f"Templates directory not found: {paths.templates_dir}",
        })

    # 2. Project dir exists
    if not paths.project_dir.exists():
        issues.append({
            "code": "missing_project_dir",
            "message": f"Project directory not found: {paths.project_dir}. Run `init` first.",
        })
    else:
        # 3. Validate project layout and frontmatter
        result = validate_project(paths.project_dir)
        for issue in result.issues:
            issues.append({"code": issue.code, "message": issue.message})

        # 4. Phase consistency (gate_not_met is advisory — not a hard failure)
        current_state = paths.project_dir / "00-current-state.md"
        if current_state.exists():
            try:
                phase_info = read_phase_info(paths.project_dir)
                if not phase_info.gate_met:
                    warnings.append({
                        "code": "gate_not_met",
                        "message": (
                            f"Gate for phase {phase_info.current_phase!r} is not met. "
                            f"Artefact {phase_info.gate_artefact!r} has status "
                            f"{phase_info.gate_artefact_status!r}."
                        ),
                    })
            except GameStudioError as err:
                issues.append({"code": "phase_error", "message": str(err)})

        # 5. Briefs dir
        if not paths.implementation_briefs_dir.exists():
            issues.append({
                "code": "missing_briefs_dir",
                "message": f"Implementation briefs directory missing: {paths.implementation_briefs_dir}",
            })

    ok = len(issues) == 0

    if args.json:
        _json_out({
            "ok": ok,
            "issues": issues,
            "warnings": warnings,
            "project_dir": str(paths.project_dir),
        })
    else:
        if ok:
            _human_ok(f"All checks passed for project: {args.project}")
            if warnings:
                for w in warnings:
                    sys.stdout.write(f"  WARN [{w['code']}] {w['message']}\n")
        else:
            sys.stdout.write(f"Doctor found {len(issues)} issue(s) for project: {args.project}\n")
            for issue in issues:
                sys.stdout.write(f"  - [{issue['code']}] {issue['message']}\n")
            if warnings:
                sys.stdout.write(f"  {len(warnings)} warning(s):\n")
                for w in warnings:
                    sys.stdout.write(f"  WARN [{w['code']}] {w['message']}\n")

    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="game-studio",
        description="Game Studio CLI — deterministic workflow operations.",
    )
    parser.add_argument("--workspace", required=True, help="Target workspace root path")
    parser.add_argument(
        "--docs-dir", required=True, help="Docs directory, relative to --workspace"
    )
    parser.add_argument("--project", required=True, help="Project slug")
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Initialise project artefacts from templates")
    p_init.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing canonical artefacts"
    )
    p_init.set_defaults(handler=cmd_init)

    # status
    p_status = subparsers.add_parser("status", help="Show project state summary")
    p_status.set_defaults(handler=cmd_status)

    # phase
    p_phase = subparsers.add_parser("phase", help="Phase inspection and advancement")
    phase_sub = p_phase.add_subparsers(dest="phase_command", required=True)

    p_phase_show = phase_sub.add_parser(
        "show", help="Show current phase, valid next phases, and gate status"
    )
    p_phase_show.set_defaults(handler=cmd_phase_show)

    p_phase_advance = phase_sub.add_parser(
        "advance", help="Advance to the next phase (gate must be met)"
    )
    p_phase_advance.add_argument(
        "--to",
        required=True,
        choices=PHASE_VALUES,
        help="Target phase to advance into",
    )
    p_phase_advance.set_defaults(handler=cmd_phase_advance)

    # artefact
    p_artefact = subparsers.add_parser("artefact", help="Artefact operations")
    artefact_sub = p_artefact.add_subparsers(dest="artefact_command", required=True)

    p_artefact_validate = artefact_sub.add_parser(
        "validate", help="Validate canonical project layout and frontmatter"
    )
    p_artefact_validate.set_defaults(handler=cmd_artefact_validate)

    p_artefact_create = artefact_sub.add_parser(
        "create", help="Create or refresh a single artefact from its template"
    )
    p_artefact_create.add_argument(
        "--artefact",
        required=True,
        choices=CANONICAL_ARTEFACT_FILES,
        help="Artefact filename to create",
    )
    p_artefact_create.add_argument(
        "--overwrite", action="store_true", help="Overwrite if already exists"
    )
    p_artefact_create.set_defaults(handler=cmd_artefact_create)

    # change
    p_change = subparsers.add_parser("change", help="Change control operations")
    change_sub = p_change.add_subparsers(dest="change_command", required=True)

    p_change_request = change_sub.add_parser(
        "request", help="Append a CHG-XXX entry to 07-change-decisions.md"
    )
    p_change_request.add_argument("--title", required=True, help="Short title for the change")
    p_change_request.add_argument(
        "--description", required=True, help="What is being changed"
    )
    p_change_request.set_defaults(handler=cmd_change_request)

    # brief
    p_brief = subparsers.add_parser("brief", help="Implementation brief operations")
    brief_sub = p_brief.add_subparsers(dest="brief_command", required=True)

    p_brief_create = brief_sub.add_parser(
        "create", help="Create the next IMP-XXX brief from the template"
    )
    p_brief_create.add_argument(
        "--slice-name", required=True, help="Human-readable name for this slice"
    )
    p_brief_create.set_defaults(handler=cmd_brief_create)

    # doctor
    p_doctor = subparsers.add_parser(
        "doctor", help="Run diagnostics across config, layout, and project consistency"
    )
    p_doctor.set_defaults(handler=cmd_doctor)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return int(args.handler(args))
    except GameStudioError as err:
        if getattr(args, "json", False):
            _json_out({"ok": False, "error": str(err)})
        else:
            sys.stderr.write(f"ERROR: {err}\n")
        return 1
    except (FileNotFoundError, OSError) as err:
        if getattr(args, "json", False):
            _json_out({"ok": False, "error": str(err)})
        else:
            sys.stderr.write(f"ERROR: {err}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
