# Default Research Scoring Criteria

These seven criteria are used in every comparison phase. Each is scored 1–10 per variant.
Copy this file verbatim to `OUT_DIR/_criteria.md` when no custom criteria are supplied.

---

| Criterion | Weight | What it measures |
|-----------|--------|-----------------|
| prompt_fidelity | 2 | Does the document directly address the research prompt or question? For open topics: does it cover the expected scope? For specific questions: does it provide a clear, direct answer? |
| content_completeness | 2 | Are all relevant facets of the topic covered? Are there notable gaps or omissions? |
| structural_clarity | 1 | Is the document easy to navigate? Are headings, flow, and information hierarchy logical? |
| reader_comprehension | 1 | Is the writing clear for the intended audience? Are concepts explained without unexplained jargon? |
| depth_vs_breadth | 1 | Does the document go appropriately deep where it matters without padding thin topics? |
| practical_applicability | 1 | Does it include actionable guidance, code examples, patterns, or decision rules? |
| source_credibility | 1 | Are claims grounded in known standards, specifications, or verifiable references? |

`prompt_fidelity` and `content_completeness` carry double weight (2) — all other criteria
carry single weight (1). The orchestrator computes a weighted mean per variant.
The `structural_clarity` score is the tie-breaker when two variants share the same weighted mean.

---

## Customising criteria

Tell the orchestrator your preferred criteria during setup, or supply a `_criteria.md` in
`OUT_DIR` before Phase 0 completes. The format must be a markdown table with columns
`Criterion`, `Weight`, and `What it measures`. Criterion names must be plain snake_case —
they are used as JSON keys in score blocks and must match exactly. Weights are positive
integers; higher = more influence on the final ranking.
