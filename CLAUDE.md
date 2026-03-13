# EU Research Project Management Application

ALWAYS WRITE IN AMERICAN ENGLISH

## Project Overview

A web application for managing European research-funded projects (Horizon Europe, Digital Europe, Erasmus+, CEF, FCT). Designed for a university research lab that needs to track projects across different programmes, cost models (actual costs, lump sum, unit costs), and roles (coordinator vs partner), while reporting to both the European Commission and university central finance services.

## Technical Architecture

- **Backend**: Python with FastAPI, PostgreSQL database
- **Frontend**: React with TypeScript, Tailwind CSS
- **Authentication**: OAuth2/SAML for institutional SSO, local accounts for external partners
- **File storage**: Local filesystem with metadata in DB (migrateable to S3/cloud later)
- **API style**: RESTful with OpenAPI/Swagger documentation

## Coding Conventions

- Python 3.11+, use type hints everywhere
- Use Pydantic models for API request/response validation
- Use SQLAlchemy 2.0 with async sessions for database access
- Use Alembic for database migrations
- Follow PEP 8, max line length 100
- React components: functional components with hooks, no class components
- Use React Query for server state management
- All monetary amounts stored as Decimal with 2 decimal places
- All dates stored as UTC, displayed in user's timezone
- Write docstrings for all public functions and classes

## Database Conventions

- Table names: snake_case, plural (e.g., `projects`, `work_packages`, `deliverables`)
- Primary keys: UUID v4, column named `id`
- Foreign keys: `{referenced_table_singular}_id` (e.g., `project_id`, `partner_id`)
- Timestamps: `created_at`, `updated_at` on every table, auto-managed
- Soft deletes: `deleted_at` column where applicable
- Enums: stored as PostgreSQL enum types
- JSON fields: use PostgreSQL JSONB

## Project Structure

```
eu-pm/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI route handlers
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── core/          # Config, security, database
│   │   └── templates/     # Document template definitions
│   ├── migrations/        # Alembic migrations
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Route-level page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API client functions
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   └── package.json
├── docs/                  # Technical specification and architecture docs
└── docker-compose.yml     # Local development environment
```

## Key Business Rules

### Cost Model Behavior

The `cost_model` field on each project controls behavior across all modules:

- **Actual Costs**: Full expense tracking, mandatory timesheets, Form C financial reporting, EC eligibility checks, audit documentation required
- **Lump Sum**: WP-level budget monitoring, optional timesheets, WP completion declarations instead of Form C, no EC eligibility checks on individual expenses
- **Unit Costs**: Unit delivery tracking, rate-based calculations, evidence of units delivered
- **Mixed**: Per-WP or per-category overrides, project-level default

### Dual Financial View

Every financial operation must maintain two parallel views:
1. **EC view**: Budget categories A-E per Horizon Europe standard
2. **University view**: Mapped to institutional account codes and overhead methodology

### Role-Based Access

- PI: Full access to own projects
- Researcher: Own timesheets and assigned deliverables
- Central Finance PM: Financial data across all projects (read + export)
- External Partner: Own partner data within shared projects

## Reference Documents

- See `EU_Project_Management_App_Technical_Specification.docx` for the complete data model, module specifications, template library, and reporting workflows
- The spec contains detailed field-level definitions for all entities

## Testing

- Write unit tests for all service layer functions
- Write integration tests for API endpoints
- Use pytest with fixtures for database setup/teardown
- Minimum 80% code coverage for business logic
