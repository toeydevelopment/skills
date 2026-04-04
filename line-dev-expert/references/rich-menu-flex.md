# Rich Menu & Flex Messages — Design, Switching, Layouts

## Rich Menu

Rich Menus are the persistent bottom menu in LINE chats — the primary navigation for Thai LINE bots.

### Creating Rich Menu via API

```typescript
// Step 1: Create rich menu object
const richMenu = await client.createRichMenu({
  size: { width: 2500, height: 1686 }, // or 843 for compact
  selected: true, // show by default
  name: 'Main Menu',
  chatBarText: 'เมนู',
  areas: [
    {
      bounds: { x: 0, y: 0, width: 833, height: 843 },
      action: { type: 'message', text: 'สินค้า' },
    },
    {
      bounds: { x: 833, y: 0, width: 834, height: 843 },
      action: { type: 'postback', data: 'action=catalog&page=1' },
    },
    {
      bounds: { x: 1667, y: 0, width: 833, height: 843 },
      action: { type: 'uri', uri: 'https://liff.line.me/{liffId}/help' },
    },
    {
      bounds: { x: 0, y: 843, width: 833, height: 843 },
      action: {
        type: 'richmenuswitch',
        richMenuAliasId: 'settings-menu',
        data: 'switch=settings',
      },
    },
    {
      bounds: { x: 833, y: 843, width: 834, height: 843 },
      action: { type: 'message', text: 'โปรโมชั่น' },
    },
    {
      bounds: { x: 1667, y: 843, width: 833, height: 843 },
      action: { type: 'message', text: 'ติดต่อเรา' },
    },
  ],
});

// Step 2: Upload image (2500x1686 or 2500x843, JPEG/PNG, < 1MB)
await client.setRichMenuImage(richMenu.richMenuId, imageBuffer, 'image/png');

// Step 3: Set as default for all users
await client.setDefaultRichMenu(richMenu.richMenuId);
```

### Image Specifications

| Size | Dimensions | Layout | Use Case |
|---|---|---|---|
| Large | 2500 x 1686 px | 6 areas (2 rows x 3) | Feature-rich bots |
| Compact | 2500 x 843 px | 3 areas (1 row x 3) | Simple bots |

- Format: JPEG or PNG
- Max file size: 1 MB
- Max tap areas: 20

### Per-User Rich Menus

Assign different menus based on user state, tier, or language:

```typescript
// Link specific rich menu to user
await client.linkRichMenuIdToUser(userId, richMenuId);

// Unlink (user falls back to default)
await client.unlinkRichMenuIdFromUser(userId);

// Bulk link (up to 500 users)
await client.linkRichMenuIdToUsers(richMenuId, [userId1, userId2]);
```

**Common per-user patterns in Thailand:**
- Membership tiers: Bronze/Silver/Gold/Platinum menus
- Language: Thai/English menus based on preference
- State: Logged-in vs guest menus
- Role: Customer vs agent menus

### Rich Menu Tab Switching

Use `richmenuswitch` action with aliases for seamless tab navigation (no server round-trip):

```typescript
// Create aliases
await client.createRichMenuAlias({
  richMenuAliasId: 'main-menu',
  richMenuId: 'richmenu-xxx-main',
});

await client.createRichMenuAlias({
  richMenuAliasId: 'settings-menu',
  richMenuId: 'richmenu-xxx-settings',
});

// In rich menu areas:
{
  "type": "richmenuswitch",
  "richMenuAliasId": "settings-menu",
  "data": "tab=settings"
}
```

### Rich Menu Action Types

| Action | Description |
|---|---|
| `message` | Sends text message |
| `postback` | Sends data to webhook |
| `uri` | Opens URL (LIFF URLs work) |
| `richmenuswitch` | Switches to another rich menu |
| `datetimepicker` | Opens date/time picker |
| `clipboard` | Copies text to clipboard |

### Design Best Practices (Thailand)

- Use Thai text with clear icons (2-3 words max per button)
- Use brand colors with sufficient contrast
- Common Thai menu items: สินค้า, โปรโมชั่น, สั่งซื้อ, ติดต่อเรา, สถานะ, คูปอง
- 6-panel layout is standard: Home, Member Card, Coupons, Order, History, Settings
- Design with accessibility in mind — large tap targets, readable text

---

## Flex Messages

