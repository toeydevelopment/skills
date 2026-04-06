---
name: task-authoring
description: >
  Standards for creating high-quality tickets that worker agents (cheaper models)
  can execute efficiently. Covers Definition of Ready, Definition of Done,
  acceptance criteria, self-test instructions, and context optimization. Install
  on lead agents (CEO, CTO, PM, architect) who create or delegate work. Trigger
  when creating tickets, delegating tasks, writing subtasks, or when a worker
  flags a ticket as underspecified.
---

# Task Authoring — Ticket Quality Standards for Lead Agents

You create tickets that **cheaper-model worker agents** execute. Every token you save them is money saved. Every ambiguity you leave costs a retry. Write tickets that a worker can start coding from immediately.

## The Ticket Template

Every ticket you create MUST include these sections:

```markdown
## [Verb-first title]: [Scope]

### Definition of Ready
- [ ] [Precondition 1 — e.g., schema finalized, API endpoint exists]
- [ ] [Precondition 2 — e.g., design spec linked, dependency ticket done]

### Acceptance Criteria
- Given [context], when [action], then [expected result]
- Given [context], when [edge case], then [expected handling]

### Context
[Inline the critical context: interface signatures, type definitions, API contract.
Keep under 30 lines. For supporting context, use precise file references:]
- `path/to/file.ext:L42-L67` — [why: "follow this repository pattern"]
- `path/to/schema.ext:L10-L25` — [why: "these are the columns you'll query"]

### Self-Test
```bash
# Exact commands the worker runs to verify their work
command-to-run-tests
command-to-typecheck
command-to-verify-endpoint
```

### Definition of Done
- [ ] Code compiles / lint passes
- [ ] Tests written and passing (cover acceptance criteria)
- [ ] Self-test commands all pass
- [ ] Clean commit with `feat/fix/test(scope): CAR-XXX — description`
- [ ] Ticket commented with what was done + files changed
```

## The 3-Zone Context Model

**Zone 1 — Inline (in ticket body):** Acceptance criteria, interface/type signatures (<30 lines), key decisions with rationale, self-test commands. The worker reads this first and may not need anything else.

**Zone 2 — Precise References:** `path/to/file.ext:L42-L67` with a reason. Never bare file paths. Never "see file X" without line numbers. Always explain WHY the worker needs to read it.

**Zone 3 — Ambient (never needed):** If the worker must grep/find/explore to understand scope, the ticket is underspecified. Rewrite it.

## Anti-Patterns

**Bad:** "Implement the user dashboard feature. See the design doc."
**Good:** "Add `GET /dashboard/stats` endpoint returning `{ totalBookings, revenue7d, activeCustomers }`. Follow repository pattern in `src/domain/billing/repository.ts:L15-L40`. AC: Given an org with 5 bookings, when GET /dashboard/stats, then totalBookings=5."

**Bad:** "Fix the auth bug" (no reproduction, no expected behavior)
**Good:** "Fix: `POST /auth/login` returns 500 when `staffCode` contains uppercase. AC: Given staffCode='HP-001', when login with valid PIN, then 200 + JWT. Self-test: `curl -X POST localhost:8787/auth/login -d '{"staffCode":"HP-001","pin":"1234"}'`"

**Bad:** A ticket with 10 file references and no inline context
**Good:** A ticket with the key interface inlined (15 lines) and 2 precise file references for pattern examples

## Quick Check (before assigning)

Before moving a ticket to `todo` and assigning a worker:

1. Can a worker start coding from the ticket body alone? (no exploration needed)
2. Are acceptance criteria testable with specific inputs/outputs?
3. Are self-test commands copy-pasteable and deterministic?
4. Is inline context < 30 lines and file references < 5?
5. Is the DoD checklist concrete (not "works correctly")?

If any answer is "no," rewrite the ticket before assigning.
