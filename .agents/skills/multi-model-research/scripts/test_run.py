#!/usr/bin/env python3
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import run


def test_emit_subagent_cmd_includes_timeout_and_separator():
    cmd = run.emit_subagent_cmd(
        model="provider/model",
        prompt_file=Path("/tmp/prompt.md"),
        input_files=[Path("/tmp/input.md")],
        output_file=Path("/tmp/out.md"),
        timeout_ms=600000,
    )

    assert "--timeout 600000" in cmd
    assert " -- \"Write your output to /tmp/out.md\"" in cmd


def test_model_selection_and_list_models(monkeypatch, capsys):
    models_output = "anthropic/claude-sonnet-4\nopenai/gpt-4o\nopenai/o3\n"
    selected = run.select_default_models(models_output)
    assert len(selected) == 2
    assert any("claude" in m.lower() for m in selected)
    assert any("gpt" in m.lower() or m.lower().startswith("openai/o") for m in selected)

    monkeypatch.setattr(run.sys, "stdin", io.StringIO(models_output))
    run.cmd_list_models(SimpleNamespace())
    out = capsys.readouterr().out.strip()
    parsed = json.loads(out)
    assert parsed == ["anthropic/claude-sonnet-4", "openai/gpt-4o", "openai/o3"]


def test_list_defaults_uses_config_first(tmp_path, monkeypatch, capsys):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("models:\n  - m1\n  - m2\n")
    monkeypatch.setattr(run, "CONFIG_PATH", cfg)
    monkeypatch.setattr(run.sys, "stdin", io.StringIO("ignored\n"))

    run.cmd_list_defaults(SimpleNamespace())
    out = capsys.readouterr().out.strip()
    assert out == "m1,m2"


def test_cmd_config_set_and_show(tmp_path, monkeypatch, capsys):
    cfg = tmp_path / "config.yaml"
    monkeypatch.setattr(run, "CONFIG_PATH", cfg)

    run.cmd_config(SimpleNamespace(set="a,b", show=False))
    assert cfg.read_text() == "models:\n  - a\n  - b\n"

    run.cmd_config(SimpleNamespace(set=None, show=True))
    out = capsys.readouterr().out
    assert "Configured models (2):" in out
    assert "- a" in out
    assert "- b" in out


def test_cmd_config_requires_set_or_show(capsys):
    with pytest.raises(SystemExit):
        run.cmd_config(SimpleNamespace(set=None, show=False))
    assert "Provide --set <models> or --show" in capsys.readouterr().err


def test_init_persists_custom_timeout(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True)
    out_dir = workspace / "research" / "topic"

    args = SimpleNamespace(
        topic="topic",
        out_dir=str(out_dir),
        workspace_dir=str(workspace),
        depth=2,
        models="a,b",
        criteria=None,
        audit_model=None,
        debug=False,
        output_file=None,
        timeout=123456,
    )

    monkeypatch.setattr(run, "_emit_round", lambda state, round_num: None)
    run.cmd_init(args)

    state = json.loads((out_dir / "_state.json").read_text())
    assert state["timeout_ms"] == 123456


def test_init_rejects_non_positive_timeout(tmp_path, capsys):
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True)
    out_dir = workspace / "research" / "topic"
    args = SimpleNamespace(
        topic="topic",
        out_dir=str(out_dir),
        workspace_dir=str(workspace),
        depth=2,
        models="a,b",
        criteria=None,
        audit_model=None,
        debug=False,
        output_file=None,
        timeout=0,
    )

    with pytest.raises(SystemExit):
        run.cmd_init(args)
    assert "--timeout must be a positive integer" in capsys.readouterr().err


def test_extract_scores_malformed_empty_and_valid(tmp_path):
    malformed = tmp_path / "malformed.md"
    malformed.write_text("<!-- scores {oops} -->")
    assert run.extract_scores(malformed) is None

    empty = tmp_path / "empty.md"
    empty.write_text("no score block")
    assert run.extract_scores(empty) is None

    valid = tmp_path / "valid.md"
    valid.write_text(
        """report
<!-- scores
{
  \"v1\": {\"prompt_fidelity\": 9},
  \"v2\": {\"prompt_fidelity\": 8}
}
-->
"""
    )
    parsed = run.extract_scores(valid)
    assert parsed == {
        "v1": {"prompt_fidelity": 9},
        "v2": {"prompt_fidelity": 8},
    }


def test_load_weights_and_compute_winner(tmp_path):
    criteria = tmp_path / "criteria.md"
    criteria.write_text(
        "| Criterion | Weight | Why it matters |\n"
        "|---|---:|---|\n"
        "| prompt_fidelity | 5 | x |\n"
        "| structural_clarity | 1 | x |\n"
    )
    weights = run.load_weights(criteria)
    assert weights == {"prompt_fidelity": 5, "structural_clarity": 1}

    score_matrix = {
        "v1": {
            "v1": {"prompt_fidelity": 8, "structural_clarity": 8},
            "v2": {"prompt_fidelity": 7, "structural_clarity": 9},
        },
        "v2": {
            "v1": {"prompt_fidelity": 9, "structural_clarity": 8},
            "v2": {"prompt_fidelity": 8, "structural_clarity": 9},
        },
    }
    winner, avgs = run.compute_winner(score_matrix, weights)
    assert winner == "v1"
    assert avgs["v1"] > avgs["v2"]


