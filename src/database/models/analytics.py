"""
Analytics and system metrics database models.
"""

from sqlalchemy import Column, String, Text, Float, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel


class SystemMetrics(BaseModel):
    """System performance metrics"""
    __tablename__ = 'system_metrics'
    
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(String(255), nullable=False)
    metric_type = Column(String(50), nullable=False)  # 'counter', 'gauge', 'histogram'
    tags = Column(Text)  # JSON string
    timestamp = Column(DateTime, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<SystemMetrics(name={self.metric_name}, value={self.metric_value})>"


class AuditLog(BaseModel):
    """Audit log for system activities"""
    __tablename__ = 'audit_logs'
    
    user_id = Column(UUID(as_uuid=True))
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(255), nullable=False, index=True)
    details = Column(Text)  # JSON string
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<AuditLog(action={self.action}, resource={self.resource_type}:{self.resource_id})>"


class CycleAnalytics(BaseModel):
    """Analytics for cycles"""
    __tablename__ = 'cycle_analytics'
    
    cycle_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(String(255), nullable=False)
    metric_type = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<CycleAnalytics(cycle_id={self.cycle_id}, metric={self.metric_name})>"


class ImplementationTracking(BaseModel):
    """Track implementation progress"""
    __tablename__ = 'implementation_tracking'
    
    solution_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    component_id = Column(UUID(as_uuid=True))
    status = Column(String(20), nullable=False)  # 'not_started', 'in_progress', 'completed', 'blocked'
    progress_percentage = Column(String(10), default='0')  # Store as string for flexibility
    notes = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    def __repr__(self) -> str:
        return f"<ImplementationTracking(solution_id={self.solution_id}, status={self.status})>"
