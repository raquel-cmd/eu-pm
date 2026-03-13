"""SQLAlchemy models - import all models here for Alembic autogenerate."""

from app.models.enums import *  # noqa: F401, F403
from app.models.project import Project  # noqa: F401
from app.models.partner import Partner, ProjectPartner  # noqa: F401
from app.models.work_package import Deliverable, Milestone, WorkPackage  # noqa: F401
from app.models.financial import (  # noqa: F401
    BudgetCategoryMapping,
    Expense,
    FundDistribution,
    Mission,
    Procurement,
)
from app.models.researcher import (  # noqa: F401
    EffortAllocation,
    Researcher,
    TimesheetEntry,
)
from app.models.reporting import (  # noqa: F401
    ReportingPeriod,
    ReportReminder,
    ReportSection,
    Risk,
    TechnicalReport,
)
from app.models.financial_reporting import (  # noqa: F401
    FinancialStatement,
    UnitDeliveryRecord,
    WPCompletionDeclaration,
)
from app.models.template import (  # noqa: F401
    DocumentTemplate,
    GeneratedDocument,
)
from app.models.additional_features import (  # noqa: F401
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
