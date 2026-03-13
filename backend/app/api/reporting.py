"""API endpoints for reporting engine (Section 8)."""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enums import RiskStatus
from app.schemas.reporting import (
    CalendarReminderItem,
    PartB2AutoData,
    PartB3AutoData,
    PartB4AutoData,
    ReportingCalendarResponse,
    ReportingPeriodCreate,
    ReportingPeriodListResponse,
    ReportingPeriodResponse,
    ReportSectionResponse,
    ReportSectionUpdate,
    RiskCreate,
    RiskListResponse,
    RiskResponse,
    RiskUpdate,
    TechnicalReportListResponse,
    TechnicalReportResponse,
    TechnicalReportUpdate,
    WorkflowStepInfo,
)
from app.services.reporting import (
    advance_report_workflow,
    auto_generate_reporting_periods,
    create_reporting_period,
    create_report_shell,
    create_risk,
    delete_reporting_period,
    delete_risk,
    generate_part_b2_data,
    generate_part_b3_data,
    generate_part_b4_data,
    get_reporting_calendar,
    get_reporting_period,
    get_risk,
    get_technical_report,
    get_workflow_steps,
    list_reporting_periods,
    list_risks,
    list_technical_reports,
    send_due_reminders,
    update_report_section,
    update_risk,
    update_technical_report,
)

router = APIRouter(prefix="/api", tags=["reporting"])


# ── Reporting Periods ─────────────────────────────────


