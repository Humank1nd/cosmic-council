"""
PURPLE ELEPHANT - Notification Engine.

Routes notifications to all relevant stakeholders.
This implements Criterion 3: Notification routing.

All parties must be properly notified.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

import structlog

from .models import (
    Stakeholder,
    ResponsibilityAssignment,
    ResponsibilityType,
    NotificationRecord,
    NotificationChannel,
    NotificationPriority,
    PurpleElephantConfig,
)

logger = structlog.get_logger(__name__)


@dataclass
class NotificationTemplate:
    """Template for notifications."""
    id: str = ""
    name: str = ""
    subject_template: str = ""
    message_template: str = ""
    channels: List[NotificationChannel] = field(default_factory=list)
    priority: NotificationPriority = NotificationPriority.MEDIUM


# Default notification templates
DEFAULT_TEMPLATES: Dict[str, NotificationTemplate] = {
    "assignment": NotificationTemplate(
        id="assignment",
        name="Responsibility Assignment",
        subject_template="[{priority}] Action Assigned: {action_id}",
        message_template="You have been assigned as {responsibility_type} for action: {action_title}\n\nDetails:\n- Action: {action_id}\n- Category: {category}\n- Risk: {risk_level}\n- Due: {due_by}",
        channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL],
        priority=NotificationPriority.MEDIUM,
    ),
    "high_risk_assignment": NotificationTemplate(
        id="high_risk_assignment",
        name="High-Risk Assignment",
        subject_template="[URGENT] High-Risk Action Assigned: {action_id}",
        message_template="URGENT: You have been assigned a HIGH-RISK action.\n\nAction: {action_title}\nRisk Level: {risk_level}\nRequires immediate attention.",
        channels=[NotificationChannel.PAGERDUTY, NotificationChannel.SLACK],
        priority=NotificationPriority.CRITICAL,
    ),
    "approval_request": NotificationTemplate(
        id="approval_request",
        name="Approval Request",
        subject_template="[Approval Required] {action_id}",
        message_template="Your approval is required for:\n\n{action_title}\n\nRisk: {risk_level}\nExecutor: {executor_name}\n\nPlease review and approve or reject.",
        channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL],
        priority=NotificationPriority.HIGH,
    ),
    "observer_notification": NotificationTemplate(
        id="observer_notification",
        name="Observer Notification",
        subject_template="[FYI] Action Scheduled: {action_id}",
        message_template="For your awareness:\n\n{action_title}\n\nThis action affects services you own or monitor.",
        channels=[NotificationChannel.SLACK],
        priority=NotificationPriority.INFO,
    ),
    "escalation": NotificationTemplate(
        id="escalation",
        name="Escalation Notice",
        subject_template="[ESCALATION] Unacknowledged Action: {action_id}",
        message_template="This action has been escalated due to no acknowledgment:\n\n{action_title}\n\nOriginal assignee: {original_assignee}\nTime since assignment: {time_elapsed}",
        channels=[NotificationChannel.PAGERDUTY, NotificationChannel.SLACK],
        priority=NotificationPriority.HIGH,
    ),
}


@dataclass
class NotificationRequest:
    """Request to send a notification."""
    stakeholder: Stakeholder
    assignment: ResponsibilityAssignment
    template_id: str = "assignment"
    priority: Optional[NotificationPriority] = None
    variables: Dict[str, str] = field(default_factory=dict)
    channels: Optional[List[NotificationChannel]] = None


@dataclass
class NotificationResult:
    """Result of sending a notification."""
    record: NotificationRecord
    success: bool = False
    channels_attempted: List[NotificationChannel] = field(default_factory=list)
    channels_succeeded: List[NotificationChannel] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class BatchNotificationResult:
    """Result of sending multiple notifications."""
    records: List[NotificationRecord] = field(default_factory=list)
    sent_count: int = 0
    failed_count: int = 0
    total_channels_used: int = 0
    duration_ms: int = 0


class NotificationEngine:
    """
    Routes and sends notifications to stakeholders.

    Criterion 3: All parties are properly notified.
    """

    def __init__(
        self,
        templates: Optional[Dict[str, NotificationTemplate]] = None,
        config: Optional[PurpleElephantConfig] = None,
    ):
        """
        Initialize the notification engine.

        Args:
            templates: Notification templates
            config: Configuration
        """
        self.templates = templates or DEFAULT_TEMPLATES
        self.config = config or PurpleElephantConfig()

        # Track sent notifications
        self._notification_history: List[NotificationRecord] = []

        logger.info(
            "notification_engine_initialized",
            template_count=len(self.templates),
        )

    async def send(
        self,
        request: NotificationRequest,
    ) -> NotificationResult:
        """
        Send a notification to a stakeholder.

        Args:
            request: Notification request

        Returns:
            NotificationResult
        """
        # Get template
        template = self.templates.get(request.template_id, self.templates["assignment"])

        # Determine priority
        priority = request.priority or template.priority

        # Build message
        variables = self._build_variables(request)
        subject = self._render_template(template.subject_template, variables)
        message = self._render_template(template.message_template, variables)

        # Determine channels
        channels = request.channels or self._get_channels_for_stakeholder(
            request.stakeholder, template, priority
        )

        # Create record
        record = NotificationRecord(
            assignment_id=request.assignment.id,
            stakeholder_id=request.stakeholder.id,
            action_id=request.assignment.action_id,
            priority=priority,
            subject=subject,
            message=message,
        )

        # Send to each channel
        channels_succeeded: List[NotificationChannel] = []
        errors: List[str] = []

        for channel in channels:
            try:
                success = await self._send_to_channel(
                    channel, request.stakeholder, subject, message, priority
                )
                if success:
                    channels_succeeded.append(channel)
                    record.channel = channel  # Record primary channel
            except Exception as e:
                errors.append(f"{channel.value}: {str(e)}")

        # Update record
        record.is_sent = len(channels_succeeded) > 0
        record.sent_at = datetime.utcnow() if record.is_sent else None

        if not record.is_sent and errors:
            record.delivery_error = "; ".join(errors)

        # Track history
        self._notification_history.append(record)

        logger.debug(
            "notification_sent",
            stakeholder=request.stakeholder.name,
            action_id=request.assignment.action_id,
            channels=len(channels_succeeded),
            success=record.is_sent,
        )

        return NotificationResult(
            record=record,
            success=record.is_sent,
            channels_attempted=channels,
            channels_succeeded=channels_succeeded,
            errors=errors,
        )

    async def _send_to_channel(
        self,
        channel: NotificationChannel,
        stakeholder: Stakeholder,
        subject: str,
        message: str,
        priority: NotificationPriority,
    ) -> bool:
        """Send notification to a specific channel."""
        # In a real implementation, this would integrate with actual services
        # For now, we simulate successful delivery

        if channel == NotificationChannel.NONE:
            return False

        # Simulate network delay
        await asyncio.sleep(0.01)

        # Simulate based on stakeholder contact info
        if channel == NotificationChannel.EMAIL:
            if not stakeholder.contact.email:
                return False
        elif channel == NotificationChannel.SLACK:
            if not stakeholder.contact.slack_id and not stakeholder.contact.slack_channel:
                return False
        elif channel == NotificationChannel.PAGERDUTY:
            if not stakeholder.contact.pagerduty_id:
                return False
        elif channel == NotificationChannel.WEBHOOK:
            if not stakeholder.contact.webhook_url:
                return False
        elif channel == NotificationChannel.SMS:
            if not stakeholder.contact.phone:
                return False

        logger.debug(
            "channel_notification_sent",
            channel=channel.value,
            stakeholder=stakeholder.name,
            priority=priority.value,
        )

        return True

    def _build_variables(self, request: NotificationRequest) -> Dict[str, str]:
        """Build template variables from request."""
        assignment = request.assignment
        stakeholder = request.stakeholder

        variables = {
            "action_id": assignment.action_id,
            "action_title": assignment.action_id,  # Would come from context
            "responsibility_type": assignment.responsibility_type.value,
            "stakeholder_name": stakeholder.name,
            "category": request.variables.get("category", ""),
            "risk_level": request.variables.get("risk_level", "MEDIUM"),
            "due_by": assignment.due_by.isoformat() if assignment.due_by else "N/A",
            "priority": request.priority.value if request.priority else "MEDIUM",
            "executor_name": request.variables.get("executor_name", ""),
            "original_assignee": request.variables.get("original_assignee", ""),
            "time_elapsed": request.variables.get("time_elapsed", ""),
        }

        # Merge with any additional variables
        variables.update(request.variables)

        return variables

    def _render_template(self, template: str, variables: Dict[str, str]) -> str:
        """Render a template with variables."""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    def _get_channels_for_stakeholder(
        self,
        stakeholder: Stakeholder,
        template: NotificationTemplate,
        priority: NotificationPriority,
    ) -> List[NotificationChannel]:
        """Determine which channels to use for a stakeholder."""
        channels: List[NotificationChannel] = []

        # Use stakeholder's preferred channel
        preferred = stakeholder.contact.preferred_channel
        if preferred != NotificationChannel.NONE:
            channels.append(preferred)

        # For critical priority, use all available channels
        if priority == NotificationPriority.CRITICAL:
            for channel in template.channels:
                if channel not in channels:
                    channels.append(channel)

        # Fallback to template channels if none selected
        if not channels:
            channels = template.channels.copy()

        return channels

    async def notify_all(
        self,
        assignments: List[ResponsibilityAssignment],
        context: Optional[Dict[str, Any]] = None,
    ) -> BatchNotificationResult:
        """
        Send notifications for all assignments.

        Args:
            assignments: List of assignments to notify
            context: Additional context

        Returns:
            BatchNotificationResult
        """
        start_time = time.time()
        context = context or {}

        records: List[NotificationRecord] = []
        sent_count = 0
        failed_count = 0
        total_channels = 0

        for assignment in assignments:
            if not assignment.stakeholder:
                continue

            # Determine template based on responsibility type and risk
            template_id = self._select_template(assignment, context)
            priority = self._determine_priority(assignment, context)

            request = NotificationRequest(
                stakeholder=assignment.stakeholder,
                assignment=assignment,
                template_id=template_id,
                priority=priority,
                variables={
                    "category": context.get("category", ""),
                    "risk_level": context.get("risk_level", "MEDIUM"),
                    "action_title": context.get(f"action_{assignment.action_id}_title", assignment.action_id),
                },
            )

            result = await self.send(request)
            records.append(result.record)
            total_channels += len(result.channels_succeeded)

            if result.success:
                sent_count += 1
                assignment.notifications_sent.append(result.record.id)
                assignment.last_notification_at = datetime.utcnow()
            else:
                failed_count += 1

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "batch_notifications_complete",
            total=len(assignments),
            sent=sent_count,
            failed=failed_count,
            channels=total_channels,
            duration_ms=duration_ms,
        )

        return BatchNotificationResult(
            records=records,
            sent_count=sent_count,
            failed_count=failed_count,
            total_channels_used=total_channels,
            duration_ms=duration_ms,
        )

    def _select_template(
        self,
        assignment: ResponsibilityAssignment,
        context: Dict[str, Any],
    ) -> str:
        """Select appropriate template for assignment."""
        risk_level = context.get("risk_level", "MEDIUM").upper()

        if risk_level in ["HIGH", "CRITICAL"]:
            if assignment.responsibility_type == ResponsibilityType.APPROVER:
                return "approval_request"
            return "high_risk_assignment"

        if assignment.responsibility_type == ResponsibilityType.APPROVER:
            return "approval_request"

        if assignment.responsibility_type == ResponsibilityType.OBSERVER:
            return "observer_notification"

        return "assignment"

    def _determine_priority(
        self,
        assignment: ResponsibilityAssignment,
        context: Dict[str, Any],
    ) -> NotificationPriority:
        """Determine notification priority."""
        risk_level = context.get("risk_level", "MEDIUM").upper()

        if risk_level == "CRITICAL":
            return NotificationPriority.CRITICAL
        elif risk_level == "HIGH":
            return NotificationPriority.HIGH
        elif assignment.responsibility_type == ResponsibilityType.APPROVER:
            return NotificationPriority.HIGH
        elif assignment.responsibility_type == ResponsibilityType.OBSERVER:
            return NotificationPriority.INFO
        else:
            return NotificationPriority.MEDIUM

    def get_notification_metrics(self) -> Dict[str, Any]:
        """Get notification metrics."""
        total = len(self._notification_history)
        sent = sum(1 for n in self._notification_history if n.is_sent)
        delivered = sum(1 for n in self._notification_history if n.is_delivered)

        by_channel: Dict[str, int] = {}
        by_priority: Dict[str, int] = {}

        for record in self._notification_history:
            channel = record.channel.value if record.channel else "unknown"
            by_channel[channel] = by_channel.get(channel, 0) + 1

            priority = record.priority.value if record.priority else "unknown"
            by_priority[priority] = by_priority.get(priority, 0) + 1

        return {
            "total_notifications": total,
            "sent": sent,
            "delivered": delivered,
            "by_channel": by_channel,
            "by_priority": by_priority,
        }


def create_notification_engine(
    templates: Optional[Dict[str, NotificationTemplate]] = None,
    config: Optional[PurpleElephantConfig] = None,
) -> NotificationEngine:
    """Factory function to create a NotificationEngine."""
    return NotificationEngine(
        templates=templates,
        config=config,
    )
