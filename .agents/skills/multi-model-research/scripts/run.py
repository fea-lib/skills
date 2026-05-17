#!/usr/bin/env python3
"""
multi-model-research orchestrator
----------------------------------
Emits subagent commands for each phase of the multi-model research workflow.
Does NOT shell out to run those commands itself — the orchestrating agent
executes them and reports results back, keeping it in the loop for retries.

Usage:
    # Step 1: agent runs `opencode models`, pipes output here to get default models
    echo "<opencode models output>" | python run.py --list-defaults

    # Step 2: full run
    python run.py --topic "..." [flags]

    # Step 3: after each subagent command completes, call back with its output file
    python run.py --score-round N --out-dir "..."
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

SKILL_DIR = Path(__file__).resolve().parent.parent
PROMPTS_PATH = SKILL_DIR / "references" / "prompts.md"
DEFAULT_CRITERIA_PATH = SKILL_DIR / "references" / "criteria.md"
CONFIG_PATH = SKILL_DIR / "config.yaml"

PERMISSION_ENV = 'OPENCODE_PERMISSION=\'{"read":"allow","write":"allow","glob":"allow","grep":"allow"}\''
SESSION_CWD = Path.cwd()
DEFAULT_TIMEOUT_MS = 600000


def slugify_topic(topic: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    return slug or "research"


def resolve_user_path(path_str: str | None, base_dir: Path | None = None) -> Path | None:
    if path_str is None:
        return None
    path = Path(path_str).expanduser()
    root = base_dir or SESSION_CWD
    return path if path.is_absolute() else (root / path)


def resolve_workspace_dir(workspace_dir_arg: str | None) -> Path:
    return resolve_user_path(workspace_dir_arg) or SESSION_CWD


def resolve_out_dir(topic: str, out_dir_arg: str | None, workspace_dir_arg: str | None) -> Path:
    workspace_dir = resolve_workspace_dir(workspace_dir_arg)
    if out_dir_arg:
        return resolve_user_path(out_dir_arg, workspace_dir)
    return workspace_dir / "research" / slugify_topic(topic)


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def _read_config() -> list[str]:
    """Return models from config.yaml, or [] if absent/empty."""
    if not CONFIG_PATH.exists():
        return []
    if _YAML_AVAILABLE:
        data = yaml.safe_load(CONFIG_PATH.read_text()) or {}
    else:
        # Minimal YAML parser: only handles the 'models: [- item]' shape we write.
        data = {}
        key = None
        items = []
        for line in CONFIG_PATH.read_text().splitlines():
            m = re.match(r'^(\w+):', line)
            if m:
                key = m.group(1)
            elif key == "models" and re.match(r'^\s+-\s+', line):
                items.append(re.sub(r'^\s+-\s+', '', line).strip())
        if items:
            data = {"models": items}
    return [m for m in data.get("models", []) if m]


def _write_config(models: list[str]) -> None:
    """Write models list to config.yaml."""
    lines = ["models:"] + [f"  - {m}" for m in models]
    CONFIG_PATH.write_text("\n".join(lines) + "\n")


def _parse_all_models(models_output: str) -> list[str]:
    """Return every model ID found in `opencode models` output."""
    result = []
    for line in models_output.strip().splitlines():
        token = line.split()[-1] if line.split() else ""
        if token:
            result.append(token)
    return result


# ---------------------------------------------------------------------------
# Model selection
# ---------------------------------------------------------------------------

def select_default_models(models_output: str) -> list[str]:
    """
    Given the text output of `opencode models`, return [best_claude, best_gpt].
    Picks the highest-ranked Claude and GPT model by version heuristic.
    """
    lines = [l.strip() for l in models_output.strip().splitlines() if l.strip()]
    # Extract model IDs — opencode models output is typically "provider/model-id"
    # or just "model-id". We match anything containing claude or gpt/o1/o3/o4.
    claude_candidates = []
    gpt_candidates = []
    for line in lines:
        # grab the last whitespace-delimited token as the model id
        token = line.split()[-1] if line.split() else ""
        tl = token.lower()
        if "claude" in tl:
            claude_candidates.append(token)
        elif re.search(r"\bgpt\b|/gpt|^gpt|/o\d|^o\d", tl):
            gpt_candidates.append(token)

    def rank_claude(m):
        # prefer opus > sonnet > haiku; higher numeric suffix wins
        m = m.lower()
        family = 3 if "opus" in m else (2 if "sonnet" in m else 1)
        nums = [int(x) for x in re.findall(r"\d+", m)]
        return (family, nums)

    def rank_gpt(m):
        m = m.lower()
        # o-series > gpt-4o > gpt-4 > gpt-3.5
        if re.search(r"^o\d|/o\d", m):
            series = 3
        elif "4o" in m:
            series = 2
        elif "4" in m:
            series = 1
        else:
            series = 0
        nums = [int(x) for x in re.findall(r"\d+", m)]
        return (series, nums)

    best_claude = max(claude_candidates, key=rank_claude) if claude_candidates else None
    best_gpt = max(gpt_candidates, key=rank_gpt) if gpt_candidates else None

    selected = [m for m in [best_claude, best_gpt] if m]
    return selected


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

def load_prompt_section(section_header: str) -> str:
    """Extract the fenced code block content for a named section from prompts.md."""
    text = PROMPTS_PATH.read_text()
    # Find the section
    pattern = rf"## {re.escape(section_header)}\n(.*?)(?=\n## |\Z)"
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        raise ValueError(f"Section '{section_header}' not found in {PROMPTS_PATH}")
    section = m.group(1)
    # Extract first fenced block
    fence = re.search(r"```\n(.*?)```", section, re.DOTALL)
    if not fence:
        raise ValueError(f"No fenced code block in section '{section_header}'")
    return fence.group(1).strip()


def render_prompt(section_header: str, placeholders: dict) -> str:
    template = load_prompt_section(section_header)
    for key, value in placeholders.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    return template


def write_prompt(out_dir: Path, name: str, content: str) -> Path:
    path = out_dir / name
    path.write_text(content)
    return path


# ---------------------------------------------------------------------------
# Score extraction
# ---------------------------------------------------------------------------

def extract_scores(filepath: Path) -> dict | None:
    """
    Extract the <!-- scores {...} --> block from the end of a comparison file.
    Returns the parsed dict or None if missing/malformed.
    """
    text = filepath.read_text()
    m = re.search(r"<!--\s*scores\s*(\{.*?\})\s*-->", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def load_weights(criteria_path: Path) -> dict[str, int]:
    """
    Parse the Weight column from _criteria.md table.
    Returns {criterion_name: weight}.
    """
    text = criteria_path.read_text()
    weights = {}
    for line in text.splitlines():
        # Match table rows: | criterion_name | N | ...
        m = re.match(r"\|\s*(\w+)\s*\|\s*(\d+)\s*\|", line)
        if m:
            weights[m.group(1)] = int(m.group(2))
    return weights


def compute_winner(
    score_matrix: dict[str, dict[str, dict[str, int]]],
    weights: dict[str, int],
) -> tuple[str, dict]:
    """
    score_matrix: {comparator_token: {variant_token: {criterion: score}}}
    weights: {criterion: weight}
    Returns (winning_variant_token, {variant: weighted_avg}).
    """
    variant_totals: dict[str, float] = {}
    variant_weight_sums: dict[str, float] = {}

    for comparator, variants in score_matrix.items():
        for variant, criteria in variants.items():
            for criterion, score in criteria.items():
                w = weights.get(criterion, 1)
                variant_totals[variant] = variant_totals.get(variant, 0) + score * w
                variant_weight_sums[variant] = variant_weight_sums.get(variant, 0) + w

    weighted_avgs = {
        v: variant_totals[v] / variant_weight_sums[v]
        for v in variant_totals
    }

    # Tie-break: highest structural_clarity across all comparators
    def tiebreak(variant):
        sc_scores = []
        for comparator, variants in score_matrix.items():
            sc = variants.get(variant, {}).get("structural_clarity")
            if sc is not None:
                sc_scores.append(sc)
        return sum(sc_scores) / len(sc_scores) if sc_scores else 0

    winner = max(weighted_avgs, key=lambda v: (weighted_avgs[v], tiebreak(v)))
    return winner, weighted_avgs


# ---------------------------------------------------------------------------
# Command emission
# ---------------------------------------------------------------------------

def emit_subagent_cmd(
    model: str,
    prompt_file: Path,
    input_files: list[Path],
    output_file: Path,
    timeout_ms: int,
) -> str:
    """Produce the opencode run bash string for the orchestrating agent to execute."""
    files = " ".join(f'-f "{p}"' for p in [prompt_file] + input_files)
    return (
        f'{PERMISSION_ENV} \\\n'
        f'  opencode run -m {model} \\\n'
        f'    --timeout {timeout_ms} \\\n'
        f'    {files} \\\n'
        f'    -- "Write your output to {output_file}"'
    )


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_list_defaults(args):
    """Read opencode models output from stdin, print the two default model IDs.
    If config.yaml exists with a models list, use that instead of auto-selecting."""
    configured = _read_config()
    if configured:
        print(",".join(configured))
        return

    models_output = sys.stdin.read()
    selected = select_default_models(models_output)
    if len(selected) < 2:
        print("ERROR: Could not identify at least one Claude and one GPT model.", file=sys.stderr)
        print("Available models parsed:", file=sys.stderr)
        for line in models_output.strip().splitlines():
            print(" ", line, file=sys.stderr)
        sys.exit(1)
    print(",".join(selected))


def cmd_list_models(args):
    """Read opencode models output from stdin, print all model IDs as JSON array."""
    models_output = sys.stdin.read()
    models = _parse_all_models(models_output)
    print(json.dumps(models))


def cmd_config(args):
    """Read or write the persistent model config."""
    if args.show:
        configured = _read_config()
        if configured:
            print(f"Configured models ({len(configured)}):")
            for m in configured:
                print(f"  - {m}")
        else:
            print("No config.yaml found — skill will auto-select models.")
        return

    if args.set:
        models = [m.strip() for m in args.set.split(",") if m.strip()]
        if not models:
            print("ERROR: No models provided.", file=sys.stderr)
            sys.exit(1)
        _write_config(models)
        print(f"Saved {len(models)} model(s) to {CONFIG_PATH}:")
        for m in models:
            print(f"  - {m}")
        return

    print("ERROR: Provide --set <models> or --show.", file=sys.stderr)
    sys.exit(1)


def cmd_init(args):
    """
    Initialise a research run. Writes _manifest.json, copies _criteria.md,
    and emits Round 1 Step-A commands.
    """
    workspace_dir = resolve_workspace_dir(args.workspace_dir)
    out_dir = resolve_out_dir(args.topic, args.out_dir, args.workspace_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if len(models) < 2:
        print("ERROR: At least 2 models are required.", file=sys.stderr)
        sys.exit(1)
    if args.timeout <= 0:
        print("ERROR: --timeout must be a positive integer in milliseconds.", file=sys.stderr)
        sys.exit(1)

    # Assign tokens
    tokens = {f"v{i+1}": model for i, model in enumerate(models)}
    manifest_path = out_dir / "_manifest.json"
    manifest_path.write_text(json.dumps(tokens, indent=2))

    # Copy criteria
    criteria_src = resolve_user_path(args.criteria, workspace_dir) if args.criteria else DEFAULT_CRITERIA_PATH
    criteria_dst = out_dir / "_criteria.md"
    criteria_dst.write_text(criteria_src.read_text())

    output_file = resolve_user_path(args.output_file, workspace_dir)

    # Write state file
    state = {
        "topic": args.topic,
        "workspace_dir": str(workspace_dir),
        "out_dir": str(out_dir),
        "depth": args.depth,
        "timeout_ms": args.timeout,
        "models": models,
        "tokens": tokens,
        "audit_model": args.audit_model,
        "debug": args.debug,
        "output_file": str(output_file) if output_file else None,
        "current_round": 1,
    }
    (out_dir / "_state.json").write_text(json.dumps(state, indent=2))

    _emit_round(state, round_num=1)


def cmd_score_round(args):
    """
    After all compare files for a round are written, score them.
    If this is the final round, emit final-merge command.
    Otherwise emit next-round produce commands.
    """
    out_dir = Path(args.out_dir)
    state = json.loads((out_dir / "_state.json").read_text())
    round_num = args.round
    depth = state["depth"]

    weights = load_weights(out_dir / "_criteria.md")
    tokens = state["tokens"]  # {token: model}

    expected_compare = {
        token: out_dir / f"r{round_num}-compare.{token}.md"
        for token in tokens
    }
    for token, compare_file in expected_compare.items():
        if not compare_file.exists():
            rerun_cmd = _build_compare_command(state, round_num, token)
            print(f"RERUN_REQUIRED: {compare_file.name} is missing")
            print(f"RERUN_COMMAND: {rerun_cmd}")
            return

    score_matrix = {}
    excluded = []
    for token, cf in expected_compare.items():
        scores = extract_scores(cf)
        if scores is None:
            rerun_cmd = _build_compare_command(state, round_num, token)
            print(f"RERUN_REQUIRED: {cf.name} has a missing or malformed score block")
            print(f"RERUN_COMMAND: {rerun_cmd}")
            return  # Caller reruns this comparator, then calls score-round again
        score_matrix[token] = scores

    if not score_matrix:
        print("ERROR: All comparison files malformed. Halting.", file=sys.stderr)
        sys.exit(2)

    winner_token, weighted_avgs = compute_winner(score_matrix, weights)
    winner_model = tokens[winner_token]

    # Persist scores into state
    state.setdefault("round_scores", {})[str(round_num)] = {
        "score_matrix": score_matrix,
        "weighted_avgs": {k: round(v, 3) for k, v in weighted_avgs.items()},
        "winner_token": winner_token,
        "winner_model": winner_model,
        "excluded": excluded,
    }
    state["current_round"] = round_num
    (out_dir / "_state.json").write_text(json.dumps(state, indent=2))

    if round_num < depth:
        _emit_round(state, round_num + 1)
    else:
        _emit_final_merge(state, winner_token, winner_model)


def cmd_finalize(args):
    """
    After final-merge is done, emit self-audit command.
    """
    out_dir = Path(args.out_dir)
    state = json.loads((out_dir / "_state.json").read_text())
    _emit_audit(state)


def cmd_deliver(args):
    """
    After audit is done, write _summary.md and emit cleanup instructions.
    """
    out_dir = Path(args.out_dir)
    state = json.loads((out_dir / "_state.json").read_text())
    _write_final_output(state)
    _write_summary(state)
    _emit_cleanup(state)


def cmd_doctor(args):
    """Run environment checks for known risk factors and dependencies."""

    def check_command(command: list[str], timeout_sec: int = 10) -> tuple[bool, str]:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False,
            )
        except FileNotFoundError:
            return False, "not installed"
        except Exception as exc:
            return False, f"error: {exc}"

        output = (result.stdout or result.stderr).strip()
        if result.returncode == 0:
            return True, output or "ok"
        return False, output or f"exited with code {result.returncode}"

    print("# multi-model-research doctor")
    print()

    bun_ok, bun_msg = check_command(["bun", "--version"])
    if bun_ok:
        print(f"[OK] bun: {bun_msg}")
    else:
        print(f"[WARN] bun: {bun_msg}")

    playwright_ok, playwright_msg = check_command(["bunx", "playwright", "--version"])
    if playwright_ok:
        print(f"[OK] playwright: {playwright_msg}")
    else:
        print(f"[WARN] playwright: {playwright_msg}")

    avx_supported = False
    avx_source = ""

    if sys.platform == "darwin":
        ok1, features = check_command(["sysctl", "-n", "machdep.cpu.features"])
        ok2, leaf7 = check_command(["sysctl", "-n", "machdep.cpu.leaf7_features"])
        feature_text = " ".join([features if ok1 else "", leaf7 if ok2 else ""]).upper()
        avx_supported = "AVX1.0" in feature_text or "AVX2.0" in feature_text or " AVX " in f" {feature_text} "
        avx_source = "sysctl"
    elif Path("/proc/cpuinfo").exists():
        try:
            cpuinfo = Path("/proc/cpuinfo").read_text().upper()
            avx_supported = " AVX " in f" {cpuinfo} " or " AVX2 " in f" {cpuinfo} "
            avx_source = "/proc/cpuinfo"
        except Exception as exc:
            avx_source = f"/proc/cpuinfo read failed: {exc}"
    else:
        avx_source = "platform unsupported for AVX probe"

    if avx_supported:
        print(f"[OK] avx: detected via {avx_source}")
    else:
        print(f"[WARN] avx: not detected via {avx_source}")
        print("       AVX-related runtime failures may occur on this environment.")

    if bun_ok and playwright_ok and avx_supported:
        print("\nDoctor result: PASS")
    else:
        print("\nDoctor result: WARN")


# ---------------------------------------------------------------------------
# Internal emitters
# ---------------------------------------------------------------------------

def _emit_round(state: dict, round_num: int):
    out_dir = Path(state["out_dir"])
    tokens = state["tokens"]  # {token: model}
    topic = state["topic"]
    depth = state["depth"]
    timeout_ms = state.get("timeout_ms", DEFAULT_TIMEOUT_MS)

    print(f"\n# === Round {round_num} of {depth} ===\n")

    # --- Step A ---
    if round_num == 1:
        section = "Step-A — Produce (Round 1: Research)"
        prior_files = []
    else:
        section = "Step-A — Produce (Round > 1: Merge)"
        prior_files = list(out_dir.glob(f"r{round_num-1}-produce.*.md"))

    print(f"## Step A — Produce (Round {round_num})\n")
    print("Execute the following commands **in parallel**:\n")

    for token, model in tokens.items():
        output_file = out_dir / f"r{round_num}-produce.{token}.md"
        placeholders = {
            "TOPIC": topic,
            "ROUND": round_num,
            "N": len(tokens),
            "TOKEN": token,
            "OUTPUT_FILE": str(output_file),
        }
        prompt_content = render_prompt(section, placeholders)
        prompt_file = write_prompt(out_dir, f"_prompt-r{round_num}a-{token}.md", prompt_content)
        cmd = emit_subagent_cmd(model, prompt_file, prior_files, output_file, timeout_ms)
        print(f"```bash\n# {token} ({model})\n{cmd}\n```\n")

    # --- Step B ---
    produce_files = [out_dir / f"r{round_num}-produce.{t}.md" for t in tokens]
    variant_list = ", ".join(tokens.keys())

    print(f"## Step B — Compare (Round {round_num})\n")
    print("After all Step-A outputs exist, execute the following commands **in parallel**:\n")

    for token, model in tokens.items():
        output_file = out_dir / f"r{round_num}-compare.{token}.md"
        placeholders = {
            "TOPIC": topic,
            "ROUND": round_num,
            "N": len(tokens),
            "TOKEN": token,
            "VARIANT_LIST": variant_list,
            "OUTPUT_FILE": str(output_file),
        }
        prompt_content = render_prompt("Step-B — Compare", placeholders)
        prompt_file = write_prompt(out_dir, f"_prompt-r{round_num}b-{token}.md", prompt_content)
        cmd = emit_subagent_cmd(
            model, prompt_file,
            [out_dir / "_criteria.md"] + produce_files,
            output_file,
            timeout_ms,
        )
        print(f"```bash\n# {token} ({model})\n{cmd}\n```\n")

    print(f"After all compare files are written, run:\n")
    print(f"```bash\npython scripts/run.py score-round --out-dir \"{state['out_dir']}\" --round {round_num}\n```\n")


def _emit_final_merge(state: dict, winner_token: str, winner_model: str):
    out_dir = Path(state["out_dir"])
    depth = state["depth"]
    topic = state["topic"]
    tokens = state["tokens"]
    timeout_ms = state.get("timeout_ms", DEFAULT_TIMEOUT_MS)

    produce_files = list(out_dir.glob(f"r{depth}-produce.*.md"))
    compare_files = list(out_dir.glob(f"r{depth}-compare.*.md"))
    draft_file = out_dir / "_final-draft.md"

    print(f"\n# === Final Merge ===\n")
    print(f"Winner: **{winner_token}** ({winner_model})\n")

    placeholders = {
        "TOPIC": topic,
        "N": len(produce_files),
        "OUTPUT_FILE": str(draft_file),
    }
    prompt_content = render_prompt("Final-Merge", placeholders)
    prompt_file = write_prompt(out_dir, "_prompt-final.md", prompt_content)
    cmd = emit_subagent_cmd(
        winner_model, prompt_file,
        produce_files + compare_files,
        draft_file,
        timeout_ms,
    )
    print(f"```bash\n{cmd}\n```\n")
    print("After the merge is complete, run:\n")
    print(f"```bash\npython scripts/run.py finalize --out-dir \"{state['out_dir']}\"\n```\n")


def _emit_audit(state: dict):
    out_dir = Path(state["out_dir"])
    tokens = state["tokens"]
    topic = state["topic"]
    timeout_ms = state.get("timeout_ms", DEFAULT_TIMEOUT_MS)
    draft_file = out_dir / "_final-draft.md"
    audit_file = out_dir / "_audit.md"

    # Determine audit model: prefer a non-winning model for independence
    last_round_scores = state.get("round_scores", {}).get(str(state["depth"]), {})
    winner_token = last_round_scores.get("winner_token")
    winner_model = last_round_scores.get("winner_model")

    if state.get("audit_model"):
        audit_model = state["audit_model"]
    else:
        # Pick a non-winning model if available
        non_winners = [m for t, m in tokens.items() if t != winner_token]
        audit_model = non_winners[0] if non_winners else winner_model

    all_compare_files = sorted(out_dir.glob("r*-compare.*.md"))

    print(f"\n# === Self-Audit ===\n")
    print(f"Audit model: **{audit_model}**\n")

    placeholders = {
        "TOPIC": topic,
        "DRAFT_FILE": str(draft_file),
        "AUDIT_FILE": str(audit_file),
    }
    prompt_content = render_prompt("Self-Audit", placeholders)
    prompt_file = write_prompt(out_dir, "_prompt-audit.md", prompt_content)
    cmd = emit_subagent_cmd(
        audit_model, prompt_file,
        [out_dir / "_criteria.md", draft_file] + all_compare_files,
        audit_file,
        timeout_ms,
    )
    print(f"```bash\n{cmd}\n```\n")
    print("After the audit is complete, run:\n")
    print(f"```bash\npython scripts/run.py deliver --out-dir \"{state['out_dir']}\"\n```\n")

    # Persist audit model into state
    state["audit_model_used"] = audit_model
    (out_dir / "_state.json").write_text(json.dumps(state, indent=2))


def _write_summary(state: dict):
    out_dir = Path(state["out_dir"])
    tokens = state["tokens"]
    lines = ["# Research Summary\n"]
    lines.append(f"**Topic:** {state['topic']}\n")
    lines.append(f"**Output:** {state.get('output_file', out_dir / 'output.md')}\n")
    lines.append(f"**Depth:** {state['depth']}\n")

    lines.append("\n## Models\n")
    lines.append("| Token | Model |")
    lines.append("|-------|-------|")
    for token, model in tokens.items():
        lines.append(f"| {token} | {model} |")

    for round_num, round_data in state.get("round_scores", {}).items():
        lines.append(f"\n## Round {round_num} Scores\n")
        avgs = round_data.get("weighted_avgs", {})
        lines.append("| Variant | Weighted Avg |")
        lines.append("|---------|--------------|")
        for v, avg in sorted(avgs.items(), key=lambda x: -x[1]):
            lines.append(f"| {v} | {avg:.3f} |")
        winner_token = round_data.get("winner_token")
        winner_model = round_data.get("winner_model")
        lines.append(f"\n**Winner:** {winner_token} ({winner_model})")
        if round_data.get("excluded"):
            for exc in round_data["excluded"]:
                lines.append(f"\n> Score block malformed in `{exc}`; excluded after rerun.")

    lines.append(f"\n## Audit\n")
    lines.append(f"**Audit model:** {state.get('audit_model_used', 'unknown')}")

    summary_path = out_dir / "_summary.md"
    summary_path.write_text("\n".join(lines) + "\n")
    print(f"_summary.md written to {summary_path}")


def _write_final_output(state: dict):
    out_dir = Path(state["out_dir"])
    draft_file = out_dir / "_final-draft.md"
    output_file = state.get("output_file")

    if not output_file:
        return

    destination = Path(output_file)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(draft_file, destination)
    print(f"Final output written to {destination}")


def _emit_cleanup(state: dict):
    out_dir = Path(state["out_dir"])
    output_file = state.get("output_file")
    debug = state.get("debug", False)

    if output_file:
        print(f"\n## Deliver\n")
        print(f"Final document saved to `{output_file}`.\n")

    if debug:
        print("**--debug is set — all intermediary files kept.**\n")
        return

    print("## Cleanup\n")
    print("Delete all files in the output directory except `_summary.md` and the final output file:\n")
    keep = {str(out_dir / "_summary.md")}
    if output_file:
        keep.add(output_file)
    print(f"```bash")
    print(f"find \"{out_dir}\" -maxdepth 1 -type f \\")
    keep_conditions = " \\\n  ".join(f'! -name "{Path(p).name}"' for p in keep)
    print(f"  {keep_conditions} \\")
    print(f"  -delete")
    print(f"```\n")


def _build_compare_command(state: dict, round_num: int, token: str) -> str:
    out_dir = Path(state["out_dir"])
    tokens = state["tokens"]
    topic = state["topic"]
    timeout_ms = state.get("timeout_ms", DEFAULT_TIMEOUT_MS)

    if token not in tokens:
        raise ValueError(f"Unknown token '{token}'")

    output_file = out_dir / f"r{round_num}-compare.{token}.md"
    placeholders = {
        "TOPIC": topic,
        "ROUND": round_num,
        "N": len(tokens),
        "TOKEN": token,
        "VARIANT_LIST": ", ".join(tokens.keys()),
        "OUTPUT_FILE": str(output_file),
    }
    prompt_content = render_prompt("Step-B — Compare", placeholders)
    prompt_file = write_prompt(out_dir, f"_prompt-r{round_num}b-{token}.md", prompt_content)
    produce_files = [out_dir / f"r{round_num}-produce.{t}.md" for t in tokens]
    return emit_subagent_cmd(
        tokens[token],
        prompt_file,
        [out_dir / "_criteria.md"] + produce_files,
        output_file,
        timeout_ms,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="multi-model-research orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)

    # list-defaults: read opencode models from stdin, print default model IDs
    sub.add_parser("list-defaults", help="Pick default models from `opencode models` output on stdin")

    # list-models: read opencode models from stdin, print all model IDs as JSON
    sub.add_parser("list-models", help="List all available models from `opencode models` output on stdin as JSON")

    # config: read/write persistent model config
    p_cfg = sub.add_parser("config", help="Read or write the persistent model config (config.yaml)")
    p_cfg.add_argument("--set", metavar="MODELS", default=None,
                       help="Comma-separated model IDs to persist as defaults")
    p_cfg.add_argument("--show", action="store_true",
                       help="Print the current config and exit")

    # init: start a new run
    p_init = sub.add_parser("init", help="Initialise a research run and emit Round 1 commands")
    p_init.add_argument("--topic", required=True)
    p_init.add_argument("--out-dir", default=None)
    p_init.add_argument("--workspace-dir", default=None,
                        help="Base directory for resolving default/relative output paths")
    p_init.add_argument("--depth", type=int, default=2)
    p_init.add_argument("--models", required=True, help="Comma-separated model IDs (≥2)")
    p_init.add_argument("--criteria", default=None)
    p_init.add_argument("--audit-model", default=None)
    p_init.add_argument("--debug", action="store_true")
    p_init.add_argument("--output-file", default=None)
    p_init.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_MS,
                        help="Global timeout (ms) for all emitted opencode sub-agent commands")

    # score-round: extract scores and emit next phase
    p_score = sub.add_parser("score-round", help="Score a completed round and emit the next phase")
    p_score.add_argument("--out-dir", required=True)
    p_score.add_argument("--round", type=int, required=True)

    # finalize: emit self-audit command
    p_fin = sub.add_parser("finalize", help="Emit self-audit command after final merge")
    p_fin.add_argument("--out-dir", required=True)

    # deliver: write _summary.md and emit cleanup
    p_del = sub.add_parser("deliver", help="Write summary and emit cleanup after audit")
    p_del.add_argument("--out-dir", required=True)

    # doctor: environment checks
    sub.add_parser("doctor", help="Run environment checks for runtime, AVX, and dependencies")

    args = parser.parse_args()

    if args.command == "list-defaults":
        cmd_list_defaults(args)
    elif args.command == "list-models":
        cmd_list_models(args)
    elif args.command == "config":
        cmd_config(args)
    elif args.command == "init":
        cmd_init(args)
    elif args.command == "score-round":
        cmd_score_round(args)
    elif args.command == "finalize":
        cmd_finalize(args)
    elif args.command == "deliver":
        cmd_deliver(args)
    elif args.command == "doctor":
        cmd_doctor(args)


if __name__ == "__main__":
    main()
