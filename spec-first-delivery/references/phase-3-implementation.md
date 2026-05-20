# Phase 3 — Implementation

Implement the task DAG with outside-in TDD, in an isolated git worktree, one
atomic green commit per leaf task.

## 1. Worktree setup

Never implement on the main working tree. Open one worktree per feature:

```bash
git worktree add ../<repo>-<feature> -b feat/<feature>
cd ../<repo>-<feature>
```

All Phase 3 work — including the Phase 1 docs if they have not been committed
yet — happens on this branch. When the feature is done and reviewed, the worktree
branch is rebased onto the trunk and merged; then `git worktree remove` it.

## 2. Detect the E2E harness

Look for, in order:

- a Playwright / Cypress config (`playwright.config.*`, `cypress.config.*`),
- Go end-to-end tests (`*_e2e_test.go`, an `e2e/` or `integration/` dir),
- a gRPC / buf integration test harness,
- a `docker-compose` test stack or test database setup.

**Harness found** → outside-in TDD (section 3). **No harness** → unit-only TDD
(section 4); record "E2E skipped — no harness" in `TEST-STRATEGY.md`.

## 3. Outside-in TDD (E2E harness present)

### 3.1 Write the RED E2E first

Before any production code, write the end-to-end test for the feature:

1. **Call the real API** — issue the actual request the PRD describes.
2. **Assert the response** — status code and body, against the API definition.
3. **Reconcile the database** — query the datastore directly and assert the
   persisted state (rows created, audit row written, `lock_version` bumped).

Run it. It **must fail** — RED. A passing test here means it tests nothing.

```
# Conceptual shape — adapt to the repo's test framework.
test "AddTag persists the tag and an audit row":
    resp = POST /v1/customers/{id}/tags  {tag: "vip"}
    assert resp.status == 200
    row = db.query("SELECT * FROM customer_tag WHERE customer_id=? AND tag=?", id, "vip")
    assert row exists
    audit = db.query("SELECT * FROM audit_log WHERE entity_id=? ORDER BY created_at DESC LIMIT 1", id)
    assert audit.action == "crm.tag.write"
```

### 3.2 Walk the task DAG

Process leaf tasks in topological order of the `workflow:` map. For each leaf
task, run one red-green-refactor cycle — a vertical tracer-bullet slice, not a
horizontal "all tests then all code" pass:

```
RED:      write one unit test for this task's behavior  → it fails
GREEN:    write the minimal code to pass it             → it passes
REFACTOR: remove duplication, deepen modules            → tests still pass
```

Rules:
- One behavior at a time. Do not anticipate later tasks.
- Test observable behavior through public interfaces — not private methods.
- Mock only at system boundaries (external APIs, time, randomness). Do not mock
  the code under test.
- Follow `CONVENTIONS.md` — reuse the cited patterns; do not reinvent.

### 3.3 E2E goes GREEN

When the last leaf task is done, the RED E2E from 3.1 passes. If it does not,
the feature is incomplete or the task DAG missed something — fix before
committing the final task.

## 4. Unit-only TDD (no E2E harness)

Same red-green-refactor loop per leaf task (3.2), without the outer E2E. The
PRD's acceptance criteria become the unit/integration test cases. Note the
absence of E2E coverage in `TEST-STRATEGY.md` so it is a known gap, not a
silent one.

## 5. Atomic green commits

One commit per leaf task. Each commit bundles **that task's tests and its
implementation together** so the tree compiles and all tests pass at every
commit — the history is bisectable.

- Conventional message, keyed to the task id:
  `feat(<scope>): <task-id> — <description>`
  e.g. `feat(crm): t2.2 — add customer_tag repository`.
- Test-only or doc tasks use the matching type: `test(...)`, `docs(...)`.
- The Phase 1 docs commit together (or per doc group):
  `docs(<scope>): ADR + PRD + diagrams + proto for <feature>`.
- **Linear history.** Integrate with `git rebase`, never a merge commit. Each
  commit is one logical change — no "fix typo" follow-ups; amend instead.

Commit sequence for a typical feature:

```
docs(crm): ADR + PRD + diagrams + proto for customer tags
test(crm): t2.1 — RED E2E for AddTag
feat(crm): t2.2 — add customer_tag repository
feat(crm): t2.3 — add CRMService.AddTag handler
```

## 6. Done

The feature is done when: every leaf task is committed, the E2E is GREEN (or
explicitly marked skipped), the worktree branch rebases cleanly onto the trunk,
and the task file's checkboxes are all `[x]`. Update `docs/wiki/log.md` with an
implementation entry, then the worktree can be merged and removed.
