from fastapi import FastAPI

from app.core.config import get_settings
from app.presentation.api.routes.health import router as health_router
from app.presentation.api.routes.password_reset import (
    router as password_reset_router,
)
from app.presentation.api.routes.protected import (
    router as protected_router,
)


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
)

app.include_router(health_router)
app.include_router(protected_router)
app.include_router(password_reset_router)


@app.get("/")
def root():
    return {"message": "CareLife API is running"}