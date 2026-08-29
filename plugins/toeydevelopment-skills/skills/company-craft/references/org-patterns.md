# Org Patterns — Agent Team Templates by Project Type

Use these patterns as starting points when bootstrapping a company. Adapt based on what workspace discovery reveals.

## Pattern Selection Guide

| Signal in Workspace | Pattern |
|---|---|
| 1 app, 1 language, no CI | Solo |
| 2-3 apps, same language family | Small Team |
| 3+ apps, mixed languages/frameworks | Full Stack |
| Customer-facing + admin + API with product docs | Product-Led |
| ML models, data pipelines, notebooks | Data/ML |
| Multi-tenant SaaS with admin panel | Platform |

## Patterns

### 1. Solo

**When:** Single app, single language, early prototype.

```
CEO (opus)
└── Engineer (sonnet)
```

- 2 agents total
- Engineer handles everything: code, tests, deployment
- CEO handles planning, priorities, delegation
- No QA/DevOps overhead — engineer self-tests

### 2. Small Team

**When:** 2-3 apps or services, same language ecosystem. Tests exist.

```
CEO (opus)
├── Engineer A (sonnet) — primary app
├── Engineer B (sonnet) — secondary app/API
└── QA Engineer (sonnet) — testing
```

- 3-4 agents
- Add QA only if test infrastructure detected (test runner, CI test step)
- Engineers are generalists within the same ecosystem
- CEO doubles as product owner

### 3. Full Stack

**When:** 3+ apps, mixed tech stacks (e.g., backend + web + mobile). CI/CD exists.

```
CEO (opus)
├── CTO (opus) — architecture gate, NO coding
├── Backend Engineer (sonnet) — API, database
├── Frontend Engineer (sonnet) — web UI(s)
├── Mobile Engineer (sonnet) — native/cross-platform app
├── QA Engineer (sonnet) — testing all stacks
└── DevOps Engineer (sonnet) — CI/CD, deployment
```

- 6-7 agents
- CTO reviews architecture, approves schemas, does NOT write code
- Each engineer specializes by runtime/framework
- DevOps only if CI configs or infra-as-code detected

### 4. Product-Led

**When:** Customer-facing app + admin panel + API, with product docs (`brain/`, PRDs, design specs).

```
CEO (opus)
├── Product Manager (opus) — PRDs, roadmap, tickets
├── CTO (opus) — architecture gate
├── Product Designer (sonnet) — design briefs, UX specs
├── Backend Engineer (sonnet)
├── Frontend Engineer (sonnet)
├── QA Engineer (sonnet)
└── DevOps Engineer (sonnet)
```

- 7-8 agents
- PM justified when product docs exist and features are user-facing
- Designer justified when design system or UI reference files detected
- Expensive models (opus) only for CEO, PM, CTO — decision-makers

### 5. Data/ML

**When:** ML models, data pipelines, Jupyter notebooks, training scripts.

```
CEO (opus)
├── Data Engineer (sonnet) — pipelines, ETL, data quality
├── ML Engineer (sonnet) — models, training, evaluation
├── DevOps Engineer (sonnet) — infra, GPU management, model serving
└── QA Engineer (sonnet) — data validation, model testing
```

- 4-5 agents
- Data vs. ML split when both pipeline code and model code exist
- Merge into single "ML Engineer" if codebase is small
- DevOps critical for model deployment infrastructure

### 6. Platform

**When:** Multi-tenant SaaS with admin/management panel, subscription/billing, multiple user types.

```
CEO (opus)
├── Product Manager (opus) — PRDs, roadmap
├── CTO (opus) — architecture, schema gate
├── Backend Engineer (sonnet) — API, multi-tenant logic
├── Frontend Engineer A (sonnet) — main product UI
├── Frontend Engineer B (sonnet) — admin panel
├── QA Engineer (sonnet)
└── DevOps Engineer (sonnet)
```

- 7-8 agents
- Split frontend engineers when product UI and admin UI are distinct apps
- CTO critical for multi-tenant data isolation review
- Merge frontend engineers if both use same framework and are small

## Model Tier Recommendations

| Tier | Roles | Reasoning |
|---|---|---|
| **Expensive (opus)** | CEO, CTO, Product Manager | Make decisions, write specs, review architecture. Quality of thought matters. |
| **Standard (sonnet)** | Engineers, QA, DevOps, Designer | Execute defined work, write code/tests. Speed and cost matter. |
| **Cheap (haiku)** | Routine tasks, simple triage | Repetitive operations, status updates, formatting. |

## Recommended Paperclip Modules per Pattern

| Pattern | Modules to Install |
|---|---|
| Solo | `ci-cd`, `documentation` |
| Small Team | `ci-cd`, `documentation`, `pr-review` |
| Full Stack | `ci-cd`, `documentation`, `pr-review`, `architecture-plan`, `triage` |
| Product-Led | `ci-cd`, `documentation`, `pr-review`, `architecture-plan`, `triage`, `hiring-review` |
| Data/ML | `ci-cd`, `documentation`, `monitoring` |
| Platform | All of the above + `security-audit`, `release-management` |

## Scaling Rules

- **Add CTO** when: 3+ engineers OR 2+ distinct tech stacks
- **Add PM** when: 2+ customer-facing surfaces OR product docs exist
- **Add QA** when: test runner detected in CI OR `test` script in package manager
- **Add DevOps** when: CI config exists OR Dockerfile/docker-compose detected OR infra-as-code present
- **Add Designer** when: design system docs exist OR UI reference files detected
- **Split engineers** when: an engineer owns 2+ distinct runtimes (e.g., Go + React)
- **Archive agent** when: 0 tickets for 2+ weeks AND no workspace surface maps to them
