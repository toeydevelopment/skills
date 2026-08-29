# Messaging API — Webhooks, Events, SDKs, Quick Reply

## Webhook Setup & Signature Validation

Every webhook request includes an `x-line-signature` header. **Always validate** to prevent spoofing.

### Node.js Signature Validation

```typescript
import crypto from 'crypto';

function validateSignature(body: string, signature: string, channelSecret: string): boolean {
  const hash = crypto
    .createHmac('SHA256', channelSecret)
    .update(body)
    .digest('base64');
  return crypto.timingSafeEqual(Buffer.from(hash), Buffer.from(signature));
}

// Express middleware — use raw body for signature validation
app.post('/webhook', express.raw({ type: '*/*' }), (req, res) => {
  const signature = req.headers['x-line-signature'] as string;
  const body = req.body.toString();

  if (!validateSignature(body, signature, CHANNEL_SECRET)) {
    return res.status(403).send('Invalid signature');
  }

  // IMPORTANT: Return 200 immediately, process async
  res.status(200).end();

  const { events } = JSON.parse(body);
  events.forEach(event => {
    if (!event.deliveryContext?.isRedelivery) {
      eventQueue.push(event);
    }
  });
});
```

### Python Signature Validation

```python
import hmac
import hashlib
import base64

def validate_signature(body: str, signature: str, channel_secret: str) -> bool:
    gen_signature = base64.b64encode(
        hmac.new(
            channel_secret.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    return hmac.compare_digest(gen_signature, signature)
```

## Webhook Event Types

| Event | Trigger | Has replyToken |
|---|---|---|
| `message` | User sends text/image/video/audio/file/location/sticker | Yes |
| `follow` | User adds bot as friend | Yes |
| `unfollow` | User blocks/removes bot | No |
| `join` | Bot joins group/room | Yes |
| `leave` | Bot removed from group/room | No |
| `memberJoined` | User joins group the bot is in | Yes |
| `memberLeft` | User leaves group the bot is in | No |
| `postback` | User triggers postback action | Yes |
| `beacon` | User enters/leaves beacon range | Yes |
| `accountLink` | Account linking completed | Yes |
| `unsend` | User unsends a message | No |
| `videoPlayComplete` | User finishes video | Yes |

### Event Structure

```json
{
  "destination": "Uxxxxxxx",
  "events": [
    {
      "type": "message",
      "message": { "type": "text", "id": "1234567890", "text": "สวัสดีครับ" },
      "webhookEventId": "event-id-xxx",
      "deliveryContext": { "isRedelivery": false },
      "timestamp": 1625000000000,
      "source": { "type": "user", "userId": "U1234567890abcdef" },
      "replyToken": "reply-token-xxx",
      "mode": "active"
    }
  ]
}
```

### Webhook Retry & Idempotency

- LINE retries webhooks if your server returns non-200 within timeout
- `deliveryContext.isRedelivery` = `true` on retried events
- Use `webhookEventId` for deduplication
- Order is NOT guaranteed on redelivery — use `timestamp` for sequencing
- LINE may force-disable redelivery if volume spikes threaten platform stability

## Message Types

### Text Message

```json
{
  "type": "text",
  "text": "สวัสดีครับ! ยินดีต้อนรับ",
  "emojis": [
    { "index": 0, "productId": "5ac1bfd5040ab15980c9b435", "emojiId": "001" }
  ]
}
```

### Sticker Message

```json
{ "type": "sticker", "packageId": "446", "stickerId": "1988" }
```

### Image Message

```json
{
  "type": "image",
  "originalContentUrl": "https://example.com/image.jpg",
  "previewImageUrl": "https://example.com/preview.jpg"
}
```

### Imagemap Message

```json
{
  "type": "imagemap",
  "baseUrl": "https://example.com/imagemap",
  "altText": "Menu",
  "baseSize": { "width": 1040, "height": 1040 },
  "actions": [
    {
      "type": "uri",
      "linkUri": "https://example.com/shop",
      "area": { "x": 0, "y": 0, "width": 520, "height": 520 }
    },
    {
      "type": "message",
      "text": "สั่งซื้อสินค้า",
      "area": { "x": 520, "y": 0, "width": 520, "height": 520 }
    }
  ]
}
```

### Template Message (Carousel)

```json
{
  "type": "template",
  "altText": "เลือกสินค้า",
  "template": {
    "type": "carousel",
    "columns": [
      {
        "thumbnailImageUrl": "https://example.com/product1.jpg",
        "title": "สินค้า A",
        "text": "ราคา 590 บาท",
        "actions": [
          { "type": "message", "label": "สั่งซื้อ", "text": "สั่งซื้อ สินค้า A" },
          { "type": "uri", "label": "รายละเอียด", "uri": "https://example.com/a" }
        ]
      }
    ]
  }
}
```

## SDK Patterns

### Node.js (Current v8+ Pattern)

```typescript
import { messagingApi, middleware, webhook } from '@line/bot-sdk';

const { MessagingApiClient } = messagingApi;

const client = new MessagingApiClient({
  channelAccessToken: process.env.LINE_CHANNEL_ACCESS_TOKEN!,
});

// Express webhook handler
app.post(
  '/webhook',
  middleware({ channelSecret: process.env.LINE_CHANNEL_SECRET! }),
  async (req, res) => {
    const events: webhook.Event[] = req.body.events;

    await Promise.all(
      events.map(async (event) => {
        if (event.type === 'message' && event.message.type === 'text') {
          await client.replyMessage({
            replyToken: event.replyToken!,
            messages: [{ type: 'text', text: `คุณพิมพ์: ${event.message.text}` }],
          });
        }
      })
    );

    res.status(200).end();
  }
);
```

