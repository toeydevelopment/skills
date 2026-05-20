# The LLM Wiki Pattern

`docs/wiki/` is not a folder of flat topic pages. It is a **compounding,
LLM-maintained knowledge base** built on the Memex / "LLM Wiki" idea: every
design doc produced in Phase 1 is read, summarized, and integrated into an
interlinked set of markdown pages. The knowledge is compiled once and kept
current — later phases query the wiki instead of re-deriving understanding from
raw docs every time.

The skill writes and maintains the entire wiki. It stays **self-contained**:
plain markdown plus git, no dependency on external skills or MCP tooling, so the
wiki travels with any repo.

## Three layers

| Layer | What | Who owns it |
|---|---|---|
| **Raw sources** | The ADR, PRD, diagrams, API/proto from Phase 1, plus any external references. Immutable — read, never edited. | The author / Phase 1 |
| **The wiki** | `docs/wiki/` markdown: synthesis, entity pages, concept pages, all interlinked. | The LLM, entirely |
| **The schema** | `docs/wiki/README.md` — how the wiki is structured and the ingest / query / lint workflows. Co-evolves with the project. | The LLM, with the user |

## Layout

```
docs/wiki/
├── README.md          # the schema — conventions + workflows
├── index.md           # content catalog (see below)
├── log.md             # chronological record (see below)
├── overview.md        # the evolving synthesis / thesis for the feature
├── entities/
│   └── <name>.md      # one page per entity (service, aggregate, actor, table)
└── concepts/
    └── <name>.md      # one page per concept (a flow, a rule, a decision theme)
```

Pages interlink with `[[wikilinks]]` — `[[customer-tag]]` points to
`entities/customer-tag.md` or `concepts/customer-tag.md`. Link liberally; a link
to a page that does not exist yet marks a page worth creating.

### Page schema

Every entity/concept page starts with frontmatter, then prose:

```markdown
---
title: <Page Title>
summary: <one-line summary, reused verbatim in index.md>
related: [[other-page]], [[another-page]]
---

# <Page Title>

<Synthesis prose. What this is, how it behaves, how it connects to the rest of
the system. Cite raw sources: "per [[ADR-0007]]" / "see docs/prd/tags.md".>
```

## index.md — the content catalog

Content-oriented. Lists every page with a link and its one-line summary, grouped
by category. The skill reads `index.md` first when answering a query, then drills
into the relevant pages. Update it on every ingest.

```markdown
# Wiki Index

## Overview
- [[overview]] — the current synthesis of the <feature> design.

## Entities
- [[crm-service]] — the service that owns customer tags and segments.
- [[customer-tag]] — a normalized tag attached to a customer.

## Concepts
- [[idempotent-writes]] — how mutating RPCs deduplicate retries.

## Sources
- docs/adr/0007-*.md — <one line>.
- docs/prd/customer-tags.md — <one line>.
```

## log.md — the chronicle

Chronological, append-only. Every entry starts with a consistent prefix so the
log is greppable (`grep "^## \[" log.md | tail -5`):

```markdown
# Wiki Log

## [2026-05-20] ingest | ADR-0007 Use MongoDB for the write model
Created [[mongodb-write-model]]; updated [[crm-service]], [[overview]].

## [2026-05-20] ingest | PRD customer-tags
Created [[customer-tag]], [[customer-segment]]; updated [[index]].

## [2026-05-20] lint | post-Phase-1 health check
No contradictions. Flagged orphan [[legacy-tag]] — linked from [[overview]].

## [2026-05-20] implement | feature customer-tags shipped
E2E green; updated [[crm-service]] with the final endpoint list.
```

`<op>` is one of `ingest`, `query`, `lint`, `implement`.

## Operations

### Ingest

Run once per Phase 1 document. For each source:

1. Read the source fully.
2. Write or update its summary into the relevant `overview` / entity / concept
   pages — one source typically touches several pages.
3. Create new entity/concept pages for concepts the source introduces.
4. Maintain cross-references — add `[[wikilinks]]` both ways.
5. Note contradictions: if the source conflicts with an existing page, flag it
   on the page rather than silently overwriting.
6. Update `index.md`.
7. Append an `ingest` entry to `log.md`.

### Query

Phase 2 and Phase 3 query the wiki to stay grounded. Read `index.md`, open the
relevant pages, synthesize. When a query produces a genuinely useful synthesis
(a comparison, a discovered connection), **file it back as a new wiki page** so
exploration compounds instead of vanishing — and log it.

### Lint

Run after Phase 1 ingest, and any time the wiki feels stale. Check for:

- contradictions between pages,
- stale claims a newer source has superseded,
- orphan pages with no inbound `[[wikilinks]]`,
- concepts mentioned across pages but lacking their own page,
- missing cross-references.

Record the lint pass and its findings in `log.md`.

## docs/wiki/README.md — the schema

When first creating the wiki, write `README.md` describing the conventions above
for this specific repo: the layout, the page schema, the `[[wikilink]]`
convention, and the ingest/query/lint workflows. It is the configuration file
that makes a future session a disciplined wiki maintainer rather than a generic
chatbot. Co-evolve it with the user as the wiki grows.

## Scaling note

`index.md` is enough at moderate scale (dozens to low hundreds of pages). If a
wiki grows past that, add a local markdown search tool (e.g. a `qmd`-style
BM25/vector search) so the skill can search instead of scanning the index — but
that is an optional scale-up, never a dependency.
