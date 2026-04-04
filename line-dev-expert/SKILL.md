---
name: line-dev-expert
description: Build LINE Platform applications — Messaging API bots, LIFF/Mini Apps, LINE Login, LINE Pay, Rich Menus, Flex Messages, and real-world integrations (CRM, loyalty programs, e-commerce). Covers webhook handling, security, architecture patterns, and Thailand market best practices. Trigger when user mentions "LINE bot", "LINE API", "LIFF", "LINE Login", "LINE Pay", "LINE OA", "Rich Menu", "Flex Message", "LINE Mini App", "LINE webhook", "LINE messaging", or building any LINE-integrated application.
---

# LINE Dev Expert — Complete LINE Platform Skill

Build production-grade LINE Platform applications with best practices for the Thailand market (54M+ LINE users).

## Platform Overview

```
LINE Platform
├── Messaging API          — Bot messaging, webhooks, push/reply/broadcast
├── LIFF (LINE Front-end Framework) — Web apps inside LINE
├── LINE Mini App          — Certified LIFF apps with service messages
├── LINE Login v2.1        — OAuth 2.0 + OIDC authentication
├── LINE Pay               — Payment processing
├── Rich Menu              — Persistent bottom navigation
├── Flex Messages          — Custom JSON-based message layouts
├── LINE Beacon            — Proximity-based interactions
└── LINE Things            — IoT / BLE device connectivity
```

## Architecture Overview

```
[LINE Platform] → [Webhook Endpoint] → [Signature Validation]
                        │
                        ▼
                  [Message Queue]  (SQS / Redis / Pub/Sub)
                        │
                        ▼
                  [Event Processor]
                  ├── Message Handler
                  ├── Postback Handler
                  ├── Follow/Unfollow Handler
                  └── Account Link Handler
                        │
                        ▼
                  [LINE API Client]  → Reply / Push / Multicast / Broadcast
                        │
                        ▼
                  [Database]  → User profiles, state, conversations
                        │
                        ▼
                  [LIFF / Mini App]  → Frontend web apps (React/Next.js)
```

**Key principle:** Return HTTP 200 from webhooks immediately, process events asynchronously.

## Tech Stack

- **Bot SDKs:** `@line/bot-sdk` (Node.js), `line-bot-sdk-python`, `line-bot-sdk-go`, `line-bot-sdk-java`, `line-bot-sdk-php`
- **LIFF SDK:** `@line/liff` (v2, browser-side)
- **Frontend:** React / Next.js for LIFF apps (dynamic import to avoid SSR issues)
- **Webhook:** Express, Fastify, Hono, or serverless (Lambda, Cloud Functions, Vercel)
- **Queue:** Redis, SQS, Cloud Tasks, RabbitMQ for async processing
- **Database:** PostgreSQL / MySQL for user data, Redis for conversation state
- **Payments:** LINE Pay API v3 (HMAC-SHA256 signed), PromptPay, Omise/Opn
- **Testing:** `@line/liff-mock`, Jest/Vitest, ngrok, LIFF Inspector

## Message Sending Methods

| Method | Endpoint | Target | Cost |
|---|---|---|---|
| **Reply** | `/v2/bot/message/reply` | Via replyToken (1 min TTL) | **FREE** |
| **Push** | `/v2/bot/message/push` | Single userId | Quota |
| **Multicast** | `/v2/bot/message/multicast` | Up to 500 users | Quota |
| **Broadcast** | `/v2/bot/message/broadcast` | All followers | Quota |
| **Narrowcast** | `/v2/bot/message/narrowcast` | Audience segments | Quota |

**Critical:** Always prefer Reply over Push — reply messages are free and don't count toward monthly quota.

## Building a LINE Bot (Step by Step)

### 1. Setup Channel & Webhook
Create a Messaging API channel in LINE Developers Console. Configure webhook URL with signature validation. Read [references/messaging-api.md](references/messaging-api.md) for all message types, event handling, and SDK patterns.

### 2. Design Rich Menu Navigation
Create rich menus (2500x1686 or 2500x843) with tap areas. Use per-user menus for personalization and richmenuswitch for tab navigation. Read [references/rich-menu-flex.md](references/rich-menu-flex.md) for design patterns.

