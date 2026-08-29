# Payments & Integrations — LINE Pay, CRM, Loyalty, E-commerce

## LINE Pay API v3

### Payment Flow

**Normal flow (auto-capture):**
```
Reserve → User approves → Confirm (captures payment)
```

**Auth & Capture flow (pre-authorization):**
```
Reserve (capture=false) → User approves → Confirm (auth only) → Capture later
                                                               → or Void
```

### Request Signing (HMAC-SHA256)

All LINE Pay API v3 requests require HMAC signature:

```typescript
import crypto from 'crypto';

function signRequest(
  channelSecret: string,
  uri: string,
  body: string,
  nonce: string
): string {
  const message = channelSecret + uri + body + nonce;
  return crypto
    .createHmac('SHA256', channelSecret)
    .update(message)
    .digest('base64');
}

// Headers:
// X-LINE-ChannelId: {channelId}
// X-LINE-Authorization: {signature}
// X-LINE-Authorization-Nonce: {nonce}
// Content-Type: application/json
```

### Reserve Payment

```typescript
const nonce = crypto.randomUUID();
const body = JSON.stringify({
  amount: 1480,
  currency: 'THB',
  orderId: 'ORDER-12345',
  packages: [
    {
      id: 'pkg-001',
      amount: 1480,
      name: 'ร้าน ABC Shop',
      products: [
        { name: 'เสื้อยืด', quantity: 2, price: 295 },
        { name: 'กางเกง', quantity: 1, price: 890 },
      ],
    },
  ],
  redirectUrls: {
    confirmUrl: 'https://example.com/pay/confirm',
    cancelUrl: 'https://example.com/pay/cancel',
  },
  options: {
    display: { locale: 'th' },
    payment: {
      capture: true, // false for pre-auth
    },
  },
});

const response = await axios.post(
  'https://api-pay.line.me/v3/payments/request',
  body,
  {
    headers: {
      'Content-Type': 'application/json',
      'X-LINE-ChannelId': LINE_PAY_CHANNEL_ID,
      'X-LINE-Authorization': signRequest(LINE_PAY_SECRET, '/v3/payments/request', body, nonce),
      'X-LINE-Authorization-Nonce': nonce,
    },
  }
);

// Redirect user to response.data.info.paymentUrl.web (or .app for LINE app)
```

### Confirm Payment

```typescript
const transactionId = req.query.transactionId;
const confirmBody = JSON.stringify({
  amount: 1480,
  currency: 'THB',
});

const confirmUri = `/v3/payments/${transactionId}/confirm`;
const nonce = crypto.randomUUID();

await axios.post(
  `https://api-pay.line.me${confirmUri}`,
  confirmBody,
  {
    headers: {
      'X-LINE-ChannelId': LINE_PAY_CHANNEL_ID,
      'X-LINE-Authorization': signRequest(LINE_PAY_SECRET, confirmUri, confirmBody, nonce),
      'X-LINE-Authorization-Nonce': nonce,
    },
  }
);
```

### Recurring Payments (Auto Pay)

```typescript
// Initial payment with PREAPPROVED
const reserveBody = {
  // ... standard fields ...
  options: {
    payment: { payType: 'PREAPPROVED' },
  },
};

// After confirm, receive regKey
const { regKey } = confirmResponse.data.info;

// Subsequent charges:
await axios.post(
  `https://api-pay.line.me/v3/payments/preapproved/${regKey}/payment`,
  JSON.stringify({
    productName: 'Monthly Subscription',
    amount: 299,
    currency: 'THB',
    orderId: 'SUB-2026-04',
  }),
  { headers: signedHeaders },
);

// Check status
await axios.get(`https://api-pay.line.me/v3/payments/preapproved/${regKey}/check`);

