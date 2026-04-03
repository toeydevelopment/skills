# Application Layer (BLoC) Reference

The application layer contains BLoCs/Cubits that orchestrate state between the presentation and domain layers. BLoCs inject facade interfaces and emit states based on Either results.

## Table of Contents
- [BLoC Structure](#bloc-structure)
- [Events](#events)
- [States](#states)
- [BLoC Implementation](#bloc-implementation)
- [Pagination Pattern](#pagination-pattern)

## BLoC Structure

Each BLoC consists of three files using `part` directives:

```
applications/
  feature_name/
    feature_bloc.dart       # Main BLoC class (imports + parts)
    feature_event.dart      # part of bloc — Freezed events
    feature_state.dart      # part of bloc — Freezed state
```

## Events

Sealed freezed classes. Verb-first naming describing user actions.

```dart
part of 'tasks_bloc.dart';

@freezed
abstract class TasksEvent with _$TasksEvent {
  const factory TasksEvent.fetchTasks() = _FetchTasks;
  const factory TasksEvent.loadMoreTasks() = _LoadMoreTasks;
  const factory TasksEvent.setDate(DateTime date) = _SetDate;
}
```

Naming conventions:
- `fetch*` — initial data load
- `loadMore*` — pagination
- `set*` — update local state (no API call)
- `create*` / `update*` / `delete*` — mutations

## States

Freezed data class with an `initial()` factory. Use `Option<Either<Failure, T>>` to represent three states: not loaded (`None`), failed (`Some(Left)`), success (`Some(Right)`).

```dart
part of 'tasks_bloc.dart';

@freezed
abstract class TasksState with _$TasksState {
  const factory TasksState({
    required Option<TaskPagingResponse<Task>> failOrPendingTasks,
    required Option<TaskPagingResponse<Task>> failOrTasksByDate,
    required DateTime date,
    required bool isLoading,
  }) = _TasksState;

  factory TasksState.initial() => TasksState(
    failOrPendingTasks: const None(),
    failOrTasksByDate: const None(),
    date: DateTime.now(),
    isLoading: false,
  );
}
```

State field patterns:
- `Option<Either<Failure, T>>` — data that can be unloaded, failed, or loaded
- `bool isLoading` — loading indicator
- `bool isSubmitting` — form submission state
- `Option<Failure> failure` — standalone failure display

## BLoC Implementation

```dart
import 'package:bloc/bloc.dart';
import 'package:dartz/dartz.dart';
import 'package:app/domains/auth/i_auth_facade.dart';
import 'package:app/domains/users/entities/user.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:injectable/injectable.dart';

part 'auth_bloc.freezed.dart';
part 'auth_event.dart';
part 'auth_state.dart';

@injectable
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  AuthBloc(this._facade) : super(AuthState.initial()) {
    on<AuthEvent>((event, emit) async {
      await event.map(
        checkAndSet: (e) async {
          final user = await _facade.checkAuthentication();
          if (user.isLeft()) {
            emit(state.copyWith(user: const None()));
            return;
          }
          emit(state.copyWith(user: user.getOrCrash()));
        },
        logout: (e) async {
          await _facade.logout();
          emit(state.copyWith(user: none()));
        },
      );
    });
  }

  final IAuthFacade _facade;
}
```

Key rules:
- Use `@injectable` for DI registration
- Inject facade interface (`IAuthFacade`), never the implementation
- Use `event.map()` (freezed pattern matching) to handle events
- Emit new states via `state.copyWith()`
- Never access repositories or APIs directly — always go through facades

## Pagination Pattern

For paginated lists, accumulate items across pages:

```dart
class TasksBloc extends Bloc<TasksEvent, TasksState> {
  TasksBloc(this._facade) : super(TasksState.initial()) {
    on<TasksEvent>((event, emit) async => event.map(
      fetchTasks: (e) async {
        emit(state.copyWith(isLoading: true));
        final failOrSuccess = await _facade.getTasks(page: 1);
        emit(state.copyWith(
          failOrPendingTasks: optionOf(failOrSuccess),
          isLoading: false,
        ));
        return null;
      },
      loadMoreTasks: (e) async {
        if (state.isLoading) return null;
        emit(state.copyWith(isLoading: true));

        final nextPage = state.failOrPendingTasks.fold(
          () => 1,
          (a) => a.fold((l) => 1, (r) => r.$2.nextPage),
        );
        final failOrSuccess = await _facade.getTasks(page: nextPage);

        // Merge new items with existing
        final allItems = _mergeItems(failOrSuccess, state.failOrPendingTasks);

        emit(state.copyWith(
          failOrPendingTasks: optionOf(
            failOrSuccess.fold(left, (r) => right((allItems, r.$2))),
          ),
          isLoading: false,
        ));
        return null;
      },
    ));
  }

  final ITaskFacade _facade;

  List<Task> _mergeItems(
    Either<TaskFailure, (List<Task>, Paging)> newResult,
    Option<Either<TaskFailure, (List<Task>, Paging)>> current,
  ) {
    if (newResult.isLeft()) return [];
    final newItems = newResult.getOrElse(() => ([], Paging.empty())).$1;
    return current.fold(
      () => newItems,
      (a) => a.fold((l) => newItems, (r) => [...r.$1, ...newItems]),
    );
  }
}
```
