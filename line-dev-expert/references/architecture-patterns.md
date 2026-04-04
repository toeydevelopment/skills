# Architecture Patterns — Serverless, Queues, Database, Scale

## Serverless Architecture

### AWS Lambda + API Gateway

```typescript
// handler.ts — Lambda webhook handler
import { APIGatewayProxyHandler } from 'aws-lambda';
import { SQSClient, SendMessageCommand } from '@aws-sdk/client-sqs';
import crypto from 'crypto';

const sqs = new SQSClient({});

export const webhook: APIGatewayProxyHandler = async (event) => {
  // Validate signature
  const signature = event.headers['x-line-signature']!;
  const body = event.body!;

  const expectedSig = crypto
    .createHmac('SHA256', process.env.CHANNEL_SECRET!)
    .update(body)
    .digest('base64');

  if (!crypto.timingSafeEqual(Buffer.from(expectedSig), Buffer.from(signature))) {
    return { statusCode: 403, body: 'Invalid signature' };
  }

  // Enqueue events for async processing
  const { events } = JSON.parse(body);
  await Promise.all(
    events.map((event: any) =>
      sqs.send(new SendMessageCommand({
        QueueUrl: process.env.QUEUE_URL!,
        MessageBody: JSON.stringify(event),
        MessageDeduplicationId: event.webhookEventId, // FIFO dedup
        MessageGroupId: event.source?.userId ?? 'system',
      }))
    )
  );

  return { statusCode: 200, body: '' };
};

// worker.ts — SQS consumer (separate Lambda)
import { SQSHandler } from 'aws-lambda';
import { messagingApi } from '@line/bot-sdk';

const client = new messagingApi.MessagingApiClient({
  channelAccessToken: process.env.CHANNEL_ACCESS_TOKEN!,
});

export const processEvent: SQSHandler = async (sqsEvent) => {
  for (const record of sqsEvent.Records) {
    const event = JSON.parse(record.body);
    await handleLineEvent(event, client);
  }
};
```

**Key considerations:**
- Use **Provisioned Concurrency** for webhook Lambda to avoid cold starts
- Return 200 immediately — LINE expects fast webhook responses
- Process events via SQS to handle spikes and prevent timeouts

### Google Cloud Functions

```typescript
import { HttpFunction } from '@google-cloud/functions-framework';
import { PubSub } from '@google-cloud/pubsub';

const pubsub = new PubSub();
const topic = pubsub.topic('line-events');

export const webhook: HttpFunction = async (req, res) => {
  // Validate signature (same pattern)
  if (!validateSignature(req.rawBody, req.headers['x-line-signature'], CHANNEL_SECRET)) {
    res.status(403).end();
    return;
  }

  // Publish events to Pub/Sub
  const { events } = req.body;
  await Promise.all(
    events.map((event: any) =>
      topic.publishMessage({
        data: Buffer.from(JSON.stringify(event)),
        attributes: { eventType: event.type, userId: event.source?.userId ?? '' },
      })
    )
  );

  res.status(200).end();
};
```

### Vercel / Edge Functions

```typescript
// app/api/webhook/route.ts (Next.js App Router)
import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

export async function POST(req: NextRequest) {
  const body = await req.text();
  const signature = req.headers.get('x-line-signature')!;

  const expectedSig = crypto
    .createHmac('SHA256', process.env.LINE_CHANNEL_SECRET!)
    .update(body)
    .digest('base64');

  if (!crypto.timingSafeEqual(Buffer.from(expectedSig), Buffer.from(signature))) {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 403 });
  }

  const { events } = JSON.parse(body);

  // Process events (for low-traffic bots, inline processing is fine)
  // For high-traffic, use external queue (Upstash Redis, Inngest, etc.)
  await Promise.all(events.map(handleEvent));

  return NextResponse.json({ status: 'ok' });
}
```

## Microservices Architecture

```
[LINE Platform]
      │
      ▼
[API Gateway / Load Balancer]
      │
      ▼
[Webhook Router Service]  ← validates signature, routes events
      │
      ├──────────────────────────────────────────┐
      │                    │                      │
      ▼                    ▼                      ▼
[Message Service]    [User Service]        [Rich Menu Service]
      │                    │                      │
      ▼                    ▼                      ▼
[Message Queue]      [User DB]             [Asset Storage (S3)]
      │
      ▼
[Worker Pool]
      ├── Text handler
      ├── Postback handler
      ├── AI/NLP handler
      └── Notification handler
            │
            ▼
      [LINE Messaging API]
```

