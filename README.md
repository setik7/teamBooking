# TeamBooking - Sports Team Booking App

Sports team members book training sessions (swim, run, gym, etc.), manage prepaid subscriptions with token-based credits, and pay via Stripe.

## Tech Stack

- **Frontend**: React 19 + Vite + React Router 7 + TanStack React Query 5 + Axios
- **Backend**: Python FastAPI + SQLAlchemy (async) + SQLite
- **Auth**: OAuth2 (Google + GitHub) via authlib + JWT
- **Payments**: Stripe sandbox (Checkout Sessions + Webhooks)
- **Security**: OWASP headers, rate limiting, input sanitization, audit logging

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt

# Copy and fill in OAuth + Stripe credentials
# Edit .env with your values

# Seed the database
python -m seed_data

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Environment Variables (.env)

```
DATABASE_URL=sqlite+aiosqlite:///./teamBooking.db
JWT_SECRET=your-secret-key
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...

STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## Token Economy

| Action | Effect |
|--------|--------|
| Book with subscription | -1 training remaining |
| Cancel subscribed booking | +1 token |
| Book extra with token | -1 token (status: token_used) |
| Cancel token booking | +1 token refund |
| Monthly renewal | Reset trainings, tokens carry over |

## Plans

| Plan | Trainings/month | Price |
|------|----------------|-------|
| Starter | 8 | €49 |
| Standard | 12 | €69 |
| Unlimited | 999 | €99 |

## API Endpoints

### Auth
- `GET /auth/login/{provider}` - Start OAuth flow
- `GET /auth/callback/{provider}` - OAuth callback
- `GET /auth/me` - Current user info
- `POST /auth/logout` - Logout

### Activities & Slots
- `GET /activities` - List all activities
- `GET /slots/week?week_start=YYYY-MM-DD` - Weekly slot schedule

### Bookings
- `POST /bookings` - Book a training
- `DELETE /bookings/{id}` - Cancel a booking
- `GET /bookings/mine` - My bookings

### Subscriptions
- `GET /subscriptions/me` - My subscription
- `GET /subscriptions/tokens/history` - Token transaction history

### Payments
- `POST /checkout/subscribe?plan_id=X` - Start subscription checkout
- `POST /checkout/tokens?amount=X` - Buy token pack
- `POST /stripe/webhook` - Stripe webhook handler

## Running Tests

```bash
cd backend
pytest tests/ -v
```

### Penetration Tests

```bash
cd backend/tests/pentest
bash run_pentest.sh http://localhost:8000
```

## Project Structure

```
teamBooking/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + middleware
│   │   ├── config.py            # Settings from .env
│   │   ├── database.py          # Async SQLAlchemy
│   │   ├── db/models.py         # 9 ORM models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   ├── auth/                # JWT + dependencies
│   │   ├── middleware/          # Security middleware
│   │   └── security/           # Audit log + validators
│   ├── tests/                   # pytest suite
│   ├── seed_data.py             # DB seeder
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Routes + layout
│   │   ├── pages/               # Page components
│   │   ├── components/          # UI components
│   │   ├── contexts/            # Auth context
│   │   ├── hooks/               # Custom hooks
│   │   └── services/api.js      # Axios client
│   └── package.json
└── README.md
```
