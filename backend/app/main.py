from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.scopes import router as scope_router
from app.api.engagements import router as engagement_router
from app.core.database import Base, engine
from app.models import (
    Activity,
    Asset,
    Engagement,
    Evidence,
    Finding,
    Scope,
    Service,
    AssetRelationship,
)
from app.api.assets import router as asset_router
from app.api.activities import router as activity_router
from app.api.evidence import router as evidence_router
from app.api.findings import router as finding_router
from app.api.events import router as event_router
from app.api.services import router as service_router
from app.api.attack_surface import router as attack_surface_router
from app.api.dashboard import router as dashboard_router
from app.api.reports import router as report_router
from app.api.coverage import router as coverage_router
from app.api.asset_relationships import (
    router as asset_relationship_router,
)


app = FastAPI(
    title="VANTA",
    description="Evidence-Driven Penetration Testing Platform",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(engagement_router)
app.include_router(scope_router)
app.include_router(asset_router)
app.include_router(activity_router)
app.include_router(evidence_router)
app.include_router(finding_router)
app.include_router(event_router)
app.include_router(service_router)
app.include_router(attack_surface_router)
app.include_router(dashboard_router)
app.include_router(report_router)
app.include_router(coverage_router)
app.include_router(asset_relationship_router)


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "ok",
        "project": "VANTA",
        "version": "0.1.0",
    }