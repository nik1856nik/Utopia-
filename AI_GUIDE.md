# Utopia Codebase Guide

Compact orientation for an AI assistant working in this repository. Treat the code as the source of truth; `README.md` is product/feature documentation and can drift.

## What this is

Utopia is a Chennai public-works transparency and operations web app. Citizens browse projects and submit questions/grievances. Authenticated admins and department officers manage works, coordination conflicts, and grievances. Field supervisors submit progress and site reports.

## Stack and startup

- Frontend: React + TypeScript + Vite, in `frontend/`. The application is largely one large file: `frontend/src/App.tsx` (UI, route selection, API calls, types, and page components). `main.tsx` mounts React Query and BrowserRouter; `style.css` contains styling.
- Backend: FastAPI + SQLAlchemy, in `backend/app/`. `main.py` registers routers and initializes the database and seed data.
- Persistence is PostgreSQL only. Outside Compose, configure `DATABASE_URL` with the `postgresql+psycopg://` driver; Compose passes PostgreSQL connection fields and the app safely builds its URL. Database files live in the `pgdata` volume. `JWT_SECRET` is required by Compose.
- `docker compose -f compose.yml up --build -d` starts PostgreSQL, the API, and Nginx. Nginx serves the built SPA on port `5174` and proxies `/api` to the API on port `8001`. Compose handles build, start, stop, restart, status, and logs; Compose Watch plus optional environment settings provide the development reload workflow.
- Dependencies: `backend/requirements.txt`, `frontend/package.json`.

## Runtime request flow

1. Browser loads `frontend/src/main.tsx` → `App.tsx`. `App.tsx` selects screens from `window.location.pathname` (it uses conditional route logic, despite BrowserRouter being mounted).
2. Frontend `fetchApi()` in `App.tsx` prefixes requests with `VITE_API_URL` or `/api`, adds the saved bearer token when present, and throws on non-2xx responses.
3. FastAPI in `backend/app/main.py` dispatches to modular routers. Routers validate request data with Pydantic schemas, use `get_db()` for a SQLAlchemy session, and call models/services.
4. SQLAlchemy models persist business data. Startup creates tables, applies best-effort legacy column additions (`ensure_columns`), and seeds demo records.
5. JSON responses are rendered/used by frontend components; mutations generally trigger local state updates or refresh queries/data.

## Frontend navigation and auth

Path selection is in `App.tsx` around `is*Route` flags and the main view router:

- `/` and `/citizen`: public map/discovery and project details.
- `/login`, `/municipality/login`, `/department/login`, `/onsite/login`: login selection and role-specific login screens.
- `/admin`, `/municipal`, `/municipality/dashboard`: municipality dashboard aliases.
- `/department`, `/department/dashboard`: department workspace; `/department/create-project` and `/official/create-project`: project creation.
- `/onsite/dashboard`: field supervisor workspace.

Login calls `POST /api/auth/login`; token and user are kept in localStorage (`utopia_token`, legacy `civicgrid_token`). `fetchApi()` attaches the bearer token. Backend authorization lives in `services/auth.py` and router checks; do not rely on frontend role visibility as security enforcement.

## Backend map

All router paths below are under `/api` unless noted.

| Area | Router / service | Main responsibilities |
|---|---|---|
| Application setup | `main.py`, `database.py`, `config.py` | FastAPI app, CORS, DB lifecycle, demo officer accounts, health endpoint |
| Projects and statistics | `routers/projects.py`, `schemas/project.py` | Public search/detail/stats; authenticated creation, updates, event history |
| Identity | `routers/auth.py`, `services/auth.py`, `schemas/auth.py` | Demo credential lookup, JWT issue/validation, current-user dependency |
| Citizen issues | `routers/issues.py`, `schemas/issue.py` | Questions/grievances, official replies, department routing/SLA fields |
| Coordination | `routers/conflicts.py`, `services/digsync.py`, `schemas/conflict.py` | Detect project overlaps, tickets, arbitration, rescheduling |
| Field operations | `routers/onsite.py`, `schemas/field.py` | Supervisor projects and submissions; official review/status |
| Geocoding | `routers/geocode.py`, `services/geocoding.py` | PIN lookup and coordinate reverse geocoding via OpenStreetMap Nominatim; reverse results are cached and public requests are serialized to respect service rate limits |
| Broadcasts | `routers/broadcasts.py`, `schemas/broadcast.py` | PIN-scoped advisory dispatch simulation and audit log |
| Persistence | `models/*.py` | SQLAlchemy tables: projects/events, issues, conflict tickets, field submissions, SMS logs |
| Demo data | `services/seeder.py` | Seeds projects and related demo content on startup |

Router modules are registered centrally in `routers/__init__.py` and included by `main.py`. Schemas serialize/validate API payloads; models define persisted state; services hold reusable logic.

## Core domain workflow

```text
Public projects ← Project/Event records ← department creates/updates work
       ↑                                      ↓
citizen issue/question → Issue ← official reply / grievance triage
                                              
project schedules → DigSync conflict scan → ConflictTicket
                                      → admin resolves or department reschedules

field supervisor → FieldSubmission → department/admin review
```

- A `Project` is the central record; its `Event`s provide timeline history. Project status, progress, milestone step, due/revised dates, location, and department drive most screens.
- `Issue` represents citizen feedback, questions, and grievances. It can link to a project and store department, reply, status, and timing data.
- Conflict detection is in `services/digsync.py`; ticket lifecycle and role checks are in `routers/conflicts.py`.
- `FieldSubmission` records field activity (progress, photo, blocker, work log, or delay); status review is a separate operation.
- `SMSLog` stores broadcast history. External messaging/geocoding integrations may be simulated, cached, or fall back; inspect the service before assuming a live provider exists.

## Where to look first

- Understand a screen or frontend behavior: search `App.tsx` for the pathname, component label, API endpoint, or `fetchApi` call. The file is very large; use `rg -n` and inspect a narrow range.
- Understand an endpoint: router → its schema → model/service. Find registrations in `main.py`.
- Change authorization: inspect both `services/auth.py` and the endpoint’s explicit role/department checks in the router.
- Change DB fields: update model definitions and PostgreSQL migration compatibility in `ensure_columns()`.
- Change demo state: `services/seeder.py` (note startup seeding may make demo data reappear).
- API docs at runtime: `/docs`; health endpoint: `/api/health`.

## Working conventions / cautions

- Use backend authorization as the security boundary. Department-scoped rules must be enforced server-side on every mutation and sensitive read.
- Database startup rejects missing or non-PostgreSQL database configuration. Tests use a disposable PostgreSQL connection and create/drop a unique schema per test; never point test configuration at a production database.
- Current location uses the browser Geolocation API (requires HTTPS/localhost and user permission). Coordinates call `/api/geocode/reverse`, which resolves locality and Indian PIN through Nominatim. If GPS is blocked or Nominatim fails, the UI asks the user to enter a PIN; there is no IP geolocation endpoint.
- The frontend currently concentrates domain logic in `App.tsx`; avoid assuming a separate API client, page directory, or generated route tree.
- The README lists intended features and demo credentials; verify the exact implementation in code before documenting or extending behavior.
- No dedicated frontend test suite is evident from the source tree. `scratch/test_acceptance.py` is an API acceptance script; inspect its setup before running it.