### Event Router Pattern

```typescript
// event-router.ts
type EventHandler = (event: webhook.Event, client: MessagingApiClient) => Promise<void>;

const handlers: Record<string, EventHandler> = {
  message: handleMessage,
  postback: handlePostback,
  follow: handleFollow,
  unfollow: handleUnfollow,
  join: handleJoin,
  memberJoined: handleMemberJoined,
  accountLink: handleAccountLink,
  beacon: handleBeacon,
};

async function routeEvent(event: webhook.Event, client: MessagingApiClient) {
  const handler = handlers[event.type];
  if (!handler) {
    console.warn(`Unhandled event type: ${event.type}`);
    return;
  }

  try {
    await handler(event, client);
  } catch (error) {
    console.error(`Error handling ${event.type}:`, error);
    // Don't throw — prevent retry for application errors
  }
}

// message-handler.ts
async function handleMessage(event: webhook.Event, client: MessagingApiClient) {
  if (event.message.type !== 'text') return;

  const text = event.message.text;
  const userId = event.source.userId!;

  // Check conversation state
  const state = await redis.hgetall(`conversation:${userId}`);

  if (state.step) {
    // Continue conversation flow
    await conversationFlow(state, text, event, client);
  } else {
    // Route by keyword or intent
    await keywordRouter(text, event, client);
  }
}
```

### Conversation State Machine

```typescript
// conversation-flow.ts
interface ConversationState {
  step: string;
  data: Record<string, any>;
  expiresAt: number;
}

async function setConversationState(userId: string, state: ConversationState) {
  await redis.hset(`conversation:${userId}`, {
    ...state,
    data: JSON.stringify(state.data),
  });
  await redis.expireat(`conversation:${userId}`, state.expiresAt);
}

async function clearConversationState(userId: string) {
  await redis.del(`conversation:${userId}`);
}

// Example: Order flow state machine
async function conversationFlow(
  state: ConversationState,
  input: string,
  event: webhook.Event,
  client: MessagingApiClient,
) {
  const userId = event.source.userId!;
  const data = JSON.parse(state.data);

  switch (state.step) {
    case 'awaiting_product': {
      data.productId = input;
      await setConversationState(userId, {
        step: 'awaiting_quantity',
        data,
        expiresAt: Math.floor(Date.now() / 1000) + 300, // 5 min timeout
      });
      await client.replyMessage({
        replyToken: event.replyToken!,
        messages: [{ type: 'text', text: 'กรุณาระบุจำนวน' }],
      });
      break;
    }

    case 'awaiting_quantity': {
      const qty = parseInt(input);
      if (isNaN(qty) || qty < 1) {
        await client.replyMessage({
          replyToken: event.replyToken!,
          messages: [{ type: 'text', text: 'กรุณาระบุจำนวนเป็นตัวเลข' }],
        });
        return;
      }
      data.quantity = qty;
      await clearConversationState(userId);
      await createOrder(userId, data);
      await client.replyMessage({
        replyToken: event.replyToken!,
        messages: [{ type: 'text', text: `สั่งซื้อสำเร็จ! ${data.quantity} ชิ้น` }],
      });
      break;
    }
  }
}
```

## Message Queue Integration

### High-Traffic Pattern

```
[Webhook Handler]
      │  (validate signature, return 200)
      ▼
[Redis Queue / SQS / Kafka]
      │
      ▼
[Worker Pool]  (controlled concurrency)
      │
      ├── Rate limiter (100K req/min for push)
      ├── Retry with exponential backoff
      └── Dead letter queue (DLQ) for failures
```

### Bull Queue (Node.js + Redis)

```typescript
import { Queue, Worker } from 'bullmq';
import Redis from 'ioredis';

const connection = new Redis(process.env.REDIS_URL!);

// Queue for LINE events
const eventQueue = new Queue('line-events', { connection });

// Queue for outbound messages (rate-limited)
const messageQueue = new Queue('line-messages', {
  connection,
  defaultJobOptions: {
    attempts: 3,
    backoff: { type: 'exponential', delay: 1000 },
    removeOnComplete: 100,
    removeOnFail: 1000,
  },
});

// Webhook handler enqueues events
app.post('/webhook', (req, res) => {
  res.status(200).end();
  const { events } = req.body;
  events.forEach((event) => {
    eventQueue.add('process', event, {
      jobId: event.webhookEventId, // deduplication
    });
  });
});

// Event processor worker
new Worker('line-events', async (job) => {
  const event = job.data;
  await routeEvent(event, client);
}, { connection, concurrency: 10 });

// Message sender worker (rate-limited)
new Worker('line-messages', async (job) => {
  const { to, messages, retryKey } = job.data;
  await client.pushMessage(
    { to, messages },
    { headers: { 'X-Line-Retry-Key': retryKey } },
  );
}, {
  connection,
  concurrency: 50, // control outbound rate
  limiter: { max: 1000, duration: 1000 }, // 1000 per second max
});
```

