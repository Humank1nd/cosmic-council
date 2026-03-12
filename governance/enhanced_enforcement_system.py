"""
Enhanced Cosmic Council Enforcement System
Database-integrated version with improved error handling and performance
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import aiohttp

from code_review_rules import CosmicCouncilCodeReviewer, Violation, ViolationType

logger = logging.getLogger(__name__)

class EnforcementAction(Enum):
    """Types of enforcement actions"""
    WARNING = "warning"
    BLOCK = "block"
    SUSPEND = "suspend"
    BAN = "ban"

class AgentLevel(Enum):
    """Agent experience levels"""
    NOVICE = "novice"
    APPRENTICE = "apprentice"
    JOURNEYMAN = "journeyman"
    MASTER = "master"
    GRANDMASTER = "grandmaster"

@dataclass
class AgentProfile:
    """Agent profile and performance tracking"""
    agent_id: str
    name: str
    stage: str
    level: AgentLevel
    cycles_completed: int
    violations_count: Dict[str, int]
    last_violation: Optional[datetime]
    suspension_count: int
    achievements: List[str]
    performance_score: float
    created_at: datetime
    updated_at: datetime

@dataclass
class EnforcementRecord:
    """Record of enforcement action taken"""
    record_id: str
    agent_id: str
    violation_type: ViolationType
    action_taken: EnforcementAction
    reason: str
    timestamp: datetime
    duration: Optional[int]  # Duration in hours for suspensions
    resolved: bool
    notes: str

class EnhancedCosmicCouncilEnforcementSystem:
    """
    Enhanced enforcement system with database integration and improved error handling
    """
    
    def __init__(self, 
                 database_url: str,
                 n8n_webhook_url: Optional[str] = None,
                 slack_webhook_url: Optional[str] = None,
                 max_retries: int = 3,
                 retry_delay: float = 1.0):
        """
        Initialize the enhanced enforcement system
        
        Args:
            database_url: Database connection for storing enforcement records
            n8n_webhook_url: N8N webhook for automated workflows
            slack_webhook_url: Slack webhook for notifications
            max_retries: Maximum number of retries for failed operations
            retry_delay: Delay between retries in seconds
        """
        self.database_url = database_url
        self.n8n_webhook_url = n8n_webhook_url
        self.slack_webhook_url = slack_webhook_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.code_reviewer = CosmicCouncilCodeReviewer()
        
        # Create async database engine
        self.engine = create_async_engine(database_url)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Enforcement thresholds
        self.thresholds = {
            AgentLevel.NOVICE: {
                'minor_violations': 10,
                'major_violations': 3,
                'critical_violations': 1
            },
            AgentLevel.APPRENTICE: {
                'minor_violations': 8,
                'major_violations': 2,
                'critical_violations': 1
            },
            AgentLevel.JOURNEYMAN: {
                'minor_violations': 6,
                'major_violations': 2,
                'critical_violations': 1
            },
            AgentLevel.MASTER: {
                'minor_violations': 4,
                'major_violations': 1,
                'critical_violations': 1
            },
            AgentLevel.GRANDMASTER: {
                'minor_violations': 2,
                'major_violations': 1,
                'critical_violations': 1
            }
        }
        
        logger.info("Enhanced Cosmic Council Enforcement System initialized")

    async def review_pull_request(self, 
                                pr_data: Dict[str, Any],
                                agent_id: str) -> Dict[str, Any]:
        """
        Review a pull request for rule violations with database persistence
        
        Args:
            pr_data: Pull request data including files and changes
            agent_id: ID of the agent submitting the PR
            
        Returns:
            Review result with violations and enforcement actions
        """
        async with self.async_session() as session:
            try:
                # Get or create agent profile
                agent_profile = await self._get_agent_profile(session, agent_id)
                
                # Review all changed files
                all_violations = []
                for file_data in pr_data.get('files', []):
                    violations = self.code_reviewer.review_file(
                        file_data['path'], 
                        file_data['content']
                    )
                    all_violations.extend(violations)
                
                # Store code review record
                review_id = await self._store_code_review(session, agent_id, pr_data, all_violations)
                
                # Determine enforcement action
                action = await self._determine_enforcement_action(agent_profile, all_violations)
                
                # Create enforcement record if action is not just a warning
                if action != EnforcementAction.WARNING:
                    await self._create_enforcement_record(session, agent_id, all_violations, action)
                
                # Update agent profile
                await self._update_agent_profile(session, agent_profile, all_violations, action)
                
                # Send notifications asynchronously
                asyncio.create_task(self._send_notifications(agent_id, all_violations, action))
                
                # Generate review report
                report = self.code_reviewer.generate_report()
                
                await session.commit()
                
                return {
                    'approved': action == EnforcementAction.WARNING,
                    'action_taken': action.value,
                    'violations_count': len(all_violations),
                    'violations_by_type': self._count_violations_by_type(all_violations),
                    'report': report,
                    'agent_level': agent_profile.level.value,
                    'performance_score': agent_profile.performance_score,
                    'review_id': review_id
                }
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error reviewing pull request: {e}")
                return {
                    'approved': False,
                    'action_taken': 'error',
                    'error': str(e)
                }

    async def _get_agent_profile(self, session: AsyncSession, agent_id: str) -> AgentProfile:
        """Get or create agent profile from database"""
        try:
            # Try to get existing agent
            result = await session.execute(
                text("SELECT * FROM governance_agents WHERE agent_id = :agent_id"),
                {"agent_id": agent_id}
            )
            agent_data = result.fetchone()
            
            if agent_data:
                return AgentProfile(
                    agent_id=agent_data.agent_id,
                    name=agent_data.name,
                    stage=agent_data.stage,
                    level=AgentLevel(agent_data.level),
                    cycles_completed=agent_data.cycles_completed,
                    violations_count=json.loads(agent_data.violations_count),
                    last_violation=agent_data.last_violation,
                    suspension_count=agent_data.suspension_count,
                    achievements=[],  # Will be loaded separately if needed
                    performance_score=float(agent_data.performance_score),
                    created_at=agent_data.created_at,
                    updated_at=agent_data.updated_at
                )
            else:
                # Create new agent profile
                return await self._create_agent_profile(session, agent_id)
                
        except Exception as e:
            logger.error(f"Error getting agent profile: {e}")
            # Fallback to creating new profile
            return await self._create_agent_profile(session, agent_id)

    async def _create_agent_profile(self, session: AsyncSession, agent_id: str) -> AgentProfile:
        """Create a new agent profile"""
        try:
            # Determine stage from agent_id or default to 'unknown'
            stage = self._determine_agent_stage(agent_id)
            
            # Create agent profile
            agent_profile = AgentProfile(
                agent_id=agent_id,
                name=f"Agent_{agent_id}",
                stage=stage,
                level=AgentLevel.NOVICE,
                cycles_completed=0,
                violations_count={'minor': 0, 'major': 0, 'critical': 0},
                last_violation=None,
                suspension_count=0,
                achievements=[],
                performance_score=100.0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            # Insert into database
            await session.execute(
                text("""
                    INSERT INTO governance_agents (
                        agent_id, name, stage, level, cycles_completed,
                        violations_count, performance_score, created_at, updated_at
                    ) VALUES (
                        :agent_id, :name, :stage, :level, :cycles_completed,
                        :violations_count, :performance_score, :created_at, :updated_at
                    )
                """),
                {
                    'agent_id': agent_profile.agent_id,
                    'name': agent_profile.name,
                    'stage': agent_profile.stage,
                    'level': agent_profile.level.value,
                    'cycles_completed': agent_profile.cycles_completed,
                    'violations_count': json.dumps(agent_profile.violations_count),
                    'performance_score': agent_profile.performance_score,
                    'created_at': agent_profile.created_at,
                    'updated_at': agent_profile.updated_at
                }
            )
            
            logger.info(f"Created new agent profile: {agent_id}")
            return agent_profile
            
        except Exception as e:
            logger.error(f"Error creating agent profile: {e}")
            raise

    def _determine_agent_stage(self, agent_id: str) -> str:
        """Determine agent stage from agent_id"""
        agent_id_lower = agent_id.lower()
        if 'research' in agent_id_lower or 'red' in agent_id_lower:
            return 'research'
        elif 'planning' in agent_id_lower or 'orange' in agent_id_lower:
            return 'planning'
        elif 'development' in agent_id_lower or 'yellow' in agent_id_lower:
            return 'development'
        elif 'budget' in agent_id_lower or 'green' in agent_id_lower:
            return 'budget'
        elif 'market' in agent_id_lower or 'blue' in agent_id_lower:
            return 'market'
        elif 'support' in agent_id_lower or 'purple' in agent_id_lower or 'violet' in agent_id_lower:
            return 'support'
        else:
            return 'unknown'

    async def _store_code_review(self, session: AsyncSession, agent_id: str, pr_data: Dict[str, Any], violations: List[Violation]) -> str:
        """Store code review record in database"""
        try:
            review_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_id}"
            
            # Calculate compliance score
            total_violations = len(violations)
            if total_violations == 0:
                compliance_score = 100.0
            else:
                total_severity = sum(v.severity_score for v in violations)
                max_severity = total_violations * 10
                compliance_score = max(0.0, 100.0 - (total_severity / max_severity * 100))
            
            await session.execute(
                text("""
                    INSERT INTO governance_code_reviews (
                        review_id, agent_id, file_path, file_content,
                        violations, compliance_score, review_type, pr_number
                    ) VALUES (
                        :review_id, :agent_id, :file_path, :file_content,
                        :violations, :compliance_score, :review_type, :pr_number
                    )
                """),
                {
                    'review_id': review_id,
                    'agent_id': agent_id,
                    'file_path': pr_data.get('files', [{}])[0].get('path', 'unknown'),
                    'file_content': json.dumps([f.get('content', '') for f in pr_data.get('files', [])]),
                    'violations': json.dumps([asdict(v) for v in violations]),
                    'compliance_score': compliance_score,
                    'review_type': 'pull_request',
                    'pr_number': pr_data.get('number')
                }
            )
            
            return review_id
            
        except Exception as e:
            logger.error(f"Error storing code review: {e}")
            return f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    async def _determine_enforcement_action(self, agent_profile: AgentProfile, violations: List[Violation]) -> EnforcementAction:
        """Determine appropriate enforcement action based on violations and agent level"""
        
        # Count violations by type
        violation_counts = self._count_violations_by_type(violations)
        
        # Get thresholds for agent level
        thresholds = self.thresholds[agent_profile.level]
        
        # Check for critical violations (immediate action)
        if violation_counts['critical'] > 0:
            return EnforcementAction.BAN
        
        # Check for major violations
        if violation_counts['major'] >= thresholds['major_violations']:
            if agent_profile.suspension_count >= 2:
                return EnforcementAction.BAN
            return EnforcementAction.SUSPEND
        
        # Check for minor violations
        if violation_counts['minor'] >= thresholds['minor_violations']:
            return EnforcementAction.BLOCK
        
        # Check cumulative violations
        total_violations = sum(violation_counts.values())
        if total_violations >= thresholds['minor_violations']:
            return EnforcementAction.BLOCK
        
        return EnforcementAction.WARNING

    def _count_violations_by_type(self, violations: List[Violation]) -> Dict[str, int]:
        """Count violations by type"""
        counts = {'minor': 0, 'major': 0, 'critical': 0}
        for violation in violations:
            counts[violation.violation_type.value] += 1
        return counts

    async def _create_enforcement_record(self, session: AsyncSession, agent_id: str, violations: List[Violation], action: EnforcementAction):
        """Create enforcement record in database"""
        try:
            record_id = f"enforcement_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_id}"
            
            # Determine violation type (use highest severity)
            violation_type = ViolationType.MINOR
            if any(v.violation_type == ViolationType.CRITICAL for v in violations):
                violation_type = ViolationType.CRITICAL
            elif any(v.violation_type == ViolationType.MAJOR for v in violations):
                violation_type = ViolationType.MAJOR
            
            # Calculate duration for suspensions
            duration_hours = 24 if action == EnforcementAction.SUSPEND else None
            
            await session.execute(
                text("""
                    INSERT INTO governance_enforcement_records (
                        record_id, agent_id, violation_type, action_taken,
                        reason, duration_hours, violations, timestamp
                    ) VALUES (
                        :record_id, :agent_id, :violation_type, :action_taken,
                        :reason, :duration_hours, :violations, :timestamp
                    )
                """),
                {
                    'record_id': record_id,
                    'agent_id': agent_id,
                    'violation_type': violation_type.value,
                    'action_taken': action.value,
                    'reason': f"Rule violations: {len(violations)} violations found",
                    'duration_hours': duration_hours,
                    'violations': json.dumps([asdict(v) for v in violations]),
                    'timestamp': datetime.now(timezone.utc)
                }
            )
            
            logger.info(f"Created enforcement record: {record_id}")
            
        except Exception as e:
            logger.error(f"Error creating enforcement record: {e}")
            raise

    async def _update_agent_profile(self, session: AsyncSession, agent_profile: AgentProfile, violations: List[Violation], action: EnforcementAction):
        """Update agent profile in database"""
        try:
            # Update violation counts
            violation_counts = self._count_violations_by_type(violations)
            for violation_type, count in violation_counts.items():
                agent_profile.violations_count[violation_type] += count
            
            # Update last violation timestamp
            if violations:
                agent_profile.last_violation = datetime.now(timezone.utc)
            
            # Update suspension count
            if action == EnforcementAction.SUSPEND:
                agent_profile.suspension_count += 1
            
            # Update performance score (database trigger will handle this)
            agent_profile.updated_at = datetime.now(timezone.utc)
            
            # Update database
            await session.execute(
                text("""
                    UPDATE governance_agents 
                    SET 
                        violations_count = :violations_count,
                        last_violation = :last_violation,
                        suspension_count = :suspension_count,
                        updated_at = :updated_at
                    WHERE agent_id = :agent_id
                """),
                {
                    'violations_count': json.dumps(agent_profile.violations_count),
                    'last_violation': agent_profile.last_violation,
                    'suspension_count': agent_profile.suspension_count,
                    'updated_at': agent_profile.updated_at,
                    'agent_id': agent_profile.agent_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error updating agent profile: {e}")
            raise

    async def _send_notifications(self, agent_id: str, violations: List[Violation], action: EnforcementAction):
        """Send notifications asynchronously with retry logic"""
        for attempt in range(self.max_retries):
            try:
                # Send to N8N workflow
                if self.n8n_webhook_url:
                    await self._send_n8n_notification(agent_id, violations, action)
                
                # Send to Slack
                if self.slack_webhook_url:
                    await self._send_slack_notification(agent_id, violations, action)
                
                # Store notification record
                await self._store_notification(agent_id, violations, action)
                
                break  # Success, exit retry loop
                
            except Exception as e:
                logger.warning(f"Notification attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"All notification attempts failed for agent {agent_id}")

    async def _send_n8n_notification(self, agent_id: str, violations: List[Violation], action: EnforcementAction):
        """Send notification to N8N workflow with retry logic"""
        try:
            payload = {
                'event_type': 'enforcement_action',
                'agent_id': agent_id,
                'action': action.value,
                'violations_count': len(violations),
                'violations': [asdict(v) for v in violations],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    self.n8n_webhook_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        logger.info(f"Successfully sent N8N notification for enforcement action: {action.value}")
                    else:
                        raise Exception(f"N8N notification failed with status: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send N8N notification {action.value}: {e}")
            raise

    async def _send_slack_notification(self, agent_id: str, violations: List[Violation], action: EnforcementAction):
        """Send notification to Slack with retry logic"""
        try:
            # Create Slack message
            if action == EnforcementAction.BAN:
                color = "danger"
                emoji = "🚨"
                message = f"{emoji} *CRITICAL VIOLATION* - Agent {agent_id} has been BANNED"
            elif action == EnforcementAction.SUSPEND:
                color = "warning"
                emoji = "⚠️"
                message = f"{emoji} *MAJOR VIOLATION* - Agent {agent_id} has been SUSPENDED"
            elif action == EnforcementAction.BLOCK:
                color = "warning"
                emoji = "🛑"
                message = f"{emoji} *RULE VIOLATION* - Agent {agent_id} PR BLOCKED"
            else:
                color = "good"
                emoji = "✅"
                message = f"{emoji} *WARNING* - Agent {agent_id} has minor violations"
            
            # Add violation details
            violation_text = "\n".join([f"• {v.rule_name}: {v.description}" for v in violations[:5]])
            if len(violations) > 5:
                violation_text += f"\n• ... and {len(violations) - 5} more violations"
            
            slack_payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": "Cosmic Council Enforcement Action",
                        "text": message,
                        "fields": [
                            {
                                "title": "Agent ID",
                                "value": agent_id,
                                "short": True
                            },
                            {
                                "title": "Action Taken",
                                "value": action.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Violations",
                                "value": violation_text,
                                "short": False
                            }
                        ],
                        "footer": "Cosmic Council Enforcement System",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    self.slack_webhook_url,
                    json=slack_payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        logger.info(f"Successfully sent Slack notification for enforcement action: {action.value}")
                    else:
                        raise Exception(f"Slack notification failed with status: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send Slack notification {action.value}: {e}")
            raise

    async def _store_notification(self, agent_id: str, violations: List[Violation], action: EnforcementAction):
        """Store notification record in database"""
        try:
            async with self.async_session() as session:
                notification_id = f"notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_id}"
                
                await session.execute(
                    text("""
                        INSERT INTO governance_notifications (
                            notification_id, agent_id, notification_type, title, message,
                            data, channels, status, created_at
                        ) VALUES (
                            :notification_id, :agent_id, :notification_type, :title, :message,
                            :data, :channels, :status, :created_at
                        )
                    """),
                    {
                        'notification_id': notification_id,
                        'agent_id': agent_id,
                        'notification_type': 'enforcement',
                        'title': f"Enforcement Action: {action.value.upper()}",
                        'message': f"Agent {agent_id} received {action.value} action due to {len(violations)} violations",
                        'data': json.dumps({
                            'action': action.value,
                            'violations_count': len(violations),
                            'violations': [asdict(v) for v in violations]
                        }),
                        'channels': json.dumps(['slack', 'n8n']),
                        'status': 'sent',
                        'created_at': datetime.now(timezone.utc)
                    }
                )
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"Error storing notification: {e}")

    async def get_agent_statistics(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get agent statistics from database"""
        try:
            async with self.async_session() as session:
                if agent_id:
                    # Get specific agent statistics
                    result = await session.execute(
                        text("SELECT get_agent_statistics(:agent_id)"),
                        {"agent_id": agent_id}
                    )
                    stats = result.scalar()
                    return json.loads(stats) if stats else {}
                else:
                    # Get overall system statistics
                    result = await session.execute(
                        text("SELECT get_governance_system_statistics()")
                    )
                    stats = result.scalar()
                    return json.loads(stats) if stats else {}
                    
        except Exception as e:
            logger.error(f"Error getting agent statistics: {e}")
            return {}

    async def resolve_enforcement_record(self, record_id: str, resolved_by: str, notes: str = ""):
        """Resolve an enforcement record"""
        try:
            async with self.async_session() as session:
                await session.execute(
                    text("""
                        UPDATE governance_enforcement_records 
                        SET 
                            resolved = TRUE,
                            resolved_at = :resolved_at,
                            resolved_by = :resolved_by,
                            notes = :notes
                        WHERE record_id = :record_id
                    """),
                    {
                        'record_id': record_id,
                        'resolved_at': datetime.now(timezone.utc),
                        'resolved_by': resolved_by,
                        'notes': notes
                    }
                )
                
                await session.commit()
                logger.info(f"Resolved enforcement record: {record_id}")
                
        except Exception as e:
            logger.error(f"Error resolving enforcement record: {e}")
            raise

    async def close(self):
        """Close the database connection"""
        await self.engine.dispose()
        logger.info("Enhanced Cosmic Council Enforcement System closed")

