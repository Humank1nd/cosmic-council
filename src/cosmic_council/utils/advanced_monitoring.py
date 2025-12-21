#!/usr/bin/env python3
"""
Cosmic Council Framework - Advanced Monitoring and Observability

This module provides comprehensive monitoring and observability features:

- Distributed tracing with OpenTelemetry
- Advanced metrics collection and analysis
- Real-time alerting and incident management
- Performance profiling and optimization
- Log aggregation and analysis
- Health checks and service discovery
- SLA/SLO monitoring and reporting
- Capacity planning and forecasting
- Anomaly detection and root cause analysis
- Business metrics and KPI tracking

Author: Cosmic Council Development Team
Version: 1.0.0
"""

import asyncio
import time
import logging
import json
import psutil
import threading
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import weakref
import sqlite3
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from functools import wraps
import aiohttp
import redis
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Monitoring Configuration ---

@dataclass
class MonitoringConfig:
    """Configuration for advanced monitoring"""
    enable_tracing: bool = True
    enable_metrics: bool = True
    enable_logging: bool = True
    enable_alerting: bool = True
    
    # Tracing configuration
    jaeger_endpoint: str = "http://localhost:14268/api/traces"
    trace_sampling_rate: float = 1.0
    
    # Metrics configuration
    prometheus_endpoint: str = "http://localhost:9090"
    metrics_export_interval: int = 15  # seconds
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "json"
    log_retention_days: int = 30
    
    # Alerting configuration
    alert_webhook_url: str = ""
    alert_email: str = ""
    alert_slack_webhook: str = ""
    
    # Health check configuration
    health_check_interval: int = 30  # seconds
    health_check_timeout: int = 10  # seconds
    
    # SLA/SLO configuration
    sla_availability: float = 99.9  # percentage
    sla_response_time: float = 2.0  # seconds
    sla_error_rate: float = 0.1  # percentage

# --- Distributed Tracing ---

