# HTML Brief

The brief is a single local HTML file, visual first, with the minimum text a
reader needs. Its diagram style follows
[diagram-design](https://github.com/cathrynlavery/diagram-design) by Cathryn
Lavery, released under the MIT license. This skill does not bundle that
project's files. Where it is installed, load its `diagram-design` skill and
follow its type references and taste gate. The conventions below are the part
this brief depends on, so the skill still works when diagram-design is absent.

Attribution: the page footer carries "Diagram style after diagram-design (MIT),
github.com/cathrynlavery/diagram-design". Keep it.

## What the page contains

1. **Header**: eyebrow (`Issue intake`), title, one snapshot line (repo, branch,
   SHA, date, "knowledge only").
2. **At-a-glance strip**: one chip per issue with its recommendation, so a reader
   can stop here.
3. **Overview map** (one diagram): issues as nodes grouped by shared area, arrows
   for needs/blocks/coordinate, the parent epic as a dashed node, and a plain
   "no parent found" note when that is the result. Up to 9 nodes. For more
   issues, group into clusters and draw each cluster as one node, then add one
   detail diagram per cluster.
4. **One card per issue**, phone-first order: title and recommendation badge,
   claim counts, problem, done-when, questions. Everything else (parent,
   affected, evidence, size/risk) sits inside `<details><summary>Evidence and
   details</summary>` so the card stays short. Long paths use `<code>` with
   `overflow-wrap:anywhere` so they wrap instead of widening the page. (evidence line: one plain sentence plus at most two
   short file names; full `path:line` lists belong in the report, not the page): the decision card fields (see
   [card-and-report-format.md](card-and-report-format.md)) as a compact panel.
   Recommendation badge top right. Claims shown as four small counts.
5. **Now versus wanted diagram** inside the card (stacks vertically on a phone), only for a complex issue (state
   change, multi-step flow, two systems). Two rows, "Now" and "Wanted", same
   shapes where nothing changes, accent on what changes. Skip it for a simple
   issue.
6. **Decide and discuss block**: numbered list at the bottom, styled so each item
   is easy to quote back.
7. **Footer**: not-checked list, attribution.

## Diagram conventions (from diagram-design)

- Single self-contained file: embedded CSS, HTML diagrams, no images, no script
  needed to read it. Fonts load from Google Fonts with system fallbacks, so it
  still reads offline.
- Tokens as CSS variables: `paper #f5f5f5`, `ink #2d3142`, `muted #4f5d75`,
  `soft #7a8399`, `rule`, `accent #eb6c36`, `link #2e5aa8`; provide a dark variant
  through `prefers-color-scheme`. If the user has a `.diagram-design` profile or
  customised style guide, use those values instead.
- Type: Instrument Serif for the title, Geist for names, Geist Mono for paths,
  numbers, and arrow labels. Mono is for technical content only.
- **Accent is editorial**: at most two accent elements per diagram. Use it for
  the thing that needs a decision or is broken, never for general emphasis.
- No shadows, no glow, small corner radius (6px), hairline borders.
- Max 9 nodes and 12 arrows per diagram. Past that, split into overview plus
  detail. Delete a node or label if the reader would still understand without it.
- Connectors are orthogonal (right-angle elbows) or straight when both ends share
  an axis. Never diagonal. Draw arrows before boxes. Arrow labels are uppercase,
  at most 14 characters, on an opaque mask with a gap from the stroke.
- Give each connector on a box edge its own attach point; do not stack strokes.
- Diagrams are HTML boxes (flex rows of `.node` and `.edge`), not scaled SVG. A
  scaled SVG shrinks its text below readable on a phone; never use one for the
  overview map or a now-versus-wanted flow. One rule for every diagram: a row on
  desktop, a vertical stack under 700px with the arrow turning to point down.
  Give each diagram a `<figure role="group">` and a `.sr` `<figcaption>` that says
  what it shows. Use `minmax(0, 1fr)` grid tracks and `min-width: 0` for
  flex/grid children so long paths wrap instead of overflowing.
- Size floor as rendered: body text 15px, every diagram and card label 13px.
  Nothing smaller, on any screen.
- Status uses shape and a word as well as color (a badge reading "wrong", not
  only a red box).

## Semantic marks

| Mark | Look |
|---|---|
| Confirmed | solid ink border, check word |
| Wrong / broken | accent border and tint |
| Stale | dashed border, "stale" |
| Unverified | dotted border, "unverified" |
| Parent epic | dashed node, outside the groups |
| Needs / blocks | solid arrow, label `NEEDS` / `BLOCKS` |
| Coordinate | dashed arrow, label `COORDINATE` |

## Presenting it

1. Write the file, for example `<out>/issue-intake-<scope>.html`.
2. If `lavish-axi` exists, run `lavish-axi <file>` so the user can annotate and
   queue replies. When the user is present to reply, read replies with
   `lavish-axi poll <file>`; skip the poll when running unattended. Answer through
   `lavish-axi reply`. Apply the user's edits to the brief and the report.
3. If it does not, give the absolute file path and say it opens offline.
4. Do not use Claude artifacts, gists, pastes, `lavish-axi share`, or any hosted
   page unless the user asks for that exact action, because the brief may name
   internal systems and customers' business.

## Checks before hand-off

Render the file twice with a headless browser (Playwright, chrome-devtools-axi,
or Chromium `--screenshot`) and look at both screenshots:

- **390px wide** (phone, device scale 2, mobile emulation) and **1280px wide**
  (desktop).
- Text readable without zoom: body at least 15px, diagram labels at least 13px
  as rendered. Check `getComputedStyle` of text nodes if unsure.
- No horizontal page scroll: `document.documentElement.scrollWidth` equals
  `innerWidth` at both widths.
- No clipped or overlapping text. Diagrams stacked on the phone, not shrunk. Decide
  block items at least 44px tall.
- Every issue number in the page matches the report.
- Every `path:line` in a card appears in the report as well.
- A headless window may have a minimum width; if the screenshot is wider than
  390px, render the file inside a 390px-wide iframe instead.
- If `diagram-design` is installed, run its self-check script on the file.
- Save both screenshots next to the brief.
