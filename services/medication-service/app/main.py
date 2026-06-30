import logging

from fastapi import FastAPI

from app.api.routes import health, medications, patients, schedules
from app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

app = FastAPI(
    title="MediBox Medication Service",
    description="Patients, medications and schedules for MediBox Cloud.",
    version="0.1.0",
    docs_url="/medications/docs",
    openapi_url="/medications/openapi.json",
)

app.include_router(health.router)
app.include_router(patients.router, prefix="/patients", tags=["patients"])
app.include_router(medications.router, prefix="/medications", tags=["medications"])
app.include_router(schedules.router, prefix="/schedules", tags=["schedules"])


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"service": settings.service_name, "status": "running"}
