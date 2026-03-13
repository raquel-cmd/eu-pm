"""Lightweight role-based access control.

Placeholder until full JWT authentication is implemented.
Role is extracted from X-User-Role header; in production this
will come from JWT token claims.
"""

from fastapi import Depends, Header, HTTPException

from app.models.enums import UserRole


async def get_current_role(
    x_user_role: str = Header(default="PI"),
) -> UserRole:
    """Extract user role from X-User-Role header."""
    try:
        return UserRole(x_user_role)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role: {x_user_role}",
        )


async def require_finance_pm(
    role: UserRole = Depends(get_current_role),
) -> UserRole:
    """Require Central Finance PM role for access."""
    if role != UserRole.CENTRAL_FINANCE_PM:
        raise HTTPException(
            status_code=403,
            detail="Access restricted to Central Finance PM",
        )
    return role
