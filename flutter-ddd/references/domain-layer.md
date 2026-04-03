# Domain Layer Reference

The domain layer is the pristine core — zero dependencies on infrastructure, UI, or third-party packages (except `dartz` and `freezed_annotation`).

## Table of Contents
- [Entities](#entities)
- [Failures](#failures)
- [Facade Interfaces](#facade-interfaces)
- [Typedefs](#typedefs)
- [Enums](#enums)

## Entities

Immutable freezed data classes representing business objects. Always include:
- `const factory` constructor with all required fields
- `const ClassName._()` private constructor (required by freezed for custom methods)
- `factory ClassName.empty()` for default/initial state
- Use `Option<T>` (from dartz) for optional fields instead of nullable types

```dart
import 'package:dartz/dartz.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'order.freezed.dart';

@freezed
abstract class Order with _$Order {
  const factory Order({
    required String id,
    required String orderNumber,
    required String customerName,
    required String customerPhone,
    required String address,
    required Option<DateTime> deliveryDate,
    required OrderStatus status,
    required Option<OrderDetail> details,
  }) = _Order;

  const Order._();

  factory Order.empty() => const Order(
    id: '',
    orderNumber: '',
    customerName: '',
    customerPhone: '',
    address: '',
    deliveryDate: None(),
    status: OrderStatus.pending,
    details: None(),
  );
}
```

## Failures

Sealed freezed classes representing domain-specific errors. Each domain feature defines its own failure type. Never throw exceptions across layers — return failures via `Either`.

```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'order_failure.freezed.dart';

@freezed
sealed class OrderFailure with _$OrderFailure {
  const factory OrderFailure.unexpected() = _Unexpected;
  const factory OrderFailure.serverError() = _ServerError;
  const factory OrderFailure.internetError() = _InternetError;
  const factory OrderFailure.notFound() = _NotFound;
  const factory OrderFailure.uploadError() = _UploadError;
  const factory OrderFailure.permissionDenied() = _PermissionDenied;
}
```

Naming: `{Feature}Failure` (e.g., `AuthFailure`, `TaskFailure`, `OrderFailure`).

## Facade Interfaces

Abstract classes defining the contract between application/presentation and infrastructure layers. Facades return `Either<Failure, T>` — never throw.

```dart
import 'package:dartz/dartz.dart' hide Order;
import 'package:app/domains/orders/entities/order.dart';
import 'package:app/domains/orders/order_failure.dart';
import 'package:app/infrastructures/core/dtos/paging.dart';

abstract class IOrderFacade {
  Future<Either<OrderFailure, (List<Order>, Paging)>> getOrders({
    required PagingRequest paging,
    required DateTime date,
    List<OrderStatus>? statuses,
  });

  Future<Either<OrderFailure, Order>> getOrder({
    required String orderID,
  });

  Future<Either<OrderFailure, Unit>> completeOrder({
    required String orderID,
    required File? photo,
  });

  Future<Either<OrderFailure, Unit>> cancelOrder({
    required String orderID,
    required List<String> reasons,
  });
}
```

Naming: `I{Feature}Facade` prefix with `I` for interface (e.g., `IAuthFacade`, `IOrderFacade`).

## Typedefs

Define reusable type aliases for common Either patterns:

```dart
import 'package:dartz/dartz.dart';
import 'package:app/infrastructures/core/dtos/paging.dart';

typedef FailureOrT<F, T> = Either<F, T>;
typedef FailureOrTPaging<F, T> = Either<F, (List<T>, Paging)>;
```

Feature-specific typedefs in the facade file:

```dart
typedef TaskResponse<T> = FailureOrT<TaskFailure, T>;
typedef TaskPagingResponse<T> = FailureOrTPaging<TaskFailure, T>;
```

## Enums

Use freezed or plain Dart enums for domain status values:

```dart
enum OrderStatus {
  pending,
  delivering,
  completed,
  cancelled,
  postponed;
}
```
