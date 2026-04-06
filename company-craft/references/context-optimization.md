# Context Optimization — Token-Efficient Tickets for Worker Agents

Worker agents run on cheaper, faster models with smaller effective context windows. Every wasted token is wasted money and degraded quality. Structure tickets so workers can start coding immediately without codebase exploration.

## The 3-Zone Model

### Zone 1 — Inline (always in ticket body)

These go directly in the ticket description. The worker reads only this and may not need anything else.

- **Acceptance criteria** with specific inputs/outputs
- **Interface or type signatures** relevant to the task (max 30 lines)
- **Key decisions** with one-line rationale (e.g., "Use repository pattern — CTO decision, see schema review")
- **Self-test commands** — exact, copy-pasteable
- **Error handling expectations** — what to do on failure cases

Example of good inline context:
```
### Interface to implement

```typescript
interface IBookingRepository {
  findByOrg(orgId: string, filters: { status?: string; date?: string }): Promise<Booking[]>;
  create(data: CreateBookingInput): Promise<Booking>;
}
```

Follow the same pattern as `src/domain/billing/repository.ts:L15-L40`.
```

### Zone 2 — Precise References

File paths with line numbers and reasons. The worker loads these only if needed.

**Format:** `path/to/file.ext:L{start}-L{end}` — "{why the worker needs this}"

Good:
- `src/domain/billing/repository.ts:L15-L40` — "follow this repository interface pattern"
- `tests/helpers.ts:L5-L20` — "use `createTestContext()` for your integration tests"
- `src/presentation/middleware/auth.ts:L30-L45` — "this is how auth plugin injects `jwtPayload`"

Bad:
- `src/domain/billing/repository.ts` (no line numbers)
- "See the auth module" (no file path)
- `src/` (a whole directory)

### Zone 3 — Ambient (never in ticket)

If the worker needs to do any of these, the ticket is underspecified:

- `grep` or `find` to locate relevant files
- Read more than 5 files to understand the task
- Guess at the expected API contract or data shape
- Ask "what does done look like?"
- Read a 500-line architecture doc to find one relevant paragraph

## Rules

### 1. Worker starts from ticket, not from codebase

The ticket body is the worker's entire world for the first 30 seconds. If they can't form a plan from the ticket alone, rewrite it.

### 2. Total inline context < 2000 tokens

About 1500 words or 30-40 lines of code. If you're exceeding this, move supporting context to Zone 2 references.

### 3. File references include WHY, not just WHERE

"Read `auth.ts:L30`" tells the worker what file to open. "Read `auth.ts:L30-L45` — this is how `jwtPayload` is injected into route handlers, you'll need to access `jwtPayload.orgId`" tells them what to learn and why.

### 4. Decision anchoring

If CTO made an architecture decision upstream, state the decision in the ticket:

Bad: "See architecture review in CAR-265 for schema decisions"
Good: "Use `soft_delete` with `deleted_at` column (CTO decision). Index on `(org_id, deleted_at)` for filtered queries."

### 5. Front-load for cheap models

Cheap models (sonnet, haiku) have less capacity for inference from sparse context. Be more explicit than you think necessary:
- State the obvious patterns
- Include the exact file to create and its expected location
- Show the expected test structure, not just "write tests"

### 6. One task, one concern

If a ticket requires changes across 3+ bounded contexts or 3+ apps, split it. Each ticket should have a single clear deliverable that one self-test can verify.

## Anti-Pattern Checklist

Before assigning a ticket, check for these red flags:

| Red Flag | Fix |
|---|---|
| No acceptance criteria | Add Given/When/Then |
| "See docs" without path + lines | Add precise references |
| Task requires >5 file reads | Inline the critical context |
| No self-test commands | Add exact verification commands |
| Multiple unrelated changes | Split into focused tickets |
| Vague DoD ("works correctly") | Add specific, testable conditions |
| Decision not anchored | State the decision + rationale inline |
