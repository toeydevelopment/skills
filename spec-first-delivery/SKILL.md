---
name: spec-first-delivery
description: >
  Documentation-first delivery pipeline. Produces design docs, then a
  dependency-ordered task list, then implements with outside-in TDD —
  autonomously, in that order, never code before docs. Phase 1 writes the ADR,
  PRD, diagrams (mermaid sequence/context, dbml ER), API definition (protobuf
  when the project uses proto, otherwise a human-readable markdown API spec),
  anti-slop docs (CONTEXT.md glossary, CONVENTIONS.md guardrails,
  TEST-STRATEGY.md), and a compounding LLM wiki. Phase 2 writes an
  agents/workflow task DAG. Phase 3 opens a git worktree and runs RED E2E then
  unit TDD then atomic green commits. Trigger when the user wants to implement a
  feature, build a service or endpoint, or says "spec first", "documentation
  first", "docs before code", "ADR before coding", "PRD then implement", or
  asks for a disciplined no-AI-slop delivery flow.
---

# Spec-First Delivery — Docs-First, Task-DAG, Outside-In TDD

A delivery pipeline that refuses to write code before the design exists. It
turns a feature request into design documents, a dependency-ordered task list,
and a TDD implementation — in that order, autonomously, without stopping for
human gates.

Use this skill the moment a feature request arrives. AI agents drift to code
immediately; that produces slop — inconsistent naming, scope creep, reinvented
patterns, missing design rationale. This pipeline front-loads the thinking into
artifacts, then lets implementation be mechanical.

## The Pipeline

Three phases run back-to-back. Ordering is mandatory; gates are not.

```
Phase 1: Documentation   →  Phase 2: Task Planning  →  Phase 3: Implementation
  ADR, PRD, diagrams,        agents/workflow DAG        worktree, RED E2E,
  API/proto, anti-slop       with [id:xxx] tasks        unit TDD, atomic
  docs, LLM wiki                                        green commits
```

**Autonomous, but never out of order.** Do not write a line of production code
until Phase 1 artifacts exist on disk. Do not start Phase 3 until the task DAG
exists. There is no human approval gate between phases — run straight through —
but each phase reads the previous phase's artifacts as its source of truth.

Before starting, scan the target repo: detect the language/stack, whether it
uses protobuf, whether an E2E harness exists, and the existing doc layout. Every
phase adapts to what it finds.

## Phase 1 — Documentation

Produce the design artifacts. Nothing here is optional; thin docs cause slop
downstream.

- **ADR** — Nygard 5-section, numbered `docs/adr/NNNN-kebab-title.md`.
- **PRD** — `docs/prd/<feature>.md`: problem, goals, user stories with
  acceptance criteria, functional requirements, non-goals, open questions.
- **Diagrams** — `docs/diagrams/`: context + sequence in mermaid, ER in dbml.
- **API definition** — protobuf project → write the `.proto` directly using the
  canonical conventions; otherwise a human-readable markdown API spec.
- **Anti-slop docs** — `CONTEXT.md` (domain glossary), `CONVENTIONS.md`
  (guardrails: patterns to reuse, non-goals, anti-patterns), `TEST-STRATEGY.md`.
- **LLM wiki** — `docs/wiki/`: ingest every doc above into a compounding,
  interlinked knowledge base.

Full procedure, doc tree, and every template: **[references/phase-1-documentation.md](references/phase-1-documentation.md)**.
API definition specifics: **[references/protobuf-conventions.md](references/protobuf-conventions.md)**.
Wiki construction: **[references/wiki-pattern.md](references/wiki-pattern.md)**.

## Phase 2 — Task Planning

Turn the docs into an executable task DAG at `docs/tasks/<feature>.md`: YAML
frontmatter declaring the `agents:` roster and a `workflow:` dependency map, then
a nested checklist where every task carries an `[id:xxx]` tag and every leaf task
an `@agent` tag. The implementation phase walks this DAG in topological order.

Format spec, agent-roster mapping, and the full template: **[references/phase-2-task-planning.md](references/phase-2-task-planning.md)**.

## Phase 3 — Implementation

Open one `git worktree` for the feature. If the project has an E2E harness,
write the RED E2E first — a real API call asserting the response, then a direct
database query to reconcile state — and confirm it fails. Walk the task DAG:
per leaf task, unit test (RED) → minimal implementation (GREEN) → refactor. The
E2E flips to GREEN when the feature is complete. Commit one atomic, build-green
commit per leaf task; keep history linear via rebase.

Worktree setup, the outside-in TDD loop, and commit discipline: **[references/phase-3-implementation.md](references/phase-3-implementation.md)**.

## Critical Rules

1. **No code before docs.** Phase 1 artifacts must exist on disk before any
   production code is written. This is the whole point of the skill.
2. **One worktree per feature.** Never implement on the main working tree.
3. **Every commit builds green.** A commit bundles a task's tests and
   implementation together; the tree compiles and tests pass at every commit.
4. **Reuse before you write.** Before implementing anything, check
   `CONVENTIONS.md` and the existing repo for a pattern to follow. Cite it.
5. **Protobuf projects get `.proto`.** If the repo declares APIs in protobuf,
   write protobuf — not OpenAPI, not a description. Otherwise write the markdown
   API spec.
6. **The wiki compounds.** Every doc produced is ingested into `docs/wiki/`;
   later phases read the wiki to stay grounded.
7. **Outside-in TDD.** When an E2E harness exists, the failing E2E comes first
   and frames the unit-level work.

## References

- **[references/phase-1-documentation.md](references/phase-1-documentation.md)** — Doc tree, ADR/PRD/diagram/anti-slop templates, the Phase 1 procedure.
- **[references/phase-2-task-planning.md](references/phase-2-task-planning.md)** — The agents/workflow task-DAG format and template.
- **[references/phase-3-implementation.md](references/phase-3-implementation.md)** — Git worktree setup, outside-in TDD loop, atomic commit discipline.
- **[references/protobuf-conventions.md](references/protobuf-conventions.md)** — Canonical protobuf conventions; markdown API spec fallback.
- **[references/wiki-pattern.md](references/wiki-pattern.md)** — The compounding LLM wiki: layers, index/log, ingest/query/lint.
