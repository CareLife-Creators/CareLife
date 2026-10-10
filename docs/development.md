# Development Guide

## Architecture

The backend follows a layered structure:

- **Presentation** contains FastAPI routes and request/response handling.
- **Application** contains use cases, schemas, and repository interfaces.
- **Domain** contains business entities and role/context rules.
- **Infrastructure** contains PostgreSQL access, SQLAlchemy models, email delivery, and repository implementations.
- **Core** contains shared configuration and security utilities.

Keep business rules in application/domain code rather than duplicating them in API routes. Reuse existing modules when their responsibilities already fit instead of creating parallel implementations.

## Local configuration

Copy `backend/.env.example` to `backend/.env`. Configure:

- `DATABASE_URL`: PostgreSQL connection string.
- `SECRET_KEY`: a secret of at least 32 characters.
- `CORS_ORIGINS`: JSON array of allowed frontend origins. For local Vite development, use `["http://localhost:5173"]`.
- `RESET_LINK_BASE_URL`: the frontend reset-password page; local default is `http://localhost:5173/reset-password`.
- `EMAIL_MODE`: `console` for local development or `smtp` after SMTP settings are configured.

When testing password reset locally in console email mode, read the generated reset link from the backend log. The frontend reset page sends the supplied token to the backend confirmation endpoint; reset tokens are time-limited and single-use.

## Migration and test workflow

From `backend/`:

```bash
alembic upgrade head
python -m pytest -q
python -m compileall -q app main.py alembic/versions tests
python -m pip check
```

From `frontend/`:

```bash
npm ci
npm run lint
npm run build
```

The GitHub Actions workflow runs the backend suite against PostgreSQL and checks frontend lint/build on pushes and pull requests. Continue to use a feature/fix branch and PR into `dev`; promote `dev` to `main` only through a separate reviewed PR.

## Security note

The current frontend stores the access token in `localStorage`, which can be read by JavaScript running in the page. Treat this as a known limitation, avoid injecting untrusted HTML, and consider an HttpOnly, Secure, SameSite cookie-based session design as a separate security improvement before production deployment.