### Python (v3+ with async)

```python
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

configuration = Configuration(access_token=os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        api = MessagingApi(api_client)
        api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f"คุณพิมพ์: {event.message.text}")]
            )
        )
```

### Error Handling

```typescript
import { HTTPFetchError } from '@line/bot-sdk';

try {
  await client.replyMessage({ replyToken, messages });
} catch (error) {
  if (error instanceof HTTPFetchError) {
    console.error('LINE API Error:', {
      status: error.status,
      body: await error.body.text(),
    });
    // If reply token expired, fall back to push
    if (error.status === 400) {
      await client.pushMessage({ to: userId, messages });
    }
  }
}
```

### Retry with X-Line-Retry-Key

```typescript
import { randomUUID } from 'crypto';

const retryKey = randomUUID().replace(/-/g, '');

await client.pushMessage(
  { to: userId, messages },
  { headers: { 'X-Line-Retry-Key': retryKey } }
);
// If request fails, retry with SAME retryKey — prevents duplicate messages
// If 409 Conflict: message already sent successfully
```

## Quick Reply

Quick Reply buttons appear at the bottom of chat, disappear after use.

```json
{
  "type": "text",
  "text": "คุณต้องการสั่งซื้อสินค้าประเภทใด?",
  "quickReply": {
    "items": [
      {
        "type": "action",
        "imageUrl": "https://example.com/icons/shirt.png",
        "action": { "type": "message", "label": "เสื้อผ้า", "text": "เสื้อผ้า" }
      },
      {
        "type": "action",
        "action": {
          "type": "postback",
          "label": "รองเท้า",
          "data": "category=shoes&action=browse",
          "displayText": "รองเท้า"
        }
      },
      {
        "type": "action",
        "action": { "type": "datetimepicker", "label": "เลือกวัน", "data": "action=date", "mode": "date" }
      },
      {
        "type": "action",
        "action": { "type": "location", "label": "ส่งตำแหน่ง" }
      },
      {
        "type": "action",
        "action": { "type": "camera", "label": "ถ่ายรูป" }
      },
      {
        "type": "action",
        "action": { "type": "cameraRoll", "label": "เลือกรูป" }
      }
    ]
  }
}
```

### Quick Reply Action Types

| Action | Description |
|---|---|
| `message` | Sends text to chat |
| `postback` | Sends data to webhook (hidden from chat) |
| `uri` | Opens URL |
| `datetimepicker` | Date/time picker (date, time, datetime modes) |
| `location` | Location picker |
| `camera` | Opens camera |
| `cameraRoll` | Opens photo gallery |
| `clipboard` | Copies text to clipboard |

**Rules:** Max 13 items. Icons optional (24x24+ PNG/JPEG, HTTPS). Can attach to any message type. Use postback over message when selection shouldn't appear in chat.

## Sending Methods

### Reply (FREE — always prefer this)

```typescript
await client.replyMessage({
  replyToken: event.replyToken,
  messages: [{ type: 'text', text: 'Response' }],
});
```

### Push (single user)

```typescript
await client.pushMessage({
  to: 'U1234...', // userId
  messages: [{ type: 'text', text: 'Notification' }],
});
```

### Multicast (up to 500 users)

```typescript
await client.multicast({
  to: ['U1234...', 'U5678...'], // max 500
  messages: [{ type: 'text', text: 'Group notification' }],
});
```

### Broadcast (all followers)

```typescript
await client.broadcast({
  messages: [{ type: 'text', text: 'Announcement to all' }],
});
```

### Narrowcast (audience-targeted)

```typescript
await client.narrowcast({
  messages: [{ type: 'text', text: 'Targeted offer' }],
  recipient: { type: 'audience', audienceGroupId: 1234567890 },
  filter: {
    demographic: {
      type: 'operator',
      and: [
        { type: 'age', gte: 'age_25', lt: 'age_40' },
        { type: 'gender', oneOf: ['female'] },
      ],
    },
  },
});
```

## Audience Management

```typescript
// Create upload audience
await client.createUploadAudienceGroup({
  description: 'VIP Customers Bangkok',
  audiences: [{ id: 'U1234...' }, { id: 'U5678...' }],
});

// Click audience — auto-created when URL is tracked
// Impression audience — users who opened a message
// Rich menu audience — based on rich menu interactions
```

## Group/Room Bot Behavior

- Enable "Allow bot to join group chats" in Messaging API settings
- Webhook includes `source.groupId` or `source.roomId`
- Can reply and push to groups using groupId/roomId
- Cannot multicast to group chats
- Events: `join`, `leave`, `memberJoined`, `memberLeft`

## Insight API

```typescript
// Message delivery stats
const delivery = await client.getMessageDelivery({ date: '20260404' });

// Follower stats
const followers = await client.getFollowers({ date: '20260404' });

// Custom aggregation units
await client.pushMessage({
  to: userId,
  messages: [...],
  customAggregationUnits: ['campaign_spring_2026'],
});
```