// Cancel subscription
await axios.post(`https://api-pay.line.me/v3/payments/preapproved/${regKey}/expire`);
```

### Refund

```typescript
await axios.post(
  `https://api-pay.line.me/v3/payments/${transactionId}/refund`,
  JSON.stringify({ refundAmount: 590 }), // partial refund; omit for full
  { headers: signedHeaders },
);
```

### Thailand Payment Landscape

LINE Pay is available as **Rabbit LINE Pay** in Thailand. Common alternatives:

| Provider | Type | Integration |
|---|---|---|
| Rabbit LINE Pay | Mobile wallet | LINE Pay API v3 |
| PromptPay | QR payment | Generate QR via bank API |
| Omise (Opn) | Payment gateway | Cards, PromptPay, TrueMoney |
| 2C2P | Payment gateway | Cards, mobile banking, installments |
| GB Prime Pay | Payment gateway | Cards, QR, e-wallets |
| SCB Easy | Bank transfer | SCB Open Banking API |
| KBank | Bank transfer | K PLUS API |

### LIFF + Payment Integration Pattern

```typescript
// In LIFF app: product selection → payment
async function checkout(cart: CartItem[]) {
  const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  // Call your backend to create payment
  const res = await fetch('/api/payments/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${liff.getAccessToken()}`,
    },
    body: JSON.stringify({ items: cart, total }),
  });

  const { paymentUrl } = await res.json();

  // Redirect to LINE Pay (or open in external browser)
  if (liff.isInClient()) {
    liff.openWindow({ url: paymentUrl, external: true });
  } else {
    window.location.href = paymentUrl;
  }
}
```

---

## CRM Integration

### LINE OA + CRM Data Flow

```
LINE Webhook Events → Your Server → CRM System
├── follow event     → Create/update contact
├── message event    → Log conversation
├── postback event   → Track interactions
├── LIFF activity    → Track behavior
└── purchase event   → Update customer value
```

### HubSpot Integration

```typescript
import { Client as HubSpotClient } from '@hubspot/api-client';

const hubspot = new HubSpotClient({ accessToken: HUBSPOT_TOKEN });

async function syncLineUserToHubSpot(lineUserId: string, profile: any) {
  // Search for existing contact by LINE user ID
  const search = await hubspot.crm.contacts.searchApi.doSearch({
    filterGroups: [{
      filters: [{
        propertyName: 'line_user_id',
        operator: 'EQ',
        value: lineUserId,
      }],
    }],
    properties: ['line_user_id', 'firstname', 'lastname', 'email'],
  });

  if (search.results.length > 0) {
    // Update existing contact
    await hubspot.crm.contacts.basicApi.update(search.results[0].id, {
      properties: {
        line_display_name: profile.displayName,
        line_picture_url: profile.pictureUrl,
        line_last_active: new Date().toISOString(),
      },
    });
  } else {
    // Create new contact
    await hubspot.crm.contacts.basicApi.create({
      properties: {
        line_user_id: lineUserId,
        line_display_name: profile.displayName,
        firstname: profile.displayName,
        line_picture_url: profile.pictureUrl,
        lifecyclestage: 'subscriber',
      },
    });
  }
}

// Log LINE conversation as HubSpot engagement
async function logConversation(contactId: string, message: string) {
  await hubspot.crm.objects.notes.basicApi.create({
    properties: {
      hs_note_body: `[LINE] ${message}`,
      hs_timestamp: new Date().toISOString(),
    },
    associations: [{
      to: { id: contactId },
      types: [{ associationCategory: 'HUBSPOT_DEFINED', associationTypeId: 202 }],
    }],
  });
}
```

### Salesforce Integration

```typescript
import jsforce from 'jsforce';

const conn = new jsforce.Connection({ loginUrl: 'https://login.salesforce.com' });
await conn.login(SF_USERNAME, SF_PASSWORD + SF_SECURITY_TOKEN);

