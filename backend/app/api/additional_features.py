"""API endpoints for Section 9 — Additional Features.

IP tracking, dissemination log, KPI indicators, ethics/DMP,
collaboration network, amendment tracking, and notification system.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enums import (
    DisseminationActivityType,
    IPStatus,
    NotificationStatus,
)
from app.schemas.additional_features import (
    AmendmentCreate,
    AmendmentListResponse,
    AmendmentResponse,
    AmendmentUpdate,
    CollaborationRecordCreate,
    CollaborationRecordListResponse,
    CollaborationRecordResponse,
    CollaborationRecordUpdate,
    DataManagementRecordCreate,
    DataManagementRecordListResponse,
    DataManagementRecordResponse,
    DataManagementRecordUpdate,
    DisseminationActivityCreate,
    DisseminationActivityListResponse,
    DisseminationActivityResponse,
    DisseminationActivityUpdate,
    EthicsRequirementCreate,
    EthicsRequirementListResponse,
    EthicsRequirementResponse,
    EthicsRequirementUpdate,
    IPAssetCreate,
    IPAssetListResponse,
    IPAssetResponse,
    IPAssetUpdate,
    KPIDefinitionCreate,
    KPIDefinitionListResponse,
    KPIDefinitionResponse,
    KPIDefinitionUpdate,
    KPIValueCreate,
    KPIValueListResponse,
    KPIValueResponse,
    KPIValueUpdate,
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
    NotificationUpdate,
)
from app.services.additional_features import (
    create_amendment,
    create_collaboration_record,
    create_data_management_record,
    create_dissemination_activity,
    create_ethics_requirement,
    create_ip_asset,
    create_kpi_definition,
    create_kpi_value,
    create_notification,
    delete_amendment,
    delete_collaboration_record,
    delete_data_management_record,
    delete_dissemination_activity,
    delete_ethics_requirement,
    delete_ip_asset,
    delete_kpi_definition,
    delete_kpi_value,
    delete_notification,
    dismiss_notification,
    get_amendment,
    get_collaboration_record,
    get_data_management_record,
    get_dissemination_activity,
    get_ethics_requirement,
    get_ip_asset,
    get_kpi_definition,
    get_kpi_value,
    get_notification,
    list_amendments,
    list_collaboration_records,
    list_data_management_records,
    list_dissemination_activities,
    list_ethics_requirements,
    list_ip_assets,
    list_kpi_definitions,
    list_kpi_values,
    list_notifications,
    mark_notification_read,
    mark_notification_sent,
    update_amendment,
    update_collaboration_record,
    update_data_management_record,
    update_dissemination_activity,
    update_ethics_requirement,
    update_ip_asset,
    update_kpi_definition,
    update_kpi_value,
    update_notification,
)

router = APIRouter(prefix="/api", tags=["additional-features"])


# ── 9.1 IP and Exploitation Tracking ─────────────────


@router.post(
    "/projects/{project_id}/ip-assets",
    response_model=IPAssetResponse,
    status_code=201,
)
async def create_ip_asset_endpoint(
    project_id: uuid.UUID,
    body: IPAssetCreate,
    db: AsyncSession = Depends(get_db),
) -> IPAssetResponse:
    """Create an IP asset for a project."""
    asset = await create_ip_asset(db, project_id, body)
    await db.commit()
    await db.refresh(asset)
    return IPAssetResponse.model_validate(asset)


@router.get(
    "/projects/{project_id}/ip-assets",
    response_model=IPAssetListResponse,
)
async def list_ip_assets_endpoint(
    project_id: uuid.UUID,
    status: IPStatus | None = None,
    db: AsyncSession = Depends(get_db),
) -> IPAssetListResponse:
    """List IP assets for a project."""
    items = await list_ip_assets(db, project_id, status=status)
    return IPAssetListResponse(
        items=[IPAssetResponse.model_validate(i) for i in items],
        total=len(items),
    )


@router.get("/ip-assets/{asset_id}", response_model=IPAssetResponse)
async def get_ip_asset_endpoint(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> IPAssetResponse:
    """Get an IP asset by ID."""
    asset = await get_ip_asset(db, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="IP asset not found")
    return IPAssetResponse.model_validate(asset)


@router.put("/ip-assets/{asset_id}", response_model=IPAssetResponse)
async def update_ip_asset_endpoint(
    asset_id: uuid.UUID,
    body: IPAssetUpdate,
    db: AsyncSession = Depends(get_db),
) -> IPAssetResponse:
    """Update an IP asset."""
    asset = await update_ip_asset(db, asset_id, body)
    if asset is None:
        raise HTTPException(status_code=404, detail="IP asset not found")
    await db.commit()
    await db.refresh(asset)
    return IPAssetResponse.model_validate(asset)


@router.delete("/ip-assets/{asset_id}", status_code=204)
async def delete_ip_asset_endpoint(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete an IP asset."""
    deleted = await delete_ip_asset(db, asset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="IP asset not found")
    await db.commit()


