# LINE Login & Security — OAuth, Tokens, Signature Validation

## LINE Login v2.1 (OAuth 2.0 + OIDC)

### Authorization Code Flow

```
1. Redirect user to LINE authorization URL
   GET https://access.line.me/oauth2/v2.1/authorize
     ?response_type=code
     &client_id={channelId}
     &redirect_uri={callbackUrl}
     &state={csrfToken}          // REQUIRED — CSRF protection
     &scope=profile%20openid%20email
     &nonce={randomString}        // OIDC replay protection
     &prompt=consent              // force consent screen
     &bot_prompt=aggressive       // show friend-add prompt

2. User authenticates on LINE → redirected to callback with code

3. Exchange code for tokens
   POST https://api.line.me/oauth2/v2.1/token
   Content-Type: application/x-www-form-urlencoded

   grant_type=authorization_code
   &code={authCode}
   &redirect_uri={callbackUrl}
   &client_id={channelId}
   &client_secret={channelSecret}

   Response: {
     access_token, token_type, refresh_token, expires_in,
     scope, id_token (JWT)
   }

4. Verify ID token and extract user info
```

### Scopes

| Scope | Data |
|---|---|
| `profile` | userId, displayName, pictureUrl, statusMessage |
| `openid` | ID token (JWT) with user identity |
| `email` | Email address (in ID token) |

### ID Token (JWT) Claims

```json
{
  "iss": "https://access.line.me",
  "sub": "U1234567890abcdef",  // LINE userId
  "aud": "1234567890",          // channel ID
  "exp": 1625000000,
  "iat": 1624999000,
  "nonce": "random-nonce-value",
  "amr": ["linesso"],           // auth method: linesso, lineqr, pwd
  "name": "สมชาย ดีใจ",
  "picture": "https://profile.line-scdn.net/...",
  "email": "somchai@example.com"
}
```

### Node.js Implementation

```typescript
import express from 'express';
import axios from 'axios';
import jwt from 'jsonwebtoken';
import crypto from 'crypto';

const app = express();

// Step 1: Redirect to LINE Login
app.get('/auth/line', (req, res) => {
  const state = crypto.randomBytes(16).toString('hex');
  const nonce = crypto.randomBytes(16).toString('hex');

  // Store state and nonce in session for verification
  req.session.lineAuthState = state;
  req.session.lineAuthNonce = nonce;

  const authUrl = new URL('https://access.line.me/oauth2/v2.1/authorize');
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('client_id', process.env.LINE_CHANNEL_ID!);
  authUrl.searchParams.set('redirect_uri', process.env.LINE_CALLBACK_URL!);
  authUrl.searchParams.set('state', state);
  authUrl.searchParams.set('scope', 'profile openid email');
  authUrl.searchParams.set('nonce', nonce);
  authUrl.searchParams.set('bot_prompt', 'normal');

  res.redirect(authUrl.toString());
});

// Step 2: Handle callback
app.get('/auth/line/callback', async (req, res) => {
  const { code, state, error } = req.query;

  // Verify state (CSRF protection)
  if (state !== req.session.lineAuthState) {
    return res.status(403).send('Invalid state');
  }

  if (error) {
    return res.status(400).send(`Login failed: ${error}`);
  }

  // Exchange code for tokens
  const tokenResponse = await axios.post(
    'https://api.line.me/oauth2/v2.1/token',
    new URLSearchParams({
      grant_type: 'authorization_code',
      code: code as string,
      redirect_uri: process.env.LINE_CALLBACK_URL!,
      client_id: process.env.LINE_CHANNEL_ID!,
      client_secret: process.env.LINE_CHANNEL_SECRET!,
    }),
  );

  const { access_token, id_token } = tokenResponse.data;

  // Verify ID token
  const verifyResponse = await axios.post(
    'https://api.line.me/oauth2/v2.1/verify',
    new URLSearchParams({
      id_token,
      client_id: process.env.LINE_CHANNEL_ID!,
      nonce: req.session.lineAuthNonce!,
    }),
  );

  const lineUser = verifyResponse.data;
  // { sub: userId, name, picture, email }

  // Create/update user in your database
  const user = await upsertUser({
    lineUserId: lineUser.sub,
    displayName: lineUser.name,
    pictureUrl: lineUser.picture,
    email: lineUser.email,
  });

  // Set session
  req.session.userId = user.id;
  res.redirect('/dashboard');
});
```

