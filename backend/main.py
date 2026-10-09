from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

from app.presentation.api.routes.health import router as health_router
from app.presentation.api.routes.protected import router as protected_router
from app.presentation.api.routes.password_reset import (
    router as password_reset_router,
)
from app.presentation.api.routes.organization_verification import (
    router as organization_verification_router,
)
from app.presentation.api.routes.organization_registration import (
    router as organization_registration_router,
)
from app.presentation.api.routes.signup import router as signup_router
from app.presentation.api.routes.login import router as login_router
from app.presentation.api.routes.children import router as children_router
from app.presentation.api.routes.enrollment import (
    router as enrollment_router,
)
from app.presentation.api.routes.attendance import (
    router as attendance_router,
)


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(protected_router)
app.include_router(password_reset_router)
app.include_router(organization_verification_router)
app.include_router(organization_registration_router)
app.include_router(signup_router)
app.include_router(login_router)
app.include_router(children_router)
app.include_router(enrollment_router)
app.include_router(attendance_router)


@app.get("/")
def root():
    return {"message": "CareLife API is running"}