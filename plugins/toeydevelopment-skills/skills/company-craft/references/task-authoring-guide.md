# Task Authoring Guide — Ticket Quality Standards

This guide defines how lead agents (CEO, CTO, PM, architects) should create tickets for worker agents. Worker agents often run on cheaper, faster models — the ticket must contain everything they need.

## The Ticket Anatomy

Every ticket created by a lead MUST contain these sections:

### 1. Title

Verb-first, scoped to a single deliverable.

Good: `Implement GET /dashboard/stats endpoint`
Good: `Add unit tests for billing calculation rules`
Bad: `Dashboard feature`
Bad: `Fix stuff`

### 2. Definition of Ready (DoR)

Preconditions that must be true before a worker starts. Check these yourself before setting the ticket to `todo`.

```markdown
### Definition of Ready
- [ ] Data model/schema finalized (link to schema review if applicable)
- [ ] API contract defined (request/response shapes in this ticket)
- [ ] Design spec available (link to design brief if UI work)
- [ ] Blocking dependencies resolved (link to parent/related tickets)
- [ ] Test infrastructure exists (test runner, helpers, fixtures available)
```

If any box is unchecked, the ticket stays in `backlog` — not `todo`.

### 3. Acceptance Criteria

Specific, testable conditions in Given/When/Then format.

```markdown
### Acceptance Criteria
- Given an organization with 5 bookings this week, when `GET /dashboard/stats` is called with valid JWT, then response includes `{ totalBookings: 5 }` with status 200
- Given no bookings exist, when `GET /dashboard/stats` is called, then response includes `{ totalBookings: 0 }` with status 200
- Given an invalid JWT, when `GET /dashboard/stats` is called, then response is 401
```

Rules:
- Each criterion is independently testable
- Include happy path, edge case, and error case
- Use concrete values, not "appropriate response"

### 4. Self-Test Instructions

Exact commands the worker runs to verify their own work. Must be copy-pasteable.

```markdown
### Self-Test
```bash
# 1. Run the test suite
bun test -- --filter=dashboard

# 2. Verify types compile
bun run typecheck

# 3. Manual verification (with dev server running)
curl -s http://localhost:8787/dashboard/stats \
  -H "Authorization: Bearer $TOKEN" | jq .
```
```

Rules:
- Commands must be deterministic (same input → same output)
- Include the setup if needed (e.g., "start dev server first")
- Test ALL acceptance criteria, not just the happy path

### 5. Context Package

Critical context inline + file references. See [context-optimization.md](context-optimization.md) for the 3-zone model.

```markdown
### Context

**Interface to implement:**
```typescript
// Inline: the exact interface the worker must implement
interface IDashboardRepository {
  getStats(orgId: string): Promise<DashboardStats>;
}
```

**References:**
- `src/domain/billing/repository.ts:L15-L40` — follow this repository pattern
- `tests/helpers.ts:L5-L20` — use `createTestContext()` for integration tests
```

### 6. Definition of Done (DoD)

Completion checklist. Must be concrete and verifiable.

```markdown
### Definition of Done
- [ ] Code compiles — typecheck/lint passes
- [ ] Tests written — cover all acceptance criteria
- [ ] Self-test passes — all commands from Self-Test section succeed
- [ ] No regressions — full test suite still passes
- [ ] Committed — clean commit with descriptive message
- [ ] Ticket commented — what was done, files changed, any follow-ups
```

## The Complete Template

```markdown
## [Verb-first title]: [Scope]

### Definition of Ready
- [ ] [Precondition — schema, design, dependencies, etc.]

### Acceptance Criteria
- Given [context], when [action], then [expected result]
- Given [edge case], when [action], then [expected handling]
- Given [error case], when [action], then [expected error]

### Context
[Inline critical context: interfaces, types, contracts — max 30 lines]

**References:**
- `path/to/file:L##-L##` — [reason]

### Self-Test
```bash
[exact verification commands]
```

### Definition of Done
- [ ] Compiles/lints
- [ ] Tests written + passing
- [ ] Self-test passes
- [ ] No regressions
- [ ] Committed
- [ ] Ticket commented
```

## Quality Scoring Rubric (for audits)

Score each ticket 0-5 when spot-checking lead output:

| Score | Criteria |
|---|---|
| 0 | Title only, no details |
| 1 | Has description but no AC or DoD |
| 2 | Has AC but vague (no Given/When/Then, no concrete values) |
| 3 | Has AC + DoD but no self-test or context references |
| 4 | Has AC + DoD + self-test but context is vague or missing line numbers |
| 5 | Complete: AC + DoD + DoR + self-test + precise context. Worker can start immediately. |

**Target:** Average score ≥ 4 across sampled tickets. Any ticket scoring < 3 should be rewritten before assigning.

## Anti-Patterns → Corrections

### 1. The Vague Epic
**Bad:** "Implement user authentication. See the auth PRD for details."
**Good:** Split into 3 tickets:
- "Add `POST /auth/login` route — returns JWT on valid credentials" (with AC, self-test, inline request/response shape)
- "Add auth middleware — verify JWT on protected routes" (with AC, inline middleware interface)
- "Add `POST /auth/refresh` route — rotate access token" (with AC, self-test)

### 2. The Exploration Ticket
**Bad:** "Fix the billing bug that customers reported" (no reproduction, no expected behavior)
**Good:** "Fix: `POST /bills` returns 500 when `items` array is empty. AC: Given empty items array, when POST /bills, then 400 with `{ error: 'items required' }`. Self-test: `curl -X POST localhost:8787/bills -d '{"items":[]}'`"

### 3. The Kitchen Sink
**Bad:** One ticket that changes 4 services, 2 UIs, and a database migration
**Good:** One parent ticket with 4 focused subtasks, each with its own AC and self-test