## Channel Linking & Provider Strategy

### Same Provider = Same userId

- All channels under one Provider share the same userId for each user
- **Best practice:** Create one Provider for all your services
- Different Providers = different userIds for the same person

### Channel Types Under a Provider

```
Provider: "My Company"
├── LINE Login Channel     — for web/app authentication
├── Messaging API Channel  — for bot messaging
├── LINE Mini App Channel  — for LIFF/Mini App
└── LINE Pay Channel       — for payments
```

Users have the same userId across all channels under "My Company".

## Account Linking

Link LINE accounts to existing service accounts:

```typescript
// Step 1: Issue link token
const { linkToken } = await client.issueLinkToken(userId);

// Step 2: Send user to your login page with link token
await client.replyMessage({
  replyToken,
  messages: [{
    type: 'template',
    altText: 'เชื่อมต่อบัญชี',
    template: {
      type: 'buttons',
      text: 'กรุณาเชื่อมต่อบัญชีของคุณ',
      actions: [{
        type: 'uri',
        label: 'เชื่อมต่อบัญชี',
        uri: `https://example.com/link?token=${linkToken}`,
      }],
    },
  }],
});

// Step 3: User logs into your service
// Your server generates a nonce and redirects to:
// https://access.line.me/dialog/bot/accountLink?linkToken={token}&nonce={nonce}

// Step 4: Handle accountLink webhook event
app.post('/webhook', (req, res) => {
  for (const event of req.body.events) {
    if (event.type === 'accountLink') {
      const { nonce, result } = event.link;
      if (result === 'ok') {
        // Look up service account by nonce → link to event.source.userId
        linkAccounts(nonce, event.source.userId);
      }
    }
  }
});
```

## Token Management

### Token Types & Lifetimes

| Token | Lifetime | Use |
|---|---|---|
| Access token (user) | 30 days | Call LINE APIs on behalf of user |
| Refresh token (user) | 90 days after last access token | Renew access token |
| Channel access token (long-lived) | No expiry | Bot API calls (not recommended for production) |
| Channel access token v2.1 (JWT) | Custom, up to 30 days | Bot API calls (recommended) |
| Stateless channel access token | 15 minutes | Bot API calls (most secure) |

### Channel Access Token v2.1 (JWT-Based)

```typescript
import jwt from 'jsonwebtoken';
import axios from 'axios';
import fs from 'fs';

// Generate JWT assertion
const privateKey = fs.readFileSync('private_key.pem');
const assertion = jwt.sign(
  {
    iss: CHANNEL_ID,
    sub: CHANNEL_ID,
    aud: 'https://api.line.me/',
    exp: Math.floor(Date.now() / 1000) + 30 * 60, // 30 minutes
    token_exp: 60 * 60 * 24, // token valid for 1 day (seconds)
  },
  privateKey,
  { algorithm: 'RS256', keyid: KEY_ID },
);

// Exchange for channel access token
const response = await axios.post(
  'https://api.line.me/oauth2/v2.1/token',
  new URLSearchParams({
    grant_type: 'client_credentials',
    client_assertion_type: 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
    client_assertion: assertion,
  }),
);