async function syncToSalesforce(lineUserId: string, profile: any) {
  // Upsert contact using LINE user ID as external ID
  await conn.sobject('Contact').upsert(
    {
      LINE_User_ID__c: lineUserId,
      LINE_Display_Name__c: profile.displayName,
      LINE_Picture_URL__c: profile.pictureUrl,
      LastName: profile.displayName,
      Description: 'Synced from LINE OA',
    },
    'LINE_User_ID__c', // external ID field
  );
}
```

### Custom CRM Database Schema

```sql
-- Core user table
CREATE TABLE line_users (
    id              SERIAL PRIMARY KEY,
    line_user_id    VARCHAR(64) UNIQUE NOT NULL,
    display_name    VARCHAR(128),
    picture_url     VARCHAR(512),
    is_following    BOOLEAN DEFAULT TRUE,
    followed_at     TIMESTAMP,
    unfollowed_at   TIMESTAMP,
    linked_account  VARCHAR(128),
    tags            JSONB DEFAULT '[]',
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Conversation history
CREATE TABLE conversations (
    id              SERIAL PRIMARY KEY,
    line_user_id    VARCHAR(64) REFERENCES line_users(line_user_id),
    direction       VARCHAR(10) NOT NULL, -- 'inbound' | 'outbound'
    message_type    VARCHAR(20) NOT NULL,
    content         JSONB NOT NULL,
    webhook_event_id VARCHAR(64) UNIQUE, -- for deduplication
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Rich menu interactions
CREATE TABLE rich_menu_events (
    id              SERIAL PRIMARY KEY,
    line_user_id    VARCHAR(64) REFERENCES line_users(line_user_id),
    action_data     VARCHAR(512),
    rich_menu_id    VARCHAR(64),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- User segments / tags
CREATE TABLE user_tags (
    line_user_id    VARCHAR(64) REFERENCES line_users(line_user_id),
    tag             VARCHAR(100),
    added_at        TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (line_user_id, tag)
);

-- Indexes
CREATE INDEX idx_line_users_following ON line_users(is_following);
CREATE INDEX idx_conversations_user ON conversations(line_user_id, created_at DESC);
CREATE INDEX idx_user_tags_tag ON user_tags(tag);
```

---

## Loyalty Programs

### Point System

```typescript
// Point accumulation on purchase
async function addPoints(lineUserId: string, purchaseAmount: number) {
  const pointsEarned = Math.floor(purchaseAmount / 25); // 1 point per 25 THB

  await db.transaction(async (tx) => {
    // Add points
    await tx.query(
      `UPDATE loyalty_members SET points = points + $1, total_spend = total_spend + $2
       WHERE line_user_id = $3`,
      [pointsEarned, purchaseAmount, lineUserId],
    );

    // Check tier upgrade
    const member = await tx.query(
      'SELECT total_spend, tier FROM loyalty_members WHERE line_user_id = $1',
      [lineUserId],
    );

    const newTier = calculateTier(member.total_spend);
    if (newTier !== member.tier) {
      await tx.query(
        'UPDATE loyalty_members SET tier = $1 WHERE line_user_id = $2',
        [newTier, lineUserId],
      );
      // Update rich menu for new tier
      await client.linkRichMenuIdToUser(lineUserId, TIER_MENUS[newTier]);
    }
  });

  // Send confirmation
  await client.pushMessage({
    to: lineUserId,
    messages: [{
      type: 'flex',
      altText: `ได้รับ ${pointsEarned} แต้ม`,
      contents: buildPointsFlexMessage(pointsEarned, member.points + pointsEarned),
    }],
  });
}

function calculateTier(totalSpend: number): string {
  if (totalSpend >= 100000) return 'Platinum';
  if (totalSpend >= 50000) return 'Gold';
  if (totalSpend >= 20000) return 'Silver';
  return 'Bronze';
}
```

### Digital Stamp Card

```typescript
async function addStamp(lineUserId: string, storeId: string) {
  const card = await db.getActiveStampCard(lineUserId, storeId);

  if (!card) {
    // Create new stamp card
    await db.createStampCard(lineUserId, storeId, { totalSlots: 10, stamps: 1 });
  } else if (card.stamps + 1 >= card.totalSlots) {
    // Card complete — issue reward
    await db.completeStampCard(card.id);
    await issueReward(lineUserId, card.rewardType);

    await client.pushMessage({
      to: lineUserId,
      messages: [{
        type: 'flex',
        altText: 'สะสมครบแล้ว! รับของรางวัล',
        contents: buildRewardFlexMessage(card.rewardType),
      }],
    });
  } else {
    // Add stamp
    await db.addStampToCard(card.id);
  }
}
```

### Per-User Rich Menu by Tier

```typescript
const TIER_MENUS: Record<string, string> = {
  Bronze: 'richmenu-bronze-id',
  Silver: 'richmenu-silver-id',
  Gold: 'richmenu-gold-id',
  Platinum: 'richmenu-platinum-id',
};

// On follow event or tier change:
async function assignTierMenu(lineUserId: string) {
  const member = await db.getLoyaltyMember(lineUserId);
  const tier = member?.tier ?? 'Bronze';
  await client.linkRichMenuIdToUser(lineUserId, TIER_MENUS[tier]);
}
```

---

## E-commerce Integration

### Order Tracking Push Messages

```typescript
async function notifyOrderStatus(lineUserId: string, order: Order) {
  const statusMessages: Record<string, string> = {
    confirmed: 'คำสั่งซื้อได้รับการยืนยันแล้ว',
    shipped: 'สินค้าถูกจัดส่งแล้ว',
    delivered: 'สินค้าถูกจัดส่งถึงแล้ว',
    cancelled: 'คำสั่งซื้อถูกยกเลิก',
  };

  await client.pushMessage({
    to: lineUserId,
    messages: [{
      type: 'flex',
      altText: statusMessages[order.status],
      contents: {
        type: 'bubble',
        body: {
          type: 'box',
          layout: 'vertical',
          contents: [
            { type: 'text', text: statusMessages[order.status], weight: 'bold', size: 'lg' },
            { type: 'text', text: `Order #${order.id}`, size: 'sm', color: '#999999', margin: 'sm' },
            ...(order.trackingNumber ? [
              { type: 'separator', margin: 'md' },
              { type: 'text', text: `Tracking: ${order.trackingNumber}`, size: 'sm', margin: 'md' },
              { type: 'text', text: `ขนส่ง: ${order.carrier}`, size: 'sm', color: '#666666' },
            ] : []),
          ],
        },
        footer: order.trackingUrl ? {
          type: 'box',
          layout: 'vertical',
          contents: [{
            type: 'button',
            action: { type: 'uri', label: 'ติดตามพัสดุ', uri: order.trackingUrl },
            style: 'primary',
          }],
        } : undefined,
      },
    }],
  });
}
```

### Thai Logistics Integration

| Carrier | API | Tracking URL Pattern |
|---|---|---|
| Kerry Express | RESTful API | `https://th.kerryexpress.com/th/track/?track={trackingNo}` |
| Flash Express | RESTful API | `https://flashexpress.com/tracking?se={trackingNo}` |
| Thailand Post | EMS API | `https://track.thailandpost.co.th/?trackNumber={trackingNo}` |
| J&T Express | RESTful API | `https://www.jtexpress.co.th/service/track?bills={trackingNo}` |
| Shopee Express | Via Shopee API | Via Shopee seller center |

---

## Healthcare / Appointment Booking

### Appointment Flow

```typescript
// LIFF-based appointment booking
async function bookAppointment(data: {
  lineUserId: string;
  department: string;
  doctorId: string;
  date: string;
  time: string;
}) {
  // Create appointment in HIS
  const appointment = await hospitalAPI.createAppointment(data);

  // Send confirmation
  await client.pushMessage({
    to: data.lineUserId,
    messages: [{
      type: 'flex',
      altText: 'ยืนยันการนัดหมาย',
      contents: buildAppointmentConfirmFlex({
        hospital: 'โรงพยาบาล ABC',
        department: data.department,
        doctor: appointment.doctorName,
        date: data.date,
        time: data.time,
        appointmentId: appointment.id,
      }),
    }],
  });

  // Schedule reminder 1 day before
  await scheduleMessage(data.lineUserId, {
    sendAt: dayBefore(data.date),
    message: buildReminderFlex(appointment),
  });
}
```

---

## Multichannel Strategy

### Unified Identity Pattern

```
Website (email/password)  ←→  LINE Login (userId)  ←→  Mobile App
                           ↓
                     Unified Customer ID
                           ↓
                     Single Customer View (CDP)
```

### Cross-Channel Messaging

```typescript
// Cart abandonment: website → LINE push
async function handleCartAbandonment(customerId: string) {
  const customer = await db.getCustomer(customerId);
  if (!customer.lineUserId || !customer.isFollowing) return;

  const cart = await db.getCart(customerId);
  if (cart.items.length === 0) return;

  await client.pushMessage({
    to: customer.lineUserId,
    messages: [{
      type: 'flex',
      altText: 'สินค้ารอคุณอยู่ในตะกร้า!',
      contents: buildCartReminderFlex(cart.items),
    }],
  });
}
```

### Thai Market Examples

| Company | Channels | Integration |
|---|---|---|
| Central Group | CentralOnline + App + LINE OA | The 1 loyalty across all |
| AIS | AIS App + LINE OA + Website | Unified customer view |
| CP ALL (7-Eleven) | App + LINE (ALL Member) + In-store | Points across channels |
| SCB | SCB Easy + LINE OA + Website | Banking notifications |
| Siam Cement Group | B2B LINE OA + Dealer portal + App | Dealer engagement |

### Thai-Specific Platform Services

| Platform | Description |
|---|---|
| Zwiz.AI | Thai AI chatbot + CRM for LINE |
| PRIMO | LINE-focused CRM platform |
| Carely | Healthcare LINE CRM |
| Amity Solutions | Enterprise LINE + CRM |
| QueQ | Queue management via LINE |
| LINE MAN Wongnai | Food delivery + LINE ecosystem |
| MyShop by LINE | Built-in e-commerce for LINE OA |
