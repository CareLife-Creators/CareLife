# CAR-154 — Selenium regression testing

## Scope

The Selenium suite targets the **deployed CareLife frontend** and does not edit frontend application source. The default URL is \`https://carelife-web.onrender.com\`; override it when the frontend is hosted elsewhere.

## Coverage

- Homepage, signup role choices, required-field validation, login, and password-reset navigation.
- Daycare, orphanage, and elderly-care module landing pages.
- Public daycare directory, elderly-care directory, caregiver directory, and orphanage support board for signed-out visitors.
- Protection of signed-out access to private child records, family check-ins, bookings, messages, account pages, and staff/admin workspaces.
- Donor-only pledge history and personal payment-history tabs remain hidden from signed-out visitors.
- Optional admin sign-in test runs only when a dedicated test account is configured.
- Screenshots and HTML are saved for Selenium failures; GitHub Actions uploads the evidence and JUnit report.

## Deployment note

The public discovery/support route-access fix was approved and merged into \`dev\`, then promoted to the Render frontend deployment branch via PR #66 on 2026-10-24. The Selenium suite intentionally checks the **deployed result**, not just the source branch. If a public route redirects to login, keep the assertion enabled and investigate deployment lag or branch configuration rather than weakening the test.

The test branch does not change the frontend application implementation. Any future frontend fix should be reviewed and merged separately from CAR-154 testing.

## Run locally (PowerShell)

From the repository's \`backend\` directory:

\`\`\`powershell
python -m pip install -r requirements-test.txt
$env:CARELIFE_E2E_BASE_URL = "https://carelife-web.onrender.com"
$env:CARELIFE_HEADLESS = "true"
New-Item -ItemType Directory -Force test-results | Out-Null
python -m pytest -q tests/e2e --junitxml=test-results/e2e-results.xml
\`\`\`

For the optional admin test, set \`CARELIFE_E2E_EMAIL\` and \`CARELIFE_E2E_PASSWORD\` to a **dedicated test account**. Do not commit credentials. In GitHub Actions, configure those as repository secrets. Configure \`CARELIFE_E2E_BASE_URL\` as a repository variable if the hosted frontend URL differs from the default.

## CI behavior

The workflow runs on pushes to \`tasnim/selenium\`, supports manual dispatch, and runs for pull requests targeting \`dev\` or \`main\` that change the Selenium suite, test dependencies, workflow, or this document. It uses headless Chrome against the deployed site and uploads \`test-results\` even if a test fails.