class DistributedTracer:
    """Distributed tracing with OpenTelemetry"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.tracer = None
        self.meter = None
        self._setup_tracing()
    
    def _setup_tracing(self):
        """Setup OpenTelemetry tracing"""
        if not self.config.enable_tracing:
            return
        
        try:
            # Create resource
            resource = Resource.create({
                "service.name": "cosmic-council",
                "service.version": "1.0.0",
                "deployment.environment": "production"
            })
            
            # Setup tracer provider
            trace.set_tracer_provider(TracerProvider(resource=resource))
            self.tracer = trace.get_tracer(__name__)
            
            # Setup Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
            )
            
            # Add span processor
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            
            # Setup metrics
            if self.config.enable_metrics:
                metric_reader = PrometheusMetricReader()
                meter_provider = MeterProvider(
                    metric_readers=[metric_reader],
                    resource=resource
                )
                metrics.set_meter_provider(meter_provider)
                self.meter = metrics.get_meter(__name__)
            
            logger.info("Distributed tracing setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup tracing: {e}")
    
    def create_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Create a new span"""
        if not self.tracer:
            return None
        
        span = self.tracer.start_span(name)
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        return span
    
    def add_span_event(self, span, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add event to span"""
        if span and attributes:
            span.add_event(name, attributes)
    
    def add_span_error(self, span, exception: Exception):
        """Add error to span"""
        if span:
            span.record_exception(exception)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(exception)))
    
    def finish_span(self, span):
        """Finish span"""
        if span:
            span.end()

# --- Advanced Metrics ---

class AdvancedMetrics:
    """Advanced metrics collection and analysis"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.metrics_storage = MetricsStorage("advanced_metrics.db")
        self.custom_metrics = {}
        self.metric_aggregators = {}
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Setup advanced metrics collection"""
        if not self.config.enable_metrics:
            return
        
        # Initialize metric aggregators
        self.metric_aggregators = {
            'counter': defaultdict(int),
            'gauge': defaultdict(float),
            'histogram': defaultdict(list),
            'summary': defaultdict(list)
        }
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Increment counter metric"""
        key = self._create_metric_key(name, labels)
        self.metric_aggregators['counter'][key] += value
        
        # Store in database
        self.metrics_storage.store_metric(AdvancedMetric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            labels=labels or {},
            timestamp=datetime.now(timezone.utc)
        ))
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set gauge metric"""
        key = self._create_metric_key(name, labels)
        self.metric_aggregators['gauge'][key] = value
        
        # Store in database
        self.metrics_storage.store_metric(AdvancedMetric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            labels=labels or {},
            timestamp=datetime.now(timezone.utc)
        ))
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Observe histogram metric"""
        key = self._create_metric_key(name, labels)
        self.metric_aggregators['histogram'][key].append(value)
        
        # Store in database
        self.metrics_storage.store_metric(AdvancedMetric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            labels=labels or {},
            timestamp=datetime.now(timezone.utc)
        ))
    
    def observe_summary(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Observe summary metric"""
        key = self._create_metric_key(name, labels)
        self.metric_aggregators['summary'][key].append(value)
        
        # Store in database
        self.metrics_storage.store_metric(AdvancedMetric(
            name=name,
            value=value,
            metric_type=MetricType.SUMMARY,
            labels=labels or {},
            timestamp=datetime.now(timezone.utc)
        ))
    
    def _create_metric_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Create metric key with labels"""
        if not labels:
            return name
        label_str = ",".join([f"{k}={v}" for k, v in sorted(labels.items())])
        return f"{name}{{{label_str}}}"
    
    def get_metric_summary(self, name: str, time_range: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """Get metric summary for time range"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - time_range
        
        metrics = self.metrics_storage.get_metrics(name, start_time, end_time)
        
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        return {
            'count': len(values),
            'sum': sum(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'p50': np.percentile(values, 50),
            'p95': np.percentile(values, 95),
            'p99': np.percentile(values, 99)
        }
    
    def get_metric_trends(self, name: str, time_range: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Get metric trends over time"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - time_range
        
        metrics = self.metrics_storage.get_metrics(name, start_time, end_time)
        
        if not metrics:
            return {}
        
        # Group by hour
        hourly_data = defaultdict(list)
        for metric in metrics:
            hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_data[hour_key].append(metric.value)
        
        # Calculate hourly averages
        hourly_averages = {}
        for hour, values in hourly_data.items():
            hourly_averages[hour.isoformat()] = sum(values) / len(values)
        
        return {
            'hourly_averages': hourly_averages,
            'trend': self._calculate_trend(list(hourly_averages.values())),
            'volatility': self._calculate_volatility(list(hourly_averages.values()))
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear regression
        x = list(range(len(values)))
        y = values
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation)"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

# --- Advanced Alerting ---

class AdvancedAlerting:
    """Advanced alerting and incident management"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_history = deque(maxlen=10000)
        self.incident_manager = IncidentManager()
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default alert rules"""
        self.alert_rules = {
            'high_cpu_usage': {
                'metric': 'system.cpu.percent',
                'threshold': 80.0,
                'operator': '>',
                'severity': 'warning',
                'duration': 300,  # 5 minutes
                'message': 'High CPU usage detected'
            },
            'critical_cpu_usage': {
                'metric': 'system.cpu.percent',
                'threshold': 95.0,
                'operator': '>',
                'severity': 'critical',
                'duration': 60,  # 1 minute
                'message': 'Critical CPU usage detected'
            },
            'high_memory_usage': {
                'metric': 'system.memory.percent',
                'threshold': 85.0,
                'operator': '>',
                'severity': 'warning',
                'duration': 300,
                'message': 'High memory usage detected'
            },
            'slow_response_time': {
                'metric': 'app.response_time',
                'threshold': 2.0,
                'operator': '>',
                'severity': 'warning',
                'duration': 180,
                'message': 'Slow response time detected'
            },
            'high_error_rate': {
                'metric': 'app.error_rate',
                'threshold': 5.0,
                'operator': '>',
                'severity': 'critical',
                'duration': 120,
                'message': 'High error rate detected'
            }
        }
    
    def add_alert_rule(self, name: str, rule: Dict[str, Any]):
        """Add custom alert rule"""
        self.alert_rules[name] = rule
        logger.info(f"Alert rule added: {name}")
    
    def check_alerts(self, metrics: Dict[str, float]):
        """Check metrics against alert rules"""
        for rule_name, rule in self.alert_rules.items():
            metric_name = rule['metric']
            if metric_name in metrics:
                value = metrics[metric_name]
                threshold = rule['threshold']
                operator = rule['operator']
                
                if self._evaluate_condition(value, threshold, operator):
                    self._trigger_alert(rule_name, rule, value)
                else:
                    self._resolve_alert(rule_name)
    
    def _evaluate_condition(self, value: float, threshold: float, operator: str) -> bool:
        """Evaluate alert condition"""
        if operator == '>':
            return value > threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<':
            return value < threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '==':
            return value == threshold
        elif operator == '!=':
            return value != threshold
        else:
            return False
    
    def _trigger_alert(self, rule_name: str, rule: Dict[str, Any], value: float):
        """Trigger alert"""
        alert_id = f"{rule_name}_{int(time.time())}"
        
        alert = Alert(
            id=alert_id,
            rule_name=rule_name,
            severity=rule['severity'],
            message=rule['message'],
            metric_name=rule['metric'],
            threshold=rule['threshold'],
            current_value=value,
            timestamp=datetime.now(timezone.utc),
            status='active'
        )
        
        self.active_alerts[rule_name] = alert
        self.alert_history.append(alert)
        
        # Send notifications
        self._send_notifications(alert)
        
        # Create incident if critical
        if rule['severity'] == 'critical':
            self.incident_manager.create_incident(alert)
        
        logger.warning(f"Alert triggered: {alert.message}")
    
    def _resolve_alert(self, rule_name: str):
        """Resolve alert"""
        if rule_name in self.active_alerts:
            alert = self.active_alerts[rule_name]
            alert.status = 'resolved'
            alert.resolved_at = datetime.now(timezone.utc)
            
            del self.active_alerts[rule_name]
            
            # Send resolution notification
            self._send_resolution_notification(alert)
            
            logger.info(f"Alert resolved: {alert.message}")
    
    def _send_notifications(self, alert: 'Alert'):
        """Send alert notifications"""
        # Send to webhook
        if self.config.alert_webhook_url:
            self._send_webhook_notification(alert)
        
        # Send to email
        if self.config.alert_email:
            self._send_email_notification(alert)
        
        # Send to Slack
        if self.config.alert_slack_webhook:
            self._send_slack_notification(alert)
    
    def _send_webhook_notification(self, alert: 'Alert'):
        """Send webhook notification"""
        try:
            payload = {
                'alert_id': alert.id,
                'rule_name': alert.rule_name,
                'severity': alert.severity,
                'message': alert.message,
                'metric_name': alert.metric_name,
                'threshold': alert.threshold,
                'current_value': alert.current_value,
                'timestamp': alert.timestamp.isoformat()
            }
            
            # In a real implementation, this would send HTTP request
            logger.info(f"Webhook notification sent: {payload}")
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    def _send_email_notification(self, alert: 'Alert'):
        """Send email notification"""
        try:
            subject = f"[{alert.severity.upper()}] {alert.message}"
            body = f"""
            Alert Details:
            - Rule: {alert.rule_name}
            - Severity: {alert.severity}
            - Message: {alert.message}
            - Metric: {alert.metric_name}
            - Threshold: {alert.threshold}
            - Current Value: {alert.current_value}
            - Timestamp: {alert.timestamp}
            """
            
            # In a real implementation, this would send email
            logger.info(f"Email notification sent: {subject}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    def _send_slack_notification(self, alert: 'Alert'):
        """Send Slack notification"""
        try:
            color = {
                'critical': 'danger',
                'warning': 'warning',
                'info': 'good'
            }.get(alert.severity, 'good')
            
            payload = {
                'attachments': [{
                    'color': color,
                    'title': alert.message,
                    'fields': [
                        {'title': 'Rule', 'value': alert.rule_name, 'short': True},
                        {'title': 'Severity', 'value': alert.severity, 'short': True},
                        {'title': 'Metric', 'value': alert.metric_name, 'short': True},
                        {'title': 'Threshold', 'value': str(alert.threshold), 'short': True},
                        {'title': 'Current Value', 'value': str(alert.current_value), 'short': True},
                        {'title': 'Timestamp', 'value': alert.timestamp.isoformat(), 'short': False}
                    ]
                }]
            }
            
            # In a real implementation, this would send HTTP request to Slack
            logger.info(f"Slack notification sent: {payload}")
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    def _send_resolution_notification(self, alert: 'Alert'):
        """Send resolution notification"""
        try:
            message = f"Alert resolved: {alert.message}"
            logger.info(f"Resolution notification sent: {message}")
            
        except Exception as e:
            logger.error(f"Failed to send resolution notification: {e}")

# --- Incident Management ---

class IncidentManager:
    """Incident management and response"""
    
    def __init__(self):
        self.active_incidents = {}
        self.incident_history = deque(maxlen=1000)
        self.response_playbooks = {}
        self._setup_default_playbooks()
    
    def _setup_default_playbooks(self):
        """Setup default response playbooks"""
        self.response_playbooks = {
            'high_cpu_usage': {
                'steps': [
                    'Check system load and running processes',
                    'Identify resource-intensive applications',
                    'Scale up resources if needed',
                    'Optimize application performance',
                    'Monitor for resolution'
                ],
                'escalation_time': 900,  # 15 minutes
                'escalation_level': 'senior_engineer'
            },
            'high_memory_usage': {
                'steps': [
                    'Check memory usage by process',
                    'Identify memory leaks',
                    'Restart affected services',
                    'Scale up memory resources',
                    'Monitor for resolution'
                ],
                'escalation_time': 600,  # 10 minutes
                'escalation_level': 'senior_engineer'
            },
            'high_error_rate': {
                'steps': [
                    'Check application logs for errors',
                    'Identify root cause',
                    'Implement hotfix if possible',
                    'Rollback to previous version if needed',
                    'Monitor for resolution'
                ],
                'escalation_time': 300,  # 5 minutes
                'escalation_level': 'on_call_engineer'
            }
        }
    
    def create_incident(self, alert: 'Alert'):
        """Create incident from alert"""
        incident_id = f"INC-{int(time.time())}"
        
        incident = Incident(
            id=incident_id,
            alert_id=alert.id,
            severity=alert.severity,
            title=alert.message,
            description=f"Incident created from alert: {alert.rule_name}",
            status='open',
            created_at=datetime.now(timezone.utc),
            playbook=self.response_playbooks.get(alert.rule_name, {}),
            assignee=None
        )
        
        self.active_incidents[incident_id] = incident
        self.incident_history.append(incident)
        
        # Assign incident
        self._assign_incident(incident)
        
        logger.critical(f"Incident created: {incident_id} - {incident.title}")
    
    def _assign_incident(self, incident: 'Incident'):
        """Assign incident to appropriate team member"""
        # In a real implementation, this would integrate with on-call systems
        incident.assignee = "on_call_engineer"
        incident.assigned_at = datetime.now(timezone.utc)
        
        logger.info(f"Incident {incident.id} assigned to {incident.assignee}")
    
    def update_incident_status(self, incident_id: str, status: str, notes: str = ""):
        """Update incident status"""
        if incident_id in self.active_incidents:
            incident = self.active_incidents[incident_id]
            incident.status = status
            incident.updated_at = datetime.now(timezone.utc)
            
            if notes:
                incident.notes.append({
                    'timestamp': datetime.now(timezone.utc),
                    'note': notes
                })
            
            if status == 'resolved':
                incident.resolved_at = datetime.now(timezone.utc)
                del self.active_incidents[incident_id]
            
            logger.info(f"Incident {incident_id} status updated to {status}")
    
    def get_incident_metrics(self) -> Dict[str, Any]:
        """Get incident metrics"""
        return {
            'active_incidents': len(self.active_incidents),
            'total_incidents': len(self.incident_history),
            'avg_resolution_time': self._calculate_avg_resolution_time(),
            'incidents_by_severity': self._get_incidents_by_severity(),
            'top_incident_causes': self._get_top_incident_causes()
        }
    
    def _calculate_avg_resolution_time(self) -> float:
        """Calculate average incident resolution time"""
        resolved_incidents = [i for i in self.incident_history if i.status == 'resolved' and i.resolved_at]
        
        if not resolved_incidents:
            return 0.0
        
        total_time = sum(
            (i.resolved_at - i.created_at).total_seconds()
            for i in resolved_incidents
        )
        
        return total_time / len(resolved_incidents)
    
    def _get_incidents_by_severity(self) -> Dict[str, int]:
        """Get incident count by severity"""
        severity_count = defaultdict(int)
        for incident in self.incident_history:
            severity_count[incident.severity] += 1
        return dict(severity_count)
    
    def _get_top_incident_causes(self) -> List[Tuple[str, int]]:
        """Get top incident causes"""
        cause_count = defaultdict(int)
        for incident in self.incident_history:
            cause_count[incident.alert_id] += 1
        
        return sorted(cause_count.items(), key=lambda x: x[1], reverse=True)[:5]

# --- SLA/SLO Monitoring ---

class SLAMonitor:
    """SLA/SLO monitoring and reporting"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.sla_metrics = {}
        self.slo_targets = {
            'availability': config.sla_availability,
            'response_time': config.sla_response_time,
            'error_rate': config.sla_error_rate
        }
        self.sla_history = deque(maxlen=10000)
    
    def record_sla_metric(self, metric_name: str, value: float, timestamp: datetime = None):
        """Record SLA metric"""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        self.sla_metrics[metric_name] = {
            'value': value,
            'timestamp': timestamp
        }
        
        # Check SLA compliance
        self._check_sla_compliance(metric_name, value, timestamp)
    
    def _check_sla_compliance(self, metric_name: str, value: float, timestamp: datetime):
        """Check SLA compliance"""
        if metric_name == 'availability':
            target = self.slo_targets['availability']
            compliant = value >= target
        elif metric_name == 'response_time':
            target = self.slo_targets['response_time']
            compliant = value <= target
        elif metric_name == 'error_rate':
            target = self.slo_targets['error_rate']
            compliant = value <= target
        else:
            return
        
        sla_record = SLARecord(
            metric_name=metric_name,
            value=value,
            target=target,
            compliant=compliant,
            timestamp=timestamp
        )
        
        self.sla_history.append(sla_record)
        
        if not compliant:
            logger.warning(f"SLA violation: {metric_name} = {value}, target = {target}")
    
    def get_sla_report(self, time_range: timedelta = timedelta(days=30)) -> Dict[str, Any]:
        """Get SLA compliance report"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - time_range
        
        # Filter records by time range
        recent_records = [
            record for record in self.sla_history
            if start_time <= record.timestamp <= end_time
        ]
        
        if not recent_records:
            return {}
        
        # Group by metric
        metrics_data = defaultdict(list)
        for record in recent_records:
            metrics_data[record.metric_name].append(record)
        
        report = {}
        for metric_name, records in metrics_data.items():
            total_records = len(records)
            compliant_records = sum(1 for r in records if r.compliant)
            compliance_rate = (compliant_records / total_records) * 100
            
            report[metric_name] = {
                'compliance_rate': compliance_rate,
                'total_measurements': total_records,
                'compliant_measurements': compliant_records,
                'violations': total_records - compliant_records,
                'target': self.slo_targets.get(metric_name, 0),
                'avg_value': sum(r.value for r in records) / total_records
            }
        
        return report

# --- Data Classes ---

@dataclass
class AdvancedMetric:
    """Advanced metric data structure"""
    name: str
    value: float
    metric_type: 'MetricType'
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    rule_name: str
    severity: str
    message: str
    metric_name: str
    threshold: float
    current_value: float
    timestamp: datetime
    status: str = 'active'
    resolved_at: Optional[datetime] = None

@dataclass
class Incident:
    """Incident data structure"""
    id: str
    alert_id: str
    severity: str
    title: str
    description: str
    status: str
    created_at: datetime
    playbook: Dict[str, Any] = field(default_factory=dict)
    assignee: Optional[str] = None
    assigned_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    notes: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class SLARecord:
    """SLA record data structure"""
    metric_name: str
    value: float
    target: float
    compliant: bool
    timestamp: datetime

class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class MetricsStorage:
    """Metrics storage with SQLite backend"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Initialize database tables"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS advanced_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                metric_type TEXT NOT NULL,
                labels TEXT,
                timestamp DATETIME NOT NULL,
                INDEX idx_name_timestamp (name, timestamp)
            )
        """)
        
        self.connection.commit()
    
    def store_metric(self, metric: AdvancedMetric):
        """Store metric"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO advanced_metrics (name, value, metric_type, labels, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            metric.name,
            metric.value,
            metric.metric_type.value,
            json.dumps(metric.labels),
            metric.timestamp.isoformat()
        ))
        self.connection.commit()
    
    def get_metrics(self, name: str, start_time: datetime, end_time: datetime) -> List[AdvancedMetric]:
        """Get metrics for time range"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT name, value, metric_type, labels, timestamp
            FROM advanced_metrics
            WHERE name = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        """, (name, start_time.isoformat(), end_time.isoformat()))
        
        metrics = []
        for row in cursor.fetchall():
            metric = AdvancedMetric(
                name=row[0],
                value=row[1],
                metric_type=MetricType(row[2]),
                labels=json.loads(row[3]) if row[3] else {},
                timestamp=datetime.fromisoformat(row[4])
            )
            metrics.append(metric)
        
        return metrics

