# Chart conventions

Hard constraints, layout recipes, theming patterns, anti-patterns, and the pre-ship checklist for Astro + D3 static SVG chart components in a Starlight docs site.

---

## Choosing a chart type

Before creating a new component, consult `references/chart-decision-tree.md` (From Data to Viz — Yan Holtz & Conor Healy). It maps data shape → recommended chart type in three steps:

1. Identify the **data family**: Categoric · Categoric+Numeric · Numeric · Relational · Map · Time Series.
2. Follow the branch for your specific shape (e.g. "one numeric value per group").
3. Pick the chart that matches the **intent** (Distribution · Correlation · Ranking · Part-of-a-whole · Evolution · Maps · Flow).

---

## Hard constraints

- **Zero client JS.** All logic runs in the Astro frontmatter (Node.js at build time). No `<script>` tags, no `client:*` directives, no browser D3.
- **`viewBox` only.** Never set `width` or `height` attributes on `<svg>`. Use `viewBox="0 0 VW VH"` and CSS `width: 100%; height: auto`.
- **Labels inside the SVG.** All text (axis labels, headers, annotations) must be `<text>` nodes inside the `viewBox`. HTML elements outside the SVG cause unrecoverable page overflow.
- **No default prop data.** Components are generic. Domain data lives in the MDX file as JSX props.
- **`@charts/` import alias.** Always. Never relative paths — they break because Vite resolves MDX from the odyssey source path.

---

## File structure

```
src/charts/MyChart.astro
```

Import in MDX:
```mdx
import MyChart from '@charts/MyChart.astro';
```

Alias is defined in `astro.config.mjs` (Vite `resolve.alias`) and `tsconfig.json` (`compilerOptions.paths`).

---

## SVG boilerplate

```astro
---
// all computation here
---

<figure class="chart-figure">
  <svg viewBox={`0 0 ${VW} ${VH}`} role="img" class="chart-svg">
    <!-- content -->
  </svg>
</figure>

<style>
  .chart-figure { margin: 1.5rem 0; }
  .chart-svg { display: block; width: 100%; height: auto; }
</style>
```

---

## Layout recipe

Define constants first, derive coordinates from them. Never use magic numbers.

```ts
// ── Constants ─────────────────────────────────────────────────────────────────
const CELL   = 100;    // grid cell size; must be ≥ 2 × R_MAX + gap
const LINE_H = 15;     // px between stacked label lines (declare FIRST — used in TOP)
const GAP    = 16;     // label-edge → bubble-edge spacing, both axes
const R_MAX  = 38;     // largest mark radius in the scale

const LEFT   = 78 + GAP;                        // fits two-line label + gap
const TOP    = LINE_H * 2 + GAP + R_MAX + GAP;  // two header lines + gaps + bubble arc

// ── Coordinate helpers ────────────────────────────────────────────────────────
const colX = (j: number) => LEFT + CELL / 2 + j * CELL;
const rowY = (i: number) => TOP  + CELL / 2 + i * CELL;

// ── ViewBox dimensions ────────────────────────────────────────────────────────
const VW = LEFT + N * CELL;
const VH = TOP  + N * CELL + 24;   // 24px bottom padding
```

**Column header base Y:**
```ts
const baseY = rowY(0) - R_MAX - GAP - 11;
// -11 is empirical; produces visual parity with the row-label horizontal gap
```

**Multi-line label vertical centring (row labels):**
```ts
const totalH = (label.length - 1) * LINE_H;
const y = cy - totalH / 2 + lineIndex * LINE_H + 4;
// +4 corrects SVG baseline vs. visual cap-height centre
```

---

## Theming recipe

### Selector rule

Always pair both selectors — Starlight uses either depending on context:

```css
:global([data-theme="dark"]) .cls,
:global(.sl-theme-dark) .cls { … }

:global([data-theme="light"]) .cls,
:global(.sl-theme-light) .cls { … }
```

### Coloured fills — use CSS custom properties, not presentation attributes

```tsx
{/* template */}
<circle
  style={`--fill-dark:${hex1};--fill-light:${hex2}`}
  class="my-bubble"
/>
```

```css
/* style block */
.my-bubble { fill: var(--fill-light); }

:global([data-theme="dark"]) .my-bubble,
:global(.sl-theme-dark) .my-bubble { fill: var(--fill-dark); }
```

### Glow / dark-only effects — CSS opacity, not conditional rendering

```css
.my-glow { opacity: 0; }

:global([data-theme="dark"]) .my-glow,
:global(.sl-theme-dark) .my-glow { opacity: 0.35; }
```

### Label fills

```css
/* Dark mode default — white */
.my-label { fill: #fff; }

/* Light mode override */
:global([data-theme="light"]) .my-label,
:global(.sl-theme-light) .my-label { fill: oklch(15% 0 0); }
```

### Axis / header labels

```css
.my-label {
  font-family: system-ui, sans-serif;
  fill: oklch(30% 0 0);
  opacity: 0.8;
}

:global([data-theme="dark"]) .my-label,
:global(.sl-theme-dark) .my-label { fill: rgba(255, 255, 255, 0.75); }
```

### Default colour palette

Use this palette when the user does not supply a `colors` prop. It covers 16 named hues, each with a dark-mode and light-mode variant:

```ts
export const colors = [
  { dark: '#f07070', light: '#c73030' }, // red
  { dark: '#5dd4c8', light: '#1a9e94' }, // teal
  { dark: '#f5c05a', light: '#c9921a' }, // amber
  { dark: '#f07ab0', light: '#c73a7a' }, // pink
  { dark: '#70d490', light: '#2a9e50' }, // green
  { dark: '#a078e8', light: '#5828b0' }, // indigo
  { dark: '#c8f060', light: '#7aaa10' }, // lime
  { dark: '#ffa07a', light: '#c85a20' }, // orange
  { dark: '#60d0f0', light: '#0878a8' }, // sky
  { dark: '#e08888', light: '#902020' }, // crimson
  { dark: '#f8e060', light: '#a87e00' }, // yellow
  { dark: '#b898f0', light: '#6c3fd4' }, // violet
  { dark: '#a8e8b8', light: '#1e7840' }, // mint
  { dark: '#f8c8a0', light: '#b85a10' }, // sienna
  { dark: '#88c8f8', light: '#1050a0' }, // cobalt
  { dark: '#f0d0f8', light: '#9a3ab8' }, // lavender
];
```

Place this constant in the MDX file (or a shared `src/data/` module) and pass it as the `colors` prop. Components cycle through the array by index — if a chart has more series than palette entries, wrap with `colors[i % colors.length]`.

---

## HTML grid + SVG chart pattern

When a set of small charts belongs together, the grid and legend live in the MDX document, not inside the chart component. The component renders only a bare `<svg>` — no `<figure>` wrapper, no legend.

```mdx
<div class="my-grid">
  {items.map((item, i) => (
    <div class="my-card">
      <MyChart ... />
    </div>
  ))}
</div>

<div class="my-legend"> ... </div>

<style>{`
  .my-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 12px;
  }
  .my-card {
    border: 1.5px solid oklch(65% 0 0 / 0.22);
    border-radius: 8px;
    padding: 6px;
  }
`}</style>
```

Use CSS custom properties (`--swatch-dark`, `--swatch-light`) for legend swatches via `style=` on HTML elements.

---

## RadialViolin — design patterns

`RadialViolin.astro` renders one continuous closed SVG path per category row, radiating as a ray from the centre.

Key design decisions (validated in v2):

- **One path per ray, not one path per bump.** `violinPath(row, θ)` samples the full radial extent, traces the right side outward then left side inward, closes with `Z`.
- **Width profile via cosine lobes.** `widthAt(row, r)` sums cosine-shaped lobes centred at each `ringR(j)` with half-height `BUMP_H2 = RING_PITCH * 0.48`. The 4% gap between adjacent bumps creates natural waist pinches.
- **Uniform bump height, variable width.** Only the perpendicular half-width `bumpW2(v)` varies with score, keeping ring radii comparable across rays.
- **12 steps per bump.** `STEPS_PER_BUMP = 12` → dense enough to look smooth without Bézier curves.
- **Ring label placement.** Labels sit at angle `−π/2 + π/N_RAYS` (halfway between ray 0 and ray 1) to avoid collisions.
- **Props share the `Row` shape with `Heatmap`.** `rows: { label: string; values: [string, number][] }[]` and `colors: { light: string; dark: string }[]` can be passed directly from the same MDX variables.

Layout constants (600×600 viewBox):

| Constant | Value | Role |
|---|---|---|
| `SIZE` | 600 | ViewBox width and height |
| `R_INNER` | 55 | Radius of innermost ring centre |
| `R_OUTER` | 220 | Radius of outermost ring centre |
| `R_LABEL` | 240 | Ray label placement radius |
| `BUMP_H2` | `RING_PITCH * 0.48` | Cosine lobe half-height along ray |
| `BUMP_W2_MAX` | `min(R_INNER * sin(π/N_RAYS) * 0.78, 30)` | Max perp half-width |
| `BUMP_W2_MIN` | 2 | Min perp half-width (keeps value=1 visible) |

---

## Voronoi half-plane clipping — sign convention

- `clipPolyByHalfPlane` sign formula: `sign(px,py) = (px−ax)*(−dy) + (py−ay)*dx`, where `(ax,ay)→(bx,by)` is the directed edge. Points with `sign ≥ 0` are **kept**.
- Clip to `x ≥ xMin`: direct the edge **upward** → `(xMin, canvasH, xMin, 0)`.
- Clip to `x ≤ xMax`: direct the edge **downward** → `(xMax, 0, xMax, canvasH)`.
- Clip to `y ≥ yMin`: direct the edge **rightward** → `(0, yMin, canvasH, yMin)`.
- **Anti-pattern**: using `y=0` and `y=1` for the clip edge makes `dy ≈ 0` and the sign formula degenerate — all polygons collapse. Always use the full canvas height.
- `computeVoronoiCell` bisector must use the **same** sign formula as `clipPolyByHalfPlane`.

---

## Anti-patterns — do not retry

| Pattern | Why it fails |
|---|---|
| `padding-top: X%` on HTML label wrapper | `%` padding is relative to container **width**, not height |
| `right: 100%` on absolutely-positioned HTML label | Escapes the container; causes page overflow |
| `overflow: visible` on SVG to let labels paint outside | Browser still allocates layout space; causes overflow |
| `fill="red"` presentation attribute on themed elements | CSS cannot reliably override SVG presentation attributes |
| Relative import path in MDX (`../../charts/Foo.astro`) | Vite resolves MDX from odyssey source path; path breaks |
| Default prop data in the component | Couples domain data to the component |

---

## Pre-ship checklist

- [ ] `<svg>` has `viewBox` only — no `width`/`height` attributes
- [ ] CSS has `width: 100%; height: auto` on the SVG
- [ ] All text is `<text>` inside the `viewBox`
- [ ] Every themed fill uses CSS custom properties, not presentation attributes
- [ ] Both `:global([data-theme])` and `:global(.sl-theme-*)` selectors present for each theme rule
- [ ] No data hardcoded in the component — all passed as props
- [ ] MDX import uses `@charts/` alias
