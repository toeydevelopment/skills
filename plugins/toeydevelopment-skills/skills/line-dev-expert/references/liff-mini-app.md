# LIFF & LINE Mini App — Init, APIs, React/Next.js, Testing

## LIFF v2 Overview

LIFF (LINE Front-end Framework) lets you build web apps that run inside LINE. LINE Mini App is the certified version with additional features (service messages, discoverability). New projects should target LINE Mini App.

## LIFF App Sizes

| Size | Height | Use Case |
|---|---|---|
| **Compact** | ~50% screen | Quick actions, confirmations |
| **Tall** | ~75% screen | Forms, lists |
| **Full** | 100% screen | Complex UIs, web apps |

- Size is set in LINE Developers Console, not in code
- In external browsers, size is irrelevant (always full viewport)
- Users can swipe down to close Compact/Tall views

## Initialization

```typescript
import liff from '@line/liff';

await liff.init({
  liffId: '1234567890-AbCdEfGh',
  withLoginOnExternalBrowser: true, // auto-redirect to login in external browsers
});
```

## Core APIs

### Profile & Identity

```typescript
// User profile (network request)
const profile = await liff.getProfile();
// { userId, displayName, pictureUrl, statusMessage }

// Access token (for calling your backend)
const token = liff.getAccessToken(); // string | null

// ID token (JWT — verify server-side)
const idToken = liff.getIDToken(); // string | null

// Decoded ID token (no network request — from JWT)
const decoded = liff.getDecodedIDToken();
// { iss, sub, aud, exp, iat, name, picture, email }

// Friendship status (has user added the bot?)
const friendship = await liff.getFriendship();
// { friendFlag: boolean }
```

### Context & Environment

```typescript
const context = liff.getContext();
// { type, viewType, userId, utouId, roomId, groupId }
// type: 'utou' | 'room' | 'group' | 'square_chat' | 'external' | 'none'

liff.getOS();         // 'ios' | 'android' | 'web'
liff.getLanguage();   // 'th', 'en', 'ja', etc.
liff.isInClient();    // true if inside LINE app
liff.isLoggedIn();    // true if user is logged in
liff.isApiAvailable('shareTargetPicker'); // check API support
```

### Messaging

```typescript
// Send messages to current chat (in-app only)
await liff.sendMessages([
  { type: 'text', text: 'Hello from LIFF!' },
  { type: 'flex', altText: 'Flex', contents: { /* ... */ } },
]);

// Share to friends/groups (works in both in-app and external)
if (liff.isApiAvailable('shareTargetPicker')) {
  const result = await liff.shareTargetPicker(
    [{ type: 'flex', altText: 'Share', contents: { /* ... */ } }],
    { isMultiple: true }, // allow selecting multiple targets
  );
  // result.status === 'success' means picker was shown (not that message was sent)
}
```

### Utilities

```typescript
// QR/Barcode scanner (in-app only)
const { value } = await liff.scanCodeV2();

// Open URL
liff.openWindow({ url: 'https://example.com', external: true });

// Close LIFF window (in-app only)
liff.closeWindow();

// Permanent link
const link = liff.permanentLink.createUrlBy('https://example.com/myapp/page');
// Returns: https://liff.line.me/{liffId}/page

// Login / Logout
liff.login({ redirectUri: window.location.href, scope: 'profile openid email' });
liff.logout();
```

## External Browser vs In-App Behavior

| Feature | In-App | External Browser |
|---|---|---|
| `isInClient()` | `true` | `false` |
| `getContext()` | Full context | `type: 'external'` only |
| `sendMessages()` | Works | Not available |
| `shareTargetPicker()` | Works | Works (opens LINE app) |
| `scanCodeV2()` | Works | Not available |
| `closeWindow()` | Closes overlay | No effect |
| Login | Automatic | Requires redirect |
| LIFF size | Compact/Tall/Full | Full viewport |

### Handling Both Environments

```typescript
await liff.init({ liffId: LIFF_ID });

if (!liff.isLoggedIn()) {
  liff.login({ redirectUri: window.location.href });
  return;
}

const profile = await liff.getProfile();

if (liff.isInClient()) {
  // In-app: send messages, use scanner
  await liff.sendMessages([{ type: 'text', text: 'Done!' }]);
  liff.closeWindow();
} else {
  // External: show result in UI
  showSuccessUI();
}
```

## LIFF URL Scheme

```
# Universal Link (recommended)
https://liff.line.me/{liffId}
https://liff.line.me/{liffId}/path?query=value

# Deep linking: extra path/query appended to endpoint URL
# LIFF endpoint: https://example.com/myapp
# User opens:    https://liff.line.me/{liffId}/products/123
# Loads:         https://example.com/myapp/products/123
```

## Authentication Flow

### In-App Flow
```
User taps LIFF link → LINE opens LIFF → liff.init()
  → First time: Channel Consent Screen
  → Access token + profile available immediately
```

### External Browser Flow
```
User opens LIFF URL → liff.init() → isLoggedIn() === false
  → liff.login() → LINE Login page → User authenticates
  → Redirect back → liff.init() resolves on reload
```

