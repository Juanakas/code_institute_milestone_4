# Stripe Test Product/Price + Webhook Checklist

## 1) Create Product + Monthly Price in Stripe (Test Mode)

1. Open Stripe Dashboard (test mode on).
2. Create Product: `Bachata Club Membership`.
3. Create recurring monthly price (for example €19.99/month).
4. Copy the generated `price_...` ID.

## 2) Update Local Environment

In `.env`, set:
- `STRIPE_PUBLIC_KEY=pk_test_...`
- `STRIPE_SECRET_KEY=sk_test_...`
- `STRIPE_WEBHOOK_SECRET=` (optional blank for local JSON test)

## 3) Update Django Admin Plan

1. Login to `/admin/`.
2. Open `Subscription plans`.
3. Edit `Monthly Membership`.
4. Paste the real `price_...` into `stripe_price_id`.
5. Save.

## 4) Checkout Flow Test (Browser)

1. Register/login as a normal user.
2. Go to `/subscriptions/` and click Subscribe.
3. Complete checkout with Stripe test card:
   - `4242 4242 4242 4242`
   - Any future expiry, any CVC, any ZIP.
4. Confirm you land on `/subscriptions/success/`.

## 5) Webhook Test Commands

### Option A: Stripe CLI (recommended)

```bash
stripe login
stripe listen --forward-to http://127.0.0.1:8000/subscriptions/webhook/
```

Copy the `whsec_...` value from CLI output into `.env` as `STRIPE_WEBHOOK_SECRET`, restart server.

Then trigger test events:

```bash
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated
stripe trigger customer.subscription.deleted
```

### Option B: Local unsigned JSON webhook test (no Stripe CLI)

Keep `STRIPE_WEBHOOK_SECRET=` blank in `.env`, then run:

```bash
curl -X POST http://127.0.0.1:8000/subscriptions/webhook/ \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"customer.subscription.updated\",\"data\":{\"object\":{\"id\":\"sub_local_test\",\"customer\":\"cus_local_test\",\"status\":\"active\",\"current_period_end\":2000000000}}}"
```

## 6) Verify Membership Access

1. Check `/subscriptions/status/` shows `Active`.
2. Open `/members/` and confirm access is granted.
3. If user is canceled/past_due, verify access is blocked and redirected to `/subscriptions/`.
