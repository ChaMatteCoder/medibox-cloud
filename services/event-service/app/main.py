import logging

from fastapi import FastAPI

from app.api.routes import events, health, patients
from app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logging.getLogger("pika").setLevel(logging.CRITICAL)

app = FastAPI(
    title="MediBox Event Service",
    description="Device event registry and notification publishing for MediBox Cloud.",
    version="0.1.0",
    docs_url="/events/docs",
    openapi_url="/events/openapi.json",
)

app.include_router(health.router)
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(patients.router, prefix="/patients", tags=["adherence"])


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"service": settings.service_name, "status": "running"}
