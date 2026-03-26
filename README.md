# MarketPy

A simple two-sided marketplace MVP built with **FastAPI** (backend) + **Next.js 15** (frontend).

---

## Project Structure

```
marketplace-mvp/
├── backend/     FastAPI app (Python)
└── frontend/    Next.js 15 app (TypeScript + Tailwind)
```

---

## Prerequisites

- Python 3.11+ and `pip`
- Node.js 18+ and `npm`
- A terminal (PowerShell, bash, etc.)

---

## 1. Backend Setup

```bash
cd backend
```

**Create and activate a virtual environment:**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Configure environment variables:**

```bash
# Copy example and edit as needed
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
```

**Run the backend:**

```bash
uvicorn main:app --reload
```

Backend runs at: **http://localhost:8000**  
Interactive API docs: **http://localhost:8000/docs**

---

## 2. Frontend Setup

```bash
cd frontend
```

**Install dependencies:**

```bash
npm install
```

**Configure environment variables:**

```bash
# Windows
copy .env.local.example .env.local
# macOS/Linux
cp .env.local.example .env.local
```

The `.env.local` should contain:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Run the frontend:**

```bash
npm run dev
```

Frontend runs at: **http://localhost:3000**

---

## 3. Running Both Together

Open two terminals:

| Terminal | Command |
|---|---|
| Terminal 1 (backend) | `cd backend && uvicorn main:app --reload` |
| Terminal 2 (frontend) | `cd frontend && npm run dev` |

---

## 4. Available Routes

### Buyer
| Route | Description |
|---|---|
| `/` | Product catalog with search + filter |
| `/products/[id]` | Product detail + Add to cart |
| `/cart` | Shopping cart |
| `/checkout` | Mock checkout |
| `/orders` | Order history |

### Seller
| Route | Description |
|---|---|
| `/seller/dashboard` | My products list |
| `/seller/products/new` | Create product |
| `/seller/products/[id]/edit` | Edit product |
| `/seller/orders` | Sales (own product order items) |

### Auth
| Route | Description |
|---|---|
| `/login` | Login |
| `/register` | Register (optional: register as seller) |

---

## 5. Mock Checkout Notes

The checkout flow is intentionally mocked — no real payment processing occurs. Orders are created with status `paid_mock` immediately.

See `PAYMENT_GATEWAY_NOTES.md` for how to integrate real Vietnamese payment gateways (PayOS, VNPay, MoMo) when you're ready.

---

## 6. Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy, SQLite, JWT (python-jose), bcrypt |
| Frontend | Next.js 15 (App Router), TypeScript, Tailwind CSS |
| Auth | JWT stored in `localStorage` |
| Cart | `localStorage` (client-side only) |
| DB | SQLite (file: `backend/marketpy.db`) |
