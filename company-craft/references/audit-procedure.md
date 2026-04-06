# Audit Procedure — Ongoing Team Optimization

Run this audit periodically (weekly recommended) or when triggered by "audit team", "optimize agents", or "review team composition".

## Prerequisites

- Company exists with agents and a project workspace
- `docs/COMPANY-CRAFT-AUDIT.md` exists (written during bootstrap)
- Paperclip API accessible

## Step 1: Agent Roster Review

```bash
# Fetch all agents
GET /api/companies/{companyId}/agents
```

For each agent, check:

| Check | How | Action if failing |
|---|---|---|
| Agent has instructions | Read instruction files from agent's path | Generate instructions using agent-templates |
| Instructions are current | Compare tech references in instructions vs. actual workspace | Update stale references |
| Agent has assigned skills | `GET /api/agents/{agentId}` → check skills | Assign relevant skills |
| Agent's specialization matches workspace | Does a workspace surface still map to this agent? | Archive if no matching surface |

## Step 2: Workload Analysis

```bash
# For each agent, count active tickets
GET /api/companies/{companyId}/issues?assigneeAgentId={agentId}&status=todo,in_progress,blocked
```

| Condition | Flag | Action |
|---|---|---|
| Agent has > 5 `todo` + `in_progress` tickets | Overloaded | Redistribute or hire additional agent |
| Agent has 0 tickets for 3+ days | Idle | Check if role is still needed; reassign or archive |
| Agent has `blocked` tickets with no recent activity | Stuck | Escalate: comment on blocked ticket, assign to blocker owner |
| Agent has `in_progress` tickets older than 3 heartbeats | Stale | Comment asking for status update |

## Step 3: Instruction Quality Check

For each agent, read their instruction files and verify:

1. **AGENTS.md** references the correct tech stack, frameworks, and file paths
2. **SOUL.md** has role-appropriate personality (not a generic copy-paste)
3. **TOOLS.md** lists commands that actually exist in the workspace (check `package.json` scripts, `Makefile` targets, etc.)
4. **Paperclip workflow** section exists with checkout/comment/status conventions
5. **Safety rules** are present and role-appropriate

Score each agent's instructions 1-5:
- 1: Missing or placeholder instructions
- 2: Generic instructions, not tailored to workspace
- 3: Tailored but missing sections (no SOUL or TOOLS)
- 4: Complete but some references are stale
- 5: Complete, current, and role-specific

**Target:** All agents ≥ 4. Rewrite any ≤ 2.

## Step 4: Ticket Quality Spot-Check

Sample the 5 most recent tickets created by each lead agent (CEO, CTO, PM).

Score each ticket using the rubric from [task-authoring-guide.md](task-authoring-guide.md):
- 0-5 scale based on DoR/DoD/AC/self-test/context completeness

Calculate per-lead average. Report:
- Overall average score
- Lowest-scoring lead (needs coaching)
- Common missing elements (e.g., "80% of tickets lack self-test instructions")

**Target:** Average ≥ 4. Any lead averaging < 3 needs the `task-authoring` skill installed.

## Step 5: Gap Analysis

Compare current agent roster against the workspace:

1. **New tech surfaces** — Has a new app, service, or framework been added since last audit? Does an existing agent cover it?
2. **Recurring blockers** — Are tickets frequently blocked on the same agent or skill gap? Suggests a missing role.
3. **Model tier alignment** — Are expensive-model agents doing worker-level tasks? Are cheap-model agents struggling with complex decisions?
4. **Skill coverage** — Are installed skills still relevant? Are new skills available that would help?

## Step 6: Recommendations

Generate a structured report:

```markdown
## Company Craft Audit — {date}

### Roster Summary
| Agent | Role | Tickets (todo/ip/blocked) | Instruction Score | Notes |
|---|---|---|---|---|

### Ticket Quality
| Lead Agent | Avg Score | Common Gaps |
|---|---|---|

### Findings
1. [Finding with supporting data]
2. [Finding with supporting data]

### Recommendations
- [ ] [Action: hire/archive/rebalance/update instructions/install skill]
- [ ] [Action]

### Changes Since Last Audit
- [What changed in workspace]
- [What changed in team]
```

Write this to `docs/COMPANY-CRAFT-AUDIT.md` (overwrite previous).

Create tickets for each recommendation:
- Hire recommendations → use `paperclip-create-agent` skill or `hiring-review` module
- Instruction updates → assign to the agent itself or to the agent's manager
- Skill installations → use company skills API
- Workload rebalancing → reassign tickets via `PATCH /api/issues/{id}`