### Server-Side ID Token Verification

```typescript
// Frontend: send ID token to backend
const idToken = liff.getIDToken();
await fetch('/api/verify', {
  headers: { Authorization: `Bearer ${idToken}` },
});

// Backend: verify via LINE API
const response = await axios.post(
  'https://api.line.me/oauth2/v2.1/verify',
  new URLSearchParams({
    id_token: idToken,
    client_id: channelId,
  }),
);
// response.data: { iss, sub, aud, exp, iat, name, picture, email }
```

**CRITICAL: Never trust userId from the frontend. Always verify the ID token server-side.**

## Next.js / React Integration

### LiffProvider (App Router)

```tsx
// app/providers.tsx
'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import type { Liff } from '@line/liff';

interface LiffContextType {
  liff: Liff | null;
  error: string | null;
  isLoggedIn: boolean;
  isInClient: boolean;
  profile: { userId: string; displayName: string; pictureUrl?: string } | null;
}

const LiffContext = createContext<LiffContextType>({
  liff: null, error: null, isLoggedIn: false, isInClient: false, profile: null,
});

export function LiffProvider({ children, liffId }: { children: ReactNode; liffId: string }) {
  const [liffObj, setLiffObj] = useState<Liff | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState<LiffContextType['profile']>(null);

  useEffect(() => {
    // Dynamic import to avoid SSR issues — LIFF requires browser
    import('@line/liff').then(({ default: liff }) => {
      liff
        .init({ liffId, withLoginOnExternalBrowser: true })
        .then(async () => {
          setLiffObj(liff);
          if (liff.isLoggedIn()) {
            const p = await liff.getProfile();
            setProfile(p);
          }
        })
        .catch((err) => setError(err.message));
    });
  }, [liffId]);

  return (
    <LiffContext.Provider
      value={{
        liff: liffObj,
        error,
        isLoggedIn: liffObj?.isLoggedIn() ?? false,
        isInClient: liffObj?.isInClient() ?? false,
        profile,
      }}
    >
      {children}
    </LiffContext.Provider>
  );
}

export const useLiff = () => useContext(LiffContext);
```

```tsx
// app/layout.tsx
import { LiffProvider } from './providers';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th">
      <body>
        <LiffProvider liffId={process.env.NEXT_PUBLIC_LIFF_ID!}>
          {children}
        </LiffProvider>
      </body>
    </html>
  );
}
```

```tsx
// app/page.tsx
'use client';
import { useLiff } from './providers';

export default function Home() {
  const { liff, profile, isLoggedIn, error } = useLiff();

  if (error) return <div>Error: {error}</div>;
  if (!liff) return <div>Loading...</div>;

  return (
    <div>
      {profile && (
        <>
          <img src={profile.pictureUrl} alt={profile.displayName} />
          <p>สวัสดี, {profile.displayName}!</p>
        </>
      )}
    </div>
  );
}
```

### Performance Tips

```typescript
// 1. Lazy load LIFF only when needed
const liff = (await import('@line/liff')).default;

// 2. Use getDecodedIDToken() over getProfile() when possible (no network request)
const decoded = liff.getDecodedIDToken();
const name = decoded?.name;

// 3. Cache profile in sessionStorage
const cached = sessionStorage.getItem('liff-profile');
if (cached) return JSON.parse(cached);
const profile = await liff.getProfile();
sessionStorage.setItem('liff-profile', JSON.stringify(profile));

// 4. Check environment before loading feature-specific code
if (liff.isInClient()) {
  // Only import scanner module in LINE app
}
```

### Error Handling

```typescript
import liff, { LiffError } from '@line/liff';

try {
  await liff.init({ liffId: LIFF_ID });
} catch (error) {
  if (error instanceof LiffError) {
    switch (error.code) {
      case 'INIT_FAILED':     // Invalid LIFF ID or network error
      case 'INVALID_ARGUMENT': // Bad arguments
      case 'UNAUTHORIZED':     // Channel status issue
      case 'FORBIDDEN':        // Permission denied
        break;
    }
  }
}

// Graceful API fallback
async function safeShare(messages: any[]) {
  if (!liff.isApiAvailable('shareTargetPicker')) {
    await navigator.clipboard.writeText(window.location.href);
    alert('ลิงก์ถูกคัดลอกแล้ว! แชร์ให้เพื่อนได้เลย');
    return;
  }
  await liff.shareTargetPicker(messages);
}
```

## LINE Mini App

### Differences from LIFF

| Aspect | LINE Mini App | LIFF |
|---|---|---|
| Review | Requires certification | No review |
| Service messages | Can send to "Mini App Notice" | Not available |
| Header | Always shows action button | Module mode hides header |
| Channels | Auto-creates 3 (Dev/Review/Published) | Single channel |
| Discovery | Discoverable in LINE app | Direct link only |

### Service Messages

- Verified Mini Apps can send notification messages to a dedicated chat room
- Templates organized by category (reservations, queue, delivery)
- Max 20 templates per channel
- Service notification token expires after 1 year, max 5 messages per token
- **Prohibited:** advertisements and promotions (confirmations/responses only)

