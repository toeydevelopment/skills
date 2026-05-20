# API Definition — Protobuf Conventions

The API definition in Phase 1 follows the project's existing declaration style.

**Detection.** If the repo has `.proto` files or a `buf.yaml` / `buf.gen.yaml`,
it is a protobuf project — write protobuf directly (sections below). Otherwise
write the markdown API spec ([fallback](#markdown-api-spec-fallback)).

## Table of Contents

1. [Canonical protobuf style](#1-canonical-protobuf-style)
2. [Per-RPC option blocks](#2-per-rpc-option-blocks)
3. [Message conventions](#3-message-conventions)
4. [Checklist](#4-checklist)
5. [Markdown API spec fallback](#markdown-api-spec-fallback)

## 1. Canonical protobuf style

`proto3`. File per service. Package `<product>.v1`. `go_package` points at the
generated-code path. Import only what is used.

```protobuf
syntax = "proto3";

package genericpos.v1;

import "genericpos/rbac/v1/rbac.proto";
import "genericpos/v1/common.proto";
import "genericpos/v1/policy.proto";
import "google/api/annotations.proto";
import "google/api/field_behavior.proto";
import "google/protobuf/empty.proto";
import "google/protobuf/field_mask.proto";

option go_package = "github.com/transformext/generic-pos/gen/go/genericpos/v1;genericposv1";

service CRMService {
  // Every RPC carries a one-line comment stating what it does and its
  // side effects (e.g. "records a semantic audit row").
  rpc AddTag(AddTagRequest) returns (google.protobuf.Empty) {
    option (google.api.http) = {
      post: "/v1/customers/{customer_id}/tags"
      body: "*"
    };
    option (genericpos.rbac.v1.require) = {
      resource: "crm.tag"
      action: "write"
    };
    option (genericpos.v1.options) = {
      auth_required: true
      tenant_scope: TENANT_SCOPE_BUSINESS
      permissions: "crm.tag.write"
      idempotent: true
      idempotency_lock_seconds: 60
      rate_limit: { key: "write" requests_per_minute: 120 }
      mutating: true
      audited: true
    };
  }

  // Reads use a `policy` block mirroring the read intent.
  rpc ListTags(ListTagsRequest) returns (ListTagsResponse) {
    option (google.api.http) = {get: "/v1/customers/{customer_id}/tags"};
    option (genericpos.rbac.v1.require) = {
      resource: "crm.tag"
      action: "read"
    };
    option (genericpos.v1.options) = {
      auth_required: true
      tenant_scope: TENANT_SCOPE_BUSINESS
      permissions: "crm.tag.read"
      rate_limit: { key: "read" requests_per_minute: 600 }
      list_total_size_supported: true
    };
    option (genericpos.v1.policy) = {
      tenant_scope: TENANT_SCOPE_BUSINESS
      mutating: false
      audited: false
      permissions: "crm.tag.read"
      rate_limit_bucket: "read"
      list_total_size_supported: true
    };
  }

  // Custom verbs use the `:verb` suffix on a POST.
  rpc ArchiveSegment(ArchiveSegmentRequest) returns (Segment) {
    option (google.api.http) = {
      post: "/v1/segments/{segment_id}:archive"
      body: "*"
    };
    option (genericpos.rbac.v1.require) = {
      resource: "crm.segment"
      action: "write"
    };
    option (genericpos.v1.options) = {
      auth_required: true
      tenant_scope: TENANT_SCOPE_BUSINESS
      permissions: "crm.segment.write"
      idempotent: true
      idempotency_lock_seconds: 60
      rate_limit: { key: "write" requests_per_minute: 120 }
      mutating: true
      audited: true
    };
  }
}
```

## 2. Per-RPC option blocks

Every RPC declares three to four option blocks:

- **`google.api.http`** — REST mapping. `get` for reads, `post`+`body` for
  creates, `delete` for removals, `patch`+`body` for partial updates,
  `post: ".../{id}:verb"` for custom verbs (`:archive`, `:rebuildMembership`).
- **`genericpos.rbac.v1.require`** — `resource` + `action` (`read` | `write`).
- **`genericpos.v1.options`** — runtime policy:
  - `auth_required`, `tenant_scope` (e.g. `TENANT_SCOPE_BUSINESS`),
  - `permissions` (the dotted permission string),
  - mutating writes: `idempotent: true` + `idempotency_lock_seconds`,
    `mutating: true`, `audited: true`,
  - `rate_limit: { key: "<bucket>" requests_per_minute: N }` — `write` bucket
    ~120/min, `read` bucket ~600/min,
  - list reads: `list_total_size_supported: true`.
- **`genericpos.v1.policy`** — present on reads, mirrors the read intent
  (`mutating: false`, `audited: false`, `rate_limit_bucket`).

Write RPCs are idempotent + audited + mutating. Read RPCs are neither mutating
nor audited.

## 3. Message conventions

```protobuf
enum SegmentKind {
  SEGMENT_KIND_UNSPECIFIED = 0;   // zero value is always _UNSPECIFIED
  SEGMENT_KIND_STATIC = 1;
  SEGMENT_KIND_RULE = 2;
}

message Segment {
  string id = 1;
  string business_id = 2;
  string name = 3;
  SegmentKind kind = 4;
  string definition_json = 5;
  SegmentStatus status = 6;
  AuditMeta audit = 7;            // shared audit metadata
  int64 lock_version = 90;        // optimistic concurrency, high field number
}

message AddTagRequest {
  string customer_id = 1 [(google.api.field_behavior) = REQUIRED];
  string tag = 2 [(google.api.field_behavior) = REQUIRED];
}

message ListTagsRequest {
  string customer_id = 1 [(google.api.field_behavior) = REQUIRED];
  PageRequest page = 2;           // shared pagination request
}

message ListTagsResponse {
  repeated string tags = 1;
  PageResponse page = 2;          // shared pagination response
}

message UpdateSegmentRequest {
  Segment segment = 1 [(google.api.field_behavior) = REQUIRED];
  google.protobuf.FieldMask update_mask = 2 [(google.api.field_behavior) = REQUIRED];
}
```

Conventions:
- Enums: zero value is `<NAME>_UNSPECIFIED = 0`.
- Required fields: `[(google.api.field_behavior) = REQUIRED]`.
- Partial updates: a `FieldMask update_mask`; callers send `If-Match`.
- Optimistic concurrency: an `int64 lock_version`, conventionally a high field
  number (e.g. `90`).
- Audit metadata: an `AuditMeta audit` field from `common.proto`.
- Pagination: `PageRequest` / `PageResponse` from `common.proto` — never
  hand-roll page/offset fields.
- Empty responses: `google.protobuf.Empty`.

## 4. Checklist

- [ ] `syntax = "proto3"`, package `<product>.v1`, correct `go_package`.
- [ ] Only-used imports.
- [ ] Every RPC has a doc comment stating effect + side effects.
- [ ] Every RPC: `http` + `rbac.require` + `options` (+ `policy` on reads).
- [ ] Writes are idempotent + audited + mutating + rate-limited.
- [ ] Enums start at `_UNSPECIFIED = 0`.
- [ ] Required fields marked; updates use `FieldMask`; lists use `PageRequest`.

## Markdown API spec fallback

When the project does **not** use protobuf, write `docs/api/<feature>-api.md`:

```markdown
# API: <Feature Name>

## <METHOD> <path>

<One line: what it does and any side effects.>

- **Auth**: <required? scope? permission string?>
- **Idempotent**: <yes/no>
- **Rate limit**: <bucket / limit>

### Request
| Field | Type | Required | Notes |
|---|---|---|---|
| <field> | <type> | yes/no | <constraint> |

### Response — <status>
| Field | Type | Notes |
|---|---|---|
| <field> | <type> | <notes> |

### Errors
| Status | When |
|---|---|
| 400 | <reason> |
| 409 | <reason — e.g. stale lock_version> |

### Example
```
<request example>
<response example>
```
```

Repeat the `## <METHOD> <path>` block per endpoint. Mirror whatever conventions
the repo's existing API docs already use; do not invent a new style.
