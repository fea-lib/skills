# Templates

Use these templates to keep output stable and auditable.

## `brief.md`

```markdown
# Research Brief

## Question
<required>

## Intended Use
<required>

## Depth and Checkpoint Mode
- Depth: quick|standard|deep
- Mode: default|afk

## Scope
- In scope:
- Out of scope:

## Source Policy
- Preferred source types:
- Source distrusts / exclusions:
- Recency constraints:

## Tool Policy
- Default allowlist:
- Run allow overrides:
- Run disallow overrides:

## Evidence Threshold
<confidence expectation>

## Defaults and Assumptions
- <each inferred value must be explicit>
```

## `source-inventory.md`

```markdown
# Source Inventory

| ID | Source | Type | Date | Quality | Contribution | Limitations |
|---|---|---|---|---|---|---|
| S1 | <name/url/path> | web|local|repo|docs|paper|video | YYYY-MM-DD | high|medium|low | <how used> | <limitations> |
```

## `notes/<source-id>.md`

```markdown
# Source Note: <source-id>

## Metadata
- Source:
- Date:
- Type:
- Quality:

## Key Claims
- <claim>

## Evidence Extracts
- <quote or precise paraphrase>

## Limitations
- <known weaknesses>

## Secondary Leads
- <follow-up links/sources>
```

## `deferred-decisions.md` (AFK only)

```markdown
# Deferred Decisions

| Time | Trigger Type | What Was Deferred | Impact | Branch/Node |
|---|---|---|---|---|
| <iso> | scope_expansion | <decision> | <effect on confidence/coverage> | <node-id> |
```

## `final-report.md`

```markdown
# <Report Title>

## Executive Summary

## Research Question and Scope

## Methodology

## Key Findings

## Source Inventory

## Conflicts and Open Questions

## Blindspot / Gap Analysis

## Recommendations and Next Steps

## Confidence and Limits

## Deferred Decisions
<required in AFK mode; otherwise omit>
```
