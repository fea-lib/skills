# Phase Prompt Templates

## Contents

- [Placeholders](#placeholders)
- [Step-A — Produce (Round 1: Research)](#step-a--produce-round-1-research)
- [Step-A — Produce (Round > 1: Merge)](#step-a--produce-round--1-merge)
- [Step-B — Compare](#step-b--compare)
- [Final-Merge](#final-merge)
- [Self-Audit](#self-audit)

---

## Placeholders

All `{{PLACEHOLDERS}}` are substituted by the orchestrator before writing the prompt file.

| Placeholder | Value |
|-------------|-------|
| `{{TOPIC}}` | The user's original research prompt — included in all phases so subagents can evaluate prompt fidelity |
| `{{ROUND}}` | Current round number (integer) |
| `{{N}}` | Number of input documents attached to this subagent call |
| `{{TOKEN}}` | The receiving model's anonymised token (e.g. `v1`) |
| `{{VARIANT_LIST}}` | Comma-separated list of all variant tokens (e.g. `v1, v2, v3`) |
| `{{OUTPUT_FILE}}` | Full path the subagent must write its output to |
| `{{DRAFT_FILE}}` | Full path to `_final-draft.md` (Self-Audit only) |
| `{{AUDIT_FILE}}` | Full path to `_audit.md` (Self-Audit only) |

---

## Step-A — Produce (Round 1: Research)

> Used when `{{ROUND}} == 1`.

```
You are a thorough research analyst. Your task is to research the following topic and produce
a comprehensive research document.

Topic / research question:
{{TOPIC}}

Requirements:
- Directly address the topic or question above. If it is a specific question, provide a
  clear, direct answer — do not bury it in general background.
- Cover all relevant facets of the topic. Prioritise depth where it matters most.
- Structure the document clearly: use a table of contents, logical section headings, and a
  brief executive summary at the top.
- Include actionable guidance, concrete examples, and references to known standards or
  specifications where applicable.
- Do not mention your own name, the name of any AI model, or any identifying information.
  The document must read as if written by an anonymous expert.

Write your output to: {{OUTPUT_FILE}}
```

---

## Step-A — Produce (Round > 1: Merge)

> Used when `{{ROUND}} > 1`.

```
You are a research synthesis expert. You have been given {{N}} research documents covering
the same topic. Your task is to merge them into a single, superior document.

Original research prompt / question:
{{TOPIC}}

Requirements:
- Ensure the merged document directly and prominently addresses the original research prompt
  above. If it is a specific question, the answer must be clearly stated.
- The merged document must preserve all unique insights from all input documents — do not
  lose content present in only one source.
- Fill gaps identified in any input document.
- Do not mention any AI model names or identifying information anywhere in the output.

Write your output to: {{OUTPUT_FILE}}
```

---

## Step-B — Compare

```
You are an impartial research evaluator. You have been given {{N}} research documents on the
same topic (labelled {{VARIANT_LIST}}) and a scoring criteria file.

Original research prompt / question:
{{TOPIC}}

Your task:
1. Read all documents carefully, keeping the original research prompt in mind.
2. Score each document against every criterion in the criteria file (integer 1–10).
   For prompt_fidelity specifically: assess how directly and completely each document
   addresses the original prompt above. A specific question deserves a direct answer;
   an open topic deserves broad coverage of the expected scope.
3. Write a structured comparison report with:
   a. A scored table: rows = criteria, columns = variant tokens.
   b. For each criterion: a short narrative explaining the scores.
   c. A "gap inventory": list every significant gap or weakness identified across all variants.
   d. A "merge strategy" section: name the variant whose structure you recommend as the
      scaffold for a merged document, and explain why. List which content from each variant
      should be preserved in the merge.

4. End your file with a machine-readable score block in exactly this format
   (an HTML comment containing JSON — this must be the very last content in the file):

<!-- scores
{
  "v1": { "<criterion_name>": <score>, ... },
  "v2": { "<criterion_name>": <score>, ... }
}
-->

Criterion names in the JSON must match the Criterion column in the criteria file exactly
(snake_case). All variant tokens must appear. Scores are integers 1–10.
No model names anywhere in the output.

Write your output to: {{OUTPUT_FILE}}
```

---

## Final-Merge

```
You are a research synthesis expert producing the definitive version of a research document.

Original research prompt / question:
{{TOPIC}}

You have been given:
- {{N}} merged research documents from the previous round.
- Comparison reports from all evaluators (not just your own prior assessment).

Your task:
1. Read all comparison reports. Identify the consensus on: best structural scaffold, critical
   gaps, strongest content sections per variant.
2. Synthesise a merge strategy that draws on the best judgement across all evaluators —
   do not default to a single evaluator's strategy.
3. Write the final research document using this synthesised strategy.

The output must be:
- Prompt-faithful: the original research question must be answered directly and prominently.
- Complete: every gap flagged by any evaluator must be addressed.
- Well-structured: clear table of contents, logical flow, executive summary.
- Practical: actionable guidance, examples, standards references where relevant.
- Anonymous: no AI model names or identifying information.

Write your output to: {{OUTPUT_FILE}}
```

---

## Self-Audit

```
You are a quality auditor for a research document. You have been given:
- A completed research document (the final draft).
- Scoring criteria.
- All comparison reports from all rounds of the research process.

Original research prompt / question:
{{TOPIC}}

Your task:
1. First, assess prompt fidelity directly: does the final draft answer the original research
   prompt above? If it is a specific question, is the answer clearly stated? Note any
   mismatch between what was asked and what was produced.
2. Compile a deduplicated list of every gap, weakness, or missing item identified across
   all comparison reports.
3. For each item, assess whether the final draft addresses it:
   - Covered — fully addressed
   - Partial — mentioned but not developed
   - Missing — not present in the final draft
4. Write an audit table to {{AUDIT_FILE}}.
5. If any items are Missing, or if prompt fidelity is insufficient: append a short addendum
   section to {{DRAFT_FILE}} addressing those gaps before writing the audit table. Title the
   section "## Addendum: Additional Coverage" and place it at the appropriate point in the
   document.

Write the audit table to: {{AUDIT_FILE}}
Update the draft if needed at: {{DRAFT_FILE}}
```