Flex Messages are LINE's most powerful message type — fully custom JSON-based layouts (the "HTML/CSS of LINE messages").

### Structure Hierarchy

```
FlexMessage
  └── FlexContainer (bubble or carousel)
        └── FlexBubble
              ├── header  (box) — optional
              ├── hero    (image/video) — optional
              ├── body    (box) — main content
              └── footer  (box) — optional, actions
                    └── FlexComponent
                          ├── box (layout container)
                          ├── text
                          ├── image
                          ├── icon
                          ├── button
                          ├── separator
                          ├── filler
                          ├── span
                          └── video
```

### Receipt / Order Confirmation (Thai)

```json
{
  "type": "flex",
  "altText": "ใบเสร็จรับเงิน",
  "contents": {
    "type": "bubble",
    "header": {
      "type": "box",
      "layout": "vertical",
      "contents": [
        { "type": "text", "text": "ใบเสร็จรับเงิน", "weight": "bold", "size": "xl", "color": "#1DB446" }
      ]
    },
    "body": {
      "type": "box",
      "layout": "vertical",
      "contents": [
        { "type": "text", "text": "ร้าน ABC Shop", "weight": "bold", "size": "lg" },
        { "type": "separator", "margin": "md" },
        {
          "type": "box", "layout": "horizontal", "margin": "md",
          "contents": [
            { "type": "text", "text": "เสื้อยืด x2", "flex": 3, "size": "sm" },
            { "type": "text", "text": "฿590", "flex": 1, "size": "sm", "align": "end" }
          ]
        },
        {
          "type": "box", "layout": "horizontal", "margin": "sm",
          "contents": [
            { "type": "text", "text": "กางเกง x1", "flex": 3, "size": "sm" },
            { "type": "text", "text": "฿890", "flex": 1, "size": "sm", "align": "end" }
          ]
        },
        { "type": "separator", "margin": "md" },
        {
          "type": "box", "layout": "horizontal", "margin": "md",
          "contents": [
            { "type": "text", "text": "รวมทั้งหมด", "weight": "bold", "flex": 3 },
            { "type": "text", "text": "฿1,480", "weight": "bold", "flex": 1, "align": "end", "color": "#1DB446" }
          ]
        }
      ]
    },
    "footer": {
      "type": "box",
      "layout": "vertical",
      "contents": [
        {
          "type": "button",
          "action": { "type": "uri", "label": "ดูรายละเอียด", "uri": "https://example.com/receipt/123" },
          "style": "primary",
          "color": "#1DB446"
        }
      ]
    }
  }
}
```

### Product Carousel

```json
{
  "type": "flex",
  "altText": "สินค้าแนะนำ",
  "contents": {
    "type": "carousel",
    "contents": [
      {
        "type": "bubble",
        "hero": {
          "type": "image",
          "url": "https://example.com/product1.jpg",
          "size": "full",
          "aspectRatio": "20:13",
          "aspectMode": "cover",
          "action": { "type": "uri", "uri": "https://example.com/product/1" }
        },
        "body": {
          "type": "box",
          "layout": "vertical",
          "contents": [
            { "type": "text", "text": "เสื้อยืดคอกลม", "weight": "bold", "size": "lg" },
            {
              "type": "box", "layout": "baseline", "margin": "md",
              "contents": [
                { "type": "text", "text": "฿590", "weight": "bold", "size": "xl", "color": "#1DB446" },
                { "type": "text", "text": "฿790", "size": "sm", "color": "#999999", "decoration": "line-through", "margin": "sm" }
              ]
            }
          ]
        },
        "footer": {
          "type": "box",
          "layout": "vertical",
          "contents": [
            {
              "type": "button",
              "action": { "type": "postback", "label": "เพิ่มลงตะกร้า", "data": "action=addToCart&productId=1" },
              "style": "primary",
              "color": "#00B900"
            }
          ]
        }
      }
    ]
  }
}
```

### Coupon / Promotion Card

