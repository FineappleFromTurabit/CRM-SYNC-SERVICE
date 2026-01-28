from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.sync import router as sync_router
from app.config import INTERNAL_API_BASE, HUBSPOT_BASE_URL, REDIS_URL

# -------------------------------------------------
# App initialization
# -------------------------------------------------
app = FastAPI(
    title="CRM Sync Service",
    description="Sync customers and tickets between Internal Support Desk and HubSpot",
    version="1.0.0",
)

# -------------------------------------------------
# CORS (safe default for internal tools)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Routers
# -------------------------------------------------
app.include_router(sync_router, prefix="/sync", tags=["Sync"])

# -------------------------------------------------
# Health check
# -------------------------------------------------
@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "crm-sync-service",
        "internal_api": INTERNAL_API_BASE,
        "hubspot_api": HUBSPOT_BASE_URL,
        "redis": REDIS_URL,
    }
    