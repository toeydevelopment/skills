# Toeydevelopment Skills

Custom skills for [Claude Code](https://claude.ai/code) and [Paperclip](https://paperclip.ing) — extend AI agents with domain-specific expertise, team orchestration, and development best practices.

## Available Skills

| Skill | Description | Key Focus |
|---|---|---|
| **[company-craft](company-craft/)** | Set up and optimize AI agent companies on Paperclip | Workspace analysis, agent instruction generation, org charts, task quality standards, ongoing audits |
| **[task-authoring](task-authoring/)** | Ticket quality standards for lead agents | DoR, DoD, acceptance criteria, self-test, context optimization for cheap-model workers |
| **[flutter-ddd](flutter-ddd/)** | Flutter/Dart with Domain-Driven Design (DDD) Clean Architecture | BLoC, dartz, freezed, retrofit, injectable, auto_route — 4-layer architecture |
| **[flutter-responsive-ui](flutter-responsive-ui/)** | Expert-level Flutter responsive UI with zero overflow errors | Constraint-aware layouts, responsive breakpoints, safe Flex/Scroll nesting, adaptive navigation |
| **[line-dev-expert](line-dev-expert/)** | LINE Platform development expertise | Messaging API, LIFF/Mini App, LINE Login, LINE Pay, Rich Menus, Flex Messages |

## Quick Start

### Install via Skills CLI (Recommended)

```bash
npx skills add toeydevelopment/skills@company-craft -g -y
npx skills add toeydevelopment/skills@task-authoring -g -y
npx skills add toeydevelopment/skills@flutter-ddd -g -y
npx skills add toeydevelopment/skills@flutter-responsive-ui -g -y
npx skills add toeydevelopment/skills@line-dev-expert -g -y
```

### Install via Plugin Marketplace

Inside Claude Code:

```
/plugin marketplace add toeydevelopment/skills
/plugin install company-craft@toeydevelopment/skills
```

### Manual Installation (Project-Scoped)

Copy a skill into your project's `.claude/skills/` directory:

```bash
mkdir -p .claude/skills/company-craft/references
curl -sL https://raw.githubusercontent.com/toeydevelopment/skills/main/company-craft/SKILL.md \
  -o .claude/skills/company-craft/SKILL.md
for ref in bootstrap-procedure agent-templates task-authoring-guide context-optimization audit-procedure org-patterns; do
  curl -sL "https://raw.githubusercontent.com/toeydevelopment/skills/main/company-craft/references/${ref}.md" \
    -o ".claude/skills/company-craft/references/${ref}.md"
done
```

### Manual Installation (Global)

Install to `~/.claude/skills/` to make skills available across all projects:

```bash
mkdir -p ~/.claude/skills/company-craft/references
# Same curl commands as above, targeting ~/.claude/skills/
```

## Skill Details

### company-craft

**Set up and optimize AI agent companies on Paperclip from any codebase.** Works with any tech stack — monorepos, single apps, backends, frontends, mobile, ML, and everything in between.

Two modes:

- **Bootstrap** (first run) — Scans workspace, detects tech stack, maps surfaces to specialist agents, generates instruction files (AGENTS.md + SOUL.md + TOOLS.md), builds org chart, seeds initial tickets
- **Audit** (ongoing) — Reviews agent roster vs. workspace, analyzes workloads, checks instruction freshness, spot-checks ticket quality, identifies gaps, recommends hires/cuts

Key concepts:
- **One agent per distinct tech surface** — a React app and a Flutter app get separate engineers
- **Model tier alignment** — opus for decision-makers (CEO, CTO, PM), sonnet for implementers
- **6 org patterns** — Solo, Small Team, Full Stack, Product-Led, Data/ML, Platform

References: `bootstrap-procedure.md`, `agent-templates.md`, `org-patterns.md`, `audit-procedure.md`

### task-authoring

**Companion skill for lead agents** (CEO, CTO, PM, architects) who create tickets for worker agents on cheaper models. Ensures every ticket is self-contained and executable.

Every ticket must include:
- **Definition of Ready (DoR)** — preconditions before worker starts
- **Definition of Done (DoD)** — concrete completion checklist
- **Acceptance Criteria** — Given/When/Then with specific values
- **Self-Test Instructions** — exact commands the worker runs to verify
- **Context Package** — 3-zone model: inline critical context, precise file references, no exploration needed

Install on all lead agents so these standards are enforced on every ticket creation.

### flutter-ddd

Generates production-ready Flutter code following strict 4-layer DDD architecture:

- **Domain** — Entities, failures, facade interfaces (zero dependencies)
- **Infrastructure** — DTOs, retrofit APIs, repositories, facade implementations
- **Application** — BLoC/Cubit with freezed events/states
- **Presentation** — Pages with AutoRouteWrapper, BlocBuilder/BlocListener

### flutter-responsive-ui

Prevents all common Flutter layout failures with constraint-aware patterns:

- **8 Critical Safety Rules** — Covers Expanded in scrollables, TextField in Row, unbounded height, and more
- **Overflow Prevention Catalog** — Every common overflow error with root cause and fix
- **Responsive Breakpoints** — Material 3 window classes (Compact/Medium/Expanded/Large)
- **9 Ready-to-Use Recipes** — Adaptive navigation, master-detail, responsive grid, forms, dialogs
- **Safe Scroll Patterns** — Nested scrollables, slivers, TabBarView with lists

### line-dev-expert

Comprehensive LINE Platform development covering:

- Messaging API, webhook handling, message types
- LIFF/Mini App development and LINE Login
- LINE Pay integration and Rich Menu management
- Thailand market-specific patterns and CRM/loyalty programs

## How Skills Work

Skills are `SKILL.md` files with YAML frontmatter that tell Claude **when** and **how** to apply domain-specific knowledge. Claude automatically activates the right skill based on your conversation context.

Each skill contains:

- **`SKILL.md`** — Main instructions with trigger conditions and critical rules
- **`references/`** — Detailed reference documents loaded on-demand to save context

## Contributing

1. Create a directory: `your-skill-name/`
2. Add `SKILL.md` with YAML frontmatter (`name`, `description`)
3. Add detailed references in `references/` subdirectory
4. Update `marketplace.json` and this README

## License

MIT