```json
{
  "type": "bubble",
  "hero": {
    "type": "image",
    "url": "https://example.com/coupon-banner.jpg",
    "size": "full",
    "aspectRatio": "20:13"
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      { "type": "text", "text": "ส่วนลด 50%", "weight": "bold", "size": "xxl", "color": "#FF0000" },
      { "type": "text", "text": "สำหรับสินค้าทุกชิ้น", "size": "md", "color": "#666666", "margin": "sm" },
      {
        "type": "box", "layout": "vertical", "margin": "lg",
        "backgroundColor": "#F5F5F5", "cornerRadius": "md", "paddingAll": "md",
        "contents": [
          { "type": "text", "text": "CODE: SAVE50", "weight": "bold", "size": "lg", "align": "center" }
        ]
      },
      { "type": "text", "text": "หมดอายุ: 30 เม.ย. 2569", "size": "xs", "color": "#999999", "margin": "md" }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "button",
        "action": { "type": "uri", "label": "ใช้คูปองเลย", "uri": "https://liff.line.me/{liffId}/coupon/123" },
        "style": "primary",
        "color": "#FF0000"
      },
      {
        "type": "button",
        "action": { "type": "uri", "label": "แชร์ให้เพื่อน", "uri": "https://liff.line.me/{liffId}/share/coupon/123" },
        "style": "secondary",
        "margin": "sm"
      }
    ]
  }
}
```

### Member Card

```json
{
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "backgroundColor": "#1A1A2E",
    "paddingAll": "xl",
    "contents": [
      {
        "type": "box", "layout": "horizontal",
        "contents": [
          {
            "type": "image",
            "url": "https://example.com/avatar.jpg",
            "size": "60px", "aspectRatio": "1:1", "aspectMode": "cover",
            "cornerRadius": "100px"
          },
          {
            "type": "box", "layout": "vertical", "margin": "lg",
            "contents": [
              { "type": "text", "text": "สมชาย ดีใจ", "color": "#FFFFFF", "weight": "bold", "size": "lg" },
              { "type": "text", "text": "Gold Member", "color": "#FFD700", "size": "sm" }
            ]
          }
        ]
      },
      {
        "type": "box", "layout": "horizontal", "margin": "xl",
        "contents": [
          {
            "type": "box", "layout": "vertical", "flex": 1,
            "contents": [
              { "type": "text", "text": "12,500", "color": "#FFFFFF", "weight": "bold", "size": "xxl", "align": "center" },
              { "type": "text", "text": "แต้มสะสม", "color": "#AAAAAA", "size": "xs", "align": "center" }
            ]
          }
        ]
      },
      {
        "type": "image",
        "url": "https://example.com/barcode/M12345.png",
        "size": "full", "aspectRatio": "3:1", "margin": "xl"
      },
      { "type": "text", "text": "Member ID: M12345", "color": "#AAAAAA", "size": "xs", "align": "center", "margin": "md" }
    ]
  }
}
```

### Flex Message Best Practices

1. **Always use Flex Message Simulator** — https://developers.line.biz/flex-simulator/
2. **Always set `altText`** — shows in notifications and on unsupported devices
3. **Max 12 bubbles** per carousel
4. **Keep JSON under 50 KB** per message, under 30 KB per bubble
5. **Make boxes tappable** — add `action` to container boxes, not just buttons
6. **Use `cornerRadius`** for modern card designs
7. **Use `backgroundColor`** on boxes for card-style layouts
8. **Test on both iOS and Android** — rendering may differ slightly
9. **Thai text:** use `size: "sm"` or larger for readability with Thai characters

### Dynamic Flex Message Builder (TypeScript)

```typescript
interface Product {
  name: string;
  price: number;
  imageUrl: string;
  productId: string;
}

function buildProductCarousel(products: Product[]): FlexCarousel {
  return {
    type: 'carousel',
    contents: products.map((p) => ({
      type: 'bubble',
      hero: {
        type: 'image',
        url: p.imageUrl,
        size: 'full',
        aspectRatio: '20:13',
        aspectMode: 'cover',
      },
      body: {
        type: 'box',
        layout: 'vertical',
        contents: [
          { type: 'text', text: p.name, weight: 'bold', size: 'lg' },
          { type: 'text', text: `฿${p.price.toLocaleString()}`, size: 'md', color: '#1DB446' },
        ],
      },
      footer: {
        type: 'box',
        layout: 'vertical',
        contents: [
          {
            type: 'button',
            action: {
              type: 'postback',
              label: 'สั่งซื้อ',
              data: `action=order&id=${p.productId}`,
            },
            style: 'primary',
            color: '#00B900',
          },
        ],
      },
    })),
  };
}
```
