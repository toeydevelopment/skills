# Toeydevelopment Skills

Custom skills for [Claude Code](https://claude.ai/code) — extend Claude with domain-specific expertise and best practices for Flutter, LINE Platform, and more.

## Available Skills

| Skill | Description | Key Focus |
|---|---|---|
| **[flutter-ddd](flutter-ddd/)** | Flutter/Dart with Domain-Driven Design (DDD) Clean Architecture | BLoC, dartz, freezed, retrofit, injectable, auto_route — 4-layer architecture |
| **[flutter-responsive-ui](flutter-responsive-ui/)** | Expert-level Flutter responsive UI with zero overflow errors | Constraint-aware layouts, responsive breakpoints, safe Flex/Scroll nesting, adaptive navigation |
| **[line-dev-expert](line-dev-expert/)** | LINE Platform development expertise | Messaging API, LIFF/Mini App, LINE Login, LINE Pay, Rich Menus, Flex Messages |

## Quick Start

### Install via Skills CLI (Recommended)

```bash
npx skills add toeydevelopment/skills@flutter-ddd -g -y
npx skills add toeydevelopment/skills@flutter-responsive-ui -g -y
npx skills add toeydevelopment/skills@line-dev-expert -g -y
```

### Install via Plugin Marketplace

Inside Claude Code:

```
/plugin marketplace add toeydevelopment/skills
/plugin install flutter-ddd@toeydevelopment/skills
```

### Manual Installation (Project-Scoped)

Copy a skill into your project's `.claude/skills/` directory:

```bash
# Example: Install flutter-responsive-ui
mkdir -p .claude/skills/flutter-responsive-ui/references
curl -sL https://raw.githubusercontent.com/toeydevelopment/skills/main/flutter-responsive-ui/SKILL.md \
  -o .claude/skills/flutter-responsive-ui/SKILL.md
for ref in overflow-prevention scroll-patterns responsive-recipes; do
  curl -sL "https://raw.githubusercontent.com/toeydevelopment/skills/main/flutter-responsive-ui/references/${ref}.md" \
    -o ".claude/skills/flutter-responsive-ui/references/${ref}.md"
done
```

### Manual Installation (Global)

Install to `~/.claude/skills/` to make skills available across all projects:

```bash
mkdir -p ~/.claude/skills/flutter-responsive-ui/references
# Same curl commands as above, targeting ~/.claude/skills/
```

## Skill Details

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
4. Update this README

## License

MIT
