---
name: flutter-ddd
description: Write Flutter/Dart code following Domain-Driven Design (DDD) with Clean Architecture. Uses BLoC state management, dartz Either/Failure error handling, freezed models, retrofit APIs, injectable DI, and auto_route navigation. Trigger when writing Flutter features, creating BLoCs, entities, repositories, facades, DTOs, or API clients. Also trigger when user mentions "DDD", "clean architecture", "add feature", "new bloc", "new entity", or "new facade" in a Flutter/Dart context.
---

# Flutter DDD — Clean Architecture Skill

Generate Flutter/Dart code following a strict 4-layer DDD architecture with functional error handling.

## Architecture Overview

```
Presentation → Application (BLoC) → Domain ← Infrastructure
```

**Dependency rule:** outer layers depend on inner layers. Domain depends on nothing.

| Layer | Location | Contains |
|---|---|---|
| **Domain** | `domains/{feature}/` | Entities, failure classes, facade interfaces (`I{Feature}Facade`), typedefs |
| **Infrastructure** | `infrastructures/{feature}/` | DTOs (with `toDomain()`), retrofit API clients, repositories (interface + impl), facade implementations |
| **Application** | `applications/{feature}/` | Global BLoCs/Cubits injecting facade interfaces |
| **Presentation** | `presentations/{feature}/` | Pages (`@RoutePage` + `AutoRouteWrapper`), feature BLoCs, widgets |

## Tech Stack

- **State management:** `flutter_bloc` (BLoC/Cubit)
- **Error handling:** `dartz` (`Either<Failure, T>`, `Option<T>`, `Unit`)
- **Code generation:** `freezed` (entities, DTOs, events, states, failures), `json_serializable`, `retrofit`, `auto_route_generator`, `injectable_generator`
- **DI:** `get_it` + `injectable` (`@injectable`, `@LazySingleton`)
- **Navigation:** `auto_route` with `@RoutePage()` and `AutoRouteWrapper`

## Adding a New Feature (Bottom-Up)

### 1. Domain Layer
Create entity, failure, and facade interface. Read [references/domain-layer.md](references/domain-layer.md) for patterns.

### 2. Infrastructure Layer
Create DTO (with `toDomain()`), retrofit API client, repository (interface + impl in same file), and facade implementation. Read [references/infrastructure-layer.md](references/infrastructure-layer.md) for patterns.

### 3. Application Layer (BLoC)
Create BLoC with freezed events/states. Inject `I{Feature}Facade`. Use `event.map()` for dispatch, `state.copyWith()` for emissions. Read [references/application-layer.md](references/application-layer.md) for patterns.

### 4. Presentation Layer
Create page with `@RoutePage()` and `AutoRouteWrapper` for BLoC provision. Use `BlocBuilder`/`BlocListener`. Read [references/presentation-layer.md](references/presentation-layer.md) for patterns.

### 5. Run code generation
```bash
melos code_gen          # single app
melos code_gen:all      # all packages
```

## Critical Rules

- Return `Either<Failure, T>` from facades and repositories — never throw exceptions across layers
- Use `Option<T>` (dartz) for optional domain fields — not nullable types
- Facades inject repositories, BLoCs inject facades — never skip layers
- Entities are freezed with `const factory`, `const Entity._()`, and `factory Entity.empty()`
- DTOs always have `toDomain()` and `fromJson` — they never leak into domain/presentation
- Repository `_request<T>` wrapper converts all exceptions to `Left(Failure)`
- Events are verb-first (`FetchOrders`, `SetDate`), states use `Option<Either<Failure, T>>` fields
- Use `@LazySingleton(as: IFeatureFacade)` for facade DI, `@injectable` for BLoCs
- Pages use `implements AutoRouteWrapper` with `wrappedRoute()` for BLoC provision