const channelAccessToken = response.data.access_token;
// Use this token for MessagingApiClient
```

### Token Refresh

```typescript
async function refreshAccessToken(refreshToken: string): Promise<string> {
  const response = await axios.post(
    'https://api.line.me/oauth2/v2.1/token',
    new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: CHANNEL_ID,
      client_secret: CHANNEL_SECRET,
    }),
  );
  return response.data.access_token;
}
```

### Token Verification

```typescript
// Verify access token
const verify = await axios.get(
  `https://api.line.me/oauth2/v2.1/verify?access_token=${accessToken}`
);
// { scope, client_id, expires_in }

// Revoke token on logout
await axios.post(
  'https://api.line.me/oauth2/v2.1/revoke',
  new URLSearchParams({ access_token: accessToken, client_id: CHANNEL_ID, client_secret: CHANNEL_SECRET }),
);
```

## Webhook Signature Validation

### Algorithm: HMAC-SHA256

```
signature = Base64(HMAC-SHA256(channelSecret, rawRequestBody))
```

**Critical rules:**
- Use the **exact raw request body** — do NOT parse/re-serialize JSON
- Use `crypto.timingSafeEqual()` to prevent timing attacks
- If signature doesn't match, reject immediately (403)
- Do NOT rely on IP filtering — always validate signature
- Require TLS 1.2+ with a public CA certificate

### Express.js Pattern

```typescript
import crypto from 'crypto';
import express from 'express';

// MUST use raw body parser for signature validation
app.post('/webhook', express.raw({ type: '*/*' }), (req, res) => {
  const signature = req.headers['x-line-signature'] as string;
  const body = req.body; // Buffer

  const expectedSig = crypto
    .createHmac('SHA256', process.env.LINE_CHANNEL_SECRET!)
    .update(body)
    .digest('base64');

  if (!crypto.timingSafeEqual(Buffer.from(expectedSig), Buffer.from(signature))) {
    return res.status(403).end();
  }

  res.status(200).end();
  processEvents(JSON.parse(body.toString()));
});
```

## LIFF Security

### Never Trust Client-Side Data

```typescript
// BAD — userId can be spoofed on client
const profile = await liff.getProfile();
fetch('/api/action', { body: JSON.stringify({ userId: profile.userId }) });

// GOOD — verify ID token on server
const idToken = liff.getIDToken();
fetch('/api/action', {
  headers: { Authorization: `Bearer ${idToken}` },
});

// Server verifies:
const verified = await axios.post(
  'https://api.line.me/oauth2/v2.1/verify',
  new URLSearchParams({ id_token: idToken, client_id: CHANNEL_ID }),
);
const userId = verified.data.sub; // trusted userId
```

### ID Token Validation Checklist

1. Verify signature (if validating locally with public key)
2. `iss` must be `https://access.line.me`
3. `aud` must match your channel ID
4. `exp` must not be expired
5. `nonce` must match what you sent (if using nonce)

## PDPA Compliance (Thailand)

Thailand's Personal Data Protection Act requires:

1. **Explicit consent** — collect before processing LINE user data
2. **Purpose limitation** — only collect data for stated purposes
3. **Data retention policy** — define and enforce how long you keep data
4. **Right to erasure** — users can request deletion of their data
5. **Privacy policy** — disclose in LINE OA and LIFF apps
6. **Data breach notification** — notify within 72 hours
7. **Cross-border transfer** — ensure adequate protection for data sent overseas

### Implementation Pattern

```typescript
// Consent collection in LIFF before accessing data
async function checkAndCollectConsent(userId: string) {
  const consent = await db.getUserConsent(userId);
  if (!consent?.accepted) {
    // Show consent form
    const accepted = await showConsentDialog({
      purposes: ['ข้อมูลสมาชิก', 'โปรโมชั่น', 'วิเคราะห์พฤติกรรม'],
      privacyPolicyUrl: 'https://example.com/privacy',
    });

    if (accepted) {
      await db.saveConsent(userId, {
        acceptedAt: new Date(),
        purposes: ['membership', 'promotions', 'analytics'],
        version: '1.0',
      });
    } else {
      liff.closeWindow();
      return false;
    }
  }
  return true;
}
```
