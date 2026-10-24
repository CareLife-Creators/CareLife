from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.presentation.api.routes.caregiver_booking import (
    router as caregiver_booking_router,
)
from app.presentation.api.routes.attendance import (
    router as attendance_router,
)
from app.presentation.api.routes.caregivers import (
    router as caregivers_router,
)
from app.presentation.api.routes.children import (
    router as children_router,
)
from app.presentation.api.routes.donations import (
    router as donations_router,
)
from app.presentation.api.routes.enrollment import (
    router as enrollment_router,
)
from app.presentation.api.routes.health import (
    router as health_router,
)
from app.presentation.api.routes.impact import (
    router as impact_router,
)
from app.presentation.api.routes.in_kind_donations import (
    router as in_kind_donations_router,
)
from app.presentation.api.routes.login import (
    router as login_router,
)
from app.presentation.api.routes.organization_profile import (
    router as organization_profile_router,
    orphanage_public_router as orphanage_public_profile_router,
)
from app.presentation.api.routes.organization_registration import (
    router as organization_registration_router,
)
from app.presentation.api.routes.organization_verification import (
    router as organization_verification_router,
)
from app.presentation.api.routes.password_reset import (
    router as password_reset_router,
)
from app.presentation.api.routes.protected import (
    router as protected_router,
)
from app.presentation.api.routes.residents import (
    router as residents_router,
)
from app.presentation.api.routes.signup import (
    router as signup_router,
)
from app.presentation.api.routes.user_profile import (
    router as user_profile_router,
)
from app.presentation.api.routes.role_requests import (
    router as role_requests_router,
)
from app.presentation.api.routes.remote_checkins import (
    router as remote_checkins_router,
)
from app.presentation.api.routes.audit_logs import (
    router as audit_logs_router,
)
from app.presentation.api.routes.messaging import (
    router as messaging_router,
)
from app.presentation.api.routes.notifications import (
    router as notifications_router,
)
from app.presentation.api.routes.donation_payments import (
    router as donation_payments_router,
)
from app.presentation.api.routes.elder_care_bookings import (
    router as elder_care_bookings_router,
)
from app.presentation.api.routes.admin_users import router as admin_users_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(elder_care_bookings_router)
app.include_router(health_router)
app.include_router(protected_router)
app.include_router(password_reset_router)
app.include_router(organization_verification_router)
app.include_router(organization_registration_router)
app.include_router(organization_profile_router)
app.include_router(orphanage_public_profile_router)
app.include_router(signup_router)
app.include_router(login_router)
app.include_router(children_router)
app.include_router(enrollment_router)
app.include_router(attendance_router)
app.include_router(donations_router)
app.include_router(in_kind_donations_router)
app.include_router(caregivers_router)
app.include_router(impact_router)
app.include_router(user_profile_router)
app.include_router(role_requests_router)
app.include_router(remote_checkins_router)
app.include_router(residents_router)
app.include_router(audit_logs_router)
app.include_router(messaging_router)
app.include_router(notifications_router)
app.include_router(caregiver_booking_router)
app.include_router(donations_router)
app.include_router(in_kind_donations_router)
app.include_router(donation_payments_router)
app.include_router(admin_users_router)


@app.get("/")
def root():
    return {"message": "CareLife API is running"}