### Key 2025-2026 Updates

- LIFF and LINE Mini App being unified under "LINE MINI App" brand
- Thailand/Taiwan: unverified Mini Apps can now be published (March 2026)
- In-app purchase feature released for Mini Apps (February 2026, Japan first)

## Common Thailand Use Cases

### Member Card (LIFF)

```tsx
function MemberCard({ profile, membership }) {
  return (
    <div className="member-card">
      <img src={profile.pictureUrl} className="avatar" />
      <h2>{profile.displayName}</h2>
      <p>Member #{membership.id}</p>
      <div className="points">
        <span className="value">{membership.points.toLocaleString()}</span>
        <span className="label">แต้มสะสม</span>
      </div>
      <QRCode value={membership.id} size={200} />
      <p className="tier">{membership.tier} Member</p>
    </div>
  );
}
```

### Registration Form (Pre-filled from LINE)

```tsx
function RegistrationForm() {
  const { liff, profile } = useLiff();
  const [formData, setFormData] = useState({
    name: profile?.displayName ?? '',
    phone: '',
    email: '',
    lineUserId: profile?.userId ?? '',
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await fetch('/api/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${liff.getAccessToken()}`,
      },
      body: JSON.stringify(formData),
    });

    if (liff.isInClient()) {
      await liff.sendMessages([{ type: 'text', text: 'ลงทะเบียนสำเร็จ!' }]);
      liff.closeWindow();
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>ชื่อ-นามสกุล</label>
      <input value={formData.name} onChange={...} />
      <label>เบอร์โทรศัพท์</label>
      <input type="tel" pattern="[0-9]{10}" placeholder="08X-XXX-XXXX" />
      <label>อีเมล</label>
      <input type="email" />
      <button type="submit">ลงทะเบียน</button>
    </form>
  );
}
```

### Event Check-in with QR Scanner

```typescript
async function handleCheckIn() {
  if (!liff.isInClient()) {
    alert('กรุณาเปิดใน LINE เพื่อใช้สแกนเนอร์');
    return;
  }

  const { value: ticketId } = await liff.scanCodeV2();

  const res = await fetch('/api/checkin', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${liff.getAccessToken()}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ ticketId }),
  });

  if (res.ok) {
    await liff.sendMessages([{ type: 'text', text: 'เช็คอินสำเร็จ!' }]);
    liff.closeWindow();
  }
}
```

## Testing

### @line/liff-mock

```typescript
import liff from '@line/liff';
import { LiffMockPlugin } from '@line/liff-mock';

if (process.env.NODE_ENV === 'development') {
  liff.use(new LiffMockPlugin());
}

await liff.init({ liffId: 'your-liff-id', mock: true });
// All LIFF APIs return mock data without LINE app
```

### Jest Mock

```typescript
// __mocks__/@line/liff.ts
const liffMock = {
  init: jest.fn().mockResolvedValue(undefined),
  isLoggedIn: jest.fn().mockReturnValue(true),
  isInClient: jest.fn().mockReturnValue(true),
  getOS: jest.fn().mockReturnValue('ios'),
  getLanguage: jest.fn().mockReturnValue('th'),
  isApiAvailable: jest.fn().mockReturnValue(true),
  login: jest.fn(),
  logout: jest.fn(),
  getAccessToken: jest.fn().mockReturnValue('mock-token'),
  getIDToken: jest.fn().mockReturnValue('mock-id-token'),
  getDecodedIDToken: jest.fn().mockReturnValue({
    sub: 'U1234567890abcdef',
    name: 'Test User',
    picture: 'https://example.com/avatar.png',
  }),
  getProfile: jest.fn().mockResolvedValue({
    userId: 'U1234567890abcdef',
    displayName: 'Test User',
    pictureUrl: 'https://example.com/avatar.png',
  }),
  getFriendship: jest.fn().mockResolvedValue({ friendFlag: true }),
  getContext: jest.fn().mockReturnValue({ type: 'utou', viewType: 'full' }),
  sendMessages: jest.fn().mockResolvedValue(undefined),
  shareTargetPicker: jest.fn().mockResolvedValue({ status: 'success' }),
  scanCodeV2: jest.fn().mockResolvedValue({ value: 'SCANNED-123' }),
  openWindow: jest.fn(),
  closeWindow: jest.fn(),
  permanentLink: { createUrlBy: jest.fn().mockReturnValue('https://liff.line.me/mock/path') },
  use: jest.fn(),
};
export default liffMock;
```

### LIFF Inspector

- Official DevTools for LIFF apps (Chrome DevTools Protocol)
- Available in LIFF SDK v2.19.0+
- Install as LIFF Plugin, use `--inspect` with `liff serve`
- Requires HTTPS (use ngrok)

### Local Development with ngrok

```bash
# Start local server
npm run dev  # http://localhost:3000

# Create HTTPS tunnel
ngrok http 3000

# Set ngrok URL as:
# - Webhook URL in LINE Developers Console
# - LIFF endpoint URL
```