## Database Design

### Core Schema

```sql
-- Users
CREATE TABLE line_users (
    id              SERIAL PRIMARY KEY,
    line_user_id    VARCHAR(64) UNIQUE NOT NULL,
    display_name    VARCHAR(128),
    picture_url     VARCHAR(512),
    status_message  TEXT,
    language        VARCHAR(10),
    is_following    BOOLEAN DEFAULT TRUE,
    followed_at     TIMESTAMP,
    unfollowed_at   TIMESTAMP,
    linked_account  VARCHAR(128),
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Conversation state (for multi-step flows)
-- Use Redis for active states, DB for history
CREATE TABLE conversation_history (
    id              SERIAL PRIMARY KEY,
    line_user_id    VARCHAR(64) NOT NULL,
    direction       VARCHAR(10) NOT NULL,  -- inbound | outbound
    message_type    VARCHAR(20) NOT NULL,
    content         JSONB NOT NULL,
    webhook_event_id VARCHAR(64) UNIQUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Loyalty
CREATE TABLE loyalty_members (
    id              SERIAL PRIMARY KEY,
    line_user_id    VARCHAR(64) UNIQUE REFERENCES line_users(line_user_id),
    member_code     VARCHAR(20) UNIQUE,
    points          INTEGER DEFAULT 0,
    total_spend     DECIMAL(12,2) DEFAULT 0,
    tier            VARCHAR(20) DEFAULT 'Bronze',
    tier_updated_at TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Orders
CREATE TABLE orders (
    id              SERIAL PRIMARY KEY,
    order_number    VARCHAR(20) UNIQUE NOT NULL,
    line_user_id    VARCHAR(64) REFERENCES line_users(line_user_id),
    status          VARCHAR(20) DEFAULT 'pending',
    total_amount    DECIMAL(12,2) NOT NULL,
    payment_method  VARCHAR(20),
    tracking_number VARCHAR(50),
    carrier         VARCHAR(50),
    items           JSONB NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Event deduplication
CREATE TABLE processed_events (
    webhook_event_id VARCHAR(64) PRIMARY KEY,
    processed_at     TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_following ON line_users(is_following);
CREATE INDEX idx_users_linked ON line_users(linked_account) WHERE linked_account IS NOT NULL;
CREATE INDEX idx_history_user ON conversation_history(line_user_id, created_at DESC);
CREATE INDEX idx_orders_user ON orders(line_user_id, created_at DESC);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_events_cleanup ON processed_events(processed_at);

-- Cleanup old dedup records (run periodically)
-- DELETE FROM processed_events WHERE processed_at < NOW() - INTERVAL '7 days';
```

### Key Design Principles

- `line_user_id` is the only immutable field — use as foreign key
- Display name, picture URL change anytime — refresh periodically via Profile API
- Use JSONB for flexible metadata (tags, preferences, custom fields)
- Separate hot data (Redis: conversation state, sessions) from cold data (PostgreSQL: history)
- Event deduplication table prevents reprocessing on webhook redelivery

## Error Handling & Retry Patterns

### Idempotent Message Sending

```typescript
import { randomUUID } from 'crypto';

async function safePushMessage(to: string, messages: any[], maxRetries = 3) {
  const retryKey = randomUUID().replace(/-/g, '');

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      await client.pushMessage(
        { to, messages },
        { headers: { 'X-Line-Retry-Key': retryKey } },
      );
      return; // success
    } catch (error) {
      if (error.status === 409) {
        return; // already sent — idempotent success
      }
      if (error.status === 429) {
        // Rate limited — exponential backoff with jitter
        const delay = Math.min(1000 * Math.pow(2, attempt) + Math.random() * 1000, 30000);
        await new Promise((r) => setTimeout(r, delay));
        continue;
      }
      if (error.status >= 500) {
        // Server error — retry
        const delay = 1000 * Math.pow(2, attempt);
        await new Promise((r) => setTimeout(r, delay));
        continue;
      }
      // 4xx (except 409/429) — don't retry, log error
      console.error(`Push failed (${error.status}):`, await error.body?.text());
      throw error;
    }
  }
  throw new Error(`Push failed after ${maxRetries} retries`);
}
```

