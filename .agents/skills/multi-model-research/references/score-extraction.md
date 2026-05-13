# Score Block Format

Every comparison file (`r<R>-compare.<token>.md`) must end with a score block in
this exact format — an HTML comment containing JSON. The score block must be the
very last content in the file.

```
<!-- scores
{
  "v1": {
    "prompt_fidelity":         9,
    "content_completeness":    8,
    "structural_clarity":      7,
    "reader_comprehension":    9,
    "depth_vs_breadth":        7,
    "practical_applicability": 8,
    "source_credibility":      7
  },
  "v2": {
    "prompt_fidelity":         7,
    "content_completeness":    7,
    "structural_clarity":      9,
    "reader_comprehension":    8,
    "depth_vs_breadth":        8,
    "practical_applicability": 7,
    "source_credibility":      8
  }
}
-->
```

Rules:
- Keys must match criterion names in `_criteria.md` exactly (plain snake_case).
- All variant tokens for the round must appear.
- Scores are integers 1–10. No decimals, no nulls.
- The block must be the very last content in the file — nothing after `-->`.

Score extraction, weighted-mean computation, tie-breaking, and malformed-block
handling are all implemented in `scripts/run.py`.