# Example usage
async def main():
    """Example usage of the enhanced enforcement system"""
    
    enforcement_system = EnhancedCosmicCouncilEnforcementSystem(
        database_url="postgresql+asyncpg://user:password@localhost/dream_caesar",
        n8n_webhook_url="https://your-n8n-instance.com/webhook/enforcement",
        slack_webhook_url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
        max_retries=3,
        retry_delay=1.0
    )
    
    try:
        # Example PR data
        pr_data = {
            'number': 123,
            'files': [
                {
                    'path': 'research/analysis.py',
                    'content': '''
# Red Owl - Research & Inquiry
import pandas as pd
from typing import List, Dict

def analyze_research_findings(data: List[Dict]) -> Dict[str, Any]:
    """Analyze research findings for relevance and credibility"""
    return {"analysis": "complete"}
'''
                }
            ]
        }
        
        # Review PR
        result = await enforcement_system.review_pull_request(pr_data, "agent_001")
        print(f"PR Review Result: {result}")
        
        # Get agent statistics
        stats = await enforcement_system.get_agent_statistics("agent_001")
        print(f"Agent Statistics: {stats}")
        
        # Get system statistics
        system_stats = await enforcement_system.get_agent_statistics()
        print(f"System Statistics: {system_stats}")
        
    finally:
        await enforcement_system.close()

if __name__ == "__main__":
    asyncio.run(main())
