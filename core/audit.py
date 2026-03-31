"""
Audit logging for access control and compliance tracking.

Logs all access attempts (successful and denied) to audit_logs table.
Gracefully handles missing table - doesn't block application startup.
"""

from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from models.audit_log import AuditLog


async def log_access(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: UUID = None,
    db: AsyncSession = None,
    ip_address: str = None,
) -> None:
    """
    Log an access event to the audit_logs table.
    
    Gracefully handles missing table to avoid breaking application.
    
    Args:
        user_id: The user performing the action (from JWT)
        action: Action type - READ, CREATE, UPDATE, DELETE, DENIED
        resource_type: Type of resource - goal, recommendation, sip_plan, etc.
        resource_id: The ID of the resource being accessed (optional for DENIED)
        db: Database session
        ip_address: Client IP address (optional)
    """
    if db is None:
        return  # Skip logging if no DB session provided
    
    try:
        audit_entry = AuditLog(
            user_id=UUID(user_id),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
        )
        
        db.add(audit_entry)
        await db.commit()
    except Exception:
        # Gracefully handle any errors (table doesn't exist, connection issues, etc.)
        # Don't break the application for audit failures
        try:
            await db.rollback()
        except Exception:
            pass  # If rollback fails, just continue

