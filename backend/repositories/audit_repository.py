from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from models.audit_log import AuditLog
from datetime import datetime, timedelta
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

class AuditRepository:
    """
    Repository for audit logging operations
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def log_action(
        self,
        table_name: str,
        record_id: str,
        action: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log an audit action
        
        Args:
            table_name: Name of the table being modified
            record_id: ID of the record being modified
            action: Action performed (CREATE, UPDATE, DELETE)
            old_values: Previous values (for UPDATE and DELETE)
            new_values: New values (for CREATE and UPDATE)
            user_id: ID of user performing action
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            Created audit log entry
        """
        try:
            audit_log = AuditLog(
                id=str(uuid4()),
                table_name=table_name,
                record_id=record_id,
                action=action.upper(),
                old_values=old_values,
                new_values=new_values,
                user_id=user_id,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.add(audit_log)
            self.db.commit()
            self.db.refresh(audit_log)
            
            logger.info(f"Logged audit action: {action} on {table_name}:{record_id}")
            return audit_log
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error logging audit action: {str(e)}")
            raise
    
    def get_audit_trail(
        self,
        table_name: Optional[str] = None,
        record_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit trail with filters
        
        Args:
            table_name: Filter by table name
            record_id: Filter by record ID
            user_id: Filter by user ID
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of records to return
            
        Returns:
            List of audit log entries
        """
        try:
            query = self.db.query(AuditLog)
            
            # Apply filters
            if table_name:
                query = query.filter(AuditLog.table_name == table_name)
            
            if record_id:
                query = query.filter(AuditLog.record_id == record_id)
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)
            
            return query.order_by(desc(AuditLog.timestamp)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting audit trail: {str(e)}")
            raise
    
    def get_audit_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get audit statistics for the specified period
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with audit statistics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Total actions
            total_actions = self.db.query(AuditLog).filter(
                AuditLog.timestamp >= cutoff_date
            ).count()
            
            # Actions by type
            action_counts = self.db.query(
                AuditLog.action,
                func.count(AuditLog.action).label('count')
            ).filter(
                AuditLog.timestamp >= cutoff_date
            ).group_by(AuditLog.action).all()
            
            # Most active tables
            table_counts = self.db.query(
                AuditLog.table_name,
                func.count(AuditLog.table_name).label('count')
            ).filter(
                AuditLog.timestamp >= cutoff_date
            ).group_by(AuditLog.table_name).order_by(
                desc('count')
            ).limit(10).all()
            
            # Most active users
            user_counts = self.db.query(
                AuditLog.user_id,
                func.count(AuditLog.user_id).label('count')
            ).filter(
                and_(
                    AuditLog.timestamp >= cutoff_date,
                    AuditLog.user_id.isnot(None)
                )
            ).group_by(AuditLog.user_id).order_by(
                desc('count')
            ).limit(10).all()
            
            return {
                "period_days": days,
                "total_actions": total_actions,
                "actions_by_type": {action: count for action, count in action_counts},
                "most_active_tables": [
                    {"table": table, "actions": count} 
                    for table, count in table_counts
                ],
                "most_active_users": [
                    {"user_id": user, "actions": count} 
                    for user, count in user_counts
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting audit statistics: {str(e)}")
            raise