def _write_score_file(path: Path, v1_score: int, v2_score: int):
    path.write_text(
        """report
<!-- scores
{
  \"v1\": {\"prompt_fidelity\": %d},
  \"v2\": {\"prompt_fidelity\": %d}
}
-->
"""
        % (v1_score, v2_score)
    )


def _write_round_state(out_dir: Path, depth: int = 2):
    state = {
        "topic": "topic",
        "workspace_dir": str(out_dir),
        "out_dir": str(out_dir),
        "depth": depth,
        "timeout_ms": 600000,
        "models": ["m1", "m2"],
        "tokens": {"v1": "m1", "v2": "m2"},
        "audit_model": None,
        "debug": False,
        "output_file": None,
        "current_round": 1,
    }
    (out_dir / "_state.json").write_text(json.dumps(state))
    (out_dir / "_criteria.md").write_text(
        "| Criterion | Weight | Why |\n"
        "|---|---:|---|\n"
        "| prompt_fidelity | 1 | x |\n"
    )
    for token in ["v1", "v2"]:
        (out_dir / f"r1-produce.{token}.md").write_text("doc")


def test_score_round_missing_compare_file_emits_rerun(tmp_path, capsys):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    _write_round_state(out_dir)
    _write_score_file(out_dir / "r1-compare.v1.md", 9, 8)

    run.cmd_score_round(SimpleNamespace(out_dir=str(out_dir), round=1))
    out = capsys.readouterr().out
    assert "RERUN_REQUIRED: r1-compare.v2.md is missing" in out
    assert "RERUN_COMMAND:" in out


def test_score_round_malformed_score_emits_rerun(tmp_path, capsys):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    _write_round_state(out_dir)
    _write_score_file(out_dir / "r1-compare.v1.md", 9, 8)
    (out_dir / "r1-compare.v2.md").write_text("bad")

    run.cmd_score_round(SimpleNamespace(out_dir=str(out_dir), round=1))
    out = capsys.readouterr().out
    assert "RERUN_REQUIRED: r1-compare.v2.md has a missing or malformed score block" in out


def test_score_round_happy_path_emits_next_round(tmp_path, monkeypatch):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    _write_round_state(out_dir, depth=2)
    _write_score_file(out_dir / "r1-compare.v1.md", 9, 8)
    _write_score_file(out_dir / "r1-compare.v2.md", 9, 8)

    called = {}
    monkeypatch.setattr(run, "_emit_round", lambda state, round_num: called.update({"round": round_num}))
    run.cmd_score_round(SimpleNamespace(out_dir=str(out_dir), round=1))

    assert called["round"] == 2
    state = json.loads((out_dir / "_state.json").read_text())
    assert state["round_scores"]["1"]["winner_token"] == "v1"


def test_score_round_final_path_emits_final_merge(tmp_path, monkeypatch):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    _write_round_state(out_dir, depth=1)
    _write_score_file(out_dir / "r1-compare.v1.md", 9, 8)
    _write_score_file(out_dir / "r1-compare.v2.md", 9, 8)

    called = {}
    monkeypatch.setattr(
        run,
        "_emit_final_merge",
        lambda state, winner_token, winner_model: called.update(
            {"winner_token": winner_token, "winner_model": winner_model}
        ),
    )
    run.cmd_score_round(SimpleNamespace(out_dir=str(out_dir), round=1))

    assert called == {"winner_token": "v1", "winner_model": "m1"}


def test_emit_round_and_build_compare_command_include_timeout(tmp_path, capsys):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    state = {
        "topic": "topic",
        "out_dir": str(out_dir),
        "depth": 2,
        "timeout_ms": 321000,
        "tokens": {"v1": "m1", "v2": "m2"},
    }
    for token in ["v1", "v2"]:
        (out_dir / f"r1-produce.{token}.md").write_text("doc")

    run._emit_round(state, 1)
    output = capsys.readouterr().out
    assert "--timeout 321000" in output
    assert "-- \"Write your output to" in output

    cmd = run._build_compare_command(state, 1, "v1")
    assert "--timeout 321000" in cmd
    assert "_prompt-r1b-v1.md" in cmd


