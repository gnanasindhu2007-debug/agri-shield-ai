from fastapi import APIRouter
from app.api.v1.endpoints import auth, diagnosis, irrigation, climate, mandi, telemetry, sync
api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(diagnosis.router, prefix="/diagnosis", tags=["AI Pathology Diagnostics"])
api_router.include_router(irrigation.router, prefix="/irrigation", tags=["Smart Penman-Monteith Irrigation"])
api_router.include_router(climate.router, prefix="/climate", tags=["Climate Risk & Resilience"])
api_router.include_router(mandi.router, prefix="/mandi", tags=["APMC Mandi Commodity Prices"])
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["IoT Sensor Telemetry"])
api_router.include_router(sync.router, prefix="/sync", tags=["Field Offline Delta Sync"])
