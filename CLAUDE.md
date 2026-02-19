# TeamBooking Project Rules

## Overview
Sports team booking app - React 19 frontend + FastAPI backend with OAuth2, Stripe payments, and token-based booking economy.

## Commands
- **Backend**: `cd backend && uvicorn app.main:app --reload --port 8000`
- **Frontend**: `cd frontend && npm run dev`
- **Seed DB**: `cd backend && python -m seed_data`
- **Tests**: `cd backend && pytest tests/ -v`

## Architecture
- Backend: `backend/app/` (routers, services, db, schemas, auth, middleware, security)
- Frontend: `frontend/src/` (pages, components, hooks, contexts, services)
- Database: SQLite async via aiosqlite
- Auth: OAuth2 (Google/GitHub) + JWT tokens
- Payments: Stripe Checkout Sessions + Webhooks
