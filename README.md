# Toeydevelopment Skills

Custom skills for [Claude Code](https://claude.ai/code) — extend Claude with domain-specific expertise and best practices.

## Available Skills

| Skill | Description |
|---|---|
| **[flutter-ddd](flutter-ddd/)** | Flutter/Dart with Domain-Driven Design (DDD) Clean Architecture — BLoC, dartz, freezed, retrofit, injectable, auto_route |
| **[line-dev-expert](line-dev-expert/)** | LINE Platform development — Messaging API, LIFF/Mini App, LINE Login, LINE Pay, Rich Menus, Flex Messages, CRM, loyalty programs, Thailand market integrations |

## Installation

### Method 1: Plugin Marketplace (Recommended)

Inside Claude Code, register this repo as a marketplace and install skills:

```
/plugin marketplace add toeydevelopment/skills
```

Then install any skill:

```
/plugin install flutter-ddd@toeydevelopment/skills
/plugin install line-dev-expert@toeydevelopment/skills
```

You can also browse available skills interactively:

```
/plugin
```

Navigate to the **Discover** tab to see all available skills from registered marketplaces.

### Method 2: Manual Installation (Project-Scoped)

Copy a skill directly into your project's `.claude/skills/` directory:

```bash
# Install flutter-ddd
mkdir -p .claude/skills/flutter-ddd
curl -sL https://raw.githubusercontent.com/toeydevelopment/skills/main/flutter-ddd/SKILL.md \
  -o .claude/skills/flutter-ddd/SKILL.md

# Install line-dev-expert
mkdir -p .claude/skills/line-dev-expert/references
curl -sL https://raw.githubusercontent.com/toeydevelopment/skills/main/line-dev-expert/SKILL.md \
  -o .claude/skills/line-dev-expert/SKILL.md
for ref in messaging-api rich-menu-flex liff-mini-app login-security payments-integrations architecture-patterns; do
  curl -sL "https://raw.githubusercontent.com/toeydevelopment/skills/main/line-dev-expert/references/${ref}.md" \
    -o ".claude/skills/line-dev-expert/references/${ref}.md"
done
```

### Method 3: Manual Installation (Global)

Install to `~/.claude/skills/` to make skills available across all your projects:

```bash
mkdir -p ~/.claude/skills/line-dev-expert/references
# Same curl commands as above, but targeting ~/.claude/skills/
```

## How Skills Work

Skills are `SKILL.md` files with YAML frontmatter that tell Claude **when** and **how** to apply domain-specific knowledge. Claude automatically activates the right skill based on your conversation context.

Each skill contains:

- **`SKILL.md`** — Main instructions with trigger conditions, architecture overview, and critical rules
- **`references/`** — Detailed reference documents with code patterns and examples

## Contributing

To add a new skill:

1. Create a directory: `your-skill-name/`
2. Add `SKILL.md` with YAML frontmatter (`name`, `description`)
3. Add detailed references in `references/` subdirectory
4. Register in `.claude-plugin/marketplace.json`

## License

MIT