def test_emit_final_merge_and_audit_and_finalize(tmp_path, monkeypatch, capsys):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    state = {
        "topic": "topic",
        "out_dir": str(out_dir),
        "depth": 1,
        "timeout_ms": 600000,
        "tokens": {"v1": "m1", "v2": "m2"},
        "round_scores": {"1": {"winner_token": "v1", "winner_model": "m1"}},
        "audit_model": None,
    }
    (out_dir / "r1-produce.v1.md").write_text("doc")
    (out_dir / "r1-produce.v2.md").write_text("doc")
    (out_dir / "r1-compare.v1.md").write_text("cmp")
    (out_dir / "r1-compare.v2.md").write_text("cmp")
    (out_dir / "_criteria.md").write_text("x")
    (out_dir / "_state.json").write_text(json.dumps(state))
    (out_dir / "_final-draft.md").write_text("draft")

    run._emit_final_merge(state, "v1", "m1")
    out1 = capsys.readouterr().out
    assert "Final Merge" in out1
    assert "--timeout 600000" in out1

    run._emit_audit(state)
    out2 = capsys.readouterr().out
    assert "Self-Audit" in out2
    assert "Audit model: **m2**" in out2

    called = {}
    monkeypatch.setattr(run, "_emit_audit", lambda s: called.update({"ok": True}))
    run.cmd_finalize(SimpleNamespace(out_dir=str(out_dir)))
    assert called.get("ok") is True


def test_deliver_summary_output_and_cleanup(tmp_path, capsys):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    final_path = tmp_path / "final.md"
    state = {
        "topic": "topic",
        "out_dir": str(out_dir),
        "depth": 1,
        "tokens": {"v1": "m1", "v2": "m2"},
        "output_file": str(final_path),
        "debug": False,
        "audit_model_used": "m2",
        "round_scores": {
            "1": {
                "weighted_avgs": {"v1": 9.0, "v2": 8.0},
                "winner_token": "v1",
                "winner_model": "m1",
                "excluded": [],
            }
        },
    }
    (out_dir / "_state.json").write_text(json.dumps(state))
    (out_dir / "_final-draft.md").write_text("final draft")

    run.cmd_deliver(SimpleNamespace(out_dir=str(out_dir)))
    out = capsys.readouterr().out
    assert "Final output written to" in out
    assert "Cleanup" in out
    assert (out_dir / "_summary.md").exists()
    assert final_path.read_text() == "final draft"


def test_deliver_debug_keeps_files(tmp_path, capsys):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    state = {
        "topic": "topic",
        "out_dir": str(out_dir),
        "depth": 1,
        "tokens": {"v1": "m1", "v2": "m2"},
        "output_file": None,
        "debug": True,
        "audit_model_used": "m2",
        "round_scores": {},
    }
    (out_dir / "_state.json").write_text(json.dumps(state))
    (out_dir / "_final-draft.md").write_text("final draft")

    run.cmd_deliver(SimpleNamespace(out_dir=str(out_dir)))
    out = capsys.readouterr().out
    assert "all intermediary files kept" in out


def test_doctor_warns_when_avx_missing(monkeypatch, capsys):
    def fake_check(command, capture_output, text, timeout, check):
        joined = " ".join(command)
        if joined == "bun --version":
            return SimpleNamespace(returncode=0, stdout="1.2.3\n", stderr="")
        if joined == "bunx playwright --version":
            return SimpleNamespace(returncode=0, stdout="Version 1.2.3\n", stderr="")
        if joined == "sysctl -n machdep.cpu.features":
            return SimpleNamespace(returncode=0, stdout="SSE4.2\n", stderr="")
        if joined == "sysctl -n machdep.cpu.leaf7_features":
            return SimpleNamespace(returncode=0, stdout="BMI1\n", stderr="")
        return SimpleNamespace(returncode=1, stdout="", stderr="unknown")

    monkeypatch.setattr(run, "sys", SimpleNamespace(platform="darwin"))
    monkeypatch.setattr(run.subprocess, "run", fake_check)

    run.cmd_doctor(SimpleNamespace())
    output = capsys.readouterr().out

    assert "[WARN] avx: not detected via sysctl" in output
    assert "Doctor result: WARN" in output


def test_doctor_passes_with_all_signals(monkeypatch, capsys):
    def fake_check(command, capture_output, text, timeout, check):
        joined = " ".join(command)
        if joined == "bun --version":
            return SimpleNamespace(returncode=0, stdout="1.2.3\n", stderr="")
        if joined == "bunx playwright --version":
            return SimpleNamespace(returncode=0, stdout="Version 1.2.3\n", stderr="")
        if joined == "sysctl -n machdep.cpu.features":
            return SimpleNamespace(returncode=0, stdout="AVX1.0\n", stderr="")
        if joined == "sysctl -n machdep.cpu.leaf7_features":
            return SimpleNamespace(returncode=0, stdout="AVX2.0\n", stderr="")
        return SimpleNamespace(returncode=1, stdout="", stderr="unknown")

    monkeypatch.setattr(run, "sys", SimpleNamespace(platform="darwin"))
    monkeypatch.setattr(run.subprocess, "run", fake_check)

    run.cmd_doctor(SimpleNamespace())
    output = capsys.readouterr().out
    assert "Doctor result: PASS" in output
