# Canvas-Height Strategy

**Purpose:** Define ONE consistent way to record a MicroSim's height and
propagate it to every iframe that shows the sim — across every library type
(p5.js, vis-network, Chart.js, Mermaid, Leaflet, vis-timeline, Plotly, custom
HTML) and every project layout.

This is the **build-time** strategy used by `scripts/sync-iframe-heights.py`.
It is complementary to the **runtime** postMessage resizer documented in
[`iframe-auto-height.md`](iframe-auto-height.md) — you can use either or both.

## The one number: CANVAS_HEIGHT

Every sim has a single content height, `CANVAS_HEIGHT` — the fully-rendered
height of the sim (drawing area + controls + any legend/graph panel), in
pixels. From it, one rule sets every iframe:

```
iframe height = CANVAS_HEIGHT + 2     # +2px for the iframe border
```

That `+ 2` is applied identically to the sim's own `docs/sims/<id>/index.md`
and to every chapter/guide page that embeds the sim, so a sim is never a
different height in two places.

## Where CANVAS_HEIGHT is stored (resolution order)

A sim may be authored in different libraries, and not every library produces a
`.js` file. So downstream tooling resolves `CANVAS_HEIGHT` from the **first**
source that has it, in this priority order:

| # | Source | Who uses it | Notes |
|---|--------|-------------|-------|
| 1 | `// CANVAS_HEIGHT: <n>` comment in the first ~15 lines of `<id>.js` | Any sim that ships a `.js` (p5.js, and JS-driven vis/chart/etc.) | **Primary.** Lives next to the code that determines the height. |
| 2 | `"canvasHeight": <n>` in `<id>/metadata.json` | Sims with **no `.js`** (pure Mermaid / vis-network / Chart.js / Leaflet / vis-timeline / Plotly / custom HTML) | **The consistent structured place.** Every sim already has a `metadata.json`. This is the answer to "where does a no-JS sim store its height." |
| 3 | `<!-- CANVAS_HEIGHT: <n> -->` comment in `main.html` | Legacy / back-compat | Some projects put the comment in the HTML host. Still read so existing sims keep working; prefer #1 or #2 going forward. |
| 4 | computed `drawHeight + controlHeight (+ graphHeight)` from `<id>.js` | Last resort | p5 sims that forgot the comment. When used, the `// CANVAS_HEIGHT` comment is **written back** to line 2 of the `.js` so it is cached. |

If none of these yields a height, the sim is reported as unresolved and its
iframes are left untouched (this is also how non-sim directories like
`shared-libs` and the learning-graph `graph-viewer` are safely skipped).

## Communicating height to downstream agents

The height must survive the hand-off between the agent that *generates* a sim
and the later agents/scripts that *embed* and *validate* it. That means the
generating agent MUST leave the height in one of the two authoritative places:

- **Sim has a `.js`** → put `// CANVAS_HEIGHT: <n>` near the top of the `.js`
  (see the per-library calculation table in the microsim-generator skill,
  Step 4.4).
- **Sim has no `.js`** (rendered entirely by `main.html`) → put
  `"canvasHeight": <n>` in `metadata.json`.

Do **not** rely on a hand-typed height in the iframe tag as the source of
truth — that value is *derived* and will be overwritten by
`sync-iframe-heights.py`.

To backfill the structured field for a project whose no-JS sims currently keep
their height only in `main.html`, run the sync script once with
`--write-metadata` (see below). It is additive and idempotent.

## Propagating with sync-iframe-heights.py

```bash
# Report what would change (nothing is written)
python3 scripts/sync-iframe-heights.py --project-dir /path/to/project --dry-run --verbose

# Apply: rewrite every sim iframe to CANVAS_HEIGHT + 2
python3 scripts/sync-iframe-heights.py --project-dir /path/to/project

# Also copy each resolved height into metadata.json canvasHeight (migration)
python3 scripts/sync-iframe-heights.py --project-dir /path/to/project --write-metadata
```

The script walks **every** markdown file under `docs/` and matches iframes by
the `sims/<id>/main.html` path, so it finds sim embeds no matter where the
embedding page lives. Poster embeds (`posters/<id>/main.html`) and the
learning-graph viewer are matched by a *different* path and are never touched.

## Project layouts (where embeds live)

The embed scan is deliberately **layout-agnostic** — it does not assume a fixed
chapter directory. Two layouts exist in the wild:

- **Standard** — `docs/chapters/<chapter>/index.md`. Used by essentially every
  intelligent-textbook project (100+ books).
- **Nested band layout** — `docs/bands/<band>/chapters/<chapter>/index.md`.
  **Unique to the `health-education` textbook**, which groups chapters under
  grade bands (`kindergarten`, `grade-1` … `grade-9-12`). No other book nests
  chapters this way. Do not hard-code `docs/bands/**` into shared tooling or
  assume it elsewhere — the recursive `docs/**/*.md` walk is what makes the one
  script serve both layouts (plus teacher guides and any future embedder).

## Related

- [`iframe-auto-height.md`](iframe-auto-height.md) — runtime postMessage
  alternative for sims whose height is only knowable in the browser.
- [`iframe-tester.md`](iframe-tester.md) — Playwright check that controls
  actually fit at the propagated height.
- microsim-generator skill, **Step 4.4** — the per-library CANVAS_HEIGHT
  calculation table (what number to store in the first place).
