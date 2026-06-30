import logging

from fastapi import FastAPI

from app.api.routes import auth, health
from app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

app = FastAPI(
    title="MediBox Auth Service",
    description="Authentication and user management for MediBox Cloud.",
    version="0.1.0",
    docs_url="/auth/docs",
    openapi_url="/auth/openapi.json",
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"service": settings.service_name, "status": "running"}
