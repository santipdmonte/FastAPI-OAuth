### FastAPI OAuth Template

A minimal, production-ready FastAPI template focused on authentication you can build on top of. It ships with email magic-link login, Google OAuth (OIDC), JWT access tokens, and a simple user model backed by SQLAlchemy.

Use this as a starting point for your next API or full‑stack app.

---

## Features

- **Email magic link**: Request a sign-in link via SMTP; verify to receive a JWT access token
- **Google OAuth (OIDC)**: Login with Google, then receive a JWT access token
- **JWT auth utilities**: Token creation, validation, current user dependencies
- **User and Social Accounts**: SQLAlchemy models with relationships and service layer
- **SQLite by default**: Configurable via `DATABASE_URL` (Postgres, etc.)
- **Typed Pydantic schemas** and clear FastAPI routers

---

## Tech Stack

- **API**: FastAPI, Starlette
- **Auth**: PyJWT, Authlib (Google OAuth)
- **DB/ORM**: SQLAlchemy 2.x
- **Validation**: Pydantic v2
- **Mail**: SMTP (TLS), optional HTML template
- **ASGI**: Uvicorn

---

## Getting Started

### Prerequisites

- Python 3.10+
- A Google OAuth client (optional, for Google login)
- SMTP credentials (for magic-link flow)

### Setup

1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Configure environment

Create a `.env` file in the project root with at least the following variables:

```bash
# Core
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Email magic-link
EMAIL_TOKEN_EXPIRE_MINUTES=10
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=you@example.com
SMTP_PASSWORD=your-app-password
SMTP_REPLY_TO=support@example.com
# Public base URL of your API (used to build the magic link in emails)
URL=http://localhost:8000

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Database (defaults to local SQLite test.db if unset)
# Examples:
# DATABASE_URL=sqlite:///./test.db
# DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/dbname
```

Note: The app reads environment variables via `os.getenv(...)`. If you prefer auto-loading `.env`, you can add the following early in your app startup (e.g., in `main.py`) or run with a dotenv runner.

```python
from dotenv import load_dotenv
load_dotenv()
```

4) Run the server

```bash
uvicorn main:app --reload
```

By default, tables are created on startup using SQLAlchemy metadata. The API is available at `http://localhost:8000` and the interactive docs at `http://localhost:8000/docs`.

---

## Auth Flows

### Email Magic Link

1) Request a login link

```http
POST /auth/login
Content-Type: application/json

{
  "email": "you@example.com"
}
```

2) Click the link in the email. It hits:

```http
GET /auth/email/verify-token/?token=...  ->  { "access_token": "...", "token_type": "bearer" }
```

3) Use the returned access token for authenticated endpoints with the `Authorization: Bearer <token>` header.

Notes:
- Email HTML template (optional): place an HTML file at `static/template/magin-link.html` with a `{{ link }}` placeholder. If missing, a minimal fallback HTML is used.
- The public base URL used in the email is taken from `URL`.

### Google OAuth (OIDC)

1) Configure OAuth client in Google Cloud Console
- Authorized redirect URI: `http://localhost:8000/auth/google/callback` (adjust for your deployment)

2) Start the flow:

```http
GET /auth/google/login  -> redirects to Google
GET /auth/google/callback -> returns { "access_token": "...", "token_type": "bearer" }
```

3) Use the token for subsequent requests via `Authorization: Bearer <token>`.

---

## API Overview

- `POST /auth/login` — Send magic-link to email
- `GET /auth/email/verify-token/` — Exchange emailed token for access token
- `GET /auth/google/login` — Begin Google OAuth
- `GET /auth/google/callback` — OAuth callback; returns access token
- `GET /users/` — List active users
- `GET /users/me/` — Get current user (auth required)
- `PATCH /users/me/` — Update current user (auth required)
- `GET /users/me/social-accounts/` — List linked social accounts (auth required)

The app uses Bearer tokens. Include `Authorization: Bearer <JWT>` for protected endpoints.

---

## Project Structure

```text
FastAPI-OAuth/
  main.py                 # App entry, mounts routers and session middleware
  database.py             # Engine/session and table creation
  dependencies.py         # DB session dependency
  models/                 # SQLAlchemy models (User, UserSocialAccount)
  schemas/                # Pydantic schemas (UserBase, UserUpdate, etc.)
  services/               # UserService (CRUD & auth provider processing)
  routes/                 # FastAPI routers (auth, users)
  utils/                  # Auth/JWT/email helpers and Google OAuth router
  requirements.txt        # Pinned dependencies
  test.db                 # Default SQLite DB (dev)
```

Routers define their own prefixes (e.g., `/auth`, `/users`).

---

## Extending

- Add providers: extend `AuthProviderType` and implement the provider flow in `services/users_services.py`
- Add fields: update SQLAlchemy models in `models/` and corresponding Pydantic schemas in `schemas/`
- Swap DB: set `DATABASE_URL` to Postgres/MySQL and ensure the driver is installed
- Session middleware: requires `SECRET_KEY` to be set

---

## Production Tips

- Use a strong `SECRET_KEY` and rotate regularly
- Serve behind a reverse proxy (HTTPS), set a correct public `URL`
- Configure a real SMTP provider and domain
- Consider a migration tool (Alembic is included) for schema changes
- Prefer a managed database (e.g., Postgres) for reliability

---

## License

MIT — see `LICENSE` for details.