### 3. Build Flex Messages
Design interactive message layouts using the Flex Message Simulator. Use bubble/carousel containers with boxes, text, images, buttons. Read [references/rich-menu-flex.md](references/rich-menu-flex.md) for structure and examples.

### 4. Build LIFF / Mini App Frontend
Create web apps that run inside LINE using `@line/liff`. Handle auth, profile, sharing, scanning. Read [references/liff-mini-app.md](references/liff-mini-app.md) for initialization, APIs, and React/Next.js integration.

### 5. Implement Authentication
Use LINE Login v2.1 (OAuth 2.0 + OIDC) for web/app login. Verify ID tokens server-side. Link LINE accounts to existing service accounts. Read [references/login-security.md](references/login-security.md) for auth flows and token management.

### 6. Add Payments
Integrate LINE Pay (Request → Confirm → Capture flow) or Thai payment gateways. Read [references/payments-integrations.md](references/payments-integrations.md) for LINE Pay API, PromptPay, and gateway patterns.

### 7. Integrate with Backend Systems
Connect to CRM, loyalty programs, e-commerce, healthcare systems. Read [references/payments-integrations.md](references/payments-integrations.md) for real-world Thai integration patterns.

### 8. Production Architecture
Implement async webhook processing, idempotency, rate limit handling, and security best practices. Read [references/architecture-patterns.md](references/architecture-patterns.md) for scalable deployment patterns.

## Critical Rules

- **Validate webhook signatures** on every request using HMAC-SHA256 with channel secret — reject unsigned requests
- **Return 200 immediately** from webhook handlers — process events asynchronously via queue
- **Use Reply over Push** whenever possible — reply messages are free, push counts toward quota
- **Never trust LIFF client-side data** — always verify `liff.getIDToken()` server-side via `/oauth2/v2.1/verify`
- **Set `X-Line-Retry-Key`** header on all message-sending requests for safe retry (UUID format)
- **Use `webhookEventId`** for deduplication — webhooks may be redelivered
- **replyToken expires in 1 minute** and is single-use — respond promptly
- **Max 5 messages per API call**, max 500 recipients per multicast, max 12 bubbles per carousel
- **Rich menu images** must be exactly 2500x1686 or 2500x843 pixels, under 1MB (JPEG/PNG)
- **Dynamic import `@line/liff`** in Next.js/React to avoid SSR issues — LIFF requires browser environment
- **Use stateless channel access tokens** (v2.1, JWT-based) in production — never hardcode long-lived tokens
- **Implement PDPA compliance** (Thailand) — collect explicit consent, support data erasure, disclose privacy policy
- **LINE Mini App replaces LIFF branding** — new projects should target Mini App certification for service messages and discoverability

## Key Limits

| Item | Limit |
|---|---|
| Messages per API call | 5 |
| Multicast recipients | 500 per call |
| Quick reply items | 13 |
| Flex carousel bubbles | 12 |
| Rich menu tap areas | 20 |
| Rich menu image | 2500x1686 or 2500x843, < 1MB |
| Flex message JSON | ~50 KB per message |
| Reply token TTL | 1 minute, single use |
| Push/Multicast rate | 100,000 req/min per channel |
| Narrowcast rate | 60 req/hour |
| Profile API rate | 2,000 req/min |
| Channel access token v2.1 | Max 30 days, up to 30 per channel |

## References

- [Messaging API — Webhooks, Events, SDKs, Quick Reply](references/messaging-api.md)
- [Rich Menu & Flex Messages — Design, Switching, Layouts](references/rich-menu-flex.md)
- [LIFF & LINE Mini App — Init, APIs, React/Next.js, Testing](references/liff-mini-app.md)
- [LINE Login & Security — OAuth, Tokens, Signature Validation](references/login-security.md)
- [Payments & Integrations — LINE Pay, CRM, Loyalty, E-commerce](references/payments-integrations.md)
- [Architecture Patterns — Serverless, Queues, Database, Scale](references/architecture-patterns.md)
