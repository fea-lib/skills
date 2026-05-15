from __future__ import annotations

import contextlib
import json
import unittest
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from game_studio.src.cli import main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _capture_json(argv: list[str]) -> dict:
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        rc = main(argv)
    return rc, json.loads(buf.getvalue())


def _base_args(workspace: str, project: str, docs_dir: str = "docs") -> list[str]:
    return ["--workspace", workspace, "--docs-dir", docs_dir, "--project", project]


def _init(workspace: str, project: str, docs_dir: str = "docs") -> int:
    return main(_base_args(workspace, project, docs_dir) + ["init"])


def _project_dir(workspace: str, project: str, docs_dir: str = "docs") -> Path:
    return Path(workspace) / docs_dir / "game-studio" / "projects" / project


# ---------------------------------------------------------------------------
# Original smoke tests (preserved)
# ---------------------------------------------------------------------------

class TestOriginalSmoke(unittest.TestCase):
    def test_init_validate_brief_happy_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "alpha"), 0)
            self.assertEqual(
                main(_base_args(tmpdir, "alpha") + ["artefact", "validate"]), 0
            )
            self.assertEqual(
                main(_base_args(tmpdir, "alpha") + ["brief", "create", "--slice-name", "Core Loop"]),
                0,
            )
            brief = _project_dir(tmpdir, "alpha") / "08-implementation-briefs" / "IMP-001-core-loop.md"
            self.assertTrue(brief.exists())

    def test_validate_rejects_invalid_status(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "beta"), 0)
            cs = _project_dir(tmpdir, "beta") / "00-current-state.md"
            cs.write_text(cs.read_text().replace("status: draft", "status: approved with conditions"))
            self.assertEqual(
                main(_base_args(tmpdir, "beta") + ["artefact", "validate"]), 1
            )

    def test_json_status_shape(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "gamma"), 0)
            rc, payload = _capture_json(
                _base_args(tmpdir, "gamma") + ["--json", "status"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["summary"]["current_phase"], "01-idea-intake")


# ---------------------------------------------------------------------------
# Phase show
# ---------------------------------------------------------------------------

class TestPhaseShow(unittest.TestCase):
    def test_phase_show_returns_current_phase(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "proj"), 0)
            rc, payload = _capture_json(
                _base_args(tmpdir, "proj") + ["--json", "phase", "show"]
            )
            self.assertEqual(rc, 0)
            self.assertEqual(payload["current_phase"], "01-idea-intake")
            self.assertIn("02-vision-definition", payload["valid_next_phases"])
            self.assertFalse(payload["gate_met"])  # 01-idea-brief.md is still draft

    def test_phase_show_gate_met_when_artefact_approved(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "proj"), 0)
            brief = _project_dir(tmpdir, "proj") / "01-idea-brief.md"
            brief.write_text(brief.read_text().replace("status: draft", "status: approved"))
            rc, payload = _capture_json(
                _base_args(tmpdir, "proj") + ["--json", "phase", "show"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["gate_met"])


# ---------------------------------------------------------------------------
# Phase advance
# ---------------------------------------------------------------------------

class TestPhaseAdvance(unittest.TestCase):
    def test_advance_blocked_when_gate_not_met(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "proj"), 0)
            rc = main(
                _base_args(tmpdir, "proj")
                + ["phase", "advance", "--to", "02-vision-definition"]
            )
            self.assertNotEqual(rc, 0)

    def test_advance_succeeds_when_gate_met(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "proj"), 0)
            brief = _project_dir(tmpdir, "proj") / "01-idea-brief.md"
            brief.write_text(brief.read_text().replace("status: draft", "status: approved"))

            rc, payload = _capture_json(
                _base_args(tmpdir, "proj")
                + ["--json", "phase", "advance", "--to", "02-vision-definition"]
            )
            self.assertEqual(rc, 0)
            self.assertEqual(payload["new_phase"], "02-vision-definition")

            # current-state.md must reflect the new phase
            rc2, status_payload = _capture_json(
                _base_args(tmpdir, "proj") + ["--json", "status"]
            )
            self.assertEqual(status_payload["summary"]["current_phase"], "02-vision-definition")

    def test_advance_rejects_invalid_transition(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "proj"), 0)
            brief = _project_dir(tmpdir, "proj") / "01-idea-brief.md"
            brief.write_text(brief.read_text().replace("status: draft", "status: approved"))
            rc = main(
                _base_args(tmpdir, "proj")
                + ["phase", "advance", "--to", "06-production-planning"]
            )
            self.assertNotEqual(rc, 0)


