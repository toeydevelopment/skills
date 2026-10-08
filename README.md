# Toeydevelopment Skills

[![skills.sh](https://skills.sh/b/toeydevelopment/skills)](https://skills.sh/toeydevelopment/skills)

Reusable agent skills for product, engineering, Flutter, LINE, and AI-team
workflows. The repository supports three standard distribution paths:

- [`skills.sh`](https://skills.sh/) for individual or bulk skill installation.
- A skills-only Codex plugin using `.codex-plugin/plugin.json`.
- A Claude Code marketplace and plugin using `.claude-plugin/`.

## Available skills

| Skill | Purpose |
|---|---|
| [company-craft](plugins/toeydevelopment-skills/skills/company-craft/) | Bootstrap and audit AI agent companies on Paperclip. |
| [evidence-first-issue-authoring](plugins/toeydevelopment-skills/skills/evidence-first-issue-authoring/) | Investigate repositories and draft or audit evidence-grounded engineering issues. |
| [issue-intake](plugins/toeydevelopment-skills/skills/issue-intake/) | Verify issues from non-technical authors against the code and return decision cards plus a visual HTML brief. |
| [task-authoring](plugins/toeydevelopment-skills/skills/task-authoring/) | Format verified work as executable tickets for worker agents. |
| [spec-first-delivery](plugins/toeydevelopment-skills/skills/spec-first-delivery/) | Deliver features through documentation, task planning, and outside-in TDD. |
| [flutter-ddd](plugins/toeydevelopment-skills/skills/flutter-ddd/) | Build Flutter features with DDD and Clean Architecture. |
| [flutter-responsive-ui](plugins/toeydevelopment-skills/skills/flutter-responsive-ui/) | Build responsive Flutter interfaces without layout overflows. |
| [line-dev-expert](plugins/toeydevelopment-skills/skills/line-dev-expert/) | Build LINE Messaging API, LIFF, Login, Pay, and Mini App integrations. |

## Install with skills.sh

List the skills without installing anything:

```bash
npx skills add toeydevelopment/skills --list
```

Install one skill globally for Codex and Claude Code:

```bash
npx skills add toeydevelopment/skills \
  --skill evidence-first-issue-authoring \
  --global \
  --agent codex \
  --agent claude-code \
  --yes
```

Install every skill globally for Codex and Claude Code:

```bash
npx skills add toeydevelopment/skills \
  --skill '*' \
  --global \
  --agent codex \
  --agent claude-code \
  --yes
```

Install every skill for every supported agent:

```bash
npx skills add toeydevelopment/skills --all
```

Use one skill without installing it:

```bash
npx skills use toeydevelopment/skills@evidence-first-issue-authoring
```

## Install as a Codex plugin

Add the GitHub repository as a Codex marketplace, then install the bundle:

```bash
codex plugin marketplace add toeydevelopment/skills --ref main
codex plugin add toeydevelopment-skills@toeydevelopment-skills
```

The plugin bundles every directory under
`plugins/toeydevelopment-skills/skills/`. Start a new Codex task after
installation so the newly installed skills are loaded.

Inspect or refresh the marketplace with:

```bash
codex plugin marketplace list
codex plugin marketplace upgrade toeydevelopment-skills
```

See the official OpenAI documentation for the
[plugin manifest and marketplace format](https://developers.openai.com/plugins/build/plugins).

## Install as a Claude Code plugin

Add the marketplace and install the bundle:

```bash
claude plugin marketplace add toeydevelopment/skills
claude plugin install toeydevelopment-skills@toeydevelopment-skills
```

Claude can also install one skill as an individual plugin:

```bash
claude plugin install evidence-first-issue-authoring@toeydevelopment-skills
```

Restart Claude Code after installing or updating a plugin.

## Example

After installing `evidence-first-issue-authoring`:

```text
Use $evidence-first-issue-authoring to investigate this reported problem and
draft the correct issue type. Do not implement it.
```

The workflow returns one of four readiness outcomes: implementation-ready,
investigation required, product decision required, or duplicate/superseded. It
keeps observed facts, code-confirmed behavior, product decisions, hypotheses,
and implementation proposals separate.

## Repository layout

```text
plugins/toeydevelopment-skills/
  skills/<skill-name>/SKILL.md       skills.sh and shared skill source
  .codex-plugin/plugin.json          Codex bundle manifest
  .claude-plugin/plugin.json         Claude bundle manifest
.agents/plugins/marketplace.json     Codex marketplace
.claude-plugin/marketplace.json      Claude marketplace
```

The two plugin manifests reference the same `skills/` directory. Skill content
is not duplicated between platforms.

## Contributing

1. Add the skill under
   `plugins/toeydevelopment-skills/skills/<skill-name>/SKILL.md`.
2. Put optional supporting material in `references/`, `scripts/`, or `assets/`
   inside that skill directory.
3. Add the skill to the table above and the Claude marketplace when it should be
   individually installable there.
4. Run the distribution checks:

```bash
python3 scripts/validate_distribution.py
npx skills add . --list
claude plugin validate . --strict
```

## License

[MIT](LICENSE)
