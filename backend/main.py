from fastapi import FastAPI

from app.core.config import get_settings
from app.presentation.api.routes.health import router as health_router


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
)

app.include_router(health_router)


@app.get("/")
def root():
    return {"message": "CareLife API is running"}