### Webhook Idempotency

```typescript
async function processEventIdempotently(event: webhook.Event) {
  const eventId = event.webhookEventId;

  // Check if already processed (atomic check-and-set)
  const inserted = await db.query(
    `INSERT INTO processed_events (webhook_event_id) VALUES ($1)
     ON CONFLICT (webhook_event_id) DO NOTHING
     RETURNING webhook_event_id`,
    [eventId],
  );

  if (inserted.rowCount === 0) {
    // Already processed — skip
    return;
  }

  await routeEvent(event, client);
}
```

## Scaling for Thai Market

### Traffic Patterns

- **Peak hours:** 12:00-13:00 (lunch), 18:00-22:00 (evening)
- **Spikes:** Flash sales, payday (25th/last day of month), Songkran, 11.11/12.12
- **Plan for:** 3-5x normal traffic during peaks

### Infrastructure

| Component | Recommendation |
|---|---|
| Region | AWS ap-southeast-1 (Singapore) or GCP asia-southeast1 |
| CDN | CloudFront / Cloudflare for LIFF assets |
| Cache | Redis (ElastiCache / Cloud Memorystore) |
| Queue | SQS (AWS) / Cloud Tasks (GCP) / Redis (BullMQ) |
| Database | RDS PostgreSQL / Cloud SQL |
| Webhook | Auto-scaling (Lambda / Cloud Run / ECS) |

### Cost Optimization

1. **Reply messages are FREE** — design conversational flows that maximize reply usage
2. **Rich menus are free interactions** — use as primary navigation (no message cost)
3. **Multicast over Push** — batch up to 500 users per API call
4. **Smart narrowcast** — target specific audiences, not broadcast
5. **5 messages per API call** — combine related messages to reduce quota usage
6. **Message count:** Each API call = 1 message per recipient, regardless of how many message objects (up to 5)

### Monitoring & Observability

```typescript
// Structured logging for LINE events
function logEvent(event: webhook.Event) {
  console.log(JSON.stringify({
    service: 'line-bot',
    eventType: event.type,
    userId: event.source?.userId,
    messageType: event.type === 'message' ? event.message.type : undefined,
    webhookEventId: event.webhookEventId,
    isRedelivery: event.deliveryContext?.isRedelivery,
    timestamp: event.timestamp,
  }));
}

// Track API call latency
async function trackedApiCall<T>(name: string, fn: () => Promise<T>): Promise<T> {
  const start = Date.now();
  try {
    const result = await fn();
    console.log(JSON.stringify({
      service: 'line-bot',
      apiCall: name,
      duration: Date.now() - start,
      status: 'success',
    }));
    return result;
  } catch (error) {
    console.error(JSON.stringify({
      service: 'line-bot',
      apiCall: name,
      duration: Date.now() - start,
      status: 'error',
      errorStatus: error.status,
    }));
    throw error;
  }
}
```

## LINE Bot MCP Server

LINE has released an official **MCP (Model Context Protocol) server** (`line/line-bot-mcp-server`) for connecting AI agents to LINE Official Accounts. It supports:

- Sending text/flex messages
- Broadcasting
- Retrieving user profiles
- Managing rich menus

This enables AI-powered LINE bots using Claude, GPT, or other LLMs as the conversation engine.

```typescript
// Example: AI-powered LINE bot
async function handleTextMessage(event: webhook.Event, client: MessagingApiClient) {
  const userMessage = event.message.text;
  const userId = event.source.userId!;

  // Get conversation history for context
  const history = await db.getRecentMessages(userId, 10);

  // Call AI
  const aiResponse = await anthropic.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 500,
    system: 'You are a helpful Thai customer service assistant for ABC Shop. Respond in Thai.',
    messages: [
      ...history.map((m) => ({
        role: m.direction === 'inbound' ? 'user' : 'assistant',
        content: m.content,
      })),
      { role: 'user', content: userMessage },
    ],
  });

  const responseText = aiResponse.content[0].text;

  // Save and reply
  await db.saveMessage(userId, 'inbound', userMessage);
  await db.saveMessage(userId, 'outbound', responseText);

  await client.replyMessage({
    replyToken: event.replyToken!,
    messages: [{ type: 'text', text: responseText }],
  });
}
```
