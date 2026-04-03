# Presentation Layer Reference

The presentation layer contains UI pages, feature-level BLoCs, and widgets. It is the "dumbest" layer — only UI logic, animations, and BLoC event dispatch.

## Table of Contents
- [Page with AutoRouteWrapper](#page-with-autoroutewrapper)
- [BlocBuilder / BlocListener Usage](#blocbuilder--bloclistener-usage)
- [Feature-Level BLoCs vs Global BLoCs](#feature-level-blocs-vs-global-blocs)
- [Folder Structure](#folder-structure)

## Page with AutoRouteWrapper

Pages use `AutoRouteWrapper` to provide BLoCs via `wrappedRoute()`. This replaces manual `BlocProvider` wrapping at the router level.

```dart
import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';

@RoutePage()
class OrdersPage extends StatefulWidget implements AutoRouteWrapper {
  const OrdersPage({super.key});

  @override
  State<OrdersPage> createState() => _OrdersPageState();

  @override
  Widget wrappedRoute(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(
          create: (context) => GetIt.I<OrdersCubit>(),
        ),
        BlocProvider(
          create: (_) => GetIt.I<ProfileAvatarCubit>(),
        ),
      ],
      child: this,
    );
  }
}

class _OrdersPageState extends State<OrdersPage> {
  @override
  void initState() {
    super.initState();
    context.read<OrdersCubit>().fetchOrders();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Orders')),
      body: BlocBuilder<OrdersCubit, OrdersState>(
        builder: (context, state) {
          return state.failOrOrders.fold(
            () => const Center(child: CircularProgressIndicator()),
            (either) => either.fold(
              (failure) => _buildError(failure),
              (data) => _buildOrderList(data.$1),
            ),
          );
        },
      ),
    );
  }

  Widget _buildError(OrderFailure failure) {
    return failure.map(
      serverError: (_) => const Center(child: Text('Server error')),
      internetError: (_) => const Center(child: Text('No internet')),
      unexpected: (_) => const Center(child: Text('Something went wrong')),
      // handle other variants...
    );
  }

  Widget _buildOrderList(List<Order> orders) {
    return ListView.builder(
      itemCount: orders.length,
      itemBuilder: (context, index) => OrderCard(order: orders[index]),
    );
  }
}
```

## BlocBuilder / BlocListener Usage

- **BlocBuilder** — rebuild UI on state changes
- **BlocListener** — one-time side effects (navigation, snackbar, dialog)
- **BlocConsumer** — both rebuild and side effects

```dart
// Listen for one-time effects (navigation on logout)
BlocListener<AuthBloc, AuthState>(
  listenWhen: (prev, curr) => prev.user != curr.user,
  listener: (context, state) {
    state.user.fold(
      () => context.router.replaceAll([const LoginRoute()]),
      (_) {},
    );
  },
  child: BlocBuilder<AuthBloc, AuthState>(
    builder: (context, state) {
      return state.user.fold(
        () => const SizedBox.shrink(),
        (user) => Text('Welcome ${user.name}'),
      );
    },
  ),
)
```

## Feature-Level BLoCs vs Global BLoCs

| Location | Scope | Example |
|---|---|---|
| `applications/` | Global — provided at app root | `AuthBloc`, `TasksBloc`, `OrdersBloc` |
| `presentations/feature/bloc/` | Feature-scoped — provided via `wrappedRoute` | `TaskMapBloc`, `LoginFormCubit` |

Global BLoCs persist across navigation. Feature BLoCs are created/destroyed with their page.

## Folder Structure

```
presentations/
  feature_name/
    bloc/                    # Feature-scoped BLoC (if needed)
      feature_bloc.dart
      feature_event.dart
      feature_state.dart
    view/                    # Main page widget
      feature_page.dart
    widgets/                 # Reusable widgets for this feature
      feature_card.dart
      feature_list.dart
  widgets/                   # Global reusable widgets
    app_bar_widget.dart
    loading_widget.dart
  app_router.dart            # Auto route configuration
  app.dart                   # Root MaterialApp.router
```
