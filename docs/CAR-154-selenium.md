# CAR-154 — Selenium regression testing

## Scope

The browser suite targets the **deployed CareLife frontend** and does not modify frontend application source. The deployed URL defaults to `https://carelife-web.onrender.com`; override it whenever the frontend is hosted at a different URL.

## Coverage

- Homepage renders and the primary hero is visible.
- Signup form fields, role choices and native required-field validation.
- Login form renders and the Forgot password link opens the reset form.
- Daycare, orphanage and elderly-care module landing pages load for a signed-out visitor.
- Daycare directory, elderly-care directory, caregiver directory and orphanage support board are tested for public access.
- Optional admin sign-in test runs only when a dedicated E2E test account is supplied.
- Screenshot and HTML evidence are saved for failing browser tests; CI uploads evidence and a JUnit report.

## Run locally (PowerShell)

From the repository's `backend` directory:

```powershell
python -m pip install -r requirements-test.txt
$env:CARELIFE_E2E_BASE_URL = "https://carelife-web.onrender.com"
$env:CARELIFE_HEADLESS = "true"
New-Item -ItemType Directory -Force test-results | Out-Null
python -m pytest -q tests/e2e --junitxml=test-results/e2e-results.xml
```

For the optional admin test, set `CARELIFE_E2E_EMAIL` and `CARELIFE_E2E_PASSWORD` to a **dedicated test account**. Do not commit credentials. In GitHub Actions, configure those as repository secrets. Configure `CARELIFE_E2E_BASE_URL` as a repository variable if the live frontend URL differs from the default.

## Known frontend blocker to report, not change in this branch

The source in `frontend/src/lib/roles.js` currently lists `#daycare-directory`, `#elderly-care-directory`, `#caregivers`, and `#orphanage-support` as protected routes. The product information-architecture document describes these as public discovery/support pages. Because CAR-154 is testing-only and frontend code must not be changed in this branch, the Selenium tests report this as a failure rather than changing the application.

### Prompt to use for the frontend fix in a separate task

> Fix the CareLife frontend route-access configuration only. The public daycare directory (`#daycare-directory`), elderly-care directory (`#elderly-care-directory`), caregiver directory (`#caregivers`), and orphanage support board (`#orphanage-support`) should render for visitors who are not signed in, as documented in `docs/frontend-information-architecture.md`. Remove the frontend sign-in gate for viewing those public pages while keeping sign-in required for personal payment history, submitting authenticated pledges/bookings, messaging, private child/resident data, and all other protected actions. Do not weaken backend role-based authorization, do not expose private records, do not change the Selenium tests to hide the issue, and add/adjust frontend route tests for signed-out access.

## CI behavior

The workflow runs on pushes to `tasnim/selenium`, can be started manually, and runs when a PR targeting `dev` or `main` changes the Selenium suite, its test dependency file, workflow, or this document. It uses headless Chrome against the deployed site and uploads `test-results` even if a test fails.
