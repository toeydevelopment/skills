# Phase 2 — Task Planning

Turn the Phase 1 docs into an executable task DAG. One file per feature:
`docs/tasks/<feature>.md`.

## The format

A task file has two parts: a YAML frontmatter block and a nested-checklist body.

### Frontmatter

```yaml
---
agents:
  - @architect
  - @backend
  - @test-engineer
  - @reviewer
workflow:
  t1.2: [t1.1]            # API design depends on the ADR
  t1.3: [t1.2]            # proto depends on API design
  t2.1: [t1.3]            # RED E2E depends on the proto
  t2.2: [t2.1]            # repository impl depends on the failing E2E
  t2.3: [t2.2]            # service impl depends on the repository
  t2:   [t2.3, t3.1]      # feature done needs impl AND review
---
```

- `agents:` — the roster of agent handles this feature will use. Each handle is
  `@name`. Pick from the project-type mapping below.
- `workflow:` — the dependency map. `taskId: [depId, ...]` means `taskId` cannot
  start until every listed dependency is complete. Inline `#` comments explain
  each edge. The graph **must be acyclic**.

### Body

Markdown sections grouping tasks. Every task — parent or leaf — carries an
`[id:xxx]` tag. Every **leaf** task also carries one `@agent` tag naming who
executes it. Parent tasks are containers; their `[id]` can appear in `workflow:`
to mean "all children done".

```markdown
# Tasks: <Feature Name>

## Design 📐
- [ ] Lock the design [id:t1]
  - [ ] Write the ADR [id:t1.1] @architect
  - [ ] Define the API surface [id:t1.2] @architect
  - [ ] Write the protobuf [id:t1.3] @backend

## Implementation 🔧
- [ ] Ship the feature [id:t2]
  - [ ] Write the RED E2E test [id:t2.1] @test-engineer
  - [ ] Implement the repository layer [id:t2.2] @backend
  - [ ] Implement the service layer [id:t2.3] @backend

## Quality ✅
- [ ] Review and verify [id:t3]
  - [ ] Code review [id:t3.1] @reviewer
```

Use `- [x]` for any task already done (e.g. setup that pre-exists).

## Agent-roster mapping

Choose the roster by project type detected in Phase 1:

| Project type | Roster |
|---|---|
| Protobuf / Go backend | `@architect`, `@backend`, `@test-engineer`, `@reviewer` |
| Web frontend | `@designer`, `@frontend`, `@test-engineer`, `@reviewer` |
| Full-stack | `@architect`, `@backend`, `@frontend`, `@test-engineer`, `@reviewer` |
| Mobile (Flutter) | `@architect`, `@mobile`, `@test-engineer`, `@reviewer` |
| Data / ML | `@analyst`, `@ml-engineer`, `@test-engineer`, `@reviewer` |

Keep the roster minimal — only agents that own at least one leaf task.

## Authoring rules

1. **Every leaf task is independently executable.** It maps to one atomic commit
   in Phase 3. If a leaf task is too big for one green commit, split it.
2. **Dependencies follow reality, not section order.** A parent depends on its
   children; cross-section edges (e.g. "feature done" needs both impl and
   review) are expressed explicitly in `workflow:`.
3. **The first implementation task is the RED E2E** when an E2E harness exists —
   it must depend on the API definition task.
4. **Trace each task to a Phase 1 artifact.** A task with no doc behind it is
   scope creep — drop it or write the missing doc.
5. **Topological order is the execution order.** Phase 3 walks the DAG; an
   acyclic graph with correct edges is what makes autonomous execution safe.

## Full template

```markdown
---
agents:
  - @architect
  - @backend
  - @test-engineer
  - @reviewer
workflow:
  t1.2: [t1.1]
  t1.3: [t1.2]
  t2.1: [t1.3]
  t2.2: [t2.1]
  t2.3: [t2.2]
  t3.1: [t2.3]
  t1:   [t1.1, t1.2, t1.3]
  t2:   [t2.1, t2.2, t2.3]
  t3:   [t3.1]
---

# Tasks: <Feature Name>

## Design 📐
- [ ] Lock the design [id:t1]
  - [ ] Write the ADR [id:t1.1] @architect
  - [ ] Define the API surface [id:t1.2] @architect
  - [ ] Write the protobuf / API spec [id:t1.3] @backend

## Implementation 🔧
- [ ] Ship the feature [id:t2]
  - [ ] Write the RED E2E test [id:t2.1] @test-engineer
  - [ ] Implement the repository layer [id:t2.2] @backend
  - [ ] Implement the service layer [id:t2.3] @backend

## Quality ✅
- [ ] Review and verify [id:t3]
  - [ ] Code review [id:t3.1] @reviewer
```