# ── 9.3 Dissemination Log ────────────────────────────


@router.post(
    "/projects/{project_id}/dissemination-activities",
    response_model=DisseminationActivityResponse,
    status_code=201,
)
async def create_dissemination_activity_endpoint(
    project_id: uuid.UUID,
    body: DisseminationActivityCreate,
    db: AsyncSession = Depends(get_db),
) -> DisseminationActivityResponse:
    """Create a dissemination activity for a project."""
    activity = await create_dissemination_activity(db, project_id, body)
    await db.commit()
    await db.refresh(activity)
    return DisseminationActivityResponse.model_validate(activity)


@router.get(
    "/projects/{project_id}/dissemination-activities",
    response_model=DisseminationActivityListResponse,
)
async def list_dissemination_activities_endpoint(
    project_id: uuid.UUID,
    activity_type: DisseminationActivityType | None = None,
    db: AsyncSession = Depends(get_db),
) -> DisseminationActivityListResponse:
    """List dissemination activities for a project."""
    items = await list_dissemination_activities(
        db, project_id, activity_type=activity_type
    )
    return DisseminationActivityListResponse(
        items=[
            DisseminationActivityResponse.model_validate(i) for i in items
        ],
        total=len(items),
    )


@router.get(
    "/dissemination-activities/{activity_id}",
    response_model=DisseminationActivityResponse,
)
async def get_dissemination_activity_endpoint(
    activity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DisseminationActivityResponse:
    """Get a dissemination activity by ID."""
    activity = await get_dissemination_activity(db, activity_id)
    if activity is None:
        raise HTTPException(
            status_code=404, detail="Dissemination activity not found"
        )
    return DisseminationActivityResponse.model_validate(activity)


@router.put(
    "/dissemination-activities/{activity_id}",
    response_model=DisseminationActivityResponse,
)
async def update_dissemination_activity_endpoint(
    activity_id: uuid.UUID,
    body: DisseminationActivityUpdate,
    db: AsyncSession = Depends(get_db),
) -> DisseminationActivityResponse:
    """Update a dissemination activity."""
    activity = await update_dissemination_activity(db, activity_id, body)
    if activity is None:
        raise HTTPException(
            status_code=404, detail="Dissemination activity not found"
        )
    await db.commit()
    await db.refresh(activity)
    return DisseminationActivityResponse.model_validate(activity)


@router.delete("/dissemination-activities/{activity_id}", status_code=204)
async def delete_dissemination_activity_endpoint(
    activity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete a dissemination activity."""
    deleted = await delete_dissemination_activity(db, activity_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Dissemination activity not found"
        )
    await db.commit()


# ── 9.4 KPI and Indicator Tracking ───────────────────


@router.post(
    "/kpi-definitions",
    response_model=KPIDefinitionResponse,
    status_code=201,
)
async def create_kpi_definition_endpoint(
    body: KPIDefinitionCreate,
    db: AsyncSession = Depends(get_db),
) -> KPIDefinitionResponse:
    """Create a KPI definition."""
    defn = await create_kpi_definition(db, body)
    await db.commit()
    await db.refresh(defn)
    return KPIDefinitionResponse.model_validate(defn)


@router.get(
    "/kpi-definitions",
    response_model=KPIDefinitionListResponse,
)
async def list_kpi_definitions_endpoint(
    programme: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> KPIDefinitionListResponse:
    """List KPI definitions."""
    items = await list_kpi_definitions(db, programme=programme)
    return KPIDefinitionListResponse(
        items=[KPIDefinitionResponse.model_validate(i) for i in items],
        total=len(items),
    )


@router.get(
    "/kpi-definitions/{defn_id}",
    response_model=KPIDefinitionResponse,
)
async def get_kpi_definition_endpoint(
    defn_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> KPIDefinitionResponse:
    """Get a KPI definition by ID."""
    defn = await get_kpi_definition(db, defn_id)
    if defn is None:
        raise HTTPException(
            status_code=404, detail="KPI definition not found"
        )
    return KPIDefinitionResponse.model_validate(defn)


@router.put(
    "/kpi-definitions/{defn_id}",
    response_model=KPIDefinitionResponse,
)
async def update_kpi_definition_endpoint(
    defn_id: uuid.UUID,
    body: KPIDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
) -> KPIDefinitionResponse:
    """Update a KPI definition."""
    defn = await update_kpi_definition(db, defn_id, body)
    if defn is None:
        raise HTTPException(
            status_code=404, detail="KPI definition not found"
        )
    await db.commit()
    await db.refresh(defn)
    return KPIDefinitionResponse.model_validate(defn)


@router.delete("/kpi-definitions/{defn_id}", status_code=204)
async def delete_kpi_definition_endpoint(
    defn_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a KPI definition."""
    deleted = await delete_kpi_definition(db, defn_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail="KPI definition not found"
        )
    await db.commit()


@router.post(
    "/projects/{project_id}/kpi-values",
    response_model=KPIValueResponse,
    status_code=201,
)
async def create_kpi_value_endpoint(
    project_id: uuid.UUID,
    body: KPIValueCreate,
    db: AsyncSession = Depends(get_db),
) -> KPIValueResponse:
    """Create a KPI value for a project."""
    value = await create_kpi_value(db, project_id, body)
    await db.commit()
    await db.refresh(value)
    return KPIValueResponse.model_validate(value)


@router.get(
    "/projects/{project_id}/kpi-values",
    response_model=KPIValueListResponse,
)
async def list_kpi_values_endpoint(
    project_id: uuid.UUID,
    kpi_definition_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> KPIValueListResponse:
    """List KPI values for a project."""
    items = await list_kpi_values(
        db, project_id, kpi_definition_id=kpi_definition_id
    )
    return KPIValueListResponse(
        items=[KPIValueResponse.model_validate(i) for i in items],
        total=len(items),
    )


@router.get("/kpi-values/{value_id}", response_model=KPIValueResponse)
async def get_kpi_value_endpoint(
    value_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> KPIValueResponse:
    """Get a KPI value by ID."""
    value = await get_kpi_value(db, value_id)
    if value is None:
        raise HTTPException(status_code=404, detail="KPI value not found")
    return KPIValueResponse.model_validate(value)


@router.put("/kpi-values/{value_id}", response_model=KPIValueResponse)
async def update_kpi_value_endpoint(
    value_id: uuid.UUID,
    body: KPIValueUpdate,
    db: AsyncSession = Depends(get_db),
) -> KPIValueResponse:
    """Update a KPI value."""
    value = await update_kpi_value(db, value_id, body)
    if value is None:
        raise HTTPException(status_code=404, detail="KPI value not found")
    await db.commit()
    await db.refresh(value)
    return KPIValueResponse.model_validate(value)


@router.delete("/kpi-values/{value_id}", status_code=204)
async def delete_kpi_value_endpoint(
    value_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a KPI value."""
    deleted = await delete_kpi_value(db, value_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="KPI value not found")
    await db.commit()


# ── 9.5 Ethics and Data Management ───────────────────


@router.post(
    "/projects/{project_id}/ethics-requirements",
    response_model=EthicsRequirementResponse,
    status_code=201,
)
async def create_ethics_requirement_endpoint(
    project_id: uuid.UUID,
    body: EthicsRequirementCreate,
    db: AsyncSession = Depends(get_db),
) -> EthicsRequirementResponse:
    """Create an ethics requirement for a project."""
    req = await create_ethics_requirement(db, project_id, body)
    await db.commit()
    await db.refresh(req)
    return EthicsRequirementResponse.model_validate(req)


@router.get(
    "/projects/{project_id}/ethics-requirements",
    response_model=EthicsRequirementListResponse,
)
async def list_ethics_requirements_endpoint(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> EthicsRequirementListResponse:
    """List ethics requirements for a project."""
    items = await list_ethics_requirements(db, project_id)
    return EthicsRequirementListResponse(
        items=[EthicsRequirementResponse.model_validate(i) for i in items],
        total=len(items),
    )


@router.get(
    "/ethics-requirements/{req_id}",
    response_model=EthicsRequirementResponse,
)
async def get_ethics_requirement_endpoint(
    req_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> EthicsRequirementResponse:
    """Get an ethics requirement by ID."""
    req = await get_ethics_requirement(db, req_id)
    if req is None:
        raise HTTPException(
            status_code=404, detail="Ethics requirement not found"
        )
    return EthicsRequirementResponse.model_validate(req)


@router.put(
    "/ethics-requirements/{req_id}",
    response_model=EthicsRequirementResponse,
)
async def update_ethics_requirement_endpoint(
    req_id: uuid.UUID,
    body: EthicsRequirementUpdate,
    db: AsyncSession = Depends(get_db),
) -> EthicsRequirementResponse:
    """Update an ethics requirement."""
    req = await update_ethics_requirement(db, req_id, body)
    if req is None:
        raise HTTPException(
            status_code=404, detail="Ethics requirement not found"
        )
    await db.commit()
    await db.refresh(req)
    return EthicsRequirementResponse.model_validate(req)


@router.delete("/ethics-requirements/{req_id}", status_code=204)
async def delete_ethics_requirement_endpoint(
    req_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete an ethics requirement."""
    deleted = await delete_ethics_requirement(db, req_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Ethics requirement not found"
        )
    await db.commit()


@router.post(
    "/projects/{project_id}/data-management-records",
    response_model=DataManagementRecordResponse,
    status_code=201,
)
async def create_data_management_record_endpoint(
    project_id: uuid.UUID,
    body: DataManagementRecordCreate,
    db: AsyncSession = Depends(get_db),
) -> DataManagementRecordResponse:
    """Create a data management record for a project."""
    record = await create_data_management_record(db, project_id, body)
    await db.commit()
    await db.refresh(record)
    return DataManagementRecordResponse.model_validate(record)


@router.get(
    "/projects/{project_id}/data-management-records",
    response_model=DataManagementRecordListResponse,
)
async def list_data_management_records_endpoint(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DataManagementRecordListResponse:
    """List data management records for a project."""
    items = await list_data_management_records(db, project_id)
    return DataManagementRecordListResponse(
        items=[
            DataManagementRecordResponse.model_validate(i) for i in items
        ],
        total=len(items),
    )


@router.get(
    "/data-management-records/{record_id}",
    response_model=DataManagementRecordResponse,
)
async def get_data_management_record_endpoint(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DataManagementRecordResponse:
    """Get a data management record by ID."""
    record = await get_data_management_record(db, record_id)
    if record is None:
        raise HTTPException(
            status_code=404, detail="Data management record not found"
        )
    return DataManagementRecordResponse.model_validate(record)


@router.put(
    "/data-management-records/{record_id}",
    response_model=DataManagementRecordResponse,
)
async def update_data_management_record_endpoint(
    record_id: uuid.UUID,
    body: DataManagementRecordUpdate,
    db: AsyncSession = Depends(get_db),
) -> DataManagementRecordResponse:
    """Update a data management record."""
    record = await update_data_management_record(db, record_id, body)
    if record is None:
        raise HTTPException(
            status_code=404, detail="Data management record not found"
        )
    await db.commit()
    await db.refresh(record)
    return DataManagementRecordResponse.model_validate(record)


@router.delete("/data-management-records/{record_id}", status_code=204)
async def delete_data_management_record_endpoint(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete a data management record."""
    deleted = await delete_data_management_record(db, record_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Data management record not found"
        )
    await db.commit()


# ── 9.6 Collaboration Network ────────────────────────


@router.post(
    "/collaboration-records",
    response_model=CollaborationRecordResponse,
    status_code=201,
)
async def create_collaboration_record_endpoint(
    body: CollaborationRecordCreate,
    db: AsyncSession = Depends(get_db),
) -> CollaborationRecordResponse:
    """Create a collaboration record."""
    record = await create_collaboration_record(db, body)
    await db.commit()
    await db.refresh(record)
    return CollaborationRecordResponse.model_validate(record)


@router.get(
    "/collaboration-records",
    response_model=CollaborationRecordListResponse,
)
async def list_collaboration_records_endpoint(
    partner_id: uuid.UUID | None = None,
    project_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> CollaborationRecordListResponse:
    """List collaboration records."""
    items = await list_collaboration_records(
        db, partner_id=partner_id, project_id=project_id
    )
    return CollaborationRecordListResponse(
        items=[
            CollaborationRecordResponse.model_validate(i) for i in items
        ],
        total=len(items),
    )


@router.get(
    "/collaboration-records/{record_id}",
    response_model=CollaborationRecordResponse,
)
async def get_collaboration_record_endpoint(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CollaborationRecordResponse:
    """Get a collaboration record by ID."""
    record = await get_collaboration_record(db, record_id)
    if record is None:
        raise HTTPException(
            status_code=404, detail="Collaboration record not found"
        )
    return CollaborationRecordResponse.model_validate(record)


@router.put(
    "/collaboration-records/{record_id}",
    response_model=CollaborationRecordResponse,
)
async def update_collaboration_record_endpoint(
    record_id: uuid.UUID,
    body: CollaborationRecordUpdate,
    db: AsyncSession = Depends(get_db),
) -> CollaborationRecordResponse:
    """Update a collaboration record."""
    record = await update_collaboration_record(db, record_id, body)
    if record is None:
        raise HTTPException(
            status_code=404, detail="Collaboration record not found"
        )
    await db.commit()
    await db.refresh(record)
    return CollaborationRecordResponse.model_validate(record)


@router.delete("/collaboration-records/{record_id}", status_code=204)
async def delete_collaboration_record_endpoint(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a collaboration record."""
    deleted = await delete_collaboration_record(db, record_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Collaboration record not found"
        )
    await db.commit()


# ── 9.7 Amendment Tracking ───────────────────────────


@router.post(
    "/projects/{project_id}/amendments",
    response_model=AmendmentResponse,
    status_code=201,
)
async def create_amendment_endpoint(
    project_id: uuid.UUID,
    body: AmendmentCreate,
    db: AsyncSession = Depends(get_db),
) -> AmendmentResponse:
    """Create an amendment for a project."""
    amendment = await create_amendment(db, project_id, body)
    await db.commit()
    await db.refresh(amendment)
    return AmendmentResponse.model_validate(amendment)


@router.get(
    "/projects/{project_id}/amendments",
    response_model=AmendmentListResponse,
)
async def list_amendments_endpoint(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> AmendmentListResponse:
    """List amendments for a project."""
    items = await list_amendments(db, project_id)
    return AmendmentListResponse(
        items=[AmendmentResponse.model_validate(i) for i in items],
        total=len(items),
    )


@router.get(
    "/amendments/{amendment_id}",
    response_model=AmendmentResponse,
)
async def get_amendment_endpoint(
    amendment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> AmendmentResponse:
    """Get an amendment by ID."""
    amendment = await get_amendment(db, amendment_id)
    if amendment is None:
        raise HTTPException(status_code=404, detail="Amendment not found")
    return AmendmentResponse.model_validate(amendment)


@router.put(
    "/amendments/{amendment_id}",
    response_model=AmendmentResponse,
)
async def update_amendment_endpoint(
    amendment_id: uuid.UUID,
    body: AmendmentUpdate,
    db: AsyncSession = Depends(get_db),
) -> AmendmentResponse:
    """Update an amendment."""
    amendment = await update_amendment(db, amendment_id, body)
    if amendment is None:
        raise HTTPException(status_code=404, detail="Amendment not found")
    await db.commit()
    await db.refresh(amendment)
    return AmendmentResponse.model_validate(amendment)


@router.delete("/amendments/{amendment_id}", status_code=204)
async def delete_amendment_endpoint(
    amendment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete an amendment."""
    deleted = await delete_amendment(db, amendment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Amendment not found")
    await db.commit()


# ── 9.8 Notification System ──────────────────────────


@router.post(
    "/notifications",
    response_model=NotificationResponse,
    status_code=201,
)
async def create_notification_endpoint(
    body: NotificationCreate,
    db: AsyncSession = Depends(get_db),
) -> NotificationResponse:
    """Create a notification."""
    notification = await create_notification(db, body)
    await db.commit()
    await db.refresh(notification)
    return NotificationResponse.model_validate(notification)


@router.get(
    "/notifications",
    response_model=NotificationListResponse,
)
async def list_notifications_endpoint(
    project_id: uuid.UUID | None = None,
    status: NotificationStatus | None = None,
    recipient_email: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> NotificationListResponse:
    """List notifications with optional filters."""
    items = await list_notifications(
        db,
        project_id=project_id,
        status=status,
        recipient_email=recipient_email,
    )
    return NotificationListResponse(
        items=[NotificationResponse.model_validate(i) for i in items],
        total=len(items),
    )


@router.get(
    "/notifications/{notification_id}",
    response_model=NotificationResponse,
)
async def get_notification_endpoint(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> NotificationResponse:
    """Get a notification by ID."""
    notification = await get_notification(db, notification_id)
    if notification is None:
        raise HTTPException(
            status_code=404, detail="Notification not found"
        )
    return NotificationResponse.model_validate(notification)


@router.put(
    "/notifications/{notification_id}",
    response_model=NotificationResponse,
)
async def update_notification_endpoint(
    notification_id: uuid.UUID,
    body: NotificationUpdate,
    db: AsyncSession = Depends(get_db),
) -> NotificationResponse:
    """Update a notification."""
    notification = await update_notification(db, notification_id, body)
    if notification is None:
        raise HTTPException(
            status_code=404, detail="Notification not found"
        )
    await db.commit()
    await db.refresh(notification)
    return NotificationResponse.model_validate(notification)


@router.post(
    "/notifications/{notification_id}/read",
    response_model=NotificationResponse,
)
async def mark_notification_read_endpoint(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> NotificationResponse:
    """Mark a notification as read."""
    notification = await mark_notification_read(db, notification_id)
    if notification is None:
        raise HTTPException(
            status_code=404, detail="Notification not found"
        )
    await db.commit()
    await db.refresh(notification)
    return NotificationResponse.model_validate(notification)


@router.post(
    "/notifications/{notification_id}/send",
    response_model=NotificationResponse,
)
async def mark_notification_sent_endpoint(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> NotificationResponse:
    """Mark a notification as sent."""
    notification = await mark_notification_sent(db, notification_id)
    if notification is None:
        raise HTTPException(
            status_code=404, detail="Notification not found"
        )
    await db.commit()
    await db.refresh(notification)
    return NotificationResponse.model_validate(notification)


@router.post(
    "/notifications/{notification_id}/dismiss",
    response_model=NotificationResponse,
)
async def dismiss_notification_endpoint(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> NotificationResponse:
    """Dismiss a notification."""
    notification = await dismiss_notification(db, notification_id)
    if notification is None:
        raise HTTPException(
            status_code=404, detail="Notification not found"
        )
    await db.commit()
    await db.refresh(notification)
    return NotificationResponse.model_validate(notification)


@router.delete("/notifications/{notification_id}", status_code=204)
async def delete_notification_endpoint(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a notification."""
    deleted = await delete_notification(db, notification_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Notification not found"
        )
    await db.commit()
