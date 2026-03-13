"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.budget_monitor import router as budget_monitor_router
from app.api.financial import router as financial_router
from app.api.partners import router as partners_router
from app.api.projects import router as projects_router
from app.api.financial_reporting import router as financial_reporting_router
from app.api.reporting import router as reporting_router
from app.api.templates import router as templates_router
from app.api.reports import router as reports_router
from app.api.additional_features import router as additional_features_router
from app.api.dashboards import router as dashboards_router
from app.api.researchers import router as researchers_router
from app.api.timesheets import router as timesheets_router
from app.api.work_packages import router as work_packages_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router)
app.include_router(partners_router)
app.include_router(work_packages_router)
app.include_router(financial_router)
app.include_router(researchers_router)
app.include_router(timesheets_router)
app.include_router(budget_monitor_router)
app.include_router(reports_router)
app.include_router(reporting_router)
app.include_router(financial_reporting_router)
app.include_router(templates_router)
app.include_router(additional_features_router)
app.include_router(dashboards_router)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
