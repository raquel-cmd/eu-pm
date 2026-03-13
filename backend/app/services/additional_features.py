"""Service layer for Section 9 — Additional Features.

CRUD operations for IP tracking, dissemination log, KPI indicators,
ethics/DMP, collaboration network, amendment tracking, and notifications.
"""

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.additional_features import (
    Amendment,
    CollaborationRecord,
    DataManagementRecord,
    DisseminationActivity,
    EthicsRequirement,
    IPAsset,
    KPIDefinition,
    KPIValue,
    Notification,
)
from app.models.enums import (
    DisseminationActivityType,
    IPStatus,
    NotificationStatus,
)
from app.models.project import Project
from app.schemas.additional_features import (
    AmendmentCreate,
    AmendmentUpdate,
    CollaborationRecordCreate,
    CollaborationRecordUpdate,
    DataManagementRecordCreate,
    DataManagementRecordUpdate,
    DisseminationActivityCreate,
    DisseminationActivityUpdate,
    EthicsRequirementCreate,
    EthicsRequirementUpdate,
    IPAssetCreate,
    IPAssetUpdate,
    KPIDefinitionCreate,
    KPIDefinitionUpdate,
    KPIValueCreate,
    KPIValueUpdate,
    NotificationCreate,
    NotificationUpdate,
)


async def _get_project(db: AsyncSession, project_id: uuid.UUID) -> Project:
    """Fetch project or raise 404."""
    stmt = select(Project).where(
        Project.id == project_id, Project.deleted_at.is_(None)
    )
    project = (await db.execute(stmt)).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ──────────────────────────────────────────────────────
#  9.1 IP and Exploitation Tracking
# ──────────────────────────────────────────────────────


async def create_ip_asset(
    db: AsyncSession, project_id: uuid.UUID, data: IPAssetCreate
) -> IPAsset:
    """Create an IP asset."""
    await _get_project(db, project_id)
    asset = IPAsset(project_id=project_id, **data.model_dump())
    db.add(asset)
    await db.flush()
    await db.refresh(asset)
    return asset


async def list_ip_assets(
    db: AsyncSession,
    project_id: uuid.UUID,
    *,
    status: IPStatus | None = None,
) -> list[IPAsset]:
    """List IP assets for a project."""
    stmt = select(IPAsset).where(
        IPAsset.project_id == project_id,
        IPAsset.deleted_at.is_(None),
    )
    if status is not None:
        stmt = stmt.where(IPAsset.status == status)
    stmt = stmt.order_by(IPAsset.created_at)
    return list((await db.execute(stmt)).scalars().all())


async def get_ip_asset(db: AsyncSession, asset_id: uuid.UUID) -> IPAsset | None:
    """Get a single IP asset."""
    stmt = select(IPAsset).where(
        IPAsset.id == asset_id, IPAsset.deleted_at.is_(None)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def update_ip_asset(
    db: AsyncSession, asset_id: uuid.UUID, data: IPAssetUpdate
) -> IPAsset | None:
    """Update an IP asset."""
    asset = await get_ip_asset(db, asset_id)
    if asset is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)
    await db.flush()
    await db.refresh(asset)
    return asset


async def delete_ip_asset(db: AsyncSession, asset_id: uuid.UUID) -> bool:
    """Soft-delete an IP asset."""
    asset = await get_ip_asset(db, asset_id)
    if asset is None:
        return False
    asset.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


# ──────────────────────────────────────────────────────
#  9.3 Communication and Dissemination Log
# ──────────────────────────────────────────────────────


async def create_dissemination_activity(
    db: AsyncSession,
    project_id: uuid.UUID,
    data: DisseminationActivityCreate,
) -> DisseminationActivity:
    """Create a dissemination activity."""
    await _get_project(db, project_id)
    activity = DisseminationActivity(
        project_id=project_id, **data.model_dump()
    )
    db.add(activity)
    await db.flush()
    await db.refresh(activity)
    return activity


async def list_dissemination_activities(
    db: AsyncSession,
    project_id: uuid.UUID,
    *,
    activity_type: DisseminationActivityType | None = None,
) -> list[DisseminationActivity]:
    """List dissemination activities for a project."""
    stmt = select(DisseminationActivity).where(
        DisseminationActivity.project_id == project_id,
        DisseminationActivity.deleted_at.is_(None),
    )
    if activity_type is not None:
        stmt = stmt.where(
            DisseminationActivity.activity_type == activity_type
        )
    stmt = stmt.order_by(DisseminationActivity.created_at)
    return list((await db.execute(stmt)).scalars().all())


async def get_dissemination_activity(
    db: AsyncSession, activity_id: uuid.UUID
) -> DisseminationActivity | None:
    """Get a single dissemination activity."""
    stmt = select(DisseminationActivity).where(
        DisseminationActivity.id == activity_id,
        DisseminationActivity.deleted_at.is_(None),
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def update_dissemination_activity(
    db: AsyncSession,
    activity_id: uuid.UUID,
    data: DisseminationActivityUpdate,
) -> DisseminationActivity | None:
    """Update a dissemination activity."""
    activity = await get_dissemination_activity(db, activity_id)
    if activity is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(activity, field, value)
    await db.flush()
    await db.refresh(activity)
    return activity


async def delete_dissemination_activity(
    db: AsyncSession, activity_id: uuid.UUID
) -> bool:
    """Soft-delete a dissemination activity."""
    activity = await get_dissemination_activity(db, activity_id)
    if activity is None:
        return False
    activity.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


# ──────────────────────────────────────────────────────
#  9.4 KPI and Indicator Tracking
# ──────────────────────────────────────────────────────


async def create_kpi_definition(
    db: AsyncSession, data: KPIDefinitionCreate
) -> KPIDefinition:
    """Create a KPI definition."""
    defn = KPIDefinition(**data.model_dump())
    db.add(defn)
    await db.flush()
    await db.refresh(defn)
    return defn


async def list_kpi_definitions(
    db: AsyncSession,
    *,
    programme: str | None = None,
) -> list[KPIDefinition]:
    """List KPI definitions, optionally filtered by programme."""
    stmt = select(KPIDefinition)
    if programme is not None:
        stmt = stmt.where(KPIDefinition.programme == programme)
    stmt = stmt.order_by(KPIDefinition.name)
    return list((await db.execute(stmt)).scalars().all())


async def get_kpi_definition(
    db: AsyncSession, defn_id: uuid.UUID
) -> KPIDefinition | None:
    """Get a single KPI definition."""
    stmt = select(KPIDefinition).where(KPIDefinition.id == defn_id)
    return (await db.execute(stmt)).scalar_one_or_none()


async def update_kpi_definition(
    db: AsyncSession, defn_id: uuid.UUID, data: KPIDefinitionUpdate
) -> KPIDefinition | None:
    """Update a KPI definition."""
    defn = await get_kpi_definition(db, defn_id)
    if defn is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(defn, field, value)
    await db.flush()
    await db.refresh(defn)
    return defn


async def delete_kpi_definition(
    db: AsyncSession, defn_id: uuid.UUID
) -> bool:
    """Delete a KPI definition."""
    defn = await get_kpi_definition(db, defn_id)
    if defn is None:
        return False
    await db.delete(defn)
    await db.flush()
    return True


async def create_kpi_value(
    db: AsyncSession, project_id: uuid.UUID, data: KPIValueCreate
) -> KPIValue:
    """Create a KPI value for a project."""
    await _get_project(db, project_id)
    value = KPIValue(project_id=project_id, **data.model_dump())
    db.add(value)
    await db.flush()
    await db.refresh(value)
    return value


async def list_kpi_values(
    db: AsyncSession,
    project_id: uuid.UUID,
    *,
    kpi_definition_id: uuid.UUID | None = None,
) -> list[KPIValue]:
    """List KPI values for a project."""
    stmt = select(KPIValue).where(KPIValue.project_id == project_id)
    if kpi_definition_id is not None:
        stmt = stmt.where(KPIValue.kpi_definition_id == kpi_definition_id)
    stmt = stmt.order_by(KPIValue.recorded_at)
    return list((await db.execute(stmt)).scalars().all())


async def get_kpi_value(
    db: AsyncSession, value_id: uuid.UUID
) -> KPIValue | None:
    """Get a single KPI value."""
    stmt = select(KPIValue).where(KPIValue.id == value_id)
    return (await db.execute(stmt)).scalar_one_or_none()


async def update_kpi_value(
    db: AsyncSession, value_id: uuid.UUID, data: KPIValueUpdate
) -> KPIValue | None:
    """Update a KPI value."""
    value = await get_kpi_value(db, value_id)
    if value is None:
        return None
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(value, field, val)
    await db.flush()
    await db.refresh(value)
    return value


async def delete_kpi_value(db: AsyncSession, value_id: uuid.UUID) -> bool:
    """Delete a KPI value."""
    value = await get_kpi_value(db, value_id)
    if value is None:
        return False
    await db.delete(value)
    await db.flush()
    return True


# ──────────────────────────────────────────────────────
#  9.5 Ethics and Data Management
# ──────────────────────────────────────────────────────


async def create_ethics_requirement(
    db: AsyncSession,
    project_id: uuid.UUID,
    data: EthicsRequirementCreate,
) -> EthicsRequirement:
    """Create an ethics requirement."""
    await _get_project(db, project_id)
    req = EthicsRequirement(project_id=project_id, **data.model_dump())
    db.add(req)
    await db.flush()
    await db.refresh(req)
    return req


async def list_ethics_requirements(
    db: AsyncSession, project_id: uuid.UUID
) -> list[EthicsRequirement]:
    """List ethics requirements for a project."""
    stmt = select(EthicsRequirement).where(
        EthicsRequirement.project_id == project_id,
        EthicsRequirement.deleted_at.is_(None),
    )
    stmt = stmt.order_by(EthicsRequirement.created_at)
    return list((await db.execute(stmt)).scalars().all())


async def get_ethics_requirement(
    db: AsyncSession, req_id: uuid.UUID
) -> EthicsRequirement | None:
    """Get a single ethics requirement."""
    stmt = select(EthicsRequirement).where(
        EthicsRequirement.id == req_id,
        EthicsRequirement.deleted_at.is_(None),
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def update_ethics_requirement(
    db: AsyncSession,
    req_id: uuid.UUID,
    data: EthicsRequirementUpdate,
) -> EthicsRequirement | None:
    """Update an ethics requirement."""
    req = await get_ethics_requirement(db, req_id)
    if req is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(req, field, value)
    await db.flush()
    await db.refresh(req)
    return req


async def delete_ethics_requirement(
    db: AsyncSession, req_id: uuid.UUID
) -> bool:
    """Soft-delete an ethics requirement."""
    req = await get_ethics_requirement(db, req_id)
    if req is None:
        return False
    req.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


async def create_data_management_record(
    db: AsyncSession,
    project_id: uuid.UUID,
    data: DataManagementRecordCreate,
) -> DataManagementRecord:
    """Create a data management record."""
    await _get_project(db, project_id)
    record = DataManagementRecord(
        project_id=project_id, **data.model_dump()
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def list_data_management_records(
    db: AsyncSession, project_id: uuid.UUID
) -> list[DataManagementRecord]:
    """List data management records for a project."""
    stmt = select(DataManagementRecord).where(
        DataManagementRecord.project_id == project_id,
        DataManagementRecord.deleted_at.is_(None),
    )
    stmt = stmt.order_by(DataManagementRecord.created_at)
    return list((await db.execute(stmt)).scalars().all())


async def get_data_management_record(
    db: AsyncSession, record_id: uuid.UUID
) -> DataManagementRecord | None:
    """Get a single data management record."""
    stmt = select(DataManagementRecord).where(
        DataManagementRecord.id == record_id,
        DataManagementRecord.deleted_at.is_(None),
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def update_data_management_record(
    db: AsyncSession,
    record_id: uuid.UUID,
    data: DataManagementRecordUpdate,
) -> DataManagementRecord | None:
    """Update a data management record."""
    record = await get_data_management_record(db, record_id)
    if record is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    await db.flush()
    await db.refresh(record)
    return record


async def delete_data_management_record(
    db: AsyncSession, record_id: uuid.UUID
) -> bool:
    """Soft-delete a data management record."""
    record = await get_data_management_record(db, record_id)
    if record is None:
        return False
    record.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


# ──────────────────────────────────────────────────────
#  9.6 Collaboration Network
# ──────────────────────────────────────────────────────


async def create_collaboration_record(
    db: AsyncSession, data: CollaborationRecordCreate
) -> CollaborationRecord:
    """Create a collaboration record."""
    record = CollaborationRecord(**data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def list_collaboration_records(
    db: AsyncSession,
    *,
    partner_id: uuid.UUID | None = None,
    project_id: uuid.UUID | None = None,
) -> list[CollaborationRecord]:
    """List collaboration records, optionally filtered."""
    stmt = select(CollaborationRecord)
    if partner_id is not None:
        stmt = stmt.where(CollaborationRecord.partner_id == partner_id)
    if project_id is not None:
        stmt = stmt.where(CollaborationRecord.project_id == project_id)
    stmt = stmt.order_by(CollaborationRecord.created_at)
    return list((await db.execute(stmt)).scalars().all())


async def get_collaboration_record(
    db: AsyncSession, record_id: uuid.UUID
) -> CollaborationRecord | None:
    """Get a single collaboration record."""
    stmt = select(CollaborationRecord).where(
        CollaborationRecord.id == record_id
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def update_collaboration_record(
    db: AsyncSession,
    record_id: uuid.UUID,
    data: CollaborationRecordUpdate,
) -> CollaborationRecord | None:
    """Update a collaboration record."""
    record = await get_collaboration_record(db, record_id)
    if record is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    await db.flush()
    await db.refresh(record)
    return record


async def delete_collaboration_record(
    db: AsyncSession, record_id: uuid.UUID
) -> bool:
    """Delete a collaboration record."""
    record = await get_collaboration_record(db, record_id)
    if record is None:
        return False
    await db.delete(record)
    await db.flush()
    return True


# ──────────────────────────────────────────────────────
#  9.7 Amendment Tracking
# ──────────────────────────────────────────────────────


async def create_amendment(
    db: AsyncSession, project_id: uuid.UUID, data: AmendmentCreate
) -> Amendment:
    """Create an amendment."""
    await _get_project(db, project_id)
    amendment = Amendment(project_id=project_id, **data.model_dump())
    db.add(amendment)
    await db.flush()
    await db.refresh(amendment)
    return amendment


async def list_amendments(
    db: AsyncSession, project_id: uuid.UUID
) -> list[Amendment]:
    """List amendments for a project."""
    stmt = select(Amendment).where(
        Amendment.project_id == project_id,
        Amendment.deleted_at.is_(None),
    )
    stmt = stmt.order_by(Amendment.amendment_number)
    return list((await db.execute(stmt)).scalars().all())


async def get_amendment(
    db: AsyncSession, amendment_id: uuid.UUID
) -> Amendment | None:
    """Get a single amendment."""
    stmt = select(Amendment).where(
        Amendment.id == amendment_id,
        Amendment.deleted_at.is_(None),
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def update_amendment(
    db: AsyncSession, amendment_id: uuid.UUID, data: AmendmentUpdate
) -> Amendment | None:
    """Update an amendment."""
    amendment = await get_amendment(db, amendment_id)
    if amendment is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(amendment, field, value)
    await db.flush()
    await db.refresh(amendment)
    return amendment


async def delete_amendment(
    db: AsyncSession, amendment_id: uuid.UUID
) -> bool:
    """Soft-delete an amendment."""
    amendment = await get_amendment(db, amendment_id)
    if amendment is None:
        return False
    amendment.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return True


# ──────────────────────────────────────────────────────
#  9.8 Notification System
# ──────────────────────────────────────────────────────


async def create_notification(
    db: AsyncSession, data: NotificationCreate
) -> Notification:
    """Create a notification."""
    notification = Notification(**data.model_dump())
    db.add(notification)
    await db.flush()
    await db.refresh(notification)
    return notification


async def list_notifications(
    db: AsyncSession,
    *,
    project_id: uuid.UUID | None = None,
    status: NotificationStatus | None = None,
    recipient_email: str | None = None,
) -> list[Notification]:
    """List notifications with optional filters."""
    stmt = select(Notification)
    if project_id is not None:
        stmt = stmt.where(Notification.project_id == project_id)
    if status is not None:
        stmt = stmt.where(Notification.status == status)
    if recipient_email is not None:
        stmt = stmt.where(Notification.recipient_email == recipient_email)
    stmt = stmt.order_by(Notification.created_at.desc())
    return list((await db.execute(stmt)).scalars().all())


async def get_notification(
    db: AsyncSession, notification_id: uuid.UUID
) -> Notification | None:
    """Get a single notification."""
    stmt = select(Notification).where(Notification.id == notification_id)
    return (await db.execute(stmt)).scalar_one_or_none()


async def update_notification(
    db: AsyncSession,
    notification_id: uuid.UUID,
    data: NotificationUpdate,
) -> Notification | None:
    """Update a notification."""
    notification = await get_notification(db, notification_id)
    if notification is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(notification, field, value)
    await db.flush()
    await db.refresh(notification)
    return notification


async def mark_notification_read(
    db: AsyncSession, notification_id: uuid.UUID
) -> Notification | None:
    """Mark a notification as read."""
    notification = await get_notification(db, notification_id)
    if notification is None:
        return None
    notification.status = NotificationStatus.READ
    notification.read_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(notification)
    return notification


async def mark_notification_sent(
    db: AsyncSession, notification_id: uuid.UUID
) -> Notification | None:
    """Mark a notification as sent."""
    notification = await get_notification(db, notification_id)
    if notification is None:
        return None
    notification.status = NotificationStatus.SENT
    notification.sent_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(notification)
    return notification


async def dismiss_notification(
    db: AsyncSession, notification_id: uuid.UUID
) -> Notification | None:
    """Dismiss a notification."""
    notification = await get_notification(db, notification_id)
    if notification is None:
        return None
    notification.status = NotificationStatus.DISMISSED
    notification.dismissed_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(notification)
    return notification


async def delete_notification(
    db: AsyncSession, notification_id: uuid.UUID
) -> bool:
    """Delete a notification."""
    notification = await get_notification(db, notification_id)
    if notification is None:
        return False
    await db.delete(notification)
    await db.flush()
    return True
