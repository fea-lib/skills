# Plug-and-Play Docs App for Markdown/MDX via npx
## Research Report

**Date:** 2026-05-14  
**Topic:** Building an npm package invocable via `npx docs` that wraps a docs framework (Astro/Starlight or alternatives) to serve and build `.md`/`.mdx` files from any directory

---

## Table of Contents

1. [Existing Tools / Prior Art](#1-existing-tools--prior-art)
2. [MDX Alternatives — Format Comparison](#2-mdx-alternatives--format-comparison)
3. [The Astro/Starlight Wrapping Approach](#3-the-astrostarlight-wrapping-approach)
4. [Alternative Architectures](#4-alternative-architectures)
5. [Recommendation](#5-recommendation)
6. [Implementation Sketch](#6-implementation-sketch)
7. [Risks and Gotchas](#7-risks-and-gotchas)

---

## 1. Existing Tools / Prior Art

### Evaluation Criteria

| Criterion | Description |
|-----------|-------------|
| **npx-friendly** | Can be run via `npx <pkg>` with zero prior installation |
| **MDX/component support** | Embeds React/Svelte/Vue/web components in markdown |
| **gitignore-aware** | Respects `.gitignore` when discovering files |
| **Zero-pollution** | No required config files committed to the user's repo |
| **Static output** | Produces deployable HTML for GitHub Pages etc. |
| **Dev mode** | Live-reloading local server |

---

### 1.1 VitePress

**Website:** vitejs.dev/vitepress  
**Stack:** Vite + Vue 3

VitePress is the most mature "npx-friendly" docs tool in the ecosystem. Its `vitepress init` scaffolds a minimal config, but you can also run `vitepress dev .` against an arbitrary directory with almost no config.

- **npx-friendly:** Excellent. `npx vitepress dev docs/` works out of the box. No install needed.
- **MDX/component support:** Uses Vue SFCs in markdown via `<script setup>`, not MDX. React/Svelte components require workarounds (web components bridge). Custom Vue components work natively.
- **gitignore-aware:** File discovery is handled by Vite's file scanner; does not natively filter `.gitignore` entries, but since the content dir is user-specified, gitignored files (like `node_modules`) are excluded by default path conventions.
- **Zero-pollution:** Near-zero. `vitepress dev` with a `--config` flag pointing to a minimal file works. However, it writes a `.vitepress/` cache dir into the content directory by default (polluting the user repo). This can be redirected via `cacheDir` option.
- **Static output:** First-class. `vitepress build` → `dist/`.
- **Dev mode:** Excellent HMR.

**Verdict:** Best out-of-the-box experience for a zero-config wrapper. The main weakness is Vue-only component embedding; React/Svelte need the web components bridge.

---

### 1.2 Docusaurus

**Website:** docusaurus.io  
**Stack:** React + MDX

Docusaurus is feature-rich but not npx-friendly in the "run against an existing dir" sense. It's a project scaffolder, not a server-against-arbitrary-dir tool.

- **npx-friendly:** Partial. `npx create-docusaurus` scaffolds a new project. Running Docusaurus against an existing arbitrary markdown directory without scaffolding requires wrapping it yourself.
- **MDX/component support:** Excellent. Native MDX 2, React components, custom layouts.
- **gitignore-aware:** No explicit gitignore integration; relies on standard node/webpack ignore patterns.
- **Zero-pollution:** Poor. Requires `docusaurus.config.js` (or `.ts`), `sidebars.js`, and a `docs/` directory structure in the project root.
- **Static output:** Excellent. `docusaurus build` → `build/`.
- **Dev mode:** Good HMR.

**Verdict:** Too much scaffolding overhead for a plug-and-play tool. Better suited as an internal framework to wrap.

---

### 1.3 Nextra

**Website:** nextra.site  
**Stack:** Next.js + MDX

Nextra is a thin layer over Next.js that turns a `pages/` directory of `.mdx` files into a docs site.

- **npx-friendly:** Poor. Requires a Next.js project structure. Not runnable against an arbitrary dir via npx.
- **MDX/component support:** Excellent. MDX native, React components.
- **gitignore-aware:** No.
- **Zero-pollution:** Poor. Needs `next.config.js`, `theme.config.jsx`, `pages/_app.tsx`.
- **Static output:** Via `next export`. Produces static HTML.
- **Dev mode:** Good.

**Verdict:** Overkill and high pollution. The Next.js overhead is not justified for a plug-and-play scenario.

---

### 1.4 Fumadocs

**Website:** fumadocs.vercel.app  
**Stack:** Next.js + MDX

Fumadocs is even more opinionated than Nextra, requiring a full Next.js app with `app/` router.

- **npx-friendly:** Very poor. No zero-config mode.
- **MDX/component support:** Excellent.
- **Zero-pollution:** Very poor.
- **Static output:** Via `next export`.

**Verdict:** Not suitable for a plug-and-play wrapper.

---

### 1.5 Starlight (Astro)

**Website:** starlight.astro.build  
**Stack:** Astro + Starlight theme

Starlight is Astro's official documentation theme. It is content-collection-based and highly configurable.

- **npx-friendly:** Partial. `npm create astro -- --template starlight` scaffolds a project. Running Starlight against an arbitrary external directory is possible but requires framework-level hacking (see Section 3).
- **MDX/component support:** Excellent. Astro supports MDX natively via `@astrojs/mdx`. You can embed React, Svelte, Vue, and web components in `.mdx` files.
- **gitignore-aware:** Not natively; Vite's scanner can be customized.
- **Zero-pollution:** Moderate. An Astro project lives in `node_modules/<your-pkg>` and can be run from there; the user's repo needs zero Astro files (see Section 3).
- **Static output:** Excellent. `astro build` → `dist/`.
- **Dev mode:** Excellent HMR.

**Verdict:** Best candidate for wrapping. The content collection system can point at a dynamically resolved external directory.

---

### 1.6 Mintlify / GitBook / ReadMe.io

These are hosted SaaS products. They can sync from a GitHub repo and render docs, but:

- Require accounts and cloud dependency.
- Do not run locally via `npx`.
- Not suitable for a self-hosted plug-and-play tool.

They are relevant as **UX references** — Mintlify in particular has a great zero-config experience from a `mint.json` file. Their config convention design is worth studying.

---

### 1.7 Docsify

**Website:** docsify.js.org  
**Stack:** Client-side JS markdown renderer

Docsify serves raw markdown and renders it in the browser. No build step needed.

- **npx-friendly:** Excellent. `npx docsify-cli serve docs/` works immediately.
- **MDX/component support:** None natively. Components can be added via custom plugins but not MDX.
- **gitignore-aware:** No file collection — serves the directory as-is.
- **Zero-pollution:** Excellent. No config required; optional `_sidebar.md`.
- **Static output:** Poor. Requires client-side JS to render; not truly static HTML.
- **Dev mode:** Good (serves live).

**Verdict:** Meets the plug-and-play bar but fails on static output (no pre-rendered HTML) and component embedding.

---

### 1.8 MkDocs

**Stack:** Python

- Requires Python. Not npx-friendly.
- No MDX support.
- Excellent static output.
- Not suitable.

---

### 1.9 mdBook

**Stack:** Rust

- Requires Rust/cargo. Not npx-friendly (though a prebuilt binary could be distributed).
- No MDX support.
- Good static output.
- Not suitable without significant wrapping work.

---

### 1.10 Docute

**Stack:** Client-side JS (similar to Docsify)

- Abandoned (last release 2020).
- Similar trade-offs to Docsify.

---

### 1.11 @slidev/cli (Slidev)

**Website:** sli.dev  
**Stack:** Vite + Vue + markdown

Slidev is the closest architectural analogue to what we want to build — it is an npm package you invoke via `npx @slidev/cli` against a single markdown file.

Key architectural patterns borrowed from Slidev:
1. The CLI writes a temporary Vite config into a temp directory and invokes Vite programmatically.
2. It uses **Vite virtual modules** to inject the user's content file path into the Vite graph without copying files.
3. It watches the user's file and triggers HMR via the virtual module.
4. The package ships a complete Vite app (Vue SPA) in `node_modules`.

**This is the architectural blueprint.** Slidev proves the pattern works at scale.

---

### 1.12 live-server + plain markdown viewers

Tools like `npx serve`, `npx http-server`, or browser extensions that render markdown are not suitable — they do not transform MDX, generate navigation, or produce static HTML.

---

### Summary Table

| Tool | npx-friendly | MDX/Components | Zero-pollution | Static output | Dev mode |
|------|-------------|----------------|----------------|---------------|----------|
| VitePress | ✅ Excellent | ⚠️ Vue only | ⚠️ Cache dir leak | ✅ | ✅ |
| Docusaurus | ⚠️ Scaffolder | ✅ React+MDX | ❌ | ✅ | ✅ |
| Nextra | ❌ | ✅ React+MDX | ❌ | ✅ | ✅ |
| Fumadocs | ❌ | ✅ React+MDX | ❌ | ✅ | ✅ |
| Starlight | ⚠️ Scaffolder | ✅ All frameworks | ✅ (wrappable) | ✅ | ✅ |
| Mintlify | ❌ SaaS | ✅ | ✅ | ✅ | ❌ |
| Docsify | ✅ | ❌ | ✅ | ❌ CSR only | ✅ |
| MkDocs | ❌ Python | ❌ | ⚠️ | ✅ | ✅ |
| mdBook | ❌ Rust | ❌ | ⚠️ | ✅ | ✅ |
| Slidev | ✅ | ✅ Vue | ✅ | ✅ | ✅ |

---

## 2. MDX Alternatives — Format Comparison

The three user requirements for format:
1. **Human-readable raw** — the raw source must be legible without rendering
2. **Component embedding** — embed React, Svelte, Vue, or web components
3. **Plug-and-play** — zero special syntax knowledge required

---

### 2.1 MDX

MDX is markdown with JSX embedded. A `.mdx` file looks like:

```mdx
# My Heading

Regular paragraph text here.

import { Chart } from './Chart'

<Chart data={myData} />

More markdown text.
```

**Human-readability:** Good for markdown portions; JSX imports are slightly noisy but readable.  
**Component embedding:** Excellent — native JSX, any React/Preact component.  
**Plug-and-play:** Framework-specific. MDX v2 has a universal compiler but needs an integration (`@astrojs/mdx`, `@next/mdx`, etc.).  
**Spec stability:** MDX 2 is stable; MDX 3 is current.  
**Ecosystem:** Large. Most docs frameworks support it.

**Verdict:** Best choice for React-centric component embedding. For multi-framework (React + Svelte + Vue), it still works via Astro's MDX integration.

---

### 2.2 Markdoc

Markdoc (by Stripe) uses a tagged template syntax rather than JSX:

```markdoc
# My Heading

Regular paragraph here.

{% chart data=$myData /%}
```

**Human-readability:** Excellent — tags look like clean annotations, not code.  
**Component embedding:** Good, but framework-agnostic via a rendering layer. Components are registered separately and the syntax is declarative (no imports in the document).  
**Plug-and-play:** Requires a Markdoc renderer integration. Less ecosystem support than MDX.  
**Spec stability:** Stable but smaller ecosystem.  
**Key advantage:** Documents are pure data — a Markdoc document can be parsed to an AST and rendered to any target (React, HTML, etc.) without evaluating JS in the document.

**Verdict:** Better raw readability than MDX, great for structured docs. Weaker ecosystem and harder to set up multi-framework component embedding. Ideal if the primary concern is human authoring and content safety.

---

### 2.3 Standard Markdown + HTML Custom Elements (Web Components)

This approach keeps `.md` files as pure CommonMark/GFM and uses HTML custom element syntax for components:

```markdown
# My Heading

Regular paragraph here.

<my-chart data="[1,2,3]"></my-chart>
```

**Human-readability:** Excellent — raw markdown is fully readable; custom element tags are simple HTML.  
**Component embedding:** Depends on registration. Web components run in the browser. For SSR, you need Declarative Shadow DOM or a pre-render step. Cannot directly embed React/Svelte/Vue components without a WC wrapper.  
**Plug-and-play:** Standard HTML. No special syntax. But requires wrapping all components as custom elements, adding friction.  
**Static output:** Requires pre-rendering for web components (Lit SSR, etc.).

**Verdict:** Best raw readability, but the component embedding story is limited to web components and adds WC-wrapper overhead for existing React/Svelte/Vue libs.

---

### 2.4 Astro's `.astro` Files

`.astro` files are a component format that mixes a frontmatter script block with an HTML template:

```astro
---
import Chart from './Chart.jsx'
---

# Not actually markdown

<h1>My Heading</h1>
<Chart data={[1,2,3]} />
```

**Human-readability:** Poor — not actual markdown. Authors must write HTML or use remark/markdown processing manually.  
**Component embedding:** Excellent.  
**Verdict:** Not suitable as an authoring format. Only useful as layout/wrapper components.

---

### 2.5 Org-mode / AsciiDoc

- **Org-mode:** Emacs-native, not widely supported in JS toolchains.
- **AsciiDoc:** Used by Antora; good tooling but smaller ecosystem than Markdown.

Neither meets the "plug-and-play" requirement without significant custom tooling.

---

### 2.6 Format Recommendation Matrix

| Format | Raw readability | Component embedding | Plug-and-play | Multi-framework |
|--------|----------------|---------------------|---------------|-----------------|
| MDX | Good | Excellent | Good | ✅ via Astro |
| Markdoc | Excellent | Good | Moderate | ✅ via renderer |
| MD + Web Components | Excellent | Limited | Excellent | ⚠️ WC only |
| `.astro` | Poor | Excellent | n/a | ✅ |
| AsciiDoc | Good | Poor | Poor | ❌ |

**Winner for this use case: MDX**, specifically because Astro's MDX integration supports all three component frameworks simultaneously. A `.mdx` file can import a React component, a Svelte component, and a Vue component in the same document when using Astro.

**Secondary recommendation:** Support both `.md` and `.mdx` — pure `.md` files work without any special syntax, satisfying the raw readability requirement for non-component pages.

---

## 3. The Astro/Starlight Wrapping Approach

### 3.1 Can Astro Content Collections Point at External Directories?

Astro's content collections (v2+) are defined in `src/content/config.ts` and by default resolve to `src/content/<collection>/`. As of Astro 4.x, the `base` configuration for a collection is always relative to `src/content/`.

**Option A: Symlink**

Create a symlink at build time:
```
<pkg>/template/src/content/docs → <user-cwd>/
```

This works on macOS/Linux. Astro follows symlinks. Vite's file watcher (`chokidar`) requires `followSymlinks: true` (which is the default).

**Option B: Astro `srcDir` + `root` flags**

Astro CLI supports:
```
astro dev --root <path> --srcDir <path>
```

The `--root` flag sets the project root (where `astro.config.mjs` is found). The `--srcDir` flag sets the source directory (equivalent to `src/`). If we point `--srcDir` at the user's directory, Astro will look for `content/`, `pages/`, etc. inside the user's directory — but Starlight uses a specific content collection structure.

This is promising for a custom Astro setup but requires more work to make Starlight's content collection work without the expected directory structure.

**Option C: Vite Virtual Modules**

Implement a Vite plugin that intercepts content collection imports and resolves them to the user's directory dynamically. This is the most robust but requires implementing a virtual file system.

```ts
// vite-plugin-user-content.ts
export function userContentPlugin(userDir: string): Plugin {
  return {
    name: 'user-content',
    resolveId(id) {
      if (id.startsWith('virtual:user-content/')) {
        return '\0' + id
      }
    },
    load(id) {
      if (id.startsWith('\0virtual:user-content/')) {
        const rel = id.replace('\0virtual:user-content/', '')
        return `export * from '${path.join(userDir, rel)}'`
      }
    }
  }
}
```

**Option D: Astro 5 `srcDir` + Content Layer API**

Astro 5 introduced the **Content Layer API**, which allows defining custom loaders for content collections. A custom loader can pull files from any location:

```ts
// astro.config.mjs (inside the package's template)
import { defineCollection } from 'astro:content'
import { glob } from 'astro/loaders'

const docs = defineCollection({
  loader: glob({
    pattern: '**/*.{md,mdx}',
    base: process.env.DOCS_USER_DIR, // injected by our CLI
  }),
})
```

This is the cleanest approach and doesn't require symlinks. The `glob` loader in Astro 5's Content Layer API can point at any absolute path.

**Recommendation:** Use **Astro 5 Content Layer API with the `glob` loader** pointed at the user's directory via an environment variable injected by the CLI. This is symlink-free, works on Windows, and is the officially supported pattern.

---

### 3.2 Running Astro from node_modules

The package would ship an `astro-template/` directory containing:

```
astro-template/
  astro.config.mjs       # shipped with the package
  src/
    content/
      config.ts          # defines collections using process.env.DOCS_USER_DIR
    pages/               # Starlight routes (or custom)
  package.json           # astro + starlight as dependencies
```

The CLI entry point would:
1. Resolve the package's own `astro-template/` directory.
2. Set `DOCS_USER_DIR` environment variable.
3. Invoke Astro programmatically or via `child_process.spawn`.

```ts
import { spawn } from 'child_process'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const templateDir = path.join(__dirname, '../astro-template')

process.env.DOCS_USER_DIR = process.cwd()

spawn('node', [
  path.join(templateDir, 'node_modules/.bin/astro'),
  'dev',
  '--root', templateDir,
], {
  stdio: 'inherit',
  env: process.env,
})
```

**Key concern:** Astro and its plugins must be installed in `astro-template/node_modules/`, not at the root. This means the package's `package.json` does not list `astro` as a direct dependency — instead, `astro-template/package.json` does, and `npm install` is run inside `astro-template/` as part of the package's `postinstall` script or bundled pre-installed.

**Preferred approach: Bundle `astro-template/node_modules` pre-installed.** When publishing the npm package, include the `astro-template/node_modules/` directory. This avoids a `postinstall` step and makes `npx` invocations faster (though it increases package size).

---

### 3.3 Starlight Sidebar Auto-Generation

Starlight supports `autogenerate` for sidebar groups:

```ts
starlight({
  sidebar: [
    {
      label: 'Docs',
      autogenerate: { directory: 'docs' },
    },
  ],
})
```

When using the Content Layer API with `glob`, the `autogenerate` directive may not work directly because it expects files relative to `src/content/docs/`. 

**Workaround:** Generate the sidebar programmatically in the `astro.config.mjs` by scanning the user's directory at startup (using `fast-glob`) and building a sidebar config. This runs at Astro startup time before content processing.

```ts
import fg from 'fast-glob'

const userDir = process.env.DOCS_USER_DIR
const files = await fg('**/*.{md,mdx}', { cwd: userDir, ignore: await getGitignorePatterns(userDir) })
const sidebar = buildSidebarFromFiles(files)
```

---

### 3.4 Gitignore Integration

Use the `ignore` npm package (same logic as git) to filter files:

```ts
import ignore from 'ignore'
import fs from 'fs'
import path from 'path'

function loadGitignore(dir: string) {
  const ig = ignore()
  const gitignorePath = path.join(dir, '.gitignore')
  if (fs.existsSync(gitignorePath)) {
    ig.add(fs.readFileSync(gitignorePath, 'utf8'))
  }
  return ig
}
```

Also respect parent `.gitignore` files by traversing up the directory tree.

---

### 3.5 Config Convention Design

The user's directory can contain an optional `docs.config.ts` (or `.js`, `.mjs`):

```ts
// docs.config.ts (in user's repo root — optional)
import { defineConfig } from 'your-pkg'

export default defineConfig({
  title: 'My Project Docs',
  description: 'Documentation for my project',
  theme: 'starlight',           // or 'minimal', custom
  logo: './logo.svg',
  favicon: './favicon.ico',
  
  // Override sidebar (otherwise auto-generated)
  sidebar: [
    { label: 'Getting Started', link: '/getting-started' },
    { label: 'API', autogenerate: { directory: 'api' } },
  ],
  
  // Custom components to make available globally in MDX
  components: {
    Callout: './src/components/Callout.jsx',
    Demo: './src/components/Demo.svelte',
  },
  
  // Framework integrations to enable
  integrations: ['react', 'svelte', 'vue'],
  
  // Output directory for static build
  outDir: './docs-dist',
  
  // GitHub Pages base path
  base: '/my-repo',
})
```

The CLI reads this config at startup using `jiti` (TypeScript-aware require) or `tsx`:

```ts
import { createJiti } from 'jiti'

const jiti = createJiti(import.meta.url)
const userConfig = await jiti.import(path.join(userDir, 'docs.config.ts'), { default: true })
```

---

### 3.6 Astro `--root` and `--srcDir` Flags

Testing these flags against Astro 4.x/5.x:

- `--root <path>`: Sets where `astro.config.mjs` is resolved. **Usable** — our CLI can point this at the package's template directory.
- `--srcDir <path>`: Sets the `src/` directory. **Limited use** — Starlight has opinions about the `src/content/docs/` structure.
- `--outDir <path>`: Sets the build output directory. **Usable** — point to user's desired output dir.

The most reliable invocation is:

```bash
astro dev \
  --root /path/to/package/astro-template \
  --outDir /path/to/user-cwd/docs-dist
```

And inject user config via environment variables.

---

### 3.7 Windows Symlink Considerations

Windows requires either:
- Developer Mode enabled (Windows 10+), OR
- Administrator privileges

for `fs.symlinkSync`. This makes the symlink approach unreliable on Windows. The **Astro 5 Content Layer API glob loader** approach completely avoids this issue and is the recommended path.

---

## 4. Alternative Architectures

### 4.1 VitePress as the Core

VitePress is actually the strongest alternative to Astro/Starlight.

**Approach:**
```
your-pkg/
  cli.ts               # CLI entry
  vitepress-app/       # Embedded VitePress "project"
    .vitepress/
      config.ts        # Dynamically generated or static with env var injection
    theme/
      index.ts         # Custom theme
```

VitePress can be run programmatically:

```ts
import { createServer } from 'vitepress'

const server = await createServer(
  root,              // points to embedded vitepress-app/
  { srcDir: userCwd }  // ← VitePress respects this
)
await server.listen()
```

VitePress's `srcDir` option directly controls where markdown files are sourced from — this is a first-class API, not a workaround.

**Component embedding limitation:** VitePress uses Vue 3. You can embed Vue components natively. For React or Svelte, you need web component wrappers or custom Vite plugins. This is the main reason VitePress loses to Astro for multi-framework component support.

**Trade-off summary:**
- Simpler architecture than Astro wrapping
- Smaller package size
- Faster cold start
- Limited to Vue components natively
- `srcDir` API is first-class and well-supported

---

### 4.2 Vite + Custom MDX Plugin

Build a fully custom wrapper:

```
your-pkg/
  cli.ts
  vite.config.ts      # Vite config with MDX plugin
  app/
    index.html
    main.ts           # React/Vue SPA entry
    App.tsx           # Renders MDX content
```

Use `@mdx-js/rollup` or `vite-plugin-mdx` to process MDX files. Write a custom navigation sidebar from file discovery.

**Pros:** Full control, minimal dependencies.  
**Cons:** Significant implementation work. You're essentially rebuilding VitePress/Starlight from scratch. Static HTML output requires implementing SSG yourself (or using `vite-ssg`, `vite-plugin-ssr`/`vike`).

---

### 4.3 Esbuild/Rollup + Remark/Rehype Pipeline

Pure pipeline approach: walk the directory tree, process each `.md`/`.mdx` file through remark/rehype, render to HTML using a React/Svelte SSR renderer, write HTML files.

```
your-pkg/
  cli.ts
  pipeline/
    discover.ts      # File discovery with gitignore support
    process.ts       # remark/rehype/MDX compilation
    render.ts        # SSR render to HTML
    write.ts         # Write output files
  theme/
    layout.tsx       # React layout component
    styles.css
```

**Pros:** Maximum control, no framework opinions.  
**Cons:** Extremely high implementation effort. HMR/dev server requires custom WebSocket plumbing. Navigation generation is manual. This is a full docs framework implementation.

---

### 4.4 Next.js or Remix with `--dir` Flag

Both require a project structure and are not runnable against an arbitrary directory via npx. Too heavy for this use case.

---

### 4.5 Parcel with MDX

Parcel supports MDX via `@parcel/transformer-mdx`. It can process files from arbitrary input paths. However:
- No built-in docs theme/navigation.
- No sidebar auto-generation.
- Would require building the docs UI from scratch.

Interesting as a bundler choice but not a complete solution.

---

### 4.6 Architecture Comparison

| Architecture | Implementation effort | Component frameworks | Static output | Dev mode | npx startup time |
|--------------|----------------------|---------------------|---------------|----------|-----------------|
| Wrap Astro/Starlight | Medium | All | Excellent | Excellent | Slower (Astro startup) |
| Wrap VitePress | Low | Vue only | Excellent | Excellent | Fast |
| Vite + MDX custom | High | All | Medium | Good | Fast |
| Remark/Rehype pipeline | Very high | All | Good | Poor | Fastest |

---

## 5. Recommendation

### 5.1 Primary Recommendation: Wrap VitePress with Web Component Bridge

**Rationale:** VitePress's `srcDir` API is precisely designed for this use case. It can point at an external directory out of the box. The architecture is simpler, the package is smaller, and the cold-start time is faster.

For multi-framework component support, use the **Vite Web Components** bridge:
- Wrap React components as custom elements using `@lit-labs/react` or `react-to-web-component`.
- Wrap Svelte components using `svelte-custom-element`.
- Ship Vue components natively.

This gives 80% of the use cases with 40% of the complexity.

**However**, if genuine first-class React/Svelte/Vue MDX embedding (not web component wrappers) is required, switch to the Astro approach.

---

### 5.2 Secondary Recommendation: Wrap Astro 5 + Starlight (for multi-framework first-class support)

Use Astro 5's Content Layer API with a `glob` loader to mount the user's directory. This is the right choice when:
- Users need to import and use React, Svelte, or Vue components directly in `.mdx` files without wrapping them as web components.
- The docs site needs a polished out-of-the-box appearance (Starlight provides this).

---

### 5.3 Content Mounting Strategy

**Recommended: Astro 5 Content Layer glob loader with environment variable injection.**

```
DOCS_USER_DIR=/path/to/user/project astro dev --root /path/to/pkg/template
```

No symlinks required. Works on Windows. Officially supported API.

---

### 5.4 Config Convention Design

Minimal `docs.config.ts` in the user's repo:

```ts
export default {
  title: string,
  description?: string,
  logo?: string,
  base?: string,           // for GitHub Pages subdirectory
  outDir?: string,         // default: './docs-dist'
  integrations?: ('react' | 'svelte' | 'vue')[],  // default: auto-detect from user's package.json
  sidebar?: SidebarItem[],  // default: auto-generated from file tree
  components?: Record<string, string>,  // global MDX component overrides
}
```

Keep it minimal. Auto-detect React/Svelte/Vue from the user's `package.json` dependencies.

---

### 5.5 npx Invocation Design

**Package name:** `@yourorg/docs` or `docs-cli` (check availability).

```bash
# Dev mode
npx @yourorg/docs

# Build static output
npx @yourorg/docs build

# Build and deploy to GitHub Pages
npx @yourorg/docs deploy

# Specify a subdirectory
npx @yourorg/docs --dir ./docs

# Use a specific config file
npx @yourorg/docs --config ./my-docs.config.ts
```

**Important:** Register the binary in `package.json`:
```json
{
  "bin": {
    "docs": "./dist/cli.js"
  }
}
```

---

### 5.6 Static Output and GitHub Pages

For GitHub Pages:
- Default output to `./docs-dist/` (not `./dist/` to avoid conflicts).
- Provide a `deploy` command that runs `build` then pushes to the `gh-pages` branch using `gh-pages` npm package.
- Auto-detect the `base` path from the user's `package.json`'s `homepage` field or GitHub remote URL.

```bash
npx @yourorg/docs deploy --base /my-repo-name
```

---

### 5.7 Monorepo Support

- Allow `--dir` flag to point at a specific package's directory.
- Support multiple `docs.config.ts` files — one per package.
- Add a `--root` flag that sets the gitignore lookup root separately from the content dir.

---

### 5.8 CI/CD Integration

GitHub Actions workflow (auto-generated by `npx @yourorg/docs init --ci`):

```yaml
name: Deploy Docs
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npx @yourorg/docs build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs-dist
```

---

## 6. Implementation Sketch

### 6.1 Package Structure

```
your-docs-pkg/
  package.json
  dist/
    cli.js             # Compiled CLI entry (ESM)
  src/
    cli.ts             # CLI entry point
    config.ts          # Config loading (jiti-based)
    discover.ts        # File discovery with gitignore
    sidebar.ts         # Sidebar auto-generation
    deploy.ts          # GitHub Pages deployment
  astro-template/      # Embedded Astro project
    package.json       # astro, @astrojs/starlight, @astrojs/mdx, etc.
    astro.config.mjs   # Dynamic config reading DOCS_* env vars
    src/
      content/
        config.ts      # Content collection using glob loader
      styles/
        custom.css
    node_modules/      # Pre-installed (bundled with package)
      astro/
      @astrojs/
      ...
```

---

### 6.2 CLI Entry Point

```ts
// src/cli.ts
import { Command } from 'commander'
import { resolve } from 'path'
import { spawn } from 'child_process'
import { loadUserConfig } from './config.js'
import { discoverFiles } from './discover.js'
import { generateSidebar } from './sidebar.js'

const program = new Command()

program
  .name('docs')
  .description('Zero-config docs from your markdown files')
  .version('1.0.0')

program
  .command('dev', { isDefault: true })
  .option('--dir <path>', 'Content directory', '.')
  .option('--config <path>', 'Config file path')
  .option('--port <number>', 'Dev server port', '4321')
  .action(async (opts) => {
    const userDir = resolve(opts.dir)
    const userConfig = await loadUserConfig(userDir, opts.config)
    const files = await discoverFiles(userDir)
    const sidebar = userConfig.sidebar ?? generateSidebar(files, userDir)

    const templateDir = new URL('../astro-template', import.meta.url).pathname
    const astroBin = resolve(templateDir, 'node_modules/.bin/astro')

    spawn('node', [astroBin, 'dev', '--root', templateDir, '--port', opts.port], {
      stdio: 'inherit',
      env: {
        ...process.env,
        DOCS_USER_DIR: userDir,
        DOCS_SIDEBAR: JSON.stringify(sidebar),
        DOCS_TITLE: userConfig.title ?? 'Docs',
        DOCS_INTEGRATIONS: JSON.stringify(userConfig.integrations ?? []),
        DOCS_OUT_DIR: resolve(userDir, userConfig.outDir ?? 'docs-dist'),
      },
    })
  })

program
  .command('build')
  .option('--dir <path>', 'Content directory', '.')
  .option('--base <path>', 'Base path for GitHub Pages')
  .action(async (opts) => {
    const userDir = resolve(opts.dir)
    const userConfig = await loadUserConfig(userDir)
    const files = await discoverFiles(userDir)
    const sidebar = userConfig.sidebar ?? generateSidebar(files, userDir)
    const templateDir = new URL('../astro-template', import.meta.url).pathname
    const astroBin = resolve(templateDir, 'node_modules/.bin/astro')

    spawn('node', [astroBin, 'build', '--root', templateDir], {
      stdio: 'inherit',
      env: {
        ...process.env,
        DOCS_USER_DIR: userDir,
        DOCS_SIDEBAR: JSON.stringify(sidebar),
        DOCS_TITLE: userConfig.title ?? 'Docs',
        DOCS_BASE: opts.base ?? userConfig.base ?? '/',
        DOCS_OUT_DIR: resolve(userDir, userConfig.outDir ?? 'docs-dist'),
      },
    })
  })

program.parse()
```

---

### 6.3 Astro Template Config

```ts
// astro-template/astro.config.mjs
import { defineConfig } from 'astro/config'
import starlight from '@astrojs/starlight'
import mdx from '@astrojs/mdx'
import react from '@astrojs/react'
import svelte from '@astrojs/svelte'
import vue from '@astrojs/vue'

const userDir = process.env.DOCS_USER_DIR
const title = process.env.DOCS_TITLE ?? 'Docs'
const sidebar = JSON.parse(process.env.DOCS_SIDEBAR ?? '[]')
const integrations = JSON.parse(process.env.DOCS_INTEGRATIONS ?? '[]')
const outDir = process.env.DOCS_OUT_DIR ?? './docs-dist'
const base = process.env.DOCS_BASE ?? '/'

const frameworkIntegrations = [
  mdx(),
  integrations.includes('react') && react(),
  integrations.includes('svelte') && svelte(),
  integrations.includes('vue') && vue(),
].filter(Boolean)

export default defineConfig({
  outDir,
  base,
  integrations: [
    starlight({
      title,
      sidebar,
    }),
    ...frameworkIntegrations,
  ],
})
```

---

### 6.4 Content Collection Config

```ts
// astro-template/src/content/config.ts
import { defineCollection } from 'astro:content'
import { glob } from 'astro/loaders'

const userDir = import.meta.env.DOCS_USER_DIR

const docs = defineCollection({
  loader: glob({
    pattern: '**/*.{md,mdx}',
    base: userDir,
    // Gitignore patterns loaded at startup by CLI and passed here
    // OR implemented via a custom loader:
  }),
})

export const collections = { docs }
```

---

### 6.5 File Discovery with Gitignore

```ts
// src/discover.ts
import ignore from 'ignore'
import { glob } from 'fast-glob'
import fs from 'fs'
import path from 'path'

export async function discoverFiles(userDir: string): Promise<string[]> {
  const ig = ignore()
  
  // Load .gitignore from userDir and all parents up to git root
  let dir = userDir
  while (dir !== path.parse(dir).root) {
    const gitignorePath = path.join(dir, '.gitignore')
    if (fs.existsSync(gitignorePath)) {
      ig.add(fs.readFileSync(gitignorePath, 'utf8'))
    }
    const gitDir = path.join(dir, '.git')
    if (fs.existsSync(gitDir)) break  // stop at git root
    dir = path.dirname(dir)
  }
  
  const allFiles = await glob('**/*.{md,mdx}', {
    cwd: userDir,
    dot: false,
    ignore: ['node_modules/**', '**/node_modules/**'],
  })
  
  return allFiles.filter(f => !ig.ignores(f))
}
```

---

### 6.6 Sidebar Auto-Generation

```ts
// src/sidebar.ts
import path from 'path'

interface SidebarItem {
  label: string
  link?: string
  items?: SidebarItem[]
}

export function generateSidebar(files: string[], userDir: string): SidebarItem[] {
  // Group by top-level directory
  const tree: Record<string, string[]> = {}
  
  for (const file of files) {
    const parts = file.split('/')
    if (parts.length === 1) {
      tree[''] = tree[''] ?? []
      tree[''].push(file)
    } else {
      const dir = parts[0]
      tree[dir] = tree[dir] ?? []
      tree[dir].push(file)
    }
  }
  
  const sidebar: SidebarItem[] = []
  
  // Top-level files first
  if (tree['']) {
    for (const f of tree['']) {
      const slug = f.replace(/\.mdx?$/, '')
      const label = slug === 'index' ? 'Home' : toTitleCase(slug)
      sidebar.push({ label, link: `/${slug}` })
    }
  }
  
  // Directory groups
  for (const [dir, dirFiles] of Object.entries(tree)) {
    if (!dir) continue
    sidebar.push({
      label: toTitleCase(dir),
      items: dirFiles.map(f => {
        const slug = f.replace(/\.mdx?$/, '')
        const name = path.basename(slug)
        return { label: toTitleCase(name), link: `/${slug}` }
      }),
    })
  }
  
  return sidebar
}

function toTitleCase(str: string): string {
  return str.replace(/[-_]/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}
```

---

### 6.7 Config Loading

```ts
// src/config.ts
import path from 'path'
import fs from 'fs'

export interface DocsConfig {
  title?: string
  description?: string
  logo?: string
  base?: string
  outDir?: string
  integrations?: ('react' | 'svelte' | 'vue')[]
  sidebar?: unknown[]
  components?: Record<string, string>
}

export async function loadUserConfig(userDir: string, configPath?: string): Promise<DocsConfig> {
  const candidates = configPath
    ? [path.resolve(configPath)]
    : [
        path.join(userDir, 'docs.config.ts'),
        path.join(userDir, 'docs.config.js'),
        path.join(userDir, 'docs.config.mjs'),
      ]
  
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      // Use jiti for TS support without requiring user to have ts-node
      const { createJiti } = await import('jiti')
      const jiti = createJiti(import.meta.url, { interopDefault: true })
      const config = await jiti.import(candidate) as DocsConfig
      
      // Auto-detect framework integrations from user's package.json
      if (!config.integrations) {
        config.integrations = await detectFrameworks(userDir)
      }
      
      return config
    }
  }
  
  return {
    integrations: await detectFrameworks(userDir),
  }
}

async function detectFrameworks(userDir: string): Promise<('react' | 'svelte' | 'vue')[]> {
  const pkgPath = path.join(userDir, 'package.json')
  if (!fs.existsSync(pkgPath)) return []
  
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'))
  const deps = { ...pkg.dependencies, ...pkg.devDependencies }
  
  const frameworks: ('react' | 'svelte' | 'vue')[] = []
  if (deps.react) frameworks.push('react')
  if (deps.svelte) frameworks.push('svelte')
  if (deps.vue) frameworks.push('vue')
  
  return frameworks
}
```

---

## 7. Risks and Gotchas

### 7.1 Symlink Permission Issues on Windows

**Risk:** `fs.symlinkSync` requires Developer Mode or admin rights on Windows.  
**Severity:** High (blocks all Windows users if symlinks are used).  
**Mitigation:** Use the Astro 5 Content Layer glob loader with environment variables instead of symlinks. This completely avoids the issue. If symlinks are used as a fallback, detect Windows and fall back gracefully with a clear error message.

```ts
if (process.platform === 'win32') {
  // Use env var approach, never symlinks
}
```

---

### 7.2 Astro Content Collection Schema Conflicts

**Risk:** If the user's `.md`/`.mdx` files have frontmatter fields that conflict with the schema defined in `config.ts`, Astro throws a validation error.  
**Severity:** Medium.  
**Mitigation:** Define the content collection schema permissively:

```ts
const docs = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: userDir }),
  schema: z.object({
    title: z.string().optional(),
    description: z.string().optional(),
    // Allow any additional frontmatter
  }).passthrough(),
})
```

Or use `schema: z.any()` for maximum permissiveness during the initial version.

---

### 7.3 HMR / File Watching Across Symlink Boundaries

**Risk:** Vite's HMR (via chokidar) may not watch files through symlinks by default.  
**Severity:** Medium (dev experience degraded, not broken).  
**Mitigation:**
- With the Content Layer glob loader approach (no symlinks), Vite must be configured to watch the user's directory directly.
- Add the user's directory to Vite's `server.watch`:

```ts
// In astro.config.mjs
vite: {
  server: {
    watch: {
      // Watch user's directory
      paths: [process.env.DOCS_USER_DIR],
    }
  }
}
```

- For symlinks (if used): set `chokidar: { followSymlinks: true }` in Vite config.

---

### 7.4 Security: Path Traversal

**Risk:** The CLI accepts a `--dir` flag that specifies an arbitrary path. A malicious `docs.config.ts` or a crafted invocation could potentially access files outside the intended directory.  
**Severity:** Low (this is a dev tool, not a server), but worth noting.  
**Mitigation:**
- Resolve and normalize all paths with `path.resolve`.
- Validate that `--dir` is a real directory that exists.
- The glob patterns should be scoped to the resolved `userDir`.

```ts
import { realpath } from 'fs/promises'
const userDir = await realpath(resolve(opts.dir))
```

---

### 7.5 Version Pinning: Package Astro vs. User Astro

**Risk:** If the user's project also has Astro installed (e.g., it's an Astro site), there may be two Astro versions in play. If the package's `astro-template/node_modules/astro` is a different major version from the user's `node_modules/astro`, there could be runtime conflicts if any shared module resolution occurs.  
**Severity:** Low (the template runs in an isolated environment), but can cause confusion.  
**Mitigation:**
- The `astro-template/` has its own `node_modules/` and `package.json`. Node module resolution in the template context will always resolve to `astro-template/node_modules/astro`.
- Document clearly that the package ships its own Astro version.
- Add a check: if the user's project has Astro installed with an incompatible major version, print a warning (not an error) suggesting they note the discrepancy.

---

### 7.6 npx Cache and Large Package Size

**Risk:** Shipping `astro-template/node_modules/` pre-installed makes the package large (~150-300MB for Astro + Starlight). `npx` caches packages in `~/.npm`, so after first run it's fast. But the initial download is slow.  
**Severity:** Medium (UX: first-run `npx` is slow).  
**Mitigation options:**
1. **Run `npm install` inside `astro-template/` as a `postinstall` script.** This keeps the published package small but adds a one-time install step on first use. Cache this in `~/.cache/your-pkg/`.
2. **Use `pnpm`'s hoisting or a shared Astro install.** Complex.
3. **Accept the tradeoff.** Starlight's template is ~50MB installed. Document the first-run behavior.

Recommended: Use `postinstall`/lazy install with a local cache directory:

```ts
const cacheDir = path.join(os.homedir(), '.cache', 'your-docs-pkg', version)
if (!fs.existsSync(path.join(cacheDir, 'node_modules', 'astro'))) {
  console.log('Setting up docs engine (one-time)...')
  await install(cacheDir)  // copies template + runs npm install
}
```

---

### 7.7 Astro Startup Time

**Risk:** Astro (especially with multiple framework integrations) has a noticeable startup time (~3-8 seconds on first run). For a "plug-and-play" tool, this can feel slow.  
**Severity:** Medium (UX concern).  
**Mitigation:**
- Use VitePress as the default engine (faster startup: ~1-2s).
- For Astro: pre-build the Vite/Rollup cache in the package's `postinstall`. This is what most CLI tools do.
- Display a friendly startup message so users know it's working.

---

### 7.8 Framework Integration Conflicts

**Risk:** If the user's project has React 18 but the package's Astro template has `@astrojs/react` pegged to React 17 (or vice versa), there may be conflicts.  
**Severity:** Medium.  
**Mitigation:** The `astro-template/node_modules/` is fully isolated. User's React version does not affect the template. However, if the user wants to import their own React components in MDX, the components will run against the template's React version. Document this and pin framework versions permissively:

```json
{
  "peerDependencies": {
    "react": ">=17"
  }
}
```

---

### 7.9 MDX Import Resolution in User Content

**Risk:** When a user writes `import { MyComponent } from './components/MyComponent'` in an `.mdx` file, Vite will try to resolve this import relative to the MDX file's location in the user's directory. This works if the content is properly mounted. But if the Vite resolver is configured for the package's `astro-template/` root, relative imports from the user's directory may fail.  
**Severity:** High (breaks component embedding).  
**Mitigation:**
- Configure Vite's `resolve.alias` to include the user's directory.
- With Astro 5's glob loader, files are loaded from their real absolute paths, so Vite's resolver handles relative imports correctly.
- Test this early in development with a concrete example.

---

### 7.10 `.md` files with JSX in frontmatter (false positives)

**Risk:** Some `.md` files (e.g., GitHub issue templates) contain YAML frontmatter with values that look like JSX tags (e.g., `title: <Component>`). MDX processing will fail on these.  
**Severity:** Low (rare in practice).  
**Mitigation:** Process `.md` files as pure CommonMark (not MDX) and `.mdx` files as MDX. Never run MDX processing on `.md` files.

---

## Appendix: Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Core framework | Astro 5 + Starlight | Best multi-framework component support, polished theme |
| Alternative core | VitePress | If Vue-only components sufficient; faster, simpler |
| Content mounting | Astro 5 Content Layer glob loader | Symlink-free, Windows-safe, officially supported |
| Config convention | `docs.config.ts` with `defineConfig` helper | Type-safe, familiar pattern |
| TypeScript config loading | `jiti` | Zero user setup, supports TS without compilation |
| File discovery | `fast-glob` + `ignore` | Standard, well-maintained, gitignore-aware |
| npx invocation | `npx @yourorg/docs` | Standard pattern, works without global install |
| Package size | Lazy install to `~/.cache` | Balance between cold-start speed and download size |
| Windows symlinks | Avoided entirely | Use env var injection instead |
| GitHub Pages | `npx @yourorg/docs deploy` via `gh-pages` package | Simple one-command deployment |

---

*End of report.*
