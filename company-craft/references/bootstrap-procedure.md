# Bootstrap Procedure — Setting Up a New Company

Run this when `docs/COMPANY-CRAFT-AUDIT.md` does NOT exist. This is the first-time setup for a Paperclip company from its workspace.

## Step 1: Workspace Discovery

Scan the workspace root for project markers. Build a **surface map** — a list of every distinct app, service, or package with its tech stack.

### Detection Table

| Marker File | Indicates |
|---|---|
| `package.json` | Node.js/JavaScript/TypeScript project |
| `Cargo.toml` | Rust project |
| `pyproject.toml` / `setup.py` / `requirements.txt` | Python project |
| `go.mod` | Go project |
| `pubspec.yaml` | Flutter/Dart project |
| `Gemfile` | Ruby project |
| `pom.xml` / `build.gradle` | Java/Kotlin project |
| `*.sln` / `*.csproj` | .NET project |
| `Dockerfile` / `docker-compose.yml` | Containerized service |
| `Makefile` | Build automation (check targets for language clues) |

### Monorepo Detection

| Marker | Type |
|---|---|
| `turbo.json` | Turborepo (JS/TS) |
| `nx.json` | Nx workspace |
| `lerna.json` | Lerna (legacy) |
| `pnpm-workspace.yaml` | pnpm workspaces |
| `melos.yaml` | Melos (Flutter/Dart) |
| `Cargo.toml` with `[workspace]` | Rust workspace |
| `go.work` | Go workspace |

For monorepos, enumerate each `apps/*/`, `packages/*/`, `services/*/` as a separate surface.

### Framework Detection

Read the detected project files to identify frameworks:

| In `package.json` dependencies | Framework |
|---|---|
| `react` | React |
| `next` | Next.js |
| `nuxt` | Nuxt |
| `vue` | Vue |
| `angular` | Angular |
| `svelte` / `@sveltejs/kit` | Svelte/SvelteKit |
| `express` / `fastify` / `hono` / `elysia` | Node API framework |
| `@cloudflare/workers-types` | Cloudflare Workers |

| In `pubspec.yaml` dependencies | Framework |
|---|---|
| `flutter` | Flutter |
| `dart_frog` | Dart Frog (backend) |

| In `Cargo.toml` dependencies | Framework |
|---|---|
| `actix-web` / `axum` / `rocket` | Rust web framework |
| `tauri` | Tauri desktop app |

| In `pyproject.toml` / `requirements.txt` | Framework |
|---|---|
| `django` | Django |
| `fastapi` | FastAPI |
| `flask` | Flask |
| `pytorch` / `tensorflow` | ML framework |

Read CI configs (`.github/workflows/*.yml`, `.gitlab-ci.yml`) for deployment targets (e.g., Vercel, AWS, Cloudflare, GCP, Heroku).

### Documentation Discovery

Check for existing product/architecture docs:
- `README.md` — project overview
- `ARCHITECTURE.md` or `docs/architecture.md` — system design
- `brain/` — product knowledge base (PRDs, design docs)
- `docs/` — general documentation
- `CLAUDE.md` / `AGENTS.md` — existing AI agent instructions
- `CONTRIBUTING.md` — development workflow

### Build the Surface Map

Output a table:

```
| Surface | Path | Language | Framework | Deploy Target | Complexity |
|---|---|---|---|---|---|
| API | apps/api/ | TypeScript | Hono | Cloudflare Workers | High |
| Web App | apps/web/ | TypeScript | Next.js | Vercel | Medium |
| Mobile | apps/mobile/ | Dart | Flutter | iOS/Android | High |
```

Complexity heuristic:
- **High**: >50 source files, custom architecture (DDD, Clean Arch), multiple integrations
- **Medium**: 20-50 source files, standard framework patterns
- **Low**: <20 source files, simple CRUD

## Step 2: Agent Needs Analysis

Apply the pattern selection guide from [org-patterns.md](org-patterns.md):

1. Count distinct tech surfaces from the surface map
2. Check if product docs exist (`brain/`, PRDs)
3. Check if test infrastructure exists (test scripts, CI test steps)
4. Check if CI/CD or infra-as-code exists
5. Check if design system or UI references exist

Decision tree:

```
Surfaces = 1, same language?
  → Solo pattern (CEO + 1 Engineer)

Surfaces = 2-3, same language family?
  → Small Team pattern (CEO + Engineers + optional QA)

Surfaces ≥ 3, mixed languages?
  → Full Stack pattern (CEO + CTO + specialist Engineers + QA + DevOps)

Product docs + multiple user-facing surfaces?
  → Product-Led pattern (add PM, Designer)

ML models + data pipelines?
  → Data/ML pattern

Multi-tenant + admin panel?
  → Platform pattern
```

For each recommended agent, determine:
- **Display name**: e.g., "Backend Engineer", "Flutter Engineer"
- **Paperclip role**: `ceo`, `cto`, `engineer`, `pm`, `qa`, `designer`, `devops`, `general`
- **Specialization**: What tech surfaces they own
- **Model tier**: opus (leads) or sonnet (workers)
- **Reports to**: Chain of command

## Step 3: Org Chart Construction

Build the hierarchy:

1. CEO is always root
2. CTO (if present) is direct report to CEO, manages engineers
3. PM (if present) is direct report to CEO
4. Engineers report to CTO (if present) or CEO
5. QA reports to CTO or CEO
6. DevOps reports to CTO or CEO
7. Designer reports to PM or CEO

Use the Paperclip API to create agents:
```bash
# Via paperclip-create-agent skill (recommended)
# Or via direct API if authorized
POST /api/companies/{companyId}/agents
```

Set chain of command via agent update or during creation.

## Step 4: Instruction Generation

For each agent, generate three files using templates from [agent-templates.md](agent-templates.md):

1. **AGENTS.md** — Role, domain (populated from surface map), commands (from detected scripts), architecture (from docs), Paperclip workflow, safety rules
2. **SOUL.md** — Personality archetype for the role (leadership, engineering, quality, operations, creative)
3. **TOOLS.md** — CLI commands detected from workspace, Paperclip API patterns with the agent's own ID

Place files in the agent's instruction directory and set the path:
```bash
PATCH /api/agents/{agentId}/instructions-path
{ "path": "path/to/AGENTS.md" }
```

### Instruction Quality Checklist

Before finalizing each agent's instructions:
- [ ] AGENTS.md references actual files/paths from this workspace
- [ ] TOOLS.md commands are runnable (verified against package.json/Makefile)
- [ ] Paperclip workflow includes the agent's own ID in checkout examples
- [ ] Safety rules are role-appropriate
- [ ] No placeholder text like `{TODO}` or `{FILL_IN}` remains

## Step 5: Seed Work

### Create Project Goal

```bash
POST /api/companies/{companyId}/goals
{ "title": "...", "description": "..." }
```

### Install Companion Skills

Install `task-authoring` skill on lead agents (CEO, CTO, PM):
```bash
POST /api/companies/{companyId}/skills/import
# Then assign to leads via
POST /api/agents/{agentId}/skills/sync
```

### Create Initial Tickets

Create a "codebase onboarding" ticket for each engineer:
- Title: "Onboard to {surface}: read architecture, run tests, document gaps"
- Follow DoR/DoD patterns from [task-authoring-guide.md](task-authoring-guide.md)
- Assign to the appropriate specialist

### Write Sentinel File

Write `docs/COMPANY-CRAFT-AUDIT.md` with:
- Bootstrap timestamp
- Agent roster (name, role, specialization, model tier)
- Surface map summary
- Org pattern selected
- Skills installed

This file's existence gates future runs into audit mode.
