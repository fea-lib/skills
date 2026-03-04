# Source Quality Rubric

Apply this rubric to every source in the source inventory. The goal is a short, honest annotation that helps the user calibrate how much weight to place on each source — not a gatekeeping filter.

Output format per source:

```
Quality: High / Medium / Low — [one-line reason]
```

Examples:
- `Quality: High — peer-reviewed, 2023, corroborated by S3 and S6`
- `Quality: Medium — credible outlet but opinion piece, no primary data cited`
- `Quality: Low — undated, no author, single uncorroborated claim`

---

## Evaluation Dimensions

Score each dimension mentally (strong / acceptable / weak). The overall rating reflects the combined picture — a single weak dimension rarely drops a source to Low, but two or more weak dimensions usually do.

---

### 1. Credibility

Who produced this, and are they in a position to know?

| Signal | Strong | Acceptable | Weak |
|--------|--------|------------|------|
| Authorship | Named expert with relevant credentials or institutional affiliation | Named author, credentials unclear | Anonymous, pseudonymous, or AI-generated without disclosure |
| Publisher | Peer-reviewed journal, reputable institution, official documentation | Established media, industry publication | Personal blog, content farm, PR wire, social media post |
| Methodology | Primary research or direct observation described | Secondary synthesis with cited sources | Assertion without evidence or sourcing |
| Transparency | Funding, conflicts of interest disclosed | Partial disclosure | No disclosure, or clear undisclosed conflict |

---

### 2. Recency

How sensitive is this topic to age?

| Domain | Acceptable age |
|--------|---------------|
| Rapidly evolving (AI/ML, crypto, geopolitics, software) | 6–18 months |
| Moderately evolving (business strategy, product design, medicine) | 1–3 years |
| Slowly evolving (foundational CS, history, law, established science) | 5–10 years or older is fine |

Flag sources that are older than the domain threshold. Note it as a weakness but do not automatically disqualify — older sources can still be valid for historical context or foundational concepts.

---

### 3. Bias Indicators

Does the source have a structural incentive to present a particular view?

- **Funding bias:** Research funded by an entity with a commercial stake in the outcome
- **Publication bias:** Only positive results published; negative results suppressed
- **Advocacy framing:** Source is produced by an organisation advocating for a particular position
- **Selection bias:** Evidence is cherry-picked; contradicting evidence ignored
- **Recency bias:** Overweights recent developments at the expense of established knowledge

Bias does not disqualify a source — it means the claim needs corroboration from an independent source before being treated as established.

---

### 4. Source Type

| Type | Default weight | Notes |
|------|---------------|-------|
| Primary research (original data, experiments, firsthand accounts) | High | The gold standard — but methodology must still be sound |
| Peer-reviewed secondary (meta-analysis, systematic review, textbook) | High | Strong if methodology is rigorous |
| Official documentation | High for factual claims about the system it describes | May be incomplete or aspirational |
| Reputable journalism / trade press | Medium | Good for context and events; weak for technical claims |
| Expert opinion / interview | Medium | Valuable perspective; not evidence by itself |
| Preprint (e.g. arXiv not yet peer-reviewed) | Medium | Treat as provisional; note if widely cited |
| Blog post / think piece | Low–Medium | Depends heavily on author credibility |
| Forum post / social media | Low | Useful for sentiment and anecdote; rarely citeable |
| AI-generated content | Low unless grounded | Treat as a starting point for search, not a source itself |

---

### 5. Corroboration

Is the claim supported by other independent sources?

- **Corroborated:** Two or more independent sources agree → increases confidence, note the agreement
- **Single source:** Only one source makes this claim → flag as unverified, especially if it is a strong or surprising claim
- **Contradicted:** Another source disagrees → surface both in Section 5 (Conflicts & Open Questions) of the report

The corroboration dimension is the most powerful single signal. A High-credibility source making an uncorroborated surprising claim should still be flagged as unverified.

---

## Overall Rating Decision Guide

| Situation | Rating |
|-----------|--------|
| Peer-reviewed, recent, corroborated, no obvious bias | High |
| Credible author/publisher, reasonable recency, mostly corroborated | High |
| Credible source but older than threshold, or single-source | Medium |
| No clear author, or known advocacy bias, or uncorroborated | Medium |
| Anonymous, undated, promotional, or contradicted by stronger sources | Low |
| AI-generated without grounding, or demonstrably incorrect | Low |

When in doubt, rate conservatively and explain why in the annotation. The user can then decide how to weight it.
