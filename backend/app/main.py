import app.models  # noqa: F401
from fastapi import FastAPI

from app.routers import analytics, auth, owners, payments, pets, practice, services, vaccinations, visits

app = FastAPI(
    title="Paw Lodge",
    summary="Multi-tenant veterinary practice management API",
    version="1.0.0",
    redirect_slashes=False,
)

API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(practice.router, prefix=API_PREFIX)
app.include_router(owners.router, prefix=API_PREFIX)
app.include_router(pets.router, prefix=API_PREFIX)
app.include_router(services.router, prefix=API_PREFIX)
app.include_router(visits.router, prefix=API_PREFIX)
app.include_router(vaccinations.router, prefix=API_PREFIX)
app.include_router(payments.router, prefix=API_PREFIX)
app.include_router(payments.visit_payment_router, prefix=API_PREFIX)
app.include_router(analytics.router, prefix=API_PREFIX)


@app.get("/health", tags=["Health"], summary="Liveness check")
def health() -> dict[str, str]:
    return {"status": "ok"}