@router.post(
    "/projects/{project_id}/reporting-periods/auto-generate",
    response_model=ReportingPeriodListResponse,
    status_code=201,
)
async def auto_generate_periods(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ReportingPeriodListResponse:
    """Auto-generate reporting periods from grant agreement data."""
    periods = await auto_generate_reporting_periods(db, project_id)
    items = [ReportingPeriodResponse.model_validate(p) for p in periods]
    return ReportingPeriodListResponse(items=items, total=len(items))


@router.post(
    "/projects/{project_id}/reporting-periods",
    response_model=ReportingPeriodResponse,
    status_code=201,
)
async def create_period(
    project_id: uuid.UUID,
    data: ReportingPeriodCreate,
    db: AsyncSession = Depends(get_db),
) -> ReportingPeriodResponse:
    """Manually create a reporting period."""
    rp = await create_reporting_period(db, project_id, data)
    return ReportingPeriodResponse.model_validate(rp)


@router.get(
    "/projects/{project_id}/reporting-periods",
    response_model=ReportingPeriodListResponse,
)
async def list_periods(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ReportingPeriodListResponse:
    """List reporting periods for a project."""
    periods = await list_reporting_periods(db, project_id)
    items = [ReportingPeriodResponse.model_validate(p) for p in periods]
    return ReportingPeriodListResponse(items=items, total=len(items))


@router.get(
    "/reporting-periods/{period_id}",
    response_model=ReportingPeriodResponse,
)
async def get_period(
    period_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ReportingPeriodResponse:
    """Get a single reporting period."""
    rp = await get_reporting_period(db, period_id)
    if rp is None:
        raise HTTPException(status_code=404, detail="Reporting period not found")
    return ReportingPeriodResponse.model_validate(rp)


@router.delete("/reporting-periods/{period_id}", status_code=204)
async def delete_period(
    period_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a reporting period."""
    deleted = await delete_reporting_period(db, period_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Reporting period not found")


# ── Reporting Calendar ────────────────────────────────


@router.get(
    "/reporting-calendar",
    response_model=ReportingCalendarResponse,
)
async def reporting_calendar(
    project_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> ReportingCalendarResponse:
    """Get the reporting calendar with upcoming deadlines and reminders."""
    return await get_reporting_calendar(db, project_id)


@router.post("/reporting-calendar/send-reminders", status_code=200)
async def trigger_reminders(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Trigger sending of due reminders."""
    sent = await send_due_reminders(db)
    return {"reminders_sent": len(sent)}


# ── Risk Register ─────────────────────────────────────


@router.post(
    "/projects/{project_id}/risks",
    response_model=RiskResponse,
    status_code=201,
)
async def create_risk_endpoint(
    project_id: uuid.UUID,
    data: RiskCreate,
    db: AsyncSession = Depends(get_db),
) -> RiskResponse:
    """Create a risk in the project risk register."""
    risk = await create_risk(db, project_id, data)
    return RiskResponse.model_validate(risk)


@router.get(
    "/projects/{project_id}/risks",
    response_model=RiskListResponse,
)
async def list_risks_endpoint(
    project_id: uuid.UUID,
    status: RiskStatus | None = None,
    db: AsyncSession = Depends(get_db),
) -> RiskListResponse:
    """List risks for a project."""
    risks = await list_risks(db, project_id, status=status)
    items = [RiskResponse.model_validate(r) for r in risks]
    return RiskListResponse(items=items, total=len(items))


@router.get("/risks/{risk_id}", response_model=RiskResponse)
async def get_risk_endpoint(
    risk_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> RiskResponse:
    """Get a single risk."""
    risk = await get_risk(db, risk_id)
    if risk is None:
        raise HTTPException(status_code=404, detail="Risk not found")
    return RiskResponse.model_validate(risk)


@router.put("/risks/{risk_id}", response_model=RiskResponse)
async def update_risk_endpoint(
    risk_id: uuid.UUID,
    data: RiskUpdate,
    db: AsyncSession = Depends(get_db),
) -> RiskResponse:
    """Update a risk."""
    risk = await update_risk(db, risk_id, data)
    if risk is None:
        raise HTTPException(status_code=404, detail="Risk not found")
    return RiskResponse.model_validate(risk)


@router.delete("/risks/{risk_id}", status_code=204)
async def delete_risk_endpoint(
    risk_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a risk."""
    deleted = await delete_risk(db, risk_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Risk not found")


# ── Technical Reports ─────────────────────────────────


@router.post(
    "/reporting-periods/{period_id}/report",
    response_model=TechnicalReportResponse,
    status_code=201,
)
async def create_report(
    period_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TechnicalReportResponse:
    """Create a report shell for a reporting period (T-90 auto-creation)."""
    report = await create_report_shell(db, period_id)
    return TechnicalReportResponse.model_validate(report)


@router.get(
    "/projects/{project_id}/technical-reports",
    response_model=TechnicalReportListResponse,
)
async def list_reports(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TechnicalReportListResponse:
    """List technical reports for a project."""
    reports = await list_technical_reports(db, project_id)
    items = [TechnicalReportResponse.model_validate(r) for r in reports]
    return TechnicalReportListResponse(items=items, total=len(items))


@router.get(
    "/technical-reports/{report_id}",
    response_model=TechnicalReportResponse,
)
async def get_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TechnicalReportResponse:
    """Get a technical report with all sections."""
    report = await get_technical_report(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return TechnicalReportResponse.model_validate(report)


@router.put(
    "/technical-reports/{report_id}",
    response_model=TechnicalReportResponse,
)
async def update_report(
    report_id: uuid.UUID,
    data: TechnicalReportUpdate,
    db: AsyncSession = Depends(get_db),
) -> TechnicalReportResponse:
    """Update a technical report."""
    report = await update_technical_report(
        db,
        report_id,
        part_a_summary=data.part_a_summary,
        status=data.status,
        ec_feedback=data.ec_feedback,
    )
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return TechnicalReportResponse.model_validate(report)


@router.post(
    "/technical-reports/{report_id}/advance",
    response_model=TechnicalReportResponse,
)
async def advance_workflow(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TechnicalReportResponse:
    """Advance report to the next workflow step."""
    report = await advance_report_workflow(db, report_id)
    return TechnicalReportResponse.model_validate(report)


@router.get(
    "/technical-reports/{report_id}/workflow",
    response_model=list[WorkflowStepInfo],
)
async def get_report_workflow(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[WorkflowStepInfo]:
    """Get workflow steps with status for a report."""
    return await get_workflow_steps(db, report_id)


# ── Report Sections ───────────────────────────────────


@router.put(
    "/report-sections/{section_id}",
    response_model=ReportSectionResponse,
)
async def update_section(
    section_id: uuid.UUID,
    data: ReportSectionUpdate,
    db: AsyncSession = Depends(get_db),
) -> ReportSectionResponse:
    """Update a report section (WP narrative, content, etc.)."""
    section = await update_report_section(
        db,
        section_id,
        content=data.content,
        narrative=data.narrative,
        status=data.status,
        assigned_to=data.assigned_to,
    )
    if section is None:
        raise HTTPException(status_code=404, detail="Section not found")
    return ReportSectionResponse.model_validate(section)


# ── Auto-Generated Section Data ───────────────────────


@router.get(
    "/technical-reports/{report_id}/part-b2",
    response_model=PartB2AutoData,
)
async def get_part_b2(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PartB2AutoData:
    """Get auto-generated Part B Section 2 (deliverables/milestones)."""
    report = await get_technical_report(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    period = await get_reporting_period(db, report.reporting_period_id)
    if period is None:
        raise HTTPException(status_code=404, detail="Period not found")
    return await generate_part_b2_data(db, report.project_id, period.end_date)


@router.get(
    "/technical-reports/{report_id}/part-b3",
    response_model=PartB3AutoData,
)
async def get_part_b3(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PartB3AutoData:
    """Get auto-generated Part B Section 3 (risks)."""
    report = await get_technical_report(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return await generate_part_b3_data(db, report.project_id)


@router.get(
    "/technical-reports/{report_id}/part-b4",
    response_model=PartB4AutoData,
)
async def get_part_b4(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PartB4AutoData:
    """Get auto-generated Part B Section 4 (resource usage)."""
    report = await get_technical_report(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    period = await get_reporting_period(db, report.reporting_period_id)
    if period is None:
        raise HTTPException(status_code=404, detail="Period not found")
    return await generate_part_b4_data(
        db, report.project_id, period.start_date, period.end_date
    )
