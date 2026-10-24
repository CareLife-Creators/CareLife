# CAR-154 — Selenium regression testing

## Scope

The Selenium suite checks the frontend built from the exact commit under test. By default GitHub Actions builds the checked-out \`frontend/\` and serves it locally at \`http://127.0.0.1:4173\`, avoiding stale-hosted-code false negatives. Frontend application source and product behavior are not changed by the Selenium workflow.

To test a deployed environment instead, set the GitHub Actions repository variable \`CARELIFE_E2E_BASE_URL\` to that environment's URL, such as \`https://carelife-web.onrender.com\`. A deployed-site run can correctly fail when the hosted frontend has not yet received the latest code.

## Coverage

- Homepage, signup role choices, required-field validation, login, and password-reset navigation.
- Daycare, orphanage, and elderly-care module landing pages.
- Public daycare directory, elderly-care directory, caregiver directory, and orphanage support board for signed-out visitors.
- Protection of signed-out access to private child records, family check-ins, bookings, messages, account pages, and staff/admin workspaces.
- Personal pledge and payment-history tabs stay hidden from signed-out visitors.
- Optional admin sign-in test runs only when a dedicated test account is configured.
- Screenshots and HTML are saved for failing Selenium tests; GitHub Actions uploads the evidence and JUnit report.

Assertions are not suppressed or skipped based on which host is used. If the current source has a route-access regression, the corresponding test should fail.

## Run locally (PowerShell)

From the repository root, build and serve the frontend:

\`\`\`powershell
cd frontend
npm ci
npm run build
npm run preview -- --host 127.0.0.1 --port 4173
\`\`\`

In a second terminal, run Selenium:

\`\`\`powershell
cd backend
python -m pip install -r requirements-test.txt
$env:CARELIFE_E2E_BASE_URL = "http://127.0.0.1:4173"
$env:CARELIFE_HEADLESS = "true"
New-Item -ItemType Directory -Force test-results | Out-Null
python -m pytest -q tests/e2e --junitxml=test-results/e2e-results.xml
\`\`\`

For deployed-site testing, set \`CARELIFE_E2E_BASE_URL\` to the hosted URL before running pytest or set it as a GitHub repository variable. For the optional admin test, set \`CARELIFE_E2E_EMAIL\` and \`CARELIFE_E2E_PASSWORD\` to a dedicated test account; do not commit credentials.

## CI behavior

The workflow runs on pushes to \`tasnim/selenium\`, supports manual dispatch, and runs for pull requests targeting \`dev\` or \`main\` that change the Selenium suite, dependencies, frontend source, workflow, or this document. It builds and serves the current frontend commit locally, uses headless Chrome, and uploads \`test-results\` even if a test fails.

## Deployment follow-up

Earlier deployed-site runs against \`https://carelife-web.onrender.com\` reported that four public routes redirected to login. Those results were preserved as failure evidence. Passing the local-source suite verifies the current checked-out code; it does not by itself certify that the Render deployment has updated.
