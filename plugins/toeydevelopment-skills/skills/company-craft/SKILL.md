---
name: company-craft
description: >
  Set up and optimize AI agent companies on Paperclip. Bootstrap mode: analyze
  workspace, detect tech stack, generate agent instructions (AGENTS/SOUL/TOOLS),
  build org chart, and seed initial tickets. Audit mode: review agent roster,
  rebalance workloads, check ticket quality, and suggest hires or cuts. Trigger
  on "set up company", "bootstrap agents", "audit team", "optimize agents",
  "review team composition", "improve agent instructions", "company setup", or
  "craft company".
---

# Company Craft — Paperclip Company Setup & Optimization

This skill helps you build and maintain a well-structured AI agent company from any codebase. It works for any tech stack — monorepos, single apps, backends, frontends, mobile, ML, and everything in between.

## Mode Detection

Check if `docs/COMPANY-CRAFT-AUDIT.md` exists in the workspace root.

- **Does not exist** → Run **Bootstrap** (first-time setup)
- **Exists** → Run **Audit** (ongoing optimization)

## Bootstrap Mode

Build a company from scratch by reading the workspace. Follow [references/bootstrap-procedure.md](references/bootstrap-procedure.md) step by step:

1. **Discover workspace** — Scan for project markers (`package.json`, `Cargo.toml`, `go.mod`, `pubspec.yaml`, etc.), detect monorepo structure, identify frameworks, read existing docs
2. **Analyze agent needs** — Map tech surfaces to agent specializations using patterns from [references/org-patterns.md](references/org-patterns.md). One distinct tech surface → one specialist agent.
3. **Build org chart** — Assign roles, chain of command, and model tiers (opus for leads, sonnet for workers)
4. **Generate instructions** — Create AGENTS.md + SOUL.md + TOOLS.md for each agent using templates from [references/agent-templates.md](references/agent-templates.md). Populate with actual workspace commands, file paths, and architecture
5. **Seed work** — Create initial tickets with DoR/DoD/AC/self-test. Install `task-authoring` skill on lead agents. Write the sentinel file.

## Audit Mode

Optimize an existing company. Follow [references/audit-procedure.md](references/audit-procedure.md):

1. **Roster review** — Compare agents vs. workspace. Flag agents with no matching tech surface.
2. **Workload analysis** — Count tickets per agent. Flag overloaded (>5 active), idle (0 for 3+ days), or stuck (blocked with no new activity).
3. **Instruction quality** — Score each agent's instructions 1-5. Rewrite any ≤ 2.
4. **Ticket quality** — Sample 5 recent tickets per lead agent. Score against the rubric in [references/task-authoring-guide.md](references/task-authoring-guide.md). Target: average ≥ 4.
5. **Gap analysis** — New tech not covered? Recurring blockers suggesting missing role? Model tier misalignment?
6. **Recommendations** — Update `docs/COMPANY-CRAFT-AUDIT.md`. Create tickets for improvements.

## Task Quality Standards

Lead agents (CEO, CTO, PM) create tickets for worker agents (engineers, QA, DevOps). Workers often run on cheaper models with smaller context windows. Every ticket MUST include:

- **Definition of Ready (DoR)** — preconditions before worker starts
- **Definition of Done (DoD)** — concrete completion checklist
- **Acceptance Criteria** — Given/When/Then, testable with specific values
- **Self-Test Instructions** — exact commands the worker runs to verify
- **Context Package** — critical context inline, supporting context as precise file references

Full standards: [references/task-authoring-guide.md](references/task-authoring-guide.md)

**Companion skill:** Install the standalone `task-authoring` skill on all lead agents so these standards are enforced on every ticket creation.

## Context Optimization

Worker agents should be able to start coding from the ticket alone — no codebase exploration required. Use the 3-zone model:

1. **Zone 1 (inline):** Acceptance criteria, type signatures (<30 lines), key decisions, self-test commands
2. **Zone 2 (precise refs):** `path/to/file:L42-L67` — "why the worker needs this"
3. **Zone 3 (ambient):** If the worker needs to grep/find, the ticket is underspecified

Full guide: [references/context-optimization.md](references/context-optimization.md)

## Critical Rules

- **Always use Paperclip API** for agent creation, skill assignment, and ticket management — never create agents by file manipulation alone
- **Never hardcode tech stacks** — detect from workspace markers, don't assume
- **Match model tier to role** — opus for decision-makers (CEO, CTO, PM), sonnet for implementers (engineers, QA), haiku for routine tasks
- **Agent instructions must reference actual files** — populate from the real workspace, not generic examples
- **Include `X-Paperclip-Run-Id`** header on all mutating Paperclip API requests
- **One agent per distinct tech surface** — a Flutter app and a React app should not share one engineer
- **CTO/architect agents do NOT write code** — they review, approve, and delegate
- **Every ticket has self-test** — if you can't write verification commands, the acceptance criteria are too vague
