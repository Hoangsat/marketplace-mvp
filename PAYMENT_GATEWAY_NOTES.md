# Payment Gateway Integration Notes

This project uses a **mock checkout** (`status: "paid_mock"`).  
Below are concise notes on how to replace it with a real Vietnamese payment gateway.

---

## Where to Make Changes

### Backend
- **`routers/orders.py`** → `POST /orders/checkout`  
  Replace the immediate `paid_mock` status with a payment intent creation.

### Frontend
- **`app/checkout/page.tsx`**  
  Replace the "Place Order" button with a redirect to the payment gateway's payment URL.

---

## Option 1: PayOS

**Website:** https://payos.vn  
**Docs:** https://docs.payos.vn

### Steps
1. Register at payos.vn, get `clientId`, `apiKey`, `checksumKey`
2. Install the Python SDK: `pip install pypayos`
3. In `routers/orders.py`:
   - Create the order in DB with `status="pending"`
   - Call `payos.create_payment_link(...)` to get a `checkoutUrl`
   - Return the `checkoutUrl` to the frontend instead of the order object
4. Frontend redirects user to `checkoutUrl`
5. PayOS calls your **webhook** (`POST /orders/payos-webhook`) on success
6. In the webhook handler: verify signature, set `order.status = "paid"`, deduct stock

```python
# Example: backend/routers/orders.py
from payos import PayOS
payos = PayOS(client_id=..., api_key=..., checksum_key=...)

payment_data = payos.create_payment_link(PaymentData(
    orderCode=order.id,
    amount=int(order.total),
    description=f"Order #{order.id}",
    returnUrl="http://localhost:3000/orders",
    cancelUrl="http://localhost:3000/cart",
))
return {"checkout_url": payment_data.checkoutUrl}
```

---

## Option 2: VNPay

**Website:** https://vnpay.vn  
**Sandbox docs:** https://sandbox.vnpayment.vn/apis/

### Steps
1. Register for a sandbox account, get `vnp_TmnCode` and `vnp_HashSecret`
2. No official Python SDK — build the HMAC-SHA512 URL manually (see docs)
3. Create order with `status="pending"`, generate the VNPay redirect URL
4. Return URL to frontend, redirect user
5. Handle `GET /orders/vnpay-return` (VNPay query params) to confirm payment

```python
# Key parameters to include in the VNPay URL:
# vnp_Amount (in VND × 100), vnp_TxnRef (order ID), vnp_SecureHash (HMAC-SHA512)
```

---

## Option 3: MoMo

**Website:** https://business.momo.vn  
**Docs:** https://developers.momo.vn

### Steps
1. Register, get `partnerCode`, `accessKey`, `secretKey`
2. `POST https://test-payment.momo.vn/v2/gateway/api/create` to create payment
3. MoMo returns a `payUrl` — redirect user there
4. MoMo sends an **IPN (webhook)** to your backend on completion
5. Verify HMAC-SHA256 signature, update `order.status = "paid"`

---

## General Pattern (same for all gateways)

```
Browser → POST /orders/checkout (create pending order)
        ← { checkout_url: "https://gateway.com/pay/..." }

Browser → redirect to checkout_url

Gateway → user pays

Gateway → POST /orders/webhook (IPN)
Backend → verify signature → update order status → deduct stock

Gateway → redirect user to returnUrl (/orders)
```

---

## Environment Variables to Add (backend/.env)

```bash
# PayOS
PAYOS_CLIENT_ID=your_client_id
PAYOS_API_KEY=your_api_key
PAYOS_CHECKSUM_KEY=your_checksum_key

# VNPay
VNPAY_TMN_CODE=your_tmn_code
VNPAY_HASH_SECRET=your_hash_secret
VNPAY_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html

# MoMo
MOMO_PARTNER_CODE=your_partner_code
MOMO_ACCESS_KEY=your_access_key
MOMO_SECRET_KEY=your_secret_key
```