# ---------------------------------------------------------------------------
# Change request
# ---------------------------------------------------------------------------

class TestChangeRequest(unittest.TestCase):
    def test_change_request_appends_entry(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "proj"), 0)
            rc, payload = _capture_json(
                _base_args(tmpdir, "proj") + [
                    "--json", "change", "request",
                    "--title", "Add crafting mechanic",
                    "--description", "Player should be able to craft items at workbenches.",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertEqual(payload["chg_id"], "CHG-001")

            change_log = _project_dir(tmpdir, "proj") / "07-change-decisions.md"
            content = change_log.read_text()
            self.assertIn("CHG-001", content)
            self.assertIn("Add crafting mechanic", content)

    def test_change_request_increments_id(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "proj"), 0)
            main(_base_args(tmpdir, "proj") + [
                "change", "request", "--title", "First", "--description", "desc"
            ])
            rc, payload = _capture_json(
                _base_args(tmpdir, "proj") + [
                    "--json", "change", "request",
                    "--title", "Second",
                    "--description", "desc",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertEqual(payload["chg_id"], "CHG-002")


# ---------------------------------------------------------------------------
# Artefact create
# ---------------------------------------------------------------------------

class TestArtefactCreate(unittest.TestCase):
    def test_create_single_artefact(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "proj"), 0)
            # delete one artefact to re-create it
            target = _project_dir(tmpdir, "proj") / "04-design-package.md"
            target.unlink()
            self.assertFalse(target.exists())
            rc = main(
                _base_args(tmpdir, "proj")
                + ["artefact", "create", "--artefact", "04-design-package.md"]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(target.exists())

    def test_create_fails_if_exists_without_overwrite(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "proj"), 0)
            rc = main(
                _base_args(tmpdir, "proj")
                + ["artefact", "create", "--artefact", "04-design-package.md"]
            )
            self.assertNotEqual(rc, 0)


# ---------------------------------------------------------------------------
# Doctor
# ---------------------------------------------------------------------------

class TestDoctor(unittest.TestCase):
    def test_doctor_passes_on_clean_project(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "proj"), 0)
            rc = main(_base_args(tmpdir, "proj") + ["doctor"])
            self.assertEqual(rc, 0)

    def test_doctor_fails_on_missing_project(self) -> None:
        with TemporaryDirectory() as tmpdir:
            rc, payload = _capture_json(
                _base_args(tmpdir, "missing") + ["--json", "doctor"]
            )
            self.assertNotEqual(rc, 0)
            self.assertFalse(payload["ok"])
            codes = [i["code"] for i in payload["issues"]]
            self.assertIn("missing_project_dir", codes)

    def test_doctor_surfaces_gate_not_met(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "proj"), 0)
            rc, payload = _capture_json(
                _base_args(tmpdir, "proj") + ["--json", "doctor"]
            )
            # gate_not_met is a warning, not a hard issue — doctor should still pass
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            warn_codes = [w["code"] for w in payload.get("warnings", [])]
            self.assertIn("gate_not_met", warn_codes)


# ---------------------------------------------------------------------------
# Brief create sequencing
# ---------------------------------------------------------------------------

class TestBriefSequencing(unittest.TestCase):
    def test_brief_ids_increment_correctly(self) -> None:
        with TemporaryDirectory() as tmpdir:
            self.assertEqual(_init(tmpdir, "proj"), 0)
            main(_base_args(tmpdir, "proj") + ["brief", "create", "--slice-name", "First Slice"])
            main(_base_args(tmpdir, "proj") + ["brief", "create", "--slice-name", "Second Slice"])
            briefs_dir = _project_dir(tmpdir, "proj") / "08-implementation-briefs"
            files = sorted(briefs_dir.glob("IMP-*.md"))
            self.assertEqual(len(files), 2)
            self.assertTrue(files[0].name.startswith("IMP-001"))
            self.assertTrue(files[1].name.startswith("IMP-002"))


if __name__ == "__main__":
    unittest.main()
