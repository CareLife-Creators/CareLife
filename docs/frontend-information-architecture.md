# CareLife Frontend Information Architecture

This is a working implementation guide matching the CareLife report with the current frontend and API. It does not claim that every documented workflow has shipped.

## Product structure

CareLife should be **one web application with three domain modules and shared services**, not three separate websites. The report describes a modular monolith: each care domain owns its own records and workflows, while shared services provide identity, verification, notifications, payment processing, messaging, media, reviews, audit records, and administration.

- **Daycare:** public daycare discovery, child profiles, enrollment, caregiver services, attendance, daily updates, communication, emergency contacts, authorized pickup persons, and applicable payments.
- **Orphanage:** organization discovery, monetary campaigns, in-kind needs and pledges, donation/utilization transparency, published impact updates, and restricted child/outcome records.
- **Elderly Care:** care-home discovery, caregiver services, resident records, consent-based family access, remote check-ins, and non-clinical wellbeing updates.
- **Shared platform:** accounts and role-based access, organization/caregiver verification, notifications, payment services, media, reviews, auditing, and admin moderation.

## Navigation rules

1. Home explains the three modules and guides users to a relevant starting point.
2. Each module landing page explains purpose, relevant roles, the main journey, and links only to implemented screens.
3. Public discovery must not expose child or resident private records.
4. Login is necessary for member-only pages/actions; the backend must also enforce roles and organization access.
5. Reuse page headers, search forms, cards, status feedback, spacing, and responsive patterns.
6. Every link navigates to a real route or is clearly labelled as a future workflow. Do not use a dead placeholder link.
7. Do not show a Verified badge unless the API supplies the corresponding verification status.
8. Do not show monetary donation checkout, appointment booking, or payment-success screens without a real transaction workflow.

## Current route map

| Route | Purpose | Backing API or page |
|---|---|---|
| #home | Public entry and module selection | Frontend page |
| #daycare | Daycare overview | Frontend page |
| #daycare-directory | Public daycare search | GET /organizations/daycare |
| #orphanage | Orphanage overview | Frontend page |
| #orphanage-support | Campaigns, in-kind needs, public updates | GET /donation-campaigns, GET /donation-needs, GET /impact-updates; POST /donation-needs/{need_id}/in-kind-pledges |
| #elderly-care | Elderly-care overview | Frontend page |
| #elderly-care-directory | Care-home search | GET /organizations/elder-care |
| #caregivers | Public caregiver discovery | GET /caregivers |
| #dashboard | Signed-in workspace | Frontend page; links to current routes |
| #verification | Organization status lookup | Existing UI/backend route; test status mapping and role-specific access |
| #organization-approval | Admin review queue | GET /organizations/verification/pending and approve/reject actions; admin role required |
| #login, #signup | Account access | Existing auth routes |

## Report-to-UI gap assessment

| Report requirement | Current coverage | Remaining UI/work |
|---|---|---|
| Daycare directory and profile discovery | Public directory exists | Profile detail improvements and verified status only when API supports it |
| Child records and enrollment | APIs exist | Parent child manager, enrollment request lifecycle, staff review screens |
| Attendance and daily updates | APIs exist | Staff check-in/out and parent read-only views |
| Emergency contacts and pickup safety | APIs exist | Parent management forms and role-restricted staff views |
| Caregiver profile and review | APIs exist for public list/profile, member profile/documents, admin review | Self-service profile, document submission UI, appointment lifecycle |
| Orphanage campaigns and needs | Public list and organization CRUD APIs exist | Campaign manager, payment transaction, digital receipts, donor history, allocation UI |
| In-kind support | Pledge and organization pledge/status APIs exist | Organization review/receive/allocate UI and donor pledge history |
| Impact updates | Create, public list, media and admin review APIs exist | Organization editor, upload UI, privacy review workflow |
| Elderly-care discovery | Public directory API exists | Resident manager, consent, remote check-in and wellbeing-update UI |
| Resident privacy and family access | Backend routes exist | End-to-end consent and role experience plus authorization tests |
| Shared verification/admin | Organization review pages exist | Caregiver moderation and clearer expiry/review status UX |
| Cross-platform usability | Common nav, login, dashboard | Accessible validation, standard states and frontend/browser tests |

## Important constraints to preserve

- The report identifies bKash as the primary payment gateway, but the inspected public campaign API does not provide a full public monetary donation transaction/checkout lifecycle. Do not create a fake confirmation.
- Booking and enrollment transitions must follow the SRS lifecycle; do not collect payment at the wrong stage.
- CareLife document review is not a replacement for government licensing or independent due diligence.
- Orphanage child and elderly resident records must stay private. The backend must enforce role and consent requirements.
- The verification-status route exists. Test response mapping and organization-access rules with role-specific accounts before calling the screen production-ready.

## Recommended delivery order

1. Shared navigation, module entry pages, visual primitives, and routing.
2. Public discovery and orphanage support board using current APIs.
3. Daycare child/enrollment/attendance and caregiver flows role by role.
4. Orphanage campaign management, donor history, in-kind fulfillment and impact moderation.
5. Elderly resident/family consent/check-in workflows, with privacy tests.
6. Frontend build/lint and browser workflow coverage.

All work remains on a feature branch and is delivered by PR into dev; keep the required independent reviewer approval.
