# Infrastructure Layer Reference

The infrastructure layer implements domain interfaces with concrete data sources: REST APIs (retrofit + dio), local storage (hive), and external services.

## Table of Contents
- [DTOs](#dtos)
- [API Clients](#api-clients)
- [Repositories](#repositories)
- [Facade Implementations](#facade-implementations)
- [Error Handling Pattern](#error-handling-pattern)

## DTOs

Freezed data classes with JSON serialization. Always include a `toDomain()` method to convert to the domain entity. DTOs mirror the API response shape; entities mirror the business model.

```dart
import 'package:dartz/dartz.dart' hide Task;
import 'package:app/domains/orders/entities/task.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'task_dto.freezed.dart';
part 'task_dto.g.dart';

@freezed
abstract class TaskDto with _$TaskDto {
  @JsonSerializable(fieldRename: FieldRename.snake)
  factory TaskDto({
    required String taskId,
    required int completedOrders,
    required int totalOrders,
    required DateTime planDate,
    required String taskStatus,
    double? totalRiderFee,
  }) = _TaskDto;

  factory TaskDto.fromJson(Map<String, dynamic> json) =>
      _$TaskDtoFromJson(json);

  const TaskDto._();

  Task toDomain() {
    return Task(
      id: taskId,
      name: taskId,
      planAt: planDate,
      totalPrice: optionOf(totalRiderFee),
      totalOrder: totalOrders,
      completedOrder: completedOrders,
    );
  }
}
```

Key rules:
- Use `@JsonSerializable(fieldRename: FieldRename.snake)` when API uses snake_case
- Nullable DTO fields map to `Option<T>` in entities via `optionOf()`
- DTO file: `{feature}_dto.dart`, class: `{Feature}Dto`

## API Clients

Abstract retrofit interfaces generating type-safe HTTP clients. Dio is the HTTP engine.

```dart
import 'package:app/infrastructures/core/dtos/api_result.dart';
import 'package:app/infrastructures/orders/dtos/order_detail_dto.dart';
import 'package:dio/dio.dart';
import 'package:retrofit/retrofit.dart';

part 'order_api.g.dart';

@RestApi()
abstract class OrderApi {
  factory OrderApi(Dio dio, {String baseUrl}) = _OrderApi;

  @GET('/orders/{order_id}')
  Future<ApiResult<OrderDetailDto>> getOrder({
    @Path('order_id') required String orderID,
    @Query('task_id') String? taskId,
  });

  @GET('/orders/delivery-history')
  Future<ApiResult<List<OrderDetailDto>>> getOrders({
    @Query('page') required int page,
    @Query('limit') required int limit,
    @Query('startDate') required String startDate,
    @Query('endDate') required String endDate,
    @Query('status') List<String>? statuses,
  });

  @PUT('/orders/{order_id}/complete')
  Future<ApiResult<dynamic>> orderCompleted({
    @Path('order_id') required String orderID,
    @Body() required OrderCompleteDto body,
  });
}
```

Naming: `{Feature}Api` (e.g., `AuthApi`, `OrderApi`, `TaskApi`).

## Repositories

Abstract interface + concrete implementation in the same file. Repositories handle raw data access and error conversion. Use `@LazySingleton` for DI registration.

```dart
import 'package:dartz/dartz.dart' hide Order;
import 'package:app/domains/orders/entities/order.dart';
import 'package:app/domains/orders/order_failure.dart';
import 'package:app/infrastructures/core/dtos/paging.dart';
import 'package:app/infrastructures/orders/order_api.dart';
import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart' hide Order;
import 'package:logger/logger.dart';

// Interface
abstract class OrderRepository {
  Future<Either<OrderFailure, (List<Order>, Paging)>> listOrder({
    required PagingRequest paging,
    required DateTime date,
    List<OrderStatus>? statuses,
  });
  Future<Either<OrderFailure, Order>> getOrder({required String orderID});
  Future<Either<OrderFailure, Unit>> completeOrder({required String orderID, String? fileUrl});
}

// Implementation
@LazySingleton(as: OrderRepository)
class OrderRepositoryImpl implements OrderRepository {
  const OrderRepositoryImpl(this._api, this._logger);

  final OrderApi _api;
  final Logger _logger;

  // Generic request wrapper for error handling
  Future<Either<OrderFailure, T>> _request<T>(
    Future<T> Function() request,
  ) async {
    try {
      return Right(await request());
    } on DioException catch (e) {
      final statusCode = e.response?.statusCode;
      if (statusCode == null) {
        return const Left(OrderFailure.serverError());
      }
      if (statusCode > 500) {
        return const Left(OrderFailure.serverError());
      }
      return const Left(OrderFailure.unexpected());
    } on Exception {
      return const Left(OrderFailure.serverError());
    }
  }

  @override
  Future<Either<OrderFailure, (List<Order>, Paging)>> listOrder({
    required PagingRequest paging,
    required DateTime date,
    List<OrderStatus>? statuses,
  }) {
    return _request(() async {
      final response = await _api.getOrders(
        page: paging.page,
        limit: paging.limit,
        startDate: date.toIso8601String(),
        endDate: date.toIso8601String(),
        statuses: statuses?.map((e) => e.name).toList(),
      );
      return (
        response.data.map((e) => e.toDomain()).toList(),
        Paging.fromApiResult(response),
      );
    });
  }
}
```

Key pattern: The `_request<T>` wrapper centralizes try-catch → `Either<Failure, T>` conversion.

## Facade Implementations

Facades orchestrate multiple repositories and cross-cutting concerns. Registered with `@LazySingleton(as: IFeatureFacade)`.

```dart
import 'package:dartz/dartz.dart' hide Order;
import 'package:app/domains/orders/i_order_facade.dart';
import 'package:app/domains/orders/order_failure.dart';
import 'package:app/infrastructures/orders/order_repository.dart';
import 'package:app/infrastructures/upload/upload_repository.dart';
import 'package:injectable/injectable.dart' hide Order;

@LazySingleton(as: IOrderFacade)
class OrderFacade implements IOrderFacade {
  const OrderFacade(this._repository, this._uploadRepository);

  final OrderRepository _repository;
  final UploadRepository _uploadRepository;

  @override
  Future<Either<OrderFailure, Unit>> completeOrder({
    required String orderID,
    required File? photo,
    required LatLng location,
    String? taskId,
  }) async {
    String? fileUrl;
    if (photo != null) {
      final result = await _uploadRepository.uploadImage(file: photo);
      fileUrl = result.fold((l) => null, (r) => r);
      if (fileUrl == null) {
        return const Left(OrderFailure.uploadError());
      }
    }
    return _repository.completeOrder(orderID: orderID, fileUrl: fileUrl);
  }
}
```

Key rules:
- Facades inject repositories (not APIs directly)
- Facades handle cross-repository orchestration (e.g., upload then complete)
- Simple pass-through methods delegate directly to the repository

## Error Handling Pattern

```
API call throws DioException
  → Repository catches in _request() wrapper
    → Converts to Left(FeatureFailure.variant())
      → Facade returns Either to BLoC
        → BLoC emits error state
          → UI shows error via BlocBuilder
```

Never let exceptions escape the repository layer. All cross-layer communication uses `Either<Failure, T>`.