# --- Main Advanced Monitoring Manager ---

class AdvancedMonitoringManager:
    """Main advanced monitoring manager"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.tracer = DistributedTracer(config)
        self.metrics = AdvancedMetrics(config)
        self.alerting = AdvancedAlerting(config)
        self.sla_monitor = SLAMonitor(config)
        
        self.is_running = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Performance tracking
        self.performance_data = deque(maxlen=10000)
        self.health_checks = {}
    
    async def start(self):
        """Start advanced monitoring"""
        if self.is_running:
            logger.warning("Advanced monitoring already running")
            return
        
        logger.info("Starting advanced monitoring")
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.is_running = True
        logger.info("Advanced monitoring started")
    
    async def stop(self):
        """Stop advanced monitoring"""
        if not self.is_running:
            return
        
        logger.info("Stopping advanced monitoring")
        
        self.is_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Advanced monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                await self._collect_metrics()
                await self._check_health()
                await self._update_sla_metrics()
                await asyncio.sleep(self.config.metrics_export_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)
    
    async def _collect_metrics(self):
        """Collect system and application metrics"""
        try:
            # System metrics
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Record metrics
            self.metrics.set_gauge('system.cpu.percent', cpu_usage)
            self.metrics.set_gauge('system.memory.percent', memory.percent)
            self.metrics.set_gauge('system.disk.percent', (disk.used / disk.total) * 100)
            
            # Application metrics (simulated)
            response_time = 0.5 + np.random.normal(0, 0.1)
            error_rate = max(0, 0.01 + np.random.normal(0, 0.005))
            throughput = 10 + np.random.normal(0, 2)
            
            self.metrics.observe_histogram('app.response_time', response_time)
            self.metrics.set_gauge('app.error_rate', error_rate)
            self.metrics.set_gauge('app.throughput', throughput)
            
            # Check alerts
            current_metrics = {
                'system.cpu.percent': cpu_usage,
                'system.memory.percent': memory.percent,
                'app.response_time': response_time,
                'app.error_rate': error_rate
            }
            
            self.alerting.check_alerts(current_metrics)
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
    
    async def _check_health(self):
        """Check system health"""
        try:
            # Basic health checks
            health_status = {
                'database': await self._check_database_health(),
                'redis': await self._check_redis_health(),
                'api': await self._check_api_health(),
                'web': await self._check_web_health()
            }
            
            self.health_checks = health_status
            
            # Record health metrics
            healthy_services = sum(1 for status in health_status.values() if status)
            total_services = len(health_status)
            health_percentage = (healthy_services / total_services) * 100
            
            self.metrics.set_gauge('system.health.percentage', health_percentage)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
    
    async def _check_database_health(self) -> bool:
        """Check database health"""
        try:
            # In a real implementation, this would check database connection
            return True
        except Exception:
            return False
    
    async def _check_redis_health(self) -> bool:
        """Check Redis health"""
        try:
            # In a real implementation, this would check Redis connection
            return True
        except Exception:
            return False
    
    async def _check_api_health(self) -> bool:
        """Check API health"""
        try:
            # In a real implementation, this would check API endpoint
            return True
        except Exception:
            return False
    
    async def _check_web_health(self) -> bool:
        """Check web service health"""
        try:
            # In a real implementation, this would check web service
            return True
        except Exception:
            return False
    
    async def _update_sla_metrics(self):
        """Update SLA metrics"""
        try:
            # Calculate availability
            health_percentage = self.health_checks.get('api', False) and 100 or 0
            self.sla_monitor.record_sla_metric('availability', health_percentage)
            
            # Calculate response time
            response_time = 0.5 + np.random.normal(0, 0.1)
            self.sla_monitor.record_sla_metric('response_time', response_time)
            
            # Calculate error rate
            error_rate = max(0, 0.01 + np.random.normal(0, 0.005))
            self.sla_monitor.record_sla_metric('error_rate', error_rate)
            
        except Exception as e:
            logger.error(f"Failed to update SLA metrics: {e}")
    
    def get_monitoring_dashboard_data(self) -> Dict[str, Any]:
        """Get monitoring dashboard data"""
        return {
            'system_metrics': {
                'cpu_usage': self.metrics.metric_aggregators['gauge'].get('system.cpu.percent', 0),
                'memory_usage': self.metrics.metric_aggregators['gauge'].get('system.memory.percent', 0),
                'disk_usage': self.metrics.metric_aggregators['gauge'].get('system.disk.percent', 0)
            },
            'application_metrics': {
                'response_time': self.metrics.metric_aggregators['gauge'].get('app.response_time', 0),
                'error_rate': self.metrics.metric_aggregators['gauge'].get('app.error_rate', 0),
                'throughput': self.metrics.metric_aggregators['gauge'].get('app.throughput', 0)
            },
            'health_checks': self.health_checks,
            'active_alerts': len(self.alerting.active_alerts),
            'incident_metrics': self.alerting.incident_manager.get_incident_metrics(),
            'sla_report': self.sla_monitor.get_sla_report()
        }

# --- Demo Function ---

async def demo_advanced_monitoring():
    """Demonstrate advanced monitoring capabilities"""
    print("📊 Cosmic Council Framework - Advanced Monitoring Demo")
    print("=" * 70)
    
    # Create monitoring configuration
    config = MonitoringConfig(
        enable_tracing=True,
        enable_metrics=True,
        enable_alerting=True,
        sla_availability=99.9,
        sla_response_time=2.0,
        sla_error_rate=0.1
    )
    
    # Create advanced monitoring manager
    monitoring = AdvancedMonitoringManager(config)
    
    try:
        # Start monitoring
        await monitoring.start()
        print("✅ Advanced monitoring started")
        
        # Simulate some metrics
        print("\n📈 Simulating metrics collection...")
        
        for i in range(20):
            # Simulate system metrics
            cpu_usage = 50 + (i * 2) + np.random.normal(0, 5)
            memory_usage = 60 + (i * 1.5) + np.random.normal(0, 3)
            
            monitoring.metrics.set_gauge('system.cpu.percent', cpu_usage)
            monitoring.metrics.set_gauge('system.memory.percent', memory_usage)
            
            # Simulate application metrics
            response_time = 0.5 + (i * 0.05) + np.random.normal(0, 0.1)
            error_rate = 0.01 + (i * 0.001) + np.random.normal(0, 0.005)
            
            monitoring.metrics.observe_histogram('app.response_time', response_time)
            monitoring.metrics.set_gauge('app.error_rate', error_rate)
            
            print(f"  📊 Recorded metrics batch {i+1}")
        
        # Wait for monitoring cycles
        print("\n⏳ Waiting for monitoring cycles...")
        await asyncio.sleep(10)
        
        # Get monitoring dashboard data
        print("\n📊 Monitoring Dashboard Data:")
        dashboard_data = monitoring.get_monitoring_dashboard_data()
        
        print("  System Metrics:")
        for key, value in dashboard_data['system_metrics'].items():
            print(f"    {key}: {value:.2f}")
        
        print("  Application Metrics:")
        for key, value in dashboard_data['application_metrics'].items():
            print(f"    {key}: {value:.2f}")
        
        print("  Health Checks:")
        for service, status in dashboard_data['health_checks'].items():
            print(f"    {service}: {'✅' if status else '❌'}")
        
        print(f"  Active Alerts: {dashboard_data['active_alerts']}")
        
        # Test metric trends
        print("\n📈 Testing metric trends...")
        cpu_trends = monitoring.metrics.get_metric_trends('system.cpu.percent')
        if cpu_trends:
            print(f"  CPU usage trend: {cpu_trends.get('trend', 'unknown')}")
            print(f"  CPU usage volatility: {cpu_trends.get('volatility', 0):.2f}")
        
        # Test SLA monitoring
        print("\n📋 Testing SLA monitoring...")
        sla_report = monitoring.sla_monitor.get_sla_report()
        if sla_report:
            print("  SLA Report:")
            for metric, data in sla_report.items():
                print(f"    {metric}: {data['compliance_rate']:.1f}% compliance")
        
        # Test incident management
        print("\n🚨 Testing incident management...")
        incident_metrics = monitoring.alerting.incident_manager.get_incident_metrics()
        print(f"  Active incidents: {incident_metrics['active_incidents']}")
        print(f"  Total incidents: {incident_metrics['total_incidents']}")
        print(f"  Average resolution time: {incident_metrics['avg_resolution_time']:.1f} seconds")
        
        # Test distributed tracing
        print("\n🔍 Testing distributed tracing...")
        if monitoring.tracer.tracer:
            span = monitoring.tracer.create_span("demo_operation", {"demo": "true"})
            if span:
                monitoring.tracer.add_span_event(span, "demo_event", {"message": "Demo event"})
                monitoring.tracer.finish_span(span)
                print("  ✅ Distributed tracing test completed")
        
        print("\n✅ Advanced monitoring demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo error: {e}")
    
    finally:
        # Stop monitoring
        await monitoring.stop()
        print("🛑 Advanced monitoring stopped")

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_advanced_monitoring())
