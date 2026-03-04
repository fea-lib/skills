# Chart Decision Tree
Source: "From Data to Viz" — Yan Holtz & Conor Healy (data-to-viz.com)

**Intent codes:** `Dist` Distribution · `Corr` Correlation · `Rank` Ranking · `Part` Part-of-a-whole · `Evo` Evolution · `Flow` Flow

## How to use this tree

To recommend a chart given a user's context:

1. **Identify the primary data type** — choose the matching top-level section:
   - **CATEGORIC** — data is labels, categories, or text with no inherent numeric value
   - **NUMERIC** — data is purely numeric variables (one or more)
   - **CATEGORIC AND NUMERIC** — groups/categories each have one or more numeric measurements
   - **RELATIONAL** — data describes connections, networks, or flows between entities
   - **MAP** — data has a geographic dimension (regions, coordinates)
   - **TIME SERIES** — one or more numeric variables measured repeatedly over time

2. **Answer the sub-questions in order** — each level narrows the options by structure (how many variables? how many groups?) and then by intent (distribution? ranking? correlation?).

3. **Match the user's intent to an intent code** — if the user says "I want to show how values are distributed", lean toward `Dist` options; "compare" or "rank" → `Rank`; "relationship" or "correlation" → `Corr`; "proportion" or "part of a whole" → `Part`; "change over time" → `Evo`; "flow" or "connections" → `Flow`.

4. **Return the chart name(s)** from the matching leaf, preferring the first listed option unless the user's context favours a specific variant.

## When a user asks "when should I use chart X?"

Scan all sections of the tree for every occurrence of that chart name. For each occurrence, reconstruct the conditions that lead to it (data type → structural question → intent), then summarise those as plain-language "use this when..." statements. If the chart appears in multiple places, explain each distinct scenario separately.

---

## CATEGORIC

- **One variable**
  - Rank / compare values → Bar [Rank] · Lollipop [Rank] · Circular barplot [Rank]
  - Show proportions → Treemap [Part] · Pie / Donut [Part]
  - Many groups, show proportions → Waffle [Part]
  - Text data → Wordcloud [Dist]
- **Several variables**
  - Nested hierarchy → Sunburst [Part] · Treemap (nested) [Part]
  - Network / co-occurrence → Network [Flow]
  - Exactly two categories → Venn diagram [Part] · Chord diagram [Flow]
- **Ordered / time-like**
  - Static snapshot → Barplot [Rank]
  - Change over time → Stacked barplot [Evo]

---

## CATEGORIC AND NUMERIC

- **One numeric value per group**
  - Few groups → Barplot [Rank] · Lollipop [Rank]
  - Many groups → Circular barplot [Rank] · Treemap [Part]
  - Groups are ordered / time-like → Line chart [Evo] · Area chart [Evo]
- **Several numeric values per group**
  - Show distribution → Violin [Dist] · Boxplot [Dist] · Ridgeline [Dist] · Jitter / Stripplot [Dist]
  - Show correlation across groups → Heatmap [Corr]
  - Multivariate profile per group → Spider / Radar [Part]
- **N groups × M measures (matrix)**
  - One value per (group, measure) → Heatmap [Corr]
  - Distribution per (group, measure) → Grouped violin [Dist]
- **Proportion per group**
  - Few groups → Stacked barplot [Part]
  - Many groups → Stacked area [Part]
- **Several groups over time**
  - Show individual trajectories → Multi-line chart [Evo]
  - Show composition change → Stacked area [Evo] · Stream graph [Evo]
- **Other**
  - One numeric value + explicit rank → Lollipop [Rank]
  - Quantity per group, size encodes magnitude → Bubble chart [Dist]

---

## NUMERIC

- **One variable**
  - Show distribution → Histogram [Dist] · Density plot [Dist]
  - Compare distribution across several groups → Violin [Dist] · Boxplot [Dist] · Ridgeline [Dist]
- **Two variables**
  - Show relationship → Scatter plot [Corr]
  - Show relationship + third quantity → Bubble chart [Corr]
  - Many overlapping points → 2D density / Hexbin [Dist] · Contour plot [Dist]
- **Several variables**
  - Pairwise correlations → Correlogram [Corr] · Scatter matrix [Corr]
  - All variables simultaneously → Parallel coordinates [Corr]
  - Variables + individual observations → Heatmap [Corr]
- **Many observations**
  - One continuous variable → Histogram [Dist] · Density [Dist]
  - Two continuous variables → 2D histogram / Hexbin [Dist]

---

## RELATIONAL

- **Network**
  - No values on edges → Network graph [Flow]
  - Values on edges → Arc diagram [Flow] · Chord diagram [Flow]
  - Hierarchical structure → Dendrogram [Flow] · Treemap [Part]
  - Similarity / distance matrix → MDS plot [Corr]
- **Flow / migration**
  - Show volume flows between nodes → Sankey [Flow] · Alluvial [Flow]

---

## MAP

- Numeric value per region → Choropleth [Dist / Corr]
- Numeric value per location → Bubble map [Dist]
- Connections between locations → Connection map [Flow]
- Density of point locations → Hexbin map [Dist]

---

## TIME SERIES

- **One series**
  - Show trend → Line chart [Evo] · Area chart [Evo]
  - Show distribution over time → Boxplot (time) [Dist] · Violin (time) [Dist] · Ridgeline [Dist]
- **Several series**
  - Show individual trajectories → Multi-line chart [Evo]
  - Show distribution over time → Boxplot (time) [Dist] · Violin (time) [Dist] · Ridgeline [Dist]
  - Show proportions / composition → Stacked area [Evo] · Stream graph [Evo]
- **Specialised**
  - Ordered events / intervals → Timeline [Evo]
  - Cyclic / seasonal pattern → Circular / Polar area [Evo]
  - Two variables correlated over time → Connected scatter [Corr]
  - Discrete events with magnitude → Lollipop (time) [Evo]
