# CareLife

CareLife is a web platform for organization verification, childcare enrollment and attendance, caregiver profiles, and donation campaign management.

## Repository layout

- `backend/` — FastAPI API, application use cases, domain entities, PostgreSQL repositories, and Alembic migrations.
- `frontend/` — React and Vite web application.
- `docs/` — development notes and configuration guidance.
- `.github/workflows/backend-ci.yml` — backend tests and frontend lint/build checks.

## Requirements

- Python 3.14
- Node.js 22 and npm
- PostgreSQL 18

## Run the backend

1. Open a terminal in `backend/`.
2. Create and activate a virtual environment:
   - Windows PowerShell: `python -m venv .venv`, then `.\.venv\Scripts\Activate.ps1`
   - macOS/Linux: `python -m venv .venv`, then `source .venv/bin/activate`
3. Install dependencies: `python -m pip install -r requirements-dev.txt`.
4. Copy `.env.example` to `.env` and set a valid PostgreSQL `DATABASE_URL` plus a `SECRET_KEY` of at least 32 characters.
5. Run migrations: `alembic upgrade head`.
6. Start the API: `uvicorn main:app --reload`.

The API is available at `http://127.0.0.1:8000`; interactive API documentation is at `http://127.0.0.1:8000/docs`.

## Run the frontend

In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Vite normally serves the frontend at `http://localhost:5173`. Set `VITE_API_BASE_URL` in `frontend/.env` if the API is hosted somewhere other than `http://127.0.0.1:8000`.

## Configuration notes

- Set `CORS_ORIGINS` in `backend/.env` to a JSON array of trusted frontend origins, for example `["http://localhost:5173"]`.
- Set `RESET_LINK_BASE_URL` to the frontend's reset-password page. The development default is `http://localhost:5173/reset-password`.
- `EMAIL_MODE=console` logs reset links for development. Configure SMTP before using email-based resets outside a development environment.
- Never commit a real `.env`, production secret, or SMTP credential.

## Checks

Run the backend suite from `backend/`:

```bash
python -m pytest -q
python -m compileall -q app main.py alembic/versions tests
```

Run the frontend checks from `frontend/`:

```bash
npm run lint
npm run build
```

Pull requests run backend tests/migrations and frontend lint/build checks in GitHub Actions. See [Development Guide](docs/development.md) for more details